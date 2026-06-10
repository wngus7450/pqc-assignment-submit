# 양자내성 암호 기반 온라인 과제 제출 암호화 및 검증 시스템

## 1. 프로젝트 개요

본 프로젝트는 온라인 과제 제출 과정에서 발생할 수 있는 보안 문제를 해결하기 위해
양자내성 암호(Post-Quantum Cryptography, PQC)를 적용한 과제 제출 암호화 및 검증
시스템이다.

일반적인 온라인 과제 제출 방식은 파일을 업로드하는 기능 자체에는 초점이 맞춰져 있지만,
다음과 같은 보안 문제를 충분히 고려하지 못할 수 있다.

```text
1. 제출 파일이 중간에 노출될 수 있다.
2. 제출 후 파일 내용이나 학생 정보가 변조될 수 있다.
3. 다른 사람이 특정 학생인 것처럼 제출할 수 있다.
4. 미래의 양자컴퓨터 환경에서 기존 공개키 암호가 약해질 수 있다.
```

이 프로젝트는 이러한 문제를 해결하기 위해 학생의 과제 파일을 암호화하고, 제출물 전체에
전자서명을 적용하며, 교수 또는 조교가 제출물의 진위와 변조 여부를 검증할 수 있도록
구현하였다.

현재 구현은 실제 웹 기반 서비스가 아니라, 온라인 과제 제출 시스템의 보안 구조를 검증하기
위한 Python CLI 기반 시제품이다. 즉, 실제 웹 화면은 없지만 과제 제출 시스템 내부에서
필요한 핵심 보안 흐름을 명령어로 실행할 수 있도록 구성되어 있다.

## 2. 프로젝트 목적

본 프로젝트의 목적은 단순히 파일을 암호화하는 것이 아니라, 온라인 과제 제출이라는 구체적인
상황에서 필요한 보안 요구사항을 함께 만족하는 것이다.

주요 목적은 다음과 같다.

| 목적 | 설명 |
|---|---|
| 과제 파일 기밀성 보장 | 제출된 과제 파일은 교수만 열어볼 수 있어야 한다. |
| 제출물 무결성 검증 | 제출 후 파일이나 메타데이터가 변경되면 검증에 실패해야 한다. |
| 제출자 인증 | 제출물이 실제 해당 학생의 개인키로 서명되었는지 확인해야 한다. |
| 양자내성 암호 적용 | 양자컴퓨터 공격 가능성을 고려한 PQC 알고리즘을 사용해야 한다. |
| 알고리즘 조합 비교 가능 | KEM과 전자서명 알고리즘을 조합하여 실험할 수 있어야 한다. |

## 3. 핵심 개념 설명

### 3.1 양자내성 암호

양자내성 암호는 미래의 양자컴퓨터가 등장하더라도 쉽게 깨지지 않도록 설계된 암호 방식이다.

현재 널리 사용되는 RSA, ECDSA, ECDH 같은 공개키 암호는 충분히 강력한 양자컴퓨터가 등장할
경우 Shor 알고리즘에 의해 안전성이 크게 약해질 수 있다. 따라서 장기적으로 보호해야 하는
데이터나 미래 환경을 고려하는 시스템에서는 양자내성 암호를 검토할 필요가 있다.

본 프로젝트에서는 양자내성 암호 알고리즘을 직접 새로 설계하지 않고, `vendor/liboqs-analysis`
안의 liboqs 기반 구현을 사용한다.

### 3.2 KEM

KEM은 Key Encapsulation Mechanism의 약자이다.

쉽게 말하면, 두 사람이 같은 비밀값을 안전하게 공유하기 위한 공개키 기반 방식이다.
본 프로젝트에서는 학생이 교수의 공개키를 사용하여 공유 비밀값을 만들고, 교수는 자신의
개인키로 같은 공유 비밀값을 복원한다.

이 공유 비밀값은 과제 파일을 직접 암호화하는 데 사용되지 않고, AES-GCM에 사용할 키를
만드는 재료로 사용된다.

### 3.3 전자서명

