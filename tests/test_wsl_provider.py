from pathlib import Path

import pytest

from pqc_submit.crypto.wsl_provider import WslOQSProvider
from pqc_submit.package import create_submission, open_submission, verify_submission
from pqc_submit.utils import write_key


@pytest.mark.skipif(not Path("build/oqs_bridge").exists(), reason="build/oqs_bridge is not built")
def test_wsl_oqs_provider_submit_flow(tmp_path: Path) -> None:
    provider = WslOQSProvider()
    professor = provider.kem_keygen("ML-KEM")
    student = provider.sig_keygen("ML-DSA")
    professor_pk = tmp_path / "professor_kem.pub"
    professor_sk = tmp_path / "professor_kem.sec"
    student_pk = tmp_path / "student_sig.pub"
    student_sk = tmp_path / "student_sig.sec"
    assignment = tmp_path / "assignment.txt"
    package = tmp_path / "assignment.pqc"
    opened = tmp_path / "opened.txt"

    write_key(professor_pk, professor.public_key)
    write_key(professor_sk, professor.secret_key)
    write_key(student_pk, student.public_key)
    write_key(student_sk, student.secret_key)
    assignment.write_text("real liboqs provider flow\n", encoding="utf-8")

    create_submission(
        provider,
        assignment,
        professor_pk,
        student_sk,
        package,
        "ML-KEM",
        "ML-DSA",
        "20241234",
        "Hong Gil Dong",
    )

    assert verify_submission(provider, package, student_pk)
    assert open_submission(provider, package, professor_sk, student_pk, opened) == b"real liboqs provider flow\n"
