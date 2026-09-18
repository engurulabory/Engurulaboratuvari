#!/usr/bin/env python3
"""Deterministic offline failure/failover harness for ENGÜRÜ Shared AI Infrastructure™."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

RETRYABLE = {"timeout", "500", "503", "network_loss", "partial_stream"}
NON_RETRYABLE = {"400", "401", "403", "429", "privacy", "commercial_use", "cost", "capability", "context_overflow", "malformed_json", "invalid_structured_output", "tool_call_mismatch"}

@dataclass
class Provider:
    name: str
    local: bool = False
    healthy: bool = True
    production_approved: bool = True
    privacy_verified: bool = True
    commercial_use_verified: bool = True
    cost_verified: bool = True
    estimated_cost: float = 0.0
    supports: set[str] = field(default_factory=lambda: {"text", "reasoning", "structured_output"})
    failures: List[str] = field(default_factory=list)
    calls: int = 0
    consecutive_failures: int = 0
    circuit_open: bool = False

    def execute(self) -> str:
        self.calls += 1
        if self.circuit_open or not self.healthy:
            return "503"
        if self.failures:
            outcome = self.failures.pop(0)
        else:
            outcome = "200"
        if outcome == "200":
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            if self.consecutive_failures >= 3:
                self.circuit_open = True
        return outcome

@dataclass
class Request:
    data_class: str = "PUBLIC"
    required_capabilities: set[str] = field(default_factory=lambda: {"text"})
    cost_ceiling: float = 0.0

@dataclass
class Result:
    state: str
    provider: str | None
    attempts: int
    path: list[str]
    reason: str

def policy_allows(req: Request, p: Provider) -> tuple[bool, str]:
    if not (p.privacy_verified and p.commercial_use_verified and p.cost_verified):
        return False, "critical_metadata"
    if req.data_class == "SECRET" and not p.local:
        return False, "privacy"
    if p.estimated_cost > req.cost_ceiling:
        return False, "cost"
    if not req.required_capabilities.issubset(p.supports):
        return False, "capability"
    if not p.production_approved:
        return False, "authority"
    if p.circuit_open or not p.healthy:
        return False, "health"
    return True, "PASS"

def run(req: Request, providers: list[Provider], max_attempts_per_provider: int = 2) -> Result:
    attempts = 0
    path: list[str] = []

    for p in providers:
        allowed, why = policy_allows(req, p)
        if not allowed:
            path.append(f"{p.name}:SKIP:{why}")
            continue

        local_attempts = 0
        while local_attempts < max_attempts_per_provider:
            outcome = p.execute()
            attempts += 1
            local_attempts += 1
            path.append(f"{p.name}:{outcome}")

            if outcome == "200":
                return Result("PASS", p.name, attempts, path, "verified_success")

            if outcome in {"400", "401", "403", "429", "privacy", "commercial_use", "cost", "capability", "context_overflow", "malformed_json", "invalid_structured_output", "tool_call_mismatch"}:
                break

            if outcome in RETRYABLE:
                continue

            break

    return Result("HOLD", None, attempts, path, "no_safe_provider")