전자서명은 디지털 환경에서 "이 데이터는 특정 사람이 만든 것이 맞다"는 것을 증명하는
기술이다.

본 프로젝트에서는 학생이 자신의 서명 개인키로 제출 패키지 전체에 서명한다. 교수 또는
조교는 학생의 서명 공개키로 서명을 검증한다.

검증에 성공하면 다음을 확인할 수 있다.

```text
1. 제출물이 해당 학생의 개인키로 서명되었다.
2. 서명 이후 제출 패키지 내용이 변경되지 않았다.
```

### 3.4 AES-GCM

AES-GCM은 실제 파일 데이터를 암호화하는 대칭키 암호 방식이다.

양자내성 KEM은 큰 파일 전체를 직접 암호화하기 위한 용도가 아니다. 따라서 본 프로젝트는
일반적인 하이브리드 암호화 구조를 사용한다.

```text
KEM
  → 공유 비밀값 생성
  → AES 키 생성
  → AES-GCM으로 실제 과제 파일 암호화
```

## 4. 전체 시스템 동작 흐름

전체 흐름은 다음과 같다.

```text
1. 교수는 KEM 공개키와 개인키를 생성한다.
2. 교수는 KEM 공개키를 학생에게 제공한다.
3. 학생은 전자서명 공개키와 개인키를 생성한다.
4. 학생의 전자서명 공개키는 교수 또는 시스템에 등록된다.
5. 학생은 과제 파일을 준비한다.
6. 학생은 교수 KEM 공개키를 사용하여 공유 비밀값을 생성한다.
7. 공유 비밀값으로부터 AES-GCM 키를 만든다.
8. AES-GCM으로 과제 파일을 암호화한다.
9. 암호화된 파일, 학생 정보, 알고리즘 정보, 제출 시간을 하나의 패키지로 묶는다.
10. 학생은 자신의 서명 개인키로 제출 패키지 전체에 전자서명한다.
11. 교수 또는 조교는 학생 공개키로 제출 패키지를 검증한다.
12. 검증에 성공하면 교수는 자신의 KEM 개인키로 공유 비밀값을 복원한다.
13. 복원한 공유 비밀값으로 AES-GCM 키를 다시 만든다.
14. 교수는 암호화된 과제 파일을 원본 파일로 복호화한다.
```

간단히 표현하면 다음과 같다.

```text
학생 과제 파일
  ↓
AES-GCM 암호화
  ↓
KEM으로 AES 키 보호
  ↓
학생 개인키로 제출 패키지 서명
  ↓
.pqc 제출 파일 생성
  ↓
교수/조교가 서명 검증
  ↓
교수 개인키로 복호화
```

## 5. 프로젝트 구조

프로젝트의 주요 구조는 다음과 같다.

