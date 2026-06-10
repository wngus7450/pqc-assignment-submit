from __future__ import annotations

from pqc_submit.crypto.provider import CryptoProvider


class OQSProvider:
    """Placeholder for a direct liboqs binding provider."""

    name = "oqs"

    def __init__(self) -> None:
        raise RuntimeError(
            "OQSProvider is an interface placeholder. Use DemoProvider for local workflow "
            "tests or WslOQSProvider for the vendored WSL liboqs-analysis project."
        )


def provider_type_hint() -> type[CryptoProvider]:
    return CryptoProvider
