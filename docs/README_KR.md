# EU AI Act 컴플라이언스 로깅 — PRISM Standard v1.0

**Art. 12 결정 추론 로그를 위한 오픈소스 pre-standard. 시스템 프롬프트 한 줄 추가. MIT 라이선스. 일반 이벤트 로그 옆에서 감사관이 기대하는 구조화된 증거 레이어를 만든다.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](../CHANGELOG.md)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Article%2012-red.svg)](#컴플라이언스-매핑-먼저-읽으세요)
[![English](https://img.shields.io/badge/docs-English-lightgrey.svg)](../README.md)

---

## 📅 일정 업데이트: AI Act Omnibus (2026년 5월 7일)

2026년 5월 7일, EU 이사회와 의회가 디지털 AI Omnibus에 **잠정 정치합의**했다. 합의된 대로 정식 채택될 경우, 본 저장소가 처음 만들어진 동인이었던 고위험 시스템 일정이 뒤로 밀린다 — 하지만 **사라진 것은 아니다**. 구조화된 로깅 문제는 여전히 실재하고, 시행 시계만 이동했다.

| 의무 | 기존 일자 | 신규 일자 (Omnibus) |
| --- | --- | --- |
| Annex III 단독형 고위험 시스템 — Art. 9–17 전체, **Art. 12 로깅 포함** | 2026년 8월 2일 | **2027년 12월 2일** |
| Annex I 제품 임베디드 고위험 시스템 | 2027년 8월 2일 | **2028년 8월 2일** |
| Art. 50 GPAI / 생성형 AI 투명성 의무 (모델 워터마킹, 딥페이크 고지) | 2026년 8월 2일 | **2026년 12월 2일** *(유예기간 6개월 → 3개월로 단축)* |
| 금지 관행 (Art. 5) | 시행 중 (2025년 2월) | 변경 없음 |
| 범용 AI 모델 의무 (Art. 53–55) | 시행 중 (2025년 8월) | 변경 없음 |

> Omnibus는 이사회·의회가 EU 규정 2024/1689 개정안을 **정식으로 채택**할 때까지 잠정안이다. 위 일자는 2026년 5월 7일 정치합의 기준이며, 통상 입법 절차를 통해 최종 확정될 예정이다. 어떤 일자라도 최종으로 간주하기 전에 공포된 개정 규정과 대조해 확인하라. *출처: [이사회 보도자료, 2026-05-07](https://www.consilium.europa.eu/en/press/press-releases/2026/05/07/artificial-intelligence-council-and-parliament-agree-to-simplify-and-streamline-rules/); [유럽의회 보도자료, 2026-03-16](https://www.europarl.europa.eu/news/en/press-room/20260316IPR38219/meps-support-postponement-of-certain-rules-on-artificial-intelligence); [Digital Omnibus on AI — Legislative Train](https://www.europarl.europa.eu/legislative-train/package-digital-package/file-digital-omnibus-on-ai).*

### 이 연기가 운영자에게 의미하는 것

1. **Art. 12 로깅 요건은 여전히 온다.** Annex III 시스템은 약 **19개월** 후 (2027년 12월), Annex I 제품 임베디드 시스템은 약 **27개월** 후 (2028년 8월)에 적용된다. CEN/CENELEC 조화 표준 작업은 병행 진행 중이며, 새 시행일보다 실질적으로 더 일찍 나올 가능성은 낮다.

2. **표준 공백 구간은 짧아진 게 아니라 길어졌다.** 조화 표준이 나오기를 기다리며 결정 로그 레이어 설계를 미루던 운영자들은 이제 *더 많은* 시간 동안 잘못된 아키텍처 결정을 내릴 여지를 갖게 됐다. 이 구간에 deployable한 오픈 pre-standard를 채택할 근거는 약해진 게 아니라 강해졌다.

3. **2026년 12월이 대부분의 팀이 주시해야 할 더 가까운 마감이다.** Art. 50 투명성 의무는 Annex III 고위험 분류보다 훨씬 더 많은 시스템에 적용되며, 정식 채택 이후 **3개월의 유예**만으로 도래한다 — Omnibus에서 이 기준은 늦춰진 게 아니라 **앞당겨졌다**.

4. **과징금 상한은 그대로다.** Art. 99는 운영자 의무 위반에 대해 €15M 또는 매출 3%, 금지 관행에 대해 €35M 또는 매출 7%의 상한을 그대로 둔다. 이번 연기는 *언제* 그 상한이 적용되는지를 늦췄을 뿐, *적용 자체*를 막지 않는다.

고위험 시스템이 적용 시점까지 감사 가능한 결정별 추론 기록을 산출하지 못한다면 운영자 의무를 충족하지 못한 것이다. 일반 이벤트 로그 (지연시간, 토큰 수, 요청 ID)는 Art. 12의 일부를 충족하지만 결정의 **추론** — 어떤 가치가 우선했는가, 어떤 증거가 가중되었는가, 어떤 출처가 신뢰되었는가 — 은 포착하지 못한다. Art. 13 (투명성)과 Art. 14 (사람 감독 가능성)는 단순 이벤트 트레이스를 넘어선 요구를 만든다.

**조화 표준 (CEN/CENELEC)은 여전히 개발 중이다.** 그 납기는 새 시행일에 맞춰 함께 연기되지 *않았다*. 운영자는 그것을 기다리며 구조화된 로깅 시작을 미룰 수 없다.

본 저장소는 더 큰 컴플라이언스 프로그램의 한 구성 요소로서 오늘 배포 가능한 working pre-standard다. 길어진 활주로는 약점이 아니라 기능이다 — 조기 도입자는 시행 이전에 12~24개월의 행동 베이스라인 데이터를 축적할 수 있고, 2027년에 retrofit 증거를 위해 허둥대지 않아도 된다.

---

## 🟦 중요: 본 표준은 보완 레이어이지 대체가 아니다

PRISM은 기존 이벤트 로그 파이프라인에 **추론 트레이스를 더하는** 레이어다. 이것만으로 Art. 12를 충족하지는 *못한다*.

여전히 로깅해야 하는 항목:

- 사용자 식별자, 타임스탬프, 세션 ID (Art. 12(1) 수명주기 기록)
- 입력 및 출력 (Art. 12(2)(c) 생체인식 시스템; 일반적으로 위험 식별)
- 시스템 운영 기간 (Art. 12(2)(a))
- 해당 시 데이터베이스 참조 (Art. 12(2)(b))

PRISM은 이들 위에 **결정당 추론 지문**을 추가한다. 어떤 것도 대체하지 않는다.

일반적인 컴플라이언트 배포는 다음과 같다:

```
[일반 이벤트 로그]      → 입력/출력/타임스탬프/사용자 ID
        +
[PRISM 추론 로그]      → 의미 있는 결정마다 C/V/E/S 코드
        +
[해시 레이어]           → 양쪽 위에 SHA-256 체인 (변조 방지 증거)
        ↓
[감사 저장소]           → 인덱스 + Art. 12(2)(a) 요건에 맞는 보관 기간
```

일반 이벤트 로그 없이 PRISM만 도입하면 여전히 비준수다. 일부 마케팅이 이와 반대로 시사하기 때문에 이 부분을 명시적으로 강조한다 — 그것은 사실이 아니다.

---

## 무엇을 얻는가

현대 LLM이 재학습 없이 산출할 수 있는 어휘. 본 저장소가 제공하는 시스템 프롬프트를 추가하기만 하면 모델이 내리는 모든 의미 있는 결정이 한 줄의 구조화된 코드를 생성한다:

```
<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>
```

약 60자. 사용자 원문(verbatim) 없음. 토픽 수준 메타데이터만 (`C:` 도메인은 "이건 의료 질문이었다"를 드러낸다 — 기존 라우팅 로그가 이미 노출하는 수준).

이 줄의 디코딩:

- **C** — 컨텍스트: 도메인, 영향 범위, 가역성, 시간 지평
- **V** — 가치 위계: 어떤 가치 우선순위가 이겼는가
- **E** — 증거 위계: 어떤 증거 유형이 결정적이었는가
- **S** — 출처 위계: 어떤 출처 클래스가 신뢰되었는가

`<` 기호는 "에 밀린다"로 읽는다. 왼쪽 = 후순위, 오른쪽 = 우선.

[전체 사양 →](../SPECIFICATION.md)

---

## 컴플라이언스 매핑 (먼저 읽으세요)

왼쪽 열은 PRISM이 기술적으로 산출하는 것이다. 오른쪽 열은 각 항목이 EU AI Act의 어떤 조문을 **뒷받침하는지**(단독으로 충족하는 것이 아님)를 표시한다. 전체 컴플라이언스 프로그램 — 위험 관리, 데이터 거버넌스, 시판 후 모니터링 — 은 PRISM 단독이 아니라 Art. 9–17 전체를 중심으로 구축되어야 한다.

| PRISM이 산출하는 것 | 뒷받침하는 EU AI Act 조문 | 감사관 관점의 유용성 |
| --- | --- | --- |
| 의미 있는 결정마다 PRISM 한 줄 | **Art. 12(1)** — 자동 기록 유지 | 일반 이벤트 로그와 보완되는 기계 생성 추론 트레이스 |
| `C:` 레이어 (도메인 / 범위 / 가역성 / 시간) | **Art. 12(2)** — 위험 상황 추적성 | 결정별 위험 컨텍스트 태그 |
| 운영 기간 전반의 집계 `C:` 분포 | **Art. 12(2)(a)** — 사용 기간 기록 (타임스탬프와 결합 시) | 시간 경과에 따른 결정 카테고리 및 양 |
| [`tools/prism_hash.py`](../tools/prism_hash.py)를 통한 SHA-256 체인 해시 | 변조 방지 증거 (일반 추적성 원칙과 Recital 73에 함의; Art. 12(3) 문언 그대로는 아님) | 로그 스트림에 대한 보관 사슬 증거 |
| `V:`, `E:` 위계 | **Art. 13** — 추론 투명성 *(뒷받침; Art. 13의 일차적 프레임은 배포자 대상 투명성)* | 출력 배후의 가치 우선순위 및 증거 유형 보고 |
| 구조화된 한 줄 코드, grep·SQL 친화적 | **Art. 14** — 사람 감독 가능성 *(기여; Art. 14의 핵심은 사람의 정지/개입 능력)* | 감사관이 AI 행동을 대규모로 점검할 수 있는 형식 |
| 버전 간 집계 코드 분포 | **Art. 15** — 정확성 및 견고성 모니터링 | 모델 버전 간 드리프트 탐지 신호 |
| 이상 코드 패턴 (예: 예상치 못한 `V:` 역전, `S:Ano` 급증) | **Art. 73** — 중대 사고 보고 | 사전 조사 단계의 신호 출처 |
| `S:` 출처 위계 | **Art. 10** — 데이터 거버넌스 *(보완 증거)* | 답변을 추동한 출처 클래스의 결정별 기록 |

**읽기 가이드**: "뒷받침한다"와 "기여한다"는 의도적으로 "충족한다"보다 약하다. PRISM 로그만으로는 위 어떤 의무도 단독으로 면제되지 않는다. PRISM 로그는 거버넌스 문서·일반 이벤트 로그·위험 관리 문서·시판 후 모니터링 산출물 옆에서 감사관과 인증기관이 참조하는 **구조화된 증거**를 제공한다. [DISCLAIMER.md](../DISCLAIMER.md) 참조.

Art. 12(3) 관련: 해당 항은 생체인식 식별 시스템 (Annex III 1(a))의 최소 로깅 항목을 명시하며 일반적으로 해싱을 요구하지 *않는다*. 본 저장소가 제공하는 해시 도구는 방어적 무결성 조치이지 Art. 12(3) 문언 그대로의 구현이 아니다.

---

## 통합 방법

세 가지 출력 모드 — 모델이 지원하는 모드를 선택한다.

| 모드 | 사용 상황 | 사용자에게 로그 노출? |
| --- | --- | --- |
| **A. 인라인 태그** | 구조화 출력이 없는 구형 모델 | 노출 안 됨 (호스트가 `<prism_log>` 태그 제거) |
| **B. 구조화 출력 (JSON)** | JSON 모드를 지원하는 OpenAI · Gemini · Claude | 노출 안 됨 (별도 JSON 필드) |
| **C. 도구 호출** | 네이티브 도구 사용이 가능한 Claude · OpenAI · Gemini | 노출 안 됨 (별도 tool_use 블록) |

시스템 프롬프트 (기존 시스템 메시지에 추가):

**10가치 프로필 (기본 — Schwartz 1992):**

- [`system_prompts/prism_v1_kr_inline.md`](../system_prompts/prism_v1_kr_inline.md) — Mode A
- [`system_prompts/prism_v1_kr_json.md`](../system_prompts/prism_v1_kr_json.md) — Mode B
- [`system_prompts/prism_v1_kr_tool.md`](../system_prompts/prism_v1_kr_tool.md) — Mode C

**19가치 프로필 (확장 — Schwartz et al. 2012, *Refined Theory of Basic Values*):**

- [`system_prompts/prism_v1_kr_inline_19v.md`](../system_prompts/prism_v1_kr_inline_19v.md) — Mode A
- [`system_prompts/prism_v1_kr_json_19v.md`](../system_prompts/prism_v1_kr_json_19v.md) — Mode B
- [`system_prompts/prism_v1_kr_tool_19v.md`](../system_prompts/prism_v1_kr_tool_19v.md) — Mode C

19가치 프로필은 10개 가치를 19개 세분 카테고리로 분할한다 (예: `Sel` → `Sdt`/`Sda`; `Sec` → `Sep`/`Ses`). 모델 간 최대 일관성을 원하면 10v, 더 세밀한 감사 신호를 원하면 19v를 선택한다. 시스템마다 한 프로필을 고르고 유지하라 — 두 프로필은 직접 비교 불가다.

**필수**: 모든 모드·프로필에서 PRISM 로그는 감사 저장소 전용이며 절대 최종 사용자에게 노출되지 않는다. Mode A는 호스트가 태그를 제거해야 한다. Mode B·C는 본질적으로 분리되어 있다.

시스템 프롬프트 추가는 빠른 첫 단계다. 전체 배포는 다음을 요구한다:

- 출력 검증 (잘못된 형식 처리)
- 기존 로그 파이프라인 (DB, S3, SIEM)에 `prism_code` 연결
- 저장 시점 해싱
- Art. 12(2)(a) 및 산업별 요건에 맞는 보관 정책
- 집계 분포에 대한 드리프트 모니터링

시스템 프롬프트 추가 자체는 몇 분 걸리지만, 프로덕션 배포는 더 오래 걸린다.

### 최소 예제 (Mode C, Claude)

```python
from anthropic import Anthropic

client = Anthropic()

PRISM_TOOL = {
    "name": "record_prism_log",
    "description": "Record the PRISM log for a substantive decision.",
    "input_schema": {
        "type": "object",
        "required": ["code"],
        "properties": {"code": {"type": "string"}}
    }
}

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2000,
    system=PRISM_MODE_C_PROMPT,  # system_prompts/prism_v1_kr_tool.md에서 로드
    tools=[PRISM_TOOL],
    messages=[{"role": "user", "content": user_input}]
)

# 사용자 노출 텍스트와 감사 로그는 별도 블록
user_facing = ""
prism_code = None
for block in response.content:
    if block.type == "text":
        user_facing += block.text
    elif block.type == "tool_use" and block.name == "record_prism_log":
        prism_code = block.input["code"]

# user_facing → 사용자 인터페이스
# prism_code  → 감사 로그 저장소
```

`prism_code`를 기존 로그 파이프라인에 연결하라. 저장 시 [`tools/prism_hash.py`](../tools/prism_hash.py)를 실행해 체인 무결성을 확보한다.

---

## 검증된 환경

| 공급자 / 모델 | 프로필 | Mode A | Mode B | Mode C |
| --- | --- | --- | --- | --- |
| Anthropic Claude (Sonnet 4.5) | 10v | 검증 완료 | 검증 완료 | 검증 완료 |
| Anthropic Claude (Sonnet 4.5) | 19v | 검증 완료 | 검증 완료 | 검증 완료 |
| OpenAI GPT 계열 | 양쪽 | 동작 예상; 커뮤니티 검증 진행 중 | 동작 예상 | 동작 예상 |
| Google Gemini 계열 | 양쪽 | 동작 예상; 커뮤니티 검증 진행 중 | 동작 예상 | 동작 예상 |
| 오픈소스 모델 (Llama, Mistral) | 양쪽 | 동작 예상; 커뮤니티 검증 대기 | 추론 스택에 따라 다름 | 다름 |

커뮤니티 검증 보고가 들어오는 대로 이 표를 업데이트한다. 출력 토큰 비용은 토크나이저에 따라 다르며, 실제로 코드당 약 25~40 토큰을 예상하면 된다 (모델 의존). 사이징 전에 자체 스택에서 측정하라.

---

## 왜 JSON이 아니라 코드인가

컴플라이언스 로그는 수년에 걸쳐 수백만 건의 결정을 기록한다. 형식이 중요하다.

| 속성 | PRISM 코드 | JSON 등가물 |
| --- | --- | --- |
| 길이 | 약 60자 | 약 300자 이상 |
| 출력 토큰 비용 | 약 25~40 토큰 (모델 의존) | 약 150 토큰 이상 |
| 프라이버시 | 원문 없음; 토픽 수준 메타데이터만 | 컨텍스트 유출 위험 |
| 집계 | 추출 후 직접 grep / SQL | 평탄화 필요 |
| 감사관 스캔 속도 | 높음 | 낮음 |

이 로그는 요약이 아니라 **구조적 지문**이다. 대화 내용은 대화 로그에 남는다. PRISM 줄은 대규모 행동 감사 가능성에 필요한 것만 포착한다.

하루 100만 건 이상의 배포에서는 ETL 파이프라인 (Airflow / Spark / ClickHouse 등)을 계획하라. Python 파서 ([`tools/prism_parser.py`](../tools/prism_parser.py))는 배치 검증과 소규모 쿼리에 적합하며 스트리밍 집계용은 아니다.

---

## 본 표준이 주장하지 *않는* 것

DPO·법무·인증기관이 무엇을 읽고 있는지 분명히 알 수 있도록 명시한다:

- **참된 추론의 증명이 아니다.** LLM 자기 보고는 사후 합리화일 수 있다. PRISM 로그는 *보고된* 추론이지 인과적 트레이스가 아니다. (이 한계는 chain-of-thought, 어텐션 트레이스, 사람이 작성한 문서에도 동일하게 적용된다.)
- **독립 감사의 대체가 아니다.** 내부 로그는 외부 검증을 통해야 규제 효력을 갖는다.
- **일반 이벤트 로그의 대체가 아니다.** 위의 보완 레이어 섹션 참조.
- **자동 컴플라이언스가 아니다.** 이것은 구조화된 증거 레이어다. 컴플라이언스는 전체 거버넌스 시스템 — 위험 관리 (Art. 9), 데이터 거버넌스 (Art. 10), 일반 로깅 (Art. 12), 투명성 (Art. 13), 사람 감독 (Art. 14), 정확성·견고성 (Art. 15), 품질 관리 (Art. 17), 시판 후 모니터링 (Art. 72), 사고 보고 (Art. 73) — 에 달려 있다.
- **단일 솔루션이 아니다.** PRISM은 더 큰 컴플라이언스 도구체인의 한 구성 요소다. 다른 보완 접근으로는 일반 이벤트 로깅, chain-of-thought 추론 캡처, NIST AI RMF 문서 패턴, IBM AI FactSheets 등이 있다. 거버넌스 프로그램에 맞는 조합을 선택하라.
- **Omnibus로 본질이 바뀌지 않았다.** 2026년 5월 연기는 Art. 9–17 자체를 수정하지 않는다 — 언제 적용되는지를 수정할 뿐이다. 본 저장소를 추동한 본질적 의무 — 감사 가능한 결정별 추론 기록 — 은 변하지 않았다.

본 표준이 *하는* 것: 컴플라이언스 증거의 추론 레이어를 위한 개방적·구조화·규제 친화적 형식. 오늘 사용 가능. 무료. 포크 가능.

---

## 저장소 구성

| 파일 | 용도 |
| --- | --- |
| [`SPECIFICATION.md`](../SPECIFICATION.md) | v1.0 코드 사양 전체 (출력 모드 정의 포함) |
| [`DISCLAIMER.md`](../DISCLAIMER.md) | 적용 범위, 한계, 무보증 조항 |
| [`system_prompts/`](../system_prompts) | 드롭인 시스템 프롬프트 (EN + KR; 10v + 19v; 3개 모드) |
| [`examples/`](../examples) | 7개 도메인 실사용 로그 예시 |
| [`tests/validate.py`](../tests/validate.py) | 다중 모드 추출 검증기 (`--profile=10v\|19v`) |
| [`tools/prism_parser.py`](../tools/prism_parser.py) | 코드 추출 및 구조화 파싱 |
| [`tools/prism_hash.py`](../tools/prism_hash.py) | SHA-256 무결성 도우미 (독립·체인 해시) |
| [`docs/integration_guide.md`](integration_guide.md) | 공급자별 통합 가이드 |
| [`README.md`](../README.md) | English documentation |

---

## 라이선스

MIT. 사용·수정·상업 제품 임베드 모두 가능. 출처 표기 권장 (필수 아님). [LICENSE](../LICENSE) 참조.

본 표준은 기술 사양이며 법률 조언이 아니다. 이를 사용한다고 어떤 규제 준수도 보장되지 않는다. 전체 적용 범위와 한계는 [DISCLAIMER.md](../DISCLAIMER.md) 참조.

---

## 유지·관리

[AI Integrity Organization (AIO)](https://aioq.org), 스위스 등록 비영리. AI 거버넌스 및 행동 감사 가능성을 다룬다.

PRISM 프레임워크의 학술적 배경은 다음 워킹 페이퍼를 참조:

- S. Lee (2026a). *AI Integrity: A New Paradigm for Verifiable AI Governance.* arXiv:[2604.11065](https://arxiv.org/abs/2604.11065) [cs.AI].
- S. Lee (2026b). *PRISM Risk Signal Framework: Hierarchy-Based Red Lines for AI Behavioral Risk.* arXiv:[2604.11070](https://arxiv.org/abs/2604.11070) [cs.AI].
- S. Lee (2026c). *Measuring the Authority Stack of AI Systems: Empirical Analysis of 366,120 Forced-Choice Responses Across 8 AI Models.* arXiv:[2604.11216](https://arxiv.org/abs/2604.11216) [cs.AI].

19가치 프로필이 특히 기반하는 문헌:

- Schwartz, S. H., Cieciuch, J., Vecchione, M., Davidov, E., Fischer, R., Beierlein, C., et al. (2012). Refining the theory of basic individual values. *Journal of Personality and Social Psychology*, 103(4), 663–688.

---

## 문의

- 이슈 / 제안: [GitHub issues](https://github.com/AI-Integrity/EU-AI-Act-Compliance-Logging/issues)
- 상업적 문의: <2sk@aioq.org>
- 웹사이트: [aioq.org](https://aioq.org)