```text
.
├─ README.md
├─ PQC-submit.md
├─ pyproject.toml
├─ Makefile
├─ examples/
│  └─ demo_assignment.txt
├─ src/
│  └─ pqc_submit/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ package.py
│     ├─ utils.py
│     └─ crypto/
│        ├─ __init__.py
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

각 구성 요소의 역할은 다음과 같다.

| 구성 요소 | 역할 |
|---|---|
| `README.md` | 프로젝트 요약 설명 및 실행 안내 |
| `PQC-submit.md` | 과제 제출용 상세 설명 문서 |
| `pyproject.toml` | Python 패키지 설정 및 테스트 설정 |
| `Makefile` | liboqs bridge 빌드 및 테스트 실행 명령 정의 |
| `examples/` | 시연용 과제 파일 |
| `src/pqc_submit/` | 실제 Python 프로그램 코드 |
| `bridge/` | Python과 C 기반 liboqs를 연결하는 bridge 코드 |
| `tests/` | 기능 검증용 자동 테스트 |
| `vendor/liboqs-analysis/` | 실제 양자내성 암호 알고리즘 구현 |

## 6. Python 코드 구성

### 6.1 `cli.py`

`cli.py`는 사용자가 명령어를 입력했을 때 가장 먼저 실행되는 부분이다.

지원하는 주요 명령어는 다음과 같다.

| 명령어 | 역할 |
|---|---|
| `professor-keygen` | 교수 KEM 공개키/개인키 생성 |
| `student-keygen` | 학생 전자서명 공개키/개인키 생성 |
| `submit` | 과제 파일을 `.pqc` 제출 패키지로 생성 |
| `verify` | 제출 패키지의 전자서명 검증 |
| `open` | 검증 후 과제 파일 복호화 |

즉, `cli.py`는 프로젝트의 조작 버튼 역할을 한다.

### 6.2 `package.py`

`package.py`는 이 프로젝트의 핵심 로직을 담당한다.

주요 함수는 다음과 같다.

| 함수 | 역할 |
|---|---|
| `create_submission` | 과제 파일을 암호화하고 `.pqc` 제출 패키지를 생성 |
| `verify_submission` | 제출 패키지의 전자서명을 검증 |
| `open_submission` | 검증 후 교수 개인키로 제출 파일 복호화 |
| `signature_payload` | 전자서명 대상 데이터를 생성 |
| `aad_for_package` | AES-GCM 인증에 사용할 메타데이터 생성 |

`create_submission`은 다음 일을 수행한다.

```text
1. 교수 공개키 읽기
2. 학생 서명 개인키 읽기
3. KEM으로 공유 비밀값 생성
4. 공유 비밀값으로 AES-GCM 키 생성
5. 과제 파일 암호화
6. 학생 정보와 알고리즘 정보를 패키지에 저장
7. 제출 패키지 전체에 전자서명
8. .pqc 파일로 저장
```

### 6.3 `crypto/provider.py`

`provider.py`는 암호 기능이 어떤 형태로 제공되어야 하는지 정의한다.

예를 들어 Provider는 다음 기능을 제공해야 한다.

```text
KEM 키 생성
KEM 캡슐화
KEM 복원
전자서명 키 생성
서명 생성
서명 검증
```

Provider 구조를 사용하면, 시연용 구현과 실제 liboqs 구현을 같은 `package.py` 로직에서
교체해 사용할 수 있다.

### 6.4 `crypto/demo_provider.py`

`DemoProvider`는 실제 보안용 구현이 아니라, 전체 프로그램 흐름을 빠르게 확인하기 위한
시연용 Provider이다.

이 Provider는 테스트와 개발 과정에서 유용하다. 실제 C 라이브러리 빌드 없이도 다음 기능이
정상적으로 이어지는지 확인할 수 있다.

```text
키 생성
제출 패키지 생성
서명 검증
복호화 흐름
변조 탐지 흐름
```

단, `DemoProvider`는 실제 양자내성 보안을 제공하는 구현이 아니므로 최종 보안 검증에서는
`WslOQSProvider`를 사용해야 한다.

### 6.5 `crypto/wsl_provider.py`

`WslOQSProvider`는 실제 `vendor/liboqs-analysis`를 사용하기 위한 Provider이다.

Python이 C 라이브러리를 직접 호출하는 대신, `build/oqs_bridge` 실행 파일을 실행하고 그
결과를 JSON으로 받아온다.

동작 예시는 다음과 같다.

```text
Python WslOQSProvider
  ↓
./build/oqs_bridge kem-keygen ML-KEM-512
  ↓
liboqs의 OQS_KEM_keypair 호출
  ↓
공개키와 개인키를 JSON으로 반환
```

### 6.6 `crypto/symmetric.py`

`symmetric.py`는 실제 과제 파일의 암호화와 복호화를 담당한다.

사용 방식은 다음과 같다.

```text
KEM 공유 비밀값
  ↓
SHA-256 기반 키 유도
  ↓
AES-GCM 키 생성
  ↓
파일 암호화 또는 복호화
```

과제 파일 자체는 KEM으로 직접 암호화하지 않고 AES-GCM으로 암호화한다.
이는 큰 데이터를 처리할 때 일반적으로 사용하는 하이브리드 암호화 방식이다.

## 7. bridge의 역할

이 프로젝트에서 `bridge`는 매우 중요한 연결 역할을 한다.

처음 보면 전체 흐름이 다음과 같아 보일 수 있다.

```text
사용자 명령어
  ↓
