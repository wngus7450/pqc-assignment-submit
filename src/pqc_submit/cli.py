from __future__ import annotations

import argparse
from pathlib import Path

from pqc_submit.crypto.demo_provider import DemoProvider
from pqc_submit.crypto.provider import normalize_kem, normalize_sig
from pqc_submit.package import create_submission, open_submission, verify_submission
from pqc_submit.utils import write_key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pqc-submit")
    parser.add_argument("--provider", choices=["demo", "wsl-oqs"], default="demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    professor = subparsers.add_parser("professor-keygen")
    professor.add_argument("--kem", required=True)
    professor.add_argument("--public-out", type=Path, default=Path("professor_kem.pub"))
    professor.add_argument("--secret-out", type=Path, default=Path("professor_kem.sec"))

    student = subparsers.add_parser("student-keygen")
    student.add_argument("--sig", required=True)
    student.add_argument("--public-out", type=Path, default=Path("student_sig.pub"))
    student.add_argument("--secret-out", type=Path, default=Path("student_sig.sec"))

    submit = subparsers.add_parser("submit")
    submit.add_argument("assignment", type=Path)
    submit.add_argument("--professor-pk", type=Path, required=True)
    submit.add_argument("--student-sk", type=Path, required=True)
    submit.add_argument("--kem", required=True)
    submit.add_argument("--sig", required=True)
    submit.add_argument("--student-id", required=True)
    submit.add_argument("--student-name", required=True)
    submit.add_argument("--out", type=Path)

    verify = subparsers.add_parser("verify")
    verify.add_argument("package", type=Path)
    verify.add_argument("--student-pk", type=Path, required=True)

    open_cmd = subparsers.add_parser("open")
    open_cmd.add_argument("package", type=Path)
    open_cmd.add_argument("--professor-sk", type=Path, required=True)
    open_cmd.add_argument("--student-pk", type=Path, required=True)
    open_cmd.add_argument("--out", type=Path)
    return parser


def make_provider(name: str):
    if name == "demo":
        return DemoProvider()
    if name == "wsl-oqs":
        from pqc_submit.crypto.wsl_provider import WslOQSProvider

        return WslOQSProvider()
    raise ValueError(f"unknown provider: {name}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    provider = make_provider(args.provider)

    if args.command == "professor-keygen":
        keypair = provider.kem_keygen(normalize_kem(args.kem))
        write_key(args.public_out, keypair.public_key)
        write_key(args.secret_out, keypair.secret_key)
        print(f"created {args.public_out} and {args.secret_out}")
        return 0

    if args.command == "student-keygen":
        keypair = provider.sig_keygen(normalize_sig(args.sig))
        write_key(args.public_out, keypair.public_key)
        write_key(args.secret_out, keypair.secret_key)
        print(f"created {args.public_out} and {args.secret_out}")
        return 0

    if args.command == "submit":
        output = args.out or args.assignment.with_suffix(args.assignment.suffix + ".pqc")
        create_submission(
            provider,
            args.assignment,
            args.professor_pk,
            args.student_sk,
            output,
            args.kem,
            args.sig,
            args.student_id,
            args.student_name,
        )
        print(f"submit success: {output}")
        return 0

    if args.command == "verify":
        if verify_submission(provider, args.package, args.student_pk):
            print("valid submission")
            return 0
        print("invalid submission or modified package")
        return 1

    if args.command == "open":
        output = args.out or Path(args.package.stem)
        try:
            open_submission(provider, args.package, args.professor_sk, args.student_pk, output)
        except Exception as exc:
            print(f"decryption failed: {exc}")
            return 1
        print(f"open success: {output}")
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
