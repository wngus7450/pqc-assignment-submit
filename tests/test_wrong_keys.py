from pathlib import Path

import pytest

from pqc_submit.crypto.demo_provider import DemoProvider
from pqc_submit.package import create_submission, open_submission, verify_submission
from pqc_submit.utils import write_key


def test_wrong_student_key_fails_verification(tmp_path: Path) -> None:
    provider = DemoProvider()
    professor = provider.kem_keygen("ML-KEM")
    student = provider.sig_keygen("ML-DSA")
    other_student = provider.sig_keygen("ML-DSA")
    professor_pk = tmp_path / "professor_kem.pub"
    student_sk = tmp_path / "student_sig.sec"
    other_student_pk = tmp_path / "other_student_sig.pub"
    assignment = tmp_path / "assignment.txt"
    package = tmp_path / "assignment.pqc"

    write_key(professor_pk, professor.public_key)
    write_key(student_sk, student.secret_key)
    write_key(other_student_pk, other_student.public_key)
    assignment.write_text("submission\n", encoding="utf-8")

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

    assert not verify_submission(provider, package, other_student_pk)


def test_wrong_professor_key_fails_open(tmp_path: Path) -> None:
    provider = DemoProvider()
    professor = provider.kem_keygen("ML-KEM")
    other_professor = provider.kem_keygen("ML-KEM")
    student = provider.sig_keygen("ML-DSA")
    professor_pk = tmp_path / "professor_kem.pub"
    other_professor_sk = tmp_path / "other_professor_kem.sec"
    student_pk = tmp_path / "student_sig.pub"
    student_sk = tmp_path / "student_sig.sec"
    assignment = tmp_path / "assignment.txt"
    package = tmp_path / "assignment.pqc"

    write_key(professor_pk, professor.public_key)
    write_key(other_professor_sk, other_professor.secret_key)
    write_key(student_pk, student.public_key)
    write_key(student_sk, student.secret_key)
    assignment.write_text("submission\n", encoding="utf-8")

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

    with pytest.raises(Exception):
        open_submission(provider, package, other_professor_sk, student_pk, tmp_path / "opened.txt")