cli.py
  ↓
package.py
  ↓
crypto provider
  ↓
실제 암호화 / 서명 / 검증
```

하지만 실제 `WslOQSProvider`를 사용할 때는 중간에 `bridge`가 들어간다.

정확한 흐름은 다음과 같다.

```text
사용자 명령어
  ↓
cli.py
  ↓
package.py
  ↓
WslOQSProvider
  ↓
build/oqs_bridge
  ↓
vendor/liboqs-analysis
  ↓
실제 ML-KEM / HQC / ML-DSA / SLH-DSA 실행
```

즉, `bridge`는 Python 코드와 C 기반 liboqs 라이브러리 사이의 통역기이다.

`bridge/oqs_bridge.c`는 내부적으로 다음 liboqs 함수를 호출한다.

```text
OQS_KEM_keypair
OQS_KEM_encaps
OQS_KEM_decaps
OQS_SIG_keypair
OQS_SIG_sign
OQS_SIG_verify
```

Python 쪽에서는 바이너리 데이터를 hex 문자열로 넘기고, bridge는 결과를 JSON 형태로
출력한다. Python은 이 JSON을 읽어서 키, ciphertext, shared secret, signature, 검증 결과를
다시 사용한다.

## 8. 사용 알고리즘과 선택 이유

`vendor/liboqs-analysis` 안에는 여러 양자내성 암호 알고리즘이 들어 있다. 그러나 본 프로젝트는
과제 제출 시스템에 필요한 기능을 보여주기 위해 대표적인 알고리즘 네 가지를 선택했다.

선택 구조는 다음과 같다.

```text
파일 암호화용 키 보호: KEM
- ML-KEM-512
- HQC-128

