#!/usr/bin/env python3
"""Executable, isolated preparation simulation. NOT a native P02 writer or issuer.

The delivered ZIP is pinned by SHA256
b513794c84854fc12f9ab231d46e1c30438ba1fc4d7053f9534b83b6a319a26f.
It has its own __main__.py entrypoint, a positive simulated P02.S01.01 CAS/readback
and 18 adversarial cases, plus 4/4 exact Mac source byte pins.

Crucial: this is an *integration-test fixture*, not a production implementation.
No real signer/issuer, no canonical state ownership, no P-256 trust-root binding.
JSON state + journal is not one crash-atomic transaction, and has no proof of
safe concurrent writers. Native 0/6 and P02 0/12 remain HOLD.
"""
from pathlib import Path

DELIVERY_ZIP_SHA256 = "b513794c84854fc12f9ab231d46e1c30438ba1fc4d7053f9534b83b6a319a26f"
NATIVE_ACCEPTANCE = "0/6_HOLD"
P02_ACCEPTANCE = "0/12_HOLD"
VERIFIED_FINISH = "HOLD"

def qualified_production_transition(*args, **kwargs):
    """A production transition must invoke the real owner-authorized P02 writer."""
    raise RuntimeError("HOLD_NATIVE_CANONICAL_WRITER_AND_SIGNER_AUTHORITY")

if __name__ == "__main__":
    print("STATE=SIMULATION_DELIVERY_ONLY")
    print("ZIP_SHA256="+DELIVERY_ZIP_SHA256)
    print("NATIVE="+NATIVE_ACCEPTANCE+" P02="+P02_ACCEPTANCE+" FINISH="+VERIFIED_FINISH)
