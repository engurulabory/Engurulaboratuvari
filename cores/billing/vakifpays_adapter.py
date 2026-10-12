from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
import os
from typing import Mapping, Optional, Protocol
from urllib import parse, request

from cores.billing.billing_core import BillingError, PaymentProof


class VakifPaySError(BillingError):
    pass


class FormTransport(Protocol):
    def post(self, url: str, fields: Mapping[str, str]) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class VakifPaySConfig:
    merchant: str
    merchant_user: str
    merchant_password: str
    secret_key: str
    mode: str = "TEST"
    timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> "VakifPaySConfig":
        required = {
            "merchant": os.getenv("VAKIFPAYS_MERCHANT", ""),
            "merchant_user": os.getenv("VAKIFPAYS_MERCHANT_USER", ""),
            "merchant_password": os.getenv("VAKIFPAYS_MERCHANT_PASSWORD", ""),
            "secret_key": os.getenv("VAKIFPAYS_SECRET_KEY", ""),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise VakifPaySError(
                "VakıfPayS credentials are not commissioned: " + ", ".join(missing)
            )
        return cls(
            **required,
            mode=os.getenv("VAKIFPAYS_MODE", "TEST").upper(),
            timeout_seconds=int(os.getenv("VAKIFPAYS_TIMEOUT_SECONDS", "30")),
        )

    @property
    def api_url(self) -> str:
        if self.mode == "TEST":
            return "https://testpos.vakifpays.com.tr/vakifpays/api/v2"
        if self.mode == "LIVE":
            return "https://pos.vakifpays.com.tr/vakifpays/api/v2"
        raise VakifPaySError("VAKIFPAYS_MODE must be TEST or LIVE")

    @property
    def hpp_base_url(self) -> str:
        if self.mode == "TEST":
            return "https://testpos.vakifpays.com.tr/merchant/payment"
        if self.mode == "LIVE":
            return "https://pos.vakifpays.com.tr/payment"
        raise VakifPaySError("VAKIFPAYS_MODE must be TEST or LIVE")


@dataclass(frozen=True)
class HostedPaymentSession:
    merchant_payment_id: str
    session_token: str
    payment_url: str
    amount: Decimal
    currency: str


class UrllibFormTransport:
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds

    def post(self, url: str, fields: Mapping[str, str]) -> Mapping[str, object]:
        body = parse.urlencode(fields).encode("utf-8")
        req = request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except Exception as exc:  # network/provider boundary
            raise VakifPaySError(f"VakıfPayS transport failure: {exc}") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise VakifPaySError("VakıfPayS returned a non-JSON API response") from exc
        if not isinstance(payload, dict):
            raise VakifPaySError("VakıfPayS returned an invalid response envelope")
        return payload


class VakifPaySAdapter:
    """
    Provider adapter for ENGÜRÜ Billing Core™.

    Security boundary:
    - HPP keeps card data outside ENGÜRÜ.
    - browser/RETURNURL callback is never authoritative by itself.
    - verified PaymentProof is emitted only after QUERYTRANSACTION confirms
      provider approval and amount/currency identity.
    """

    APPROVED_CODE = "00"

    def __init__(
        self,
        config: VakifPaySConfig,
        transport: Optional[FormTransport] = None,
    ):
        self.config = config
        self.transport = transport or UrllibFormTransport(config.timeout_seconds)

    def create_hpp_session(
        self,
        *,
        merchant_payment_id: str,
        amount: Decimal,
        currency: str,
        return_url: str,
        customer_id: str,
        session_expiry: Optional[str] = None,
        extra_fields: Optional[Mapping[str, str]] = None,
    ) -> HostedPaymentSession:
        if not merchant_payment_id.strip():
            raise VakifPaySError("merchant_payment_id is required")
        if amount <= 0:
            raise VakifPaySError("amount must be positive")
        if not return_url.startswith("https://"):
            raise VakifPaySError("return_url must use HTTPS")

        fields = self._auth_fields()
        fields.update(
            {
                "ACTION": "SESSIONTOKEN",
                "MERCHANTPAYMENTID": merchant_payment_id,
                "AMOUNT": self._amount(amount),
                "CURRENCY": currency.upper(),
                "RETURNURL": return_url,
                "CUSTOMER": customer_id,
            }
        )
        if session_expiry:
            fields["SESSIONEXPIRY"] = session_expiry
        if extra_fields:
            protected = {
                "ACTION",
                "MERCHANT",
                "MERCHANTUSER",
                "MERCHANTPASSWORD",
                "MERCHANTPAYMENTID",
                "AMOUNT",
                "CURRENCY",
                "RETURNURL",
                "CUSTOMER",
            }
            collision = protected.intersection(extra_fields)
            if collision:
                raise VakifPaySError(
                    "extra_fields cannot override protected fields: "
                    + ", ".join(sorted(collision))
                )
            fields.update({str(k): str(v) for k, v in extra_fields.items()})

        response = self.transport.post(self.config.api_url, fields)
        self._require_approved(response, "SESSIONTOKEN")
        token = str(
            response.get("sessionToken")
            or response.get("sessiontoken")
            or response.get("token")
            or ""
        )
        if not token:
            raise VakifPaySError("Approved SESSIONTOKEN response has no session token")

        return HostedPaymentSession(
            merchant_payment_id=merchant_payment_id,
            session_token=token,
            payment_url=f"{self.config.hpp_base_url}/{token}",
            amount=amount,
            currency=currency.upper(),
        )

    def verify_return_callback(self, callback: Mapping[str, str]) -> bool:
        """
        Verify the current sdSha512 callback signature documented by VakıfPayS.
        This verifies message integrity only; it does NOT prove settlement.
        """
        required = (
            "merchantPaymentId",
            "customerId",
            "sessionToken",
            "responseCode",
            "random",
            "sdSha512",
        )
        if any(not callback.get(name) for name in required):
            return False

        material = "|".join(
            [
                callback["merchantPaymentId"],
                callback["customerId"],
                callback["sessionToken"],
                callback["responseCode"],
                callback["random"],
                self.config.secret_key,
            ]
        )
        expected = hashlib.sha512(material.encode("utf-8")).hexdigest()
        return expected.lower() == callback["sdSha512"].lower()

    def verify_payment(
        self,
        *,
        merchant_payment_id: str,
        expected_amount: Decimal,
        expected_currency: str,
    ) -> PaymentProof:
        response = self.query_transaction(merchant_payment_id=merchant_payment_id)
        self._require_approved(response, "QUERYTRANSACTION")

        transaction = self._transaction_object(response)
        provider_amount = self._decimal(
            transaction.get("amount") or transaction.get("AMOUNT"),
            "amount",
        )
        provider_currency = str(
            transaction.get("currency") or transaction.get("CURRENCY") or ""
        ).upper()
        if provider_amount != expected_amount:
            raise VakifPaySError("VakıfPayS verified amount mismatch")
        if provider_currency != expected_currency.upper():
            raise VakifPaySError("VakıfPayS verified currency mismatch")

        payment_id = str(
            transaction.get("pgTranId")
            or transaction.get("PGTRANID")
            or transaction.get("merchantPaymentId")
            or merchant_payment_id
        )
        return PaymentProof(
            provider="VAKIFPAYS",
            payment_id=payment_id,
            verified=True,
            amount=provider_amount,
            currency=provider_currency,
        )

    def query_transaction(self, *, merchant_payment_id: str) -> Mapping[str, object]:
        fields = self._auth_fields()
        fields.update(
            {
                "ACTION": "QUERYTRANSACTION",
                "MERCHANTPAYMENTID": merchant_payment_id,
            }
        )
        return self.transport.post(self.config.api_url, fields)

    def refund(
        self,
        *,
        pg_tran_id: str,
        amount: Decimal,
        currency: str,
        reflect_commission: bool = False,
    ) -> Mapping[str, object]:
        if amount <= 0:
            raise VakifPaySError("refund amount must be positive")
        fields = self._auth_fields()
        fields.update(
            {
                "ACTION": "REFUND",
                "PGTRANID": pg_tran_id,
                "AMOUNT": self._amount(amount),
                "CURRENCY": currency.upper(),
                "REFLECTCOMMISSION": "Yes" if reflect_commission else "No",
            }
        )
        response = self.transport.post(self.config.api_url, fields)
        self._require_approved(response, "REFUND")
        return response

    def _auth_fields(self) -> dict[str, str]:
        return {
            "MERCHANT": self.config.merchant,
            "MERCHANTUSER": self.config.merchant_user,
            "MERCHANTPASSWORD": self.config.merchant_password,
        }

    @classmethod
    def _require_approved(cls, response: Mapping[str, object], action: str) -> None:
        code = str(response.get("responseCode") or response.get("RESPONSECODE") or "")
        if code != cls.APPROVED_CODE:
            message = str(response.get("responseMsg") or response.get("RESPONSEMSG") or "")
            raise VakifPaySError(f"VakıfPayS {action} not approved: {code} {message}".strip())

    @staticmethod
    def _transaction_object(response: Mapping[str, object]) -> Mapping[str, object]:
        for key in ("transaction", "payment", "response"):
            value = response.get(key)
            if isinstance(value, dict):
                return value
        transactions = response.get("transactions")
        if isinstance(transactions, list) and len(transactions) == 1 and isinstance(transactions[0], dict):
            return transactions[0]
        return response

    @staticmethod
    def _amount(value: Decimal) -> str:
        return format(value.quantize(Decimal("0.01")), "f")

    @staticmethod
    def _decimal(value: object, name: str) -> Decimal:
        if value is None or value == "":
            raise VakifPaySError(f"VakıfPayS verified response has no {name}")
        try:
            return Decimal(str(value))
        except Exception as exc:
            raise VakifPaySError(f"Invalid VakıfPayS {name}") from exc
