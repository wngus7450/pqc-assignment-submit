from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


KEM_ALIASES = {
    "ML-KEM": "ML-KEM-512",
    "ML-KEM-512": "ML-KEM-512",
    "HQC": "HQC-128",
    "HQC-128": "HQC-128",
}

SIG_ALIASES = {
    "ML-DSA": "ML-DSA-44",
    "ML-DSA-44": "ML-DSA-44",
    "SLH-DSA": "SLH_DSA_PURE_SHA2_128S",
    "SLH_DSA_PURE_SHA2_128S": "SLH_DSA_PURE_SHA2_128S",
}


@dataclass(frozen=True)
class KeyPair:
    public_key: bytes
    secret_key: bytes


@dataclass(frozen=True)
class Encapsulation:
    ciphertext: bytes
    shared_secret: bytes


class CryptoProvider(Protocol):
    name: str

    def kem_keygen(self, algorithm: str) -> KeyPair:
        ...

    def kem_encapsulate(self, algorithm: str, public_key: bytes) -> Encapsulation:
        ...

    def kem_decapsulate(self, algorithm: str, secret_key: bytes, ciphertext: bytes) -> bytes:
        ...

    def sig_keygen(self, algorithm: str) -> KeyPair:
        ...

    def sign(self, algorithm: str, secret_key: bytes, message: bytes) -> bytes:
        ...

    def verify(self, algorithm: str, public_key: bytes, message: bytes, signature: bytes) -> bool:
        ...


def normalize_kem(name: str) -> str:
    try:
        return KEM_ALIASES[name.upper()]
    except KeyError as exc:
        supported = ", ".join(sorted(KEM_ALIASES))
        raise ValueError(f"unsupported KEM algorithm {name!r}; supported: {supported}") from exc


def normalize_sig(name: str) -> str:
    normalized = name.upper().replace("-", "_") if name.upper().startswith("SLH") else name.upper()
    if name.upper() in SIG_ALIASES:
        return SIG_ALIASES[name.upper()]
    if normalized in SIG_ALIASES:
        return SIG_ALIASES[normalized]
    supported = ", ".join(sorted(SIG_ALIASES))
    raise ValueError(f"unsupported signature algorithm {name!r}; supported: {supported}")