제출자 인증 및 변조 검출: 전자서명
- ML-DSA-44
- SLH_DSA_PURE_SHA2_128S
```

### 8.1 ML-KEM-512

`ML-KEM`은 양자내성 KEM 계열의 대표 알고리즘이다.

본 프로젝트에서는 `ML-KEM-512`를 사용한다. `512`는 ML-KEM 계열 안에서 비교적 가벼운
기본 보안 수준 설정이다. 과제 프로젝트에서는 매우 높은 보안 강도보다 전체 제출 흐름을
명확히 구현하고 테스트하는 것이 중요하므로 기본 설정인 `ML-KEM-512`를 선택했다.

### 8.2 HQC-128

`HQC`는 ML-KEM과 다른 수학적 기반을 가진 KEM 알고리즘이다.

ML-KEM만 사용하면 하나의 알고리즘 계열만 확인하게 되므로, 본 프로젝트에서는 비교 및
백업 관점에서 `HQC-128`도 함께 사용한다. `128`은 128-bit 보안 수준을 의미한다.

### 8.3 ML-DSA-44

`ML-DSA`는 양자내성 전자서명 계열의 대표 알고리즘이다.

본 프로젝트에서는 학생이 제출 패키지에 전자서명을 해야 하므로 `ML-DSA-44`를 사용한다.
`44`는 ML-DSA 계열에서 비교적 가벼운 기본 설정이다.

### 8.4 SLH_DSA_PURE_SHA2_128S

`SLH-DSA`는 해시 기반 전자서명 알고리즘이다.

`ML-DSA`와 다른 방식의 전자서명을 함께 사용하면, 전자서명 알고리즘의 조합을 비교할 수
있다. 본 프로젝트에서는 `SLH_DSA_PURE_SHA2_128S`를 사용하여 128-bit 보안 수준의 해시 기반
서명을 실험할 수 있도록 했다.

### 8.5 네 가지 알고리즘만 선택한 이유

`vendor/liboqs-analysis`에는 더 많은 알고리즘이 있지만, 본 프로젝트의 목적은 모든 알고리즘을
나열하는 것이 아니라 과제 제출 보안 흐름을 명확하게 구현하는 것이다.

따라서 다음 기준으로 알고리즘을 골랐다.

| 기준 | 설명 |
|---|---|
| 역할 구분 | KEM 2개, 전자서명 2개로 역할을 명확히 나눔 |
| 대표성 | ML-KEM과 ML-DSA는 각 영역의 대표 알고리즘 |
| 비교 가능성 | HQC와 SLH-DSA를 통해 다른 기반의 알고리즘도 비교 가능 |
| 구현 부담 | 과제 프로젝트 범위에서 테스트 가능한 수준으로 제한 |
| 성능 고려 | 기본 보안 수준 설정을 사용하여 키 크기와 실행 부담을 줄임 |

## 9. 제출 패키지 형식

학생이 과제를 제출하면 `.pqc` 파일이 생성된다.

이 파일은 JSON 형식이며 다음과 같은 정보를 포함한다.

```json
{
  "version": 1,
  "student_id": "20241234",
  "student_name": "Hong Gil Dong",
  "kem_algorithm": "ML-KEM-512",
  "signature_algorithm": "ML-DSA-44",
  "original_filename": "assignment.txt",
  "submitted_at": "2026-06-03T10:00:00+00:00",
  "kem_ciphertext": "...",
  "nonce": "...",
  "encrypted_file": "...",
  "signature": "..."
}
```

각 필드의 의미는 다음과 같다.

| 필드 | 의미 |
|---|---|
| `version` | 제출 패키지 형식 버전 |
| `student_id` | 학번 |
| `student_name` | 학생 이름 |
| `kem_algorithm` | 사용한 KEM 알고리즘 |
| `signature_algorithm` | 사용한 전자서명 알고리즘 |
| `original_filename` | 원본 과제 파일명 |
| `submitted_at` | 제출 시각 |
| `kem_ciphertext` | KEM으로 생성된 캡슐화 결과 |
| `nonce` | AES-GCM 암호화에 사용한 nonce |
| `encrypted_file` | 암호화된 과제 파일 |
| `signature` | 학생 개인키로 생성한 전자서명 |

전자서명은 `signature` 필드를 제외한 제출 패키지 전체에 대해 생성된다.
따라서 제출 이후 학생 이름, 파일명, 암호문, 알고리즘 정보, 제출 시각 중 하나라도 바뀌면
전자서명 검증이 실패한다.

## 10. 주요 명령어

### 10.1 교수 KEM 키 생성

```bash
pqc-submit professor-keygen --kem ML-KEM
```

생성되는 파일:

```text
professor_kem.pub
professor_kem.sec
```

`professor_kem.pub`은 학생에게 공개할 수 있는 공개키이고,
`professor_kem.sec`은 교수가 보관해야 하는 개인키이다.

### 10.2 학생 전자서명 키 생성

```bash
pqc-submit student-keygen --sig ML-DSA
```

생성되는 파일:

```text
student_sig.pub
student_sig.sec
```

`student_sig.pub`은 교수 또는 시스템에 등록하는 공개키이고,
`student_sig.sec`은 학생이 안전하게 보관해야 하는 개인키이다.

### 10.3 과제 제출 패키지 생성

```bash
pqc-submit submit examples/demo_assignment.txt \
  --professor-pk professor_kem.pub \
  --student-sk student_sig.sec \
  --kem ML-KEM \
  --sig ML-DSA \
  --student-id 20241234 \
  --student-name "Hong Gil Dong"
```

결과로 다음 파일이 생성된다.

```text
examples/demo_assignment.txt.pqc
```

이 `.pqc` 파일은 원본 과제 파일, 학생 정보, 알고리즘 정보, 전자서명을 포함한 제출 패키지이다.

### 10.4 제출물 검증

```bash
pqc-submit verify examples/demo_assignment.txt.pqc \
  --student-pk student_sig.pub
