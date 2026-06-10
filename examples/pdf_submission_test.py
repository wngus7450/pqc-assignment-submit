from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

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


def main() -> int:
    provider = DemoProvider()
    output_dir = PROJECT_ROOT / "examples" / "pdf_submission_test_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    professor = provider.kem_keygen("ML-KEM")
    student = provider.sig_keygen("ML-DSA")

    professor_pk = output_dir / "professor_kem.pub"
    professor_sk = output_dir / "professor_kem.sec"
    student_pk = output_dir / "student_sig.pub"
    student_sk = output_dir / "student_sig.sec"
    assignment = output_dir / "assignment.pdf"
    package = output_dir / "assignment.pdf.pqc"
    opened = output_dir / "opened_assignment.pdf"

    pdf_bytes = minimal_pdf_bytes()
    assignment.write_bytes(pdf_bytes)
    write_key(professor_pk, professor.public_key)
    write_key(professor_sk, professor.secret_key)
    write_key(student_pk, student.public_key)
    write_key(student_sk, student.secret_key)

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

    if created["original_filename"] != "assignment.pdf":
        raise RuntimeError("PDF filename was not preserved in the package")
    if not verify_submission(provider, package, student_pk):
        raise RuntimeError("PDF submission verification failed")

    opened_bytes = open_submission(provider, package, professor_sk, student_pk, opened)
    if opened_bytes != pdf_bytes or opened.read_bytes() != pdf_bytes:
        raise RuntimeError("Opened PDF does not match the original PDF")

    print("PDF submission test passed")
    print(f"original PDF: {assignment}")
    print(f"submission package: {package}")
    print(f"opened PDF: {opened}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
