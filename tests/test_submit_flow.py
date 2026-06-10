from pathlib import Path

from pqc_submit.crypto.demo_provider import DemoProvider
from pqc_submit.package import create_submission, open_submission, verify_submission
from pqc_submit.utils import write_key


def test_submit_verify_open_flow(tmp_path: Path) -> None:
    provider = DemoProvider()
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
    assignment.write_text("hello pqc\n", encoding="utf-8")

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
    assert open_submission(provider, package, professor_sk, student_pk, opened) == b"hello pqc\n"
    assert opened.read_text(encoding="utf-8") == "hello pqc\n"
