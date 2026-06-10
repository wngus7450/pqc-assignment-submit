from pathlib import Path

from pqc_submit.crypto.demo_provider import DemoProvider
from pqc_submit.package import create_submission, verify_submission
from pqc_submit.utils import read_json, write_json, write_key


def test_tampered_package_fails_verification(tmp_path: Path) -> None:
    provider = DemoProvider()
    professor = provider.kem_keygen("HQC")
    student = provider.sig_keygen("SLH-DSA")
    professor_pk = tmp_path / "professor_kem.pub"
    student_pk = tmp_path / "student_sig.pub"
    student_sk = tmp_path / "student_sig.sec"
    assignment = tmp_path / "assignment.txt"
    package = tmp_path / "assignment.pqc"

    write_key(professor_pk, professor.public_key)
    write_key(student_pk, student.public_key)
    write_key(student_sk, student.secret_key)
    assignment.write_text("original\n", encoding="utf-8")

    create_submission(
        provider,
        assignment,
        professor_pk,
        student_sk,
        package,
        "HQC",
        "SLH-DSA",
        "20241234",
        "Hong Gil Dong",
    )

    data = read_json(package)
    data["student_name"] = "Modified Name"
    write_json(package, data)

    assert not verify_submission(provider, package, student_pk)
