from pathlib import Path

from pqc_submit.crypto.demo_provider import DemoProvider
from pqc_submit.package import create_submission, open_submission, verify_submission
from pqc_submit.utils import write_key


def minimal_pdf_bytes() -> bytes:
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n"
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] "
            b"/Contents 4 0 R >>\n"
            b"endobj\n"
        ),
        (
            b"4 0 obj\n"
            b"<< /Length 44 >>\n"
            b"stream\n"
            b"BT /F1 12 Tf 72 96 Td (PQC PDF test) Tj ET\n"
            b"endstream\n"
            b"endobj\n"
        ),
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Root 1 0 R /Size {len(objects) + 1} >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


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


def test_pdf_submit_verify_open_flow(tmp_path: Path) -> None:
    provider = DemoProvider()
    professor = provider.kem_keygen("ML-KEM")
    student = provider.sig_keygen("ML-DSA")
    professor_pk = tmp_path / "professor_kem.pub"
    professor_sk = tmp_path / "professor_kem.sec"
    student_pk = tmp_path / "student_sig.pub"
    student_sk = tmp_path / "student_sig.sec"
    assignment = tmp_path / "assignment.pdf"
    package = tmp_path / "assignment.pdf.pqc"
    opened = tmp_path / "opened_assignment.pdf"
    pdf_bytes = minimal_pdf_bytes()

    write_key(professor_pk, professor.public_key)
    write_key(professor_sk, professor.secret_key)
    write_key(student_pk, student.public_key)
    write_key(student_sk, student.secret_key)
    assignment.write_bytes(pdf_bytes)

    created = create_submission(
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

    assert created["original_filename"] == "assignment.pdf"
    assert verify_submission(provider, package, student_pk)
    assert open_submission(provider, package, professor_sk, student_pk, opened) == pdf_bytes
    assert opened.read_bytes() == pdf_bytes
