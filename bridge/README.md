# oqs_bridge 설명

## 1. bridge의 목적

`oqs_bridge`는 Python 코드와 C 기반 `liboqs-analysis` 라이브러리를 연결하기 위한 작은
Linux 실행 파일이다.

이 프로젝트의 Python 코드는 과제 제출 패키지 생성, 검증, 복호화 흐름을 담당한다.
하지만 실제 양자내성 암호 알고리즘은 `vendor/liboqs-analysis` 안의 C 코드로 구현되어 있다.

따라서 Python에서 직접 C 함수를 호출하는 대신, 중간 실행 파일인 `build/oqs_bridge`를 실행하여
필요한 암호 기능을 호출한다.

```text
Python WslOQSProvider
  ↓
build/oqs_bridge
  ↓
vendor/liboqs-analysis
  ↓
실제 양자내성 암호 함수 실행
```

## 2. 언제 사용되는가?

`oqs_bridge`는 `WslOQSProvider`를 사용할 때만 필요하다.

```text
--provider demo
  → bridge 사용 안 함
  → Python 시연용 Provider 사용

--provider wsl-oqs
  → bridge 사용
  → 실제 liboqs-analysis 호출
```

## 3. 지원하는 명령

`oqs_bridge`는 다음 명령을 지원한다.

| 명령 | 역할 |
|---|---|
| `kem-keygen` | KEM 공개키/개인키 생성 |
| `kem-encaps` | KEM 캡슐화, 공유 비밀값 생성 |
| `kem-decaps` | KEM 복원, 공유 비밀값 복원 |
| `sig-keygen` | 전자서명 공개키/개인키 생성 |
| `sign` | 전자서명 생성 |
| `verify` | 전자서명 검증 |

내부적으로 호출하는 liboqs 함수는 다음과 같다.

```text
OQS_KEM_keypair
OQS_KEM_encaps
OQS_KEM_decaps
OQS_SIG_keypair
OQS_SIG_sign
OQS_SIG_verify
```

## 4. 데이터 전달 방식

Python과 bridge 사이에서는 바이너리 데이터를 그대로 주고받지 않는다.

대신 Python은 키, 메시지, 서명 같은 데이터를 hex 문자열로 바꾸어 bridge에 전달한다.
bridge는 결과를 JSON 형태로 출력하고, Python은 그 JSON을 다시 읽어 사용한다.

예시:

```text
./build/oqs_bridge kem-keygen ML-KEM-512
```

출력 예시:

```json
{
  "public_key": "...",
  "secret_key": "..."
}
```

## 5. 빌드 방법

프로젝트 루트에서 WSL을 사용하여 다음 명령을 실행한다.

```bash
make oqs-bridge
```

이 명령은 다음 작업을 수행한다.

```text
1. vendor/liboqs-analysis 빌드
2. bridge/oqs_bridge.c 컴파일
3. build/oqs_bridge 실행 파일 생성
```

수동으로 빌드하면 다음과 같은 형태이다.

```bash
make -C vendor/liboqs-analysis
mkdir -p build
cc -std=gnu11 -O2 \
  -Ivendor/liboqs-analysis/include \
  -Ivendor/liboqs-analysis/include/oqs \
  -Ivendor/liboqs-analysis/src \
  -Ivendor/liboqs-analysis/build/include \
  -o build/oqs_bridge bridge/oqs_bridge.c \
  vendor/liboqs-analysis/build/lib/liboqs.a \
  vendor/liboqs-analysis/build/lib/liboqs-internal.a \
  -lm -lcrypto -lpthread
```

## 6. 정리

`oqs_bridge`는 프로젝트의 사용자 기능을 직접 담당하지 않는다.

대신 Python 프로젝트가 실제 C 기반 양자내성 암호 라이브러리를 사용할 수 있도록 연결하는
어댑터 역할을 한다. 따라서 실제 liboqs 기반 알고리즘을 검증하려면 `build/oqs_bridge`가
빌드되어 있어야 한다.
