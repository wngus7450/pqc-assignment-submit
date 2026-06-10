from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pqc_submit.crypto.provider import CryptoProvider, normalize_kem, normalize_sig
from pqc_submit.crypto.symmetric import decrypt_file_bytes, encrypt_file_bytes
from pqc_submit.utils import b64d, b64e, canonical_json, read_key, read_json, write_json


PACKAGE_VERSION = 1


def signature_payload(package: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in package.items() if key != "signature"}
    return canonical_json(unsigned)


def aad_for_package(package: dict[str, Any]) -> bytes:
    aad_fields = {
        "version": package["version"],
        "student_id": package["student_id"],
        "student_name": package["student_name"],
        "kem_algorithm": package["kem_algorithm"],
        "signature_algorithm": package["signature_algorithm"],
        "original_filename": package["original_filename"],
        "submitted_at": package["submitted_at"],
    }
    return canonical_json(aad_fields)


def create_submission(
    provider: CryptoProvider,
    assignment_path: Path,
    professor_public_key_path: Path,
    student_secret_key_path: Path,
    output_path: Path,
    kem_algorithm: str,
    signature_algorithm: str,
    student_id: str,
    student_name: str,
) -> dict[str, Any]:
    kem = normalize_kem(kem_algorithm)
    sig = normalize_sig(signature_algorithm)
    professor_pk = read_key(professor_public_key_path)
    student_sk = read_key(student_secret_key_path)

    encapsulation = provider.kem_encapsulate(kem, professor_pk)
    base_package = {
        "version": PACKAGE_VERSION,
        "student_id": student_id,
        "student_name": student_name,
        "kem_algorithm": kem,
        "signature_algorithm": sig,
        "original_filename": assignment_path.name,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    nonce, encrypted = encrypt_file_bytes(
        assignment_path.read_bytes(),
        encapsulation.shared_secret,
        canonical_json(base_package),
    )
    package = {
        **base_package,
        "kem_ciphertext": b64e(encapsulation.ciphertext),
        "nonce": b64e(nonce),
        "encrypted_file": b64e(encrypted),
    }
    package["signature"] = b64e(provider.sign(sig, student_sk, signature_payload(package)))
    write_json(output_path, package)
    return package


def verify_submission(provider: CryptoProvider, package_path: Path, student_public_key_path: Path) -> bool:
    package = read_json(package_path)
    signature = b64d(package.get("signature", ""))
    student_pk = read_key(student_public_key_path)
    return provider.verify(
        package["signature_algorithm"],
        student_pk,
        signature_payload(package),
        signature,
    )


def open_submission(
    provider: CryptoProvider,
    package_path: Path,
    professor_secret_key_path: Path,
    student_public_key_path: Path,
    output_path: Path,
) -> bytes:
    package = read_json(package_path)
    if not verify_submission(provider, package_path, student_public_key_path):
        raise ValueError("invalid submission or modified package")

    shared_secret = provider.kem_decapsulate(
        package["kem_algorithm"],
        read_key(professor_secret_key_path),
        b64d(package["kem_ciphertext"]),
    )
    plaintext = decrypt_file_bytes(
        b64d(package["encrypted_file"]),
        shared_secret,
        b64d(package["nonce"]),
        aad_for_package(package),
    )
    output_path.write_bytes(plaintext)
    return plaintext
