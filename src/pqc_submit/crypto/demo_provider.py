from __future__ import annotations

import hmac
import os
from hashlib import sha256

from pqc_submit.crypto.provider import Encapsulation, KeyPair, normalize_kem, normalize_sig


class DemoProvider:
    """Workflow-only provider. This is not a real post-quantum implementation."""

    name = "demo"

    def kem_keygen(self, algorithm: str) -> KeyPair:
        alg = normalize_kem(algorithm)
        seed = os.urandom(32)
        public_key = b"DEMO-KEM-PK:" + alg.encode() + b":" + seed
        secret_key = b"DEMO-KEM-SK:" + alg.encode() + b":" + seed
        return KeyPair(public_key=public_key, secret_key=secret_key)

    def kem_encapsulate(self, algorithm: str, public_key: bytes) -> Encapsulation:
        alg = normalize_kem(algorithm)
        ephemeral = os.urandom(32)
        shared_secret = sha256(b"DEMO-KEM-SS:" + alg.encode() + b":" + public_key + ephemeral).digest()
        ciphertext = b"DEMO-KEM-CT:" + alg.encode() + b":" + ephemeral
        return Encapsulation(ciphertext=ciphertext, shared_secret=shared_secret)

    def kem_decapsulate(self, algorithm: str, secret_key: bytes, ciphertext: bytes) -> bytes:
        alg = normalize_kem(algorithm)
        parts = secret_key.split(b":", 2)
        ct_parts = ciphertext.split(b":", 2)
        if len(parts) != 3 or len(ct_parts) != 3:
            raise ValueError("invalid demo KEM key or ciphertext")
        if parts[0] != b"DEMO-KEM-SK" or ct_parts[0] != b"DEMO-KEM-CT":
            raise ValueError("invalid demo KEM key or ciphertext")
        if parts[1].decode() != alg or ct_parts[1].decode() != alg:
            raise ValueError("KEM algorithm mismatch")
        public_key = b"DEMO-KEM-PK:" + parts[1] + b":" + parts[2]
        return sha256(b"DEMO-KEM-SS:" + alg.encode() + b":" + public_key + ct_parts[2]).digest()

    def sig_keygen(self, algorithm: str) -> KeyPair:
        alg = normalize_sig(algorithm)
        key = os.urandom(32)
        public_key = b"DEMO-SIG-PK:" + alg.encode() + b":" + key
        secret_key = b"DEMO-SIG-SK:" + alg.encode() + b":" + key
        return KeyPair(public_key=public_key, secret_key=secret_key)

    def sign(self, algorithm: str, secret_key: bytes, message: bytes) -> bytes:
        alg = normalize_sig(algorithm)
        parts = secret_key.split(b":", 2)
        if len(parts) != 3 or parts[0] != b"DEMO-SIG-SK" or parts[1].decode() != alg:
            raise ValueError("invalid demo signature secret key")
        public_key = b"DEMO-SIG-PK:" + parts[1] + b":" + parts[2]
        return hmac.new(public_key, b"DEMO-SIGN:" + alg.encode() + b":" + message, sha256).digest()

    def verify(self, algorithm: str, public_key: bytes, message: bytes, signature: bytes) -> bool:
        alg = normalize_sig(algorithm)
        parts = public_key.split(b":", 2)
        if len(parts) != 3 or parts[0] != b"DEMO-SIG-PK" or parts[1].decode() != alg:
            return False
        expected = hmac.new(public_key, b"DEMO-SIGN:" + alg.encode() + b":" + message, sha256).digest()
        return hmac.compare_digest(expected, signature)