```

정상 결과:

```text
valid submission
```

검증 실패 결과:

```text
invalid submission or modified package
```

### 10.5 제출물 복호화

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

이 명령은 먼저 제출물의 전자서명을 검증하고, 검증에 성공한 경우에만 복호화를 진행한다.

## 11. 테스트 설명

테스트는 이 프로젝트가 의도한 기능대로 동작하는지 자동으로 확인하는 코드이다.

사람이 직접 확인하려면 다음 과정을 반복해야 한다.

```text
1. 교수 키를 만든다.
2. 학생 키를 만든다.
3. 과제 파일을 만든다.
4. 제출 패키지를 만든다.
5. 검증이 성공하는지 확인한다.
6. 복호화 결과가 원본과 같은지 확인한다.
7. 제출 패키지를 일부러 바꿔보고 검증 실패를 확인한다.
8. 다른 학생 공개키로 검증해보고 실패를 확인한다.
9. 다른 교수 개인키로 복호화해보고 실패를 확인한다.
```

이 과정을 자동화한 것이 `tests/` 폴더의 테스트 파일들이다.

| 테스트 파일 | 확인 내용 |
|---|---|
| `test_submit_flow.py` | 정상 제출, 검증, 복호화 흐름 확인 |
| `test_tamper_detection.py` | 제출 패키지를 변조하면 검증이 실패하는지 확인 |
| `test_wrong_keys.py` | 잘못된 학생 공개키 또는 교수 개인키 사용 시 실패 확인 |
| `test_wsl_provider.py` | 실제 WSL bridge와 liboqs 연동 확인 |

### 11.1 정상 제출 테스트

`test_submit_flow.py`는 다음을 확인한다.

```text
교수 키 생성
학생 키 생성
과제 파일 생성
.pqc 제출 패키지 생성
학생 공개키로 제출물 검증
교수 개인키로 복호화
복호화 결과가 원본과 같은지 확인
```

이 테스트가 통과하면 정상적인 제출 흐름이 동작한다는 뜻이다.

### 11.2 변조 탐지 테스트

`test_tamper_detection.py`는 제출 패키지를 만든 뒤 일부러 `student_name` 값을 바꾼다.

그 후 검증을 수행했을 때 실패해야 한다.

이 테스트가 통과하면 제출 패키지 안의 정보가 바뀌었을 때 전자서명 검증으로 탐지할 수
있다는 뜻이다.

### 11.3 잘못된 키 테스트

`test_wrong_keys.py`는 두 가지 상황을 확인한다.

```text
1. 다른 학생 공개키로 제출물을 검증하면 실패해야 한다.
2. 다른 교수 개인키로 제출물을 열면 복호화에 실패해야 한다.
```

이 테스트는 제출자 인증과 교수 전용 복호화가 제대로 동작하는지 확인한다.

### 11.4 WSL Provider 테스트

`test_wsl_provider.py`는 `DemoProvider`가 아니라 실제 `WslOQSProvider`를 사용한다.

즉, 다음 흐름이 실제로 동작하는지 확인한다.

```text
Python
  ↓
WslOQSProvider
  ↓
build/oqs_bridge
  ↓
vendor/liboqs-analysis
```

단, `build/oqs_bridge`가 빌드되어 있지 않으면 이 테스트는 자동으로 건너뛴다.

## 12. 테스트 실행 방법과 결과

프로젝트 루트에서 다음 명령을 실행한다.

```bash
python -m pytest
```

Windows 환경에서 `python` 명령이 실제 Python으로 연결되어 있지 않은 경우 WSL에서 다음처럼
실행할 수 있다.

```bash
cd '/mnt/c/Users/wngus/Desktop/소프트웨어의 실제/양자내성 암호 기반 온라인 과제 제출 암호화 및 검증 시스템'
python3 -m pytest
```

현재 WSL 환경에서 테스트를 실행한 결과는 다음과 같다.

```text
collected 5 items

tests/test_submit_flow.py .                                              [ 20%]
tests/test_tamper_detection.py .                                         [ 40%]
tests/test_wrong_keys.py ..                                              [ 80%]
tests/test_wsl_provider.py .                                             [100%]

