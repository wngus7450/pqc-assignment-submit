from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from pqc_submit.crypto.provider import Encapsulation, KeyPair, normalize_kem, normalize_sig


class WslOQSProvider:
    """Provider that calls the vendored liboqs-analysis through a WSL bridge."""

    name = "wsl-oqs"

    def __init__(self, repo_path: Path | None = None) -> None:
        self.project_root = Path.cwd()
        self.repo_path = repo_path or Path("vendor/liboqs-analysis")
        self.bridge_path = Path("build/oqs_bridge")

    def kem_keygen(self, algorithm: str) -> KeyPair:
        data = self._run("kem-keygen", normalize_kem(algorithm))
        return KeyPair(bytes.fromhex(data["public_key"]), bytes.fromhex(data["secret_key"]))

    def kem_encapsulate(self, algorithm: str, public_key: bytes) -> Encapsulation:
        data = self._run("kem-encaps", normalize_kem(algorithm), public_key.hex())
        return Encapsulation(bytes.fromhex(data["ciphertext"]), bytes.fromhex(data["shared_secret"]))

    def kem_decapsulate(self, algorithm: str, secret_key: bytes, ciphertext: bytes) -> bytes:
        data = self._run("kem-decaps", normalize_kem(algorithm), secret_key.hex(), ciphertext.hex())
        return bytes.fromhex(data["shared_secret"])

    def sig_keygen(self, algorithm: str) -> KeyPair:
        data = self._run("sig-keygen", normalize_sig(algorithm))
        return KeyPair(bytes.fromhex(data["public_key"]), bytes.fromhex(data["secret_key"]))

    def sign(self, algorithm: str, secret_key: bytes, message: bytes) -> bytes:
        data = self._run("sign", normalize_sig(algorithm), secret_key.hex(), message.hex())
        return bytes.fromhex(data["signature"])

    def verify(self, algorithm: str, public_key: bytes, message: bytes, signature: bytes) -> bool:
        data = self._run("verify", normalize_sig(algorithm), public_key.hex(), message.hex(), signature.hex())
        return bool(data["valid"])

    def _run(self, command: str, algorithm: str, *hex_args: str) -> dict:
        if not (self.project_root / self.bridge_path).exists():
            raise RuntimeError("missing build/oqs_bridge; build it in WSL with: make oqs-bridge")

        if os.name == "nt":
            cmd = [
                "wsl.exe",
                "--cd",
                str(self.project_root),
                "-e",
                f"./{self.bridge_path.as_posix()}",
                command,
                algorithm,
                *hex_args,
            ]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        else:
            cmd = [f"./{self.bridge_path.as_posix()}", command, algorithm, *hex_args]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, cwd=self.project_root)

        if result.returncode != 0:
            stderr = result.stderr.strip() or "unknown bridge error"
            raise RuntimeError(f"WslOQSProvider bridge failed: {stderr}")
        return json.loads(result.stdout)
