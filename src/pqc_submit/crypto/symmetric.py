from __future__ import annotations

import os
from hashlib import sha256

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def derive_aes_key(shared_secret: bytes) -> bytes:
    return sha256(b"pqc-submit:aes-gcm:" + shared_secret).digest()


def encrypt_file_bytes(plaintext: bytes, shared_secret: bytes, aad: bytes) -> tuple[bytes, bytes]:
    key = derive_aes_key(shared_secret)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce, aesgcm.encrypt(nonce, plaintext, aad)


def decrypt_file_bytes(ciphertext: bytes, shared_secret: bytes, nonce: bytes, aad: bytes) -> bytes:
    key = derive_aes_key(shared_secret)
    return AESGCM(key).decrypt(nonce, ciphertext, aad)
