# 양자내성 암호 기반 온라인 과제 제출 암호화 및 검증 시스템

## 1. 프로젝트 한 줄 설명

본 프로젝트는 학생이 온라인으로 과제를 제출할 때, 과제 파일을 암호화하고 전자서명을 적용하여
교수 또는 조교가 제출물의 기밀성, 무결성, 제출자 인증 여부를 확인할 수 있도록 구현한
Python 기반 CLI 시제품이다.

본 프로젝트가 확인하고자 하는 핵심 내용은 다음과 같다.

```text
1. 과제 파일을 교수만 열 수 있는가?
2. 제출물이 중간에 변조되지 않았는가?
3. 실제 해당 학생이 제출한 파일인가?
4. 양자컴퓨터 공격을 고려한 양자내성 암호 알고리즘을 적용할 수 있는가?
```

현재 구현은 실제 웹사이트 형태의 온라인 제출 서비스가 아니라, 온라인 과제 제출 시스템에서
필요한 핵심 보안 흐름을 명령어로 실행하고 검증하는 CLI(Command Line Interface) 프로그램이다.

## 2. 프로젝트 필요성

일반적인 온라인 과제 제출 환경에서는 다음과 같은 보안 문제가 발생할 수 있다.

| 문제 | 예시 |
|---|---|
| 파일 노출 | 제출 파일이 중간에 유출되어 다른 사람이 내용을 볼 수 있음 |
| 파일 변조 | 제출 후 파일 내용이나 학생 정보가 변경될 수 있음 |
| 제출자 위조 | 다른 사람이 특정 학생인 것처럼 제출할 수 있음 |
| 미래 보안 위협 | 기존 공개키 암호가 양자컴퓨터에 의해 약해질 가능성이 있음 |

본 프로젝트는 이러한 문제를 해결하기 위해 다음 보안 기능을 구현한다.

| 보안 목표 | 구현 방식 |
|---|---|
| 기밀성 | 과제 파일을 AES-GCM으로 암호화하고, 교수만 복호화할 수 있도록 KEM을 사용 |
| 무결성 | 제출 패키지 전체에 전자서명을 적용하여 변조 여부 검출 |
| 제출자 인증 | 학생 개인키로 서명하고 학생 공개키로 검증 |
| 양자내성 | ML-KEM, HQC, ML-DSA, SLH-DSA 계열 알고리즘 사용 |

## 3. 전체 동작 흐름

시스템의 전체 흐름은 다음과 같다.

```text
교수 KEM 키 생성
  ↓
학생 서명 키 생성
  ↓
학생이 과제 파일 제출 패키지(.pqc) 생성
  ↓
교수/조교가 학생 공개키로 제출물 검증
  ↓
교수가 교수 개인키로 제출 파일 복호화
```

프로그램 내부 구조는 다음과 같다.

```text
사용자 명령어
  ↓
src/pqc_submit/cli.py
  ↓
src/pqc_submit/package.py
  ↓
src/pqc_submit/crypto/
  ↓
DemoProvider 또는 WslOQSProvider
  ↓
실제 암호화 / 서명 / 검증
```

`DemoProvider`는 전체 제출 흐름을 빠르게 확인하기 위한 시연용 Provider이다.
`WslOQSProvider`는 WSL에서 빌드된 실제 `liboqs-analysis` 라이브러리를 호출하는 Provider이다.

## 4. 프로젝트 구조

```text
.
├─ README.md
├─ PQC-submit.md
├─ pyproject.toml
├─ Makefile
├─ examples/
│  ├─ demo_assignment.txt
│  └─ pdf_submission_test.py
├─ src/
│  └─ pqc_submit/
│     ├─ cli.py
│     ├─ package.py
│     ├─ utils.py
│     └─ crypto/
│        ├─ provider.py
│        ├─ demo_provider.py
│        ├─ wsl_provider.py
│        ├─ oqs_provider.py
│        └─ symmetric.py
├─ bridge/
│  ├─ README.md
│  └─ oqs_bridge.c
├─ tests/
│  ├─ test_submit_flow.py
│  ├─ test_tamper_detection.py
│  ├─ test_wrong_keys.py
│  └─ test_wsl_provider.py
└─ vendor/
   └─ liboqs-analysis/
```

주요 파일과 폴더의 역할은 다음과 같다.

| 파일 또는 폴더 | 역할 |
|---|---|
| `src/pqc_submit/cli.py` | 사용자가 입력한 명령어 처리 |
| `src/pqc_submit/package.py` | `.pqc` 제출 패키지 생성, 검증, 복호화 |
| `src/pqc_submit/crypto/symmetric.py` | AES-GCM 기반 실제 파일 암호화 |
| `src/pqc_submit/crypto/provider.py` | 암호 Provider 공통 규칙 정의 |
| `src/pqc_submit/crypto/demo_provider.py` | 시연 및 테스트용 Provider |
| `src/pqc_submit/crypto/wsl_provider.py` | WSL bridge를 통해 실제 liboqs 호출 |
| `bridge/oqs_bridge.c` | Python과 C 기반 liboqs 사이의 연결 프로그램 |
| `vendor/liboqs-analysis/` | 실제 양자내성 암호 구현이 포함된 외부 라이브러리 |
| `tests/` | 프로젝트 기능 자동 검증 |
| `examples/pdf_submission_test.py` | 사용자가 직접 실행할 수 있는 PDF 제출 테스트 코드 |

## 5. 사용 알고리즘

`vendor/liboqs-analysis`에는 여러 양자내성 암호 알고리즘이 포함되어 있다.
본 프로젝트에서는 과제 제출 흐름에 필요한 대표 알고리즘 네 가지를 사용한다.