5 passed in 2.67s
```

이는 현재 구현된 5개의 테스트가 모두 통과했다는 뜻이다.

테스트 통과로 확인할 수 있는 내용은 다음과 같다.

```text
정상 제출 가능
제출물 검증 가능
교수 개인키로 복호화 가능
제출물 변조 탐지 가능
잘못된 학생 공개키 거부 가능
잘못된 교수 개인키 복호화 실패 확인
실제 liboqs bridge 연동 확인
```

단, 테스트 통과가 상용 수준의 완전한 보안성을 증명하는 것은 아니다.
테스트는 본 프로젝트가 목표로 한 주요 기능이 기대한 방식대로 동작하는지 확인하는 수단이다.

## 13. 프로젝트의 의의

본 프로젝트의 의의는 단순히 암호 알고리즘을 호출하는 데 있지 않다.

양자내성 암호를 실제 서비스 흐름에 어떻게 적용할 수 있는지, 즉 온라인 과제 제출이라는
구체적인 상황에 맞추어 다음 요소들을 하나의 구조로 연결했다는 점에 의미가 있다.

```text
1. 학생 과제 파일 암호화
2. 교수만 복호화 가능한 구조
3. 학생 전자서명 기반 제출자 인증
4. 제출 패키지 변조 탐지
5. ML-KEM, HQC, ML-DSA, SLH-DSA 알고리즘 조합
6. Python CLI와 C 기반 liboqs 라이브러리 연동
7. 자동 테스트를 통한 기능 검증
```

이를 통해 양자내성 암호가 단순한 이론이나 알고리즘 호출에 그치지 않고, 실제 제출 시스템에서
어떤 역할을 맡을 수 있는지 보여준다.

## 14. 한계와 향후 개선 방향

현재 구현은 CLI 기반 시제품이므로 다음과 같은 한계가 있다.

| 한계 | 설명 |
|---|---|
| 웹 인터페이스 없음 | 실제 사용자가 브라우저에서 제출하는 화면은 구현되어 있지 않음 |
| 키 관리 단순화 | 학생 공개키 등록, 교수 개인키 보관 정책 등이 실제 서비스 수준은 아님 |
| DemoProvider 보안 한계 | DemoProvider는 흐름 확인용이며 실제 보안용이 아님 |
| 사용자 인증 미구현 | 로그인, 계정 관리, 권한 관리 기능은 없음 |
| 운영 환경 고려 부족 | 서버 저장소, DB, 접근 제어, 감사 로그 등은 포함되지 않음 |

향후 개선 방향은 다음과 같다.

```text
1. 웹 기반 제출 화면 구현
2. 교수/학생 계정 및 권한 관리 추가
3. 학생 공개키 등록 및 검증 절차 추가
4. 제출 패키지 저장용 데이터베이스 연동
5. 알고리즘별 성능 비교 결과 정리
6. 파일 크기별 암호화/복호화 시간 측정
7. 실제 배포 환경을 고려한 키 관리 정책 추가
```

## 15. 결론

본 프로젝트는 양자내성 암호를 기반으로 온라인 과제 제출물을 보호하는 CLI 기반 시제품이다.

학생은 과제 파일을 암호화하고 자신의 전자서명을 붙여 `.pqc` 제출 패키지를 생성한다.
교수 또는 조교는 학생 공개키로 제출물이 변조되지 않았는지 검증하고, 교수 개인키로 원본
과제 파일을 복호화할 수 있다.

프로젝트는 Python으로 제출 흐름을 구현하고, 실제 양자내성 암호 알고리즘은
`vendor/liboqs-analysis`와 `bridge/oqs_bridge.c`를 통해 연결한다. 또한 자동 테스트를 통해
정상 제출, 변조 탐지, 잘못된 키 사용 실패, 실제 liboqs 연동 여부를 확인한다.

따라서 본 프로젝트는 온라인 과제 제출 환경에서 필요한 기밀성, 무결성, 제출자 인증을
양자내성 암호 기반으로 구현하고 검증한 교육용 및 실험용 보안 시스템이라고 할 수 있다.