| 역할 | 알고리즘 | 이유 |
|---|---|---|
| KEM | `ML-KEM-512` | 양자내성 키 교환/키 캡슐화의 대표 알고리즘 |
| KEM | `HQC-128` | ML-KEM과 다른 기반의 비교/백업용 KEM |
| 전자서명 | `ML-DSA-44` | 양자내성 전자서명의 대표 알고리즘 |
| 전자서명 | `SLH_DSA_PURE_SHA2_128S` | 해시 기반의 비교/백업용 전자서명 |

KEM은 과제 파일 자체를 직접 암호화하는 알고리즘이 아니라, 과제 파일 암호화에 사용할
비밀값을 안전하게 공유하기 위한 알고리즘이다.

실제 과제 파일은 AES-GCM으로 암호화하며, AES-GCM에 사용할 키는 KEM에서 나온 공유
비밀값으로부터 생성한다.

## 6. bridge가 필요한 이유

Python 코드는 `vendor/liboqs-analysis` 안의 C 함수를 직접 호출하지 않는다.
따라서 Python 요청을 C 라이브러리 호출로 변환하는 `bridge/oqs_bridge.c`가 필요하다.

`--provider wsl-oqs`를 사용할 때의 실제 흐름은 다음과 같다.

```text
Python 코드
  ↓
WslOQSProvider
  ↓
build/oqs_bridge 실행
  ↓
vendor/liboqs-analysis의 C API 호출
  ↓
ML-KEM / HQC / ML-DSA / SLH-DSA 실행
```

반대로 `--provider demo`를 사용할 때는 bridge를 사용하지 않는다.

## 7. 기본 사용 예시

### 7.1 교수 KEM 키 생성

```bash
pqc-submit professor-keygen --kem ML-KEM
```

생성 파일:

```text
professor_kem.pub
professor_kem.sec
```

### 7.2 학생 서명 키 생성

```bash
pqc-submit student-keygen --sig ML-DSA
```

생성 파일:

```text
student_sig.pub
student_sig.sec
```

### 7.3 제출 패키지 생성

```bash
pqc-submit submit examples/demo_assignment.txt \
  --professor-pk professor_kem.pub \
  --student-sk student_sig.sec \
  --kem ML-KEM \
  --sig ML-DSA \
  --student-id 20241234 \
  --student-name "Hong Gil Dong"
```

결과 파일:

```text
examples/demo_assignment.txt.pqc
```

### 7.4 제출물 검증

```bash
pqc-submit verify examples/demo_assignment.txt.pqc \
  --student-pk student_sig.pub
```

정상 결과:

```text
valid submission
```

### 7.5 제출물 복호화

```bash
pqc-submit open examples/demo_assignment.txt.pqc \
  --professor-sk professor_kem.sec \
  --student-pk student_sig.pub \
  --out opened_demo_assignment.txt
```

정상 결과:

```text
open success: opened_demo_assignment.txt
```

## 8. 테스트 실행 방법

### 8.1 자동 테스트 실행

프로젝트 루트에서 다음 명령을 실행한다.

```bash
python -m pytest
```

Windows에서 `python` 명령이 실제 Python으로 연결되어 있지 않은 경우 WSL에서 실행할 수 있다.

```bash
cd '/mnt/c/Users/wngus/Desktop/소프트웨어의 실제/양자내성 암호 기반 온라인 과제 제출 암호화 및 검증 시스템'
python3 -m pytest
```

현재 확인한 테스트 결과는 다음과 같다.

```text
6 passed in 0.62s
```

테스트는 다음 내용을 확인한다.

| 테스트 | 확인 내용 |
|---|---|
| `test_submit_flow.py` | TXT와 PDF 파일의 정상 제출, 검증, 복호화가 되는지 확인 |
| `test_tamper_detection.py` | 제출 패키지를 변조하면 검증이 실패하는지 확인 |
| `test_wrong_keys.py` | 다른 학생 키 또는 다른 교수 키를 쓰면 실패하는지 확인 |
| `test_wsl_provider.py` | 실제 liboqs bridge 연동이 되는지 확인 |

### 8.2 직접 실행 가능한 PDF 테스트 코드

`pytest`와 별도로 사용자가 직접 실행할 수 있는 PDF 테스트 코드를 제공한다.

```text
examples/pdf_submission_test.py
```

이 코드는 테스트용 PDF 파일을 직접 생성한 뒤 다음 과정을 수행한다.

```text
1. 교수 KEM 키 생성
2. 학생 전자서명 키 생성
3. 테스트용 assignment.pdf 생성
4. assignment.pdf.pqc 제출 패키지 생성
5. 학생 공개키로 제출 패키지 검증
6. 교수 개인키로 opened_assignment.pdf 복호화
7. 원본 PDF와 복호화된 PDF가 같은지 비교
```

실행 명령은 다음과 같다.

```bash
python examples/pdf_submission_test.py
```

WSL 환경에서는 다음처럼 실행할 수 있다.

```bash
python3 examples/pdf_submission_test.py
```

정상 실행 결과는 다음과 같은 형태이다.

```text
PDF submission test passed
original PDF: .../examples/pdf_submission_test_output/assignment.pdf
submission package: .../examples/pdf_submission_test_output/assignment.pdf.pqc
opened PDF: .../examples/pdf_submission_test_output/opened_assignment.pdf
```

이 스크립트가 생성하는 파일은 `examples/pdf_submission_test_output/`에 저장되며, 해당 폴더는
Git에 올라가지 않도록 `.gitignore`에 등록되어 있다.

## 9. 상세 설명 문서

과제 제출용 상세 설명은 `PQC-submit.md`에 작성되어 있다.
해당 문서에는 프로젝트 목적, 구조, 알고리즘 선택 이유, bridge 역할, 테스트 방식이 더 자세히
정리되어 있다.
