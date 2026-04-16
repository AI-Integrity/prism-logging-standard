# PRISM Logging Standard

**AI 추론 결정의 가치·증거·출처 위계를 구조화된 한 줄 코드로 기록하는 오픈 표준. 규제 준수 및 행동 감사를 위한.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](../CHANGELOG.md)
[![English](https://img.shields.io/badge/docs-English-blue.svg)](../README.md)

---

## PRISM 로그의 형태

```
<prism_log>
C:MD/IXi | V:Ben<Sel | E:Exp<Gui | S:Usr<Pro
</prism_log>
```

한 줄. 약 60자. 포함 내용:

- **C** — 컨텍스트: 도메인, 영향 범위, 가역성, 시간 지평
- **V** — 가치 위계: 밀린 Schwartz 가치 < 우선된 Schwartz 가치
- **E** — 증거 위계: 밀린 증거 유형 < 우선된 증거 유형
- **S** — 출처 위계: 밀린 출처 유형 < 우선된 출처 유형

`<`는 "~에 밀림"을 의미합니다. 왼쪽 = 덜 중시됨. 오른쪽 = 우선됨.

[전체 명세 →](../SPECIFICATION.md)

---

## 왜 필요한가

AI 규제는 제품 수준의 준수에서 행동 수준의 책무성으로 이동하고 있습니다. 2026년 8월부터 시행되는 EU AI Act의 고위험 조항은 고위험 AI 시스템 운영자가 **감사 가능한 추론 기록**을 유지할 것을 요구합니다. 지연시간과 토큰 수가 아니라, 각 결정을 이끈 가치·증거·출처가 기록되어야 합니다. 다른 관할권에서도 유사한 체계가 개발되고 있습니다.

현재의 로깅 프레임워크는 이를 포착하지 못합니다. **PRISM Logging Standard는 가능합니다.**

시스템 프롬프트에 구조화된 어휘를 추가하면 주요 LLM이 규제 친화적 추론 코드를 출력하도록 할 수 있습니다. 새로운 인프라도, API 변경도, 모델 재학습도 필요 없습니다.

### 표준 공백기의 "Pre-standard"

EU AI Act의 공식 조화 표준(CEN/CENELEC 등이 개발)은 v1.0 발행 시점 기준 아직 개발 중입니다. 2026년 8월 시행 기한을 앞둔 조직은 공식 표준 확정을 기다리고 나서 구조화된 로깅을 시작할 수는 없습니다.

PRISM v1.0은 **Pre-standard**로 설계되었습니다: 지금 사용 가능하고, 알려진 요구사항(제12조 자동 로깅, 제13조 추론의 투명성, 제14조 인간 감독)과 구조적으로 정합하며, 공식 표준이 수렴할 때 적응 가능하도록 모듈화되었습니다.

**Modular Design:** 어휘(도메인, Schwartz 가치, 증거 유형, 출처 유형, 범위, 가역성, 시간)는 구조적 형식을 바꾸지 않고도 확장·재매핑할 수 있는 고정 테이블로 정의됩니다. 향후 조화 표준이 다른 분류체계를 요구하면, PRISM 적응은 재구현이 아닌 **어휘 업데이트** 작업으로 해결됩니다.

---

## 빠른 시작

PRISM v1.0은 세 가지 출력 모드를 지원합니다. 모델 기능에 맞게 선택하십시오:

| 모드 | 사용 시점 | 사용자가 로그 봄? |
|---|---|---|
| **A. 인라인 태그** | 구조화 출력 미지원 구형 모델 | 아니오 (호스트가 태그 제거) |
| **B. 구조화 출력** | JSON 모드 지원 모델 (OpenAI, Gemini, Claude) | 아니오 (별도 JSON 필드) |
| **C. 도구 호출** | 네이티브 도구 사용 지원 모델 (Claude, OpenAI, Gemini) | 아니오 (별도 tool_use 블록) |

**중요:** 모든 모드에서 PRISM 로그는 감사 저장용이며 최종 사용자에게 노출되어서는 안 됩니다. Mode A는 호스트가 태그를 제거해야 하며, Mode B와 C는 API 차원에서 분리를 보장합니다.

선택한 모드에 해당하는 시스템 프롬프트:

- [`system_prompts/prism_v1_kr_inline.md`](../system_prompts/prism_v1_kr_inline.md) — Mode A
- [`system_prompts/prism_v1_kr_json.md`](../system_prompts/prism_v1_kr_json.md) — Mode B
- [`system_prompts/prism_v1_kr_tool.md`](../system_prompts/prism_v1_kr_tool.md) — Mode C

### 최소 통합 예시 (Mode C, Anthropic Claude)

```python
from anthropic import Anthropic

client = Anthropic()

PRISM_TOOL = {
    "name": "record_prism_log",
    "description": "실질적 결정에 대한 PRISM 로그 기록.",
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

# 사용자 응답 텍스트와 감사 로그는 별도 블록
user_facing = ""
prism_code = None
for block in response.content:
    if block.type == "text":
        user_facing += block.text
    elif block.type == "tool_use" and block.name == "record_prism_log":
        prism_code = block.input["code"]

# user_facing → 사용자 인터페이스
# prism_code → 감사 로그 저장소
```

---

## 왜 JSON이 아니라 코드 형식인가

PRISM 로그는 의도적으로 장황한 JSON이 아닌 간결한 코드로 설계되었습니다:

| 속성 | 코드 형식 | JSON 형식 |
|---|---|---|
| 길이 | ~60자 | ~300자 이상 |
| 프라이버시 | 사용자 콘텐츠 없음 | 컨텍스트 유출 리스크 |
| 집계 | 직접 SQL/grep 가능 | flatten 필요 |
| 호출당 비용 | ~25 출력 토큰 | ~150 출력 토큰 |
| 대규모 가독성 | 가능 | 불가능 |

로그는 **요약이 아닌 구조적 지문**입니다. 컨텍스트와 콘텐츠는 대화 로그에 이미 존재합니다. PRISM 코드는 행동 감사에 필요한 것만 포착합니다.

---

## PRISM 로그가 규제 준수에 맞닿는 방식

규제 기관은 점점 더 모든 중요한 AI 결정에 대해 세 가지 질문에 답할 수 있는 기록을 기대하고 있습니다: 맥락이 무엇이었는가, 어떤 추론이 그 결정을 이끌었는가, 사후 검토가 가능한가. PRISM 로그는 각각에 대해 구조화된 증거를 제공합니다:

| 규제 준수 요구 | PRISM 필드 |
|---|---|
| 각 결정의 맥락 기록 | `C:` 레이어 (도메인, 범위, 가역성, 시간) |
| 추론 우선순위의 투명성 | `V:`, `E:` 레이어 |
| 식별 가능한 출처 신뢰 패턴 | `S:` 레이어 |
| 감사용 집계 가능 증거 | 전체 코드 (검색 가능) |
| 모델 버전 간 편차 탐지 | 코드 분포의 시계열 |

### EU AI Act에 대한 참고 매핑

다음 표는 PRISM 필드가 EU AI Act 고위험 조항의 증거로 어떻게 기여할 수 있는지 보여줍니다. **이는 방향 안내이지 준수 주장이 아닙니다** — PRISM 로그는 이 요구사항들에 기여하지만, 단독으로 충족시키지는 않습니다. [DISCLAIMER.md](../DISCLAIMER.md) 참조.

| EU AI Act 조항 | 요구 초점 | 기여하는 PRISM 필드 |
|---|---|---|
| 제12조(1) — 자동 로깅 | 시스템 수명 동안 자동 이벤트 기록 | 실질적 결정마다 방출되는 전체 PRISM 코드 |
| 제12조(2)(a) — 사용 기간 | 시스템 작동 시점 기록 | 호스트가 로그 저장 시점에 추가하는 타임스탬프 |
| 제12조(2) — 추적 가능성 | 위험을 발생시킬 수 있는 상황 식별 | `C:` 레이어 (도메인, 범위, 가역성, 시간) |
| 제12조(3) — 로그 무결성 | 무단 수정에 대한 보호 | 선택적 SHA-256 무결성 헬퍼 ([tools/](../tools/) 참조) |
| 제13조 — 투명성 | 출력 해석을 가능케 하는 정보 | `V:`와 `E:` 레이어 (보고된 추론 우선순위) |
| 제14조 — 인간 감독 | 인간이 AI 작동을 감독할 능력 | 인간 감사인이 검토 가능한 구조화 코드 |
| 제15조 — 정확성·견고성 | 유사 조건에서 일관된 행동 | 시간·버전에 걸친 코드 집계 분석 |

제12조(3)의 로그 무결성은 선택적 `prism-hash` 유틸리티([tools/prism_hash.py](../tools/prism_hash.py))로 지원됩니다. 이 도구는 각 로그에 대해 변조 탐지 가능한 SHA-256 해시를 생성합니다.

본 표준은 특정 규제와의 법적 동등성을 주장하지 않습니다. 제공하는 것은 컴플라이언스 프로그램과 제3자 감사인이 자체 문서와 함께 참조할 수 있는 **구조화된 증거**입니다.

---

## 이 표준이 주장하지 않는 것

솔직한 한계:

- **모델이 "실제로" 그렇게 추론했다는 증명이 아닙니다.** LLM의 자기 보고는 사후적 정당화일 수 있습니다. PRISM 로그는 *보고된* 추론이지, 인과적 트레이스가 아닙니다.
- **독립 감사를 대체하지 않습니다.** 내부 로그는 규제 효력을 가지려면 외부 검증이 필요합니다.
- **이것만으로 특정 규제 준수가 보장되지 않습니다.** 구조화된 증거를 제공할 뿐, 준수는 이를 둘러싼 거버넌스 체계 전체에 달려 있습니다.

이 한계는 모든 추론 로그(CoT, 어텐션 트레이스, 내부 문서)의 공통 특성입니다. PRISM 로그는 대규모 감사 관점에서 가장 우월한 포맷이지, 완전한 해법은 아닙니다.

---

## 상업 서비스 (선택 사항)

이 표준은 MIT 라이선스 하에 영구 무료입니다. 일부 조직은 추가로 다음이 필요할 수 있습니다:

- **"PRISM Compliant" 인증** — 배치된 시스템이 표준에 부합하는지 제3자 검증
- **업계 벤치마크 데이터** — 자사 시스템을 업계 평균과 비교
- **감사인 교육** — 인증 감사인 프로그램
- **엔터프라이즈 컨설팅** — 조직 맞춤 가치 위계 설계 및 거버넌스 통합

이 서비스는 [AI Integrity Organization (AIO)](https://aioq.org)에서 제공합니다. 표준 사용에 서비스 구매는 필요 없습니다.

---

## 이론적 기반

PRISM은 스위스 등록 비영리 기관 [AI Integrity Organization (AIO)](https://aioq.org)이 개발하고 유지합니다.

본 표준은 다음에 기반합니다:

- **Schwartz 가치 이론** (Schwartz, 1992, 2012) — 80개 이상 문화에서 검증된 10가지 보편적 인간 가치
- **Walton 논증 스킴** (Walton, 2008) — 추론에서의 증거 유형 분류
- **Source Credibility Theory** (Hovland, Janis & Kelley, 1953; Pornpitakpan, 2004) — 출처 신뢰도 위계

Working Papers:

- S. Lee (2026a). AI Integrity: Definition, Authority Stack Model, and Enhanced Cascade Mapping Hypothesis. arXiv:cs.AI.
- S. Lee (2026b). The PRISM Framework for Measuring AI Value Hierarchies. arXiv:cs.AI.
- S. Lee (2026c). Measuring AI Value Priorities: Empirical Analysis. arXiv:cs.AI.
- S. Lee (2026d). PRISM Risk Signal Framework: Hierarchy-Based Red Lines for AI Behavioral Risk. SSRN 6449079.

[OECD Catalogue of Tools & Metrics for Trustworthy AI](https://oecd.ai)에 등재.

---

## 레포 구성

| 파일 | 목적 |
|---|---|
| [`SPECIFICATION.md`](../SPECIFICATION.md) | v1.0 코드 명세 전체 (출력 모드 정의 포함) |
| [`DISCLAIMER.md`](../DISCLAIMER.md) | 범위, 한계, 무보증 조항 |
| [`system_prompts/prism_v1_en_inline.md`](../system_prompts/prism_v1_en_inline.md) | Mode A 프롬프트 — 영문 |
| [`system_prompts/prism_v1_en_json.md`](../system_prompts/prism_v1_en_json.md) | Mode B 프롬프트 — 영문 |
| [`system_prompts/prism_v1_en_tool.md`](../system_prompts/prism_v1_en_tool.md) | Mode C 프롬프트 — 영문 |
| [`system_prompts/prism_v1_kr_*.md`](../system_prompts/) | 세 모드의 한국어 버전 |
| [`examples/`](../examples/) | 7개 도메인 실제 로그 예시 |
| [`tests/validate.py`](../tests/validate.py) | 다중 모드 추출 지원 검증기 |
| [`tools/prism_parser.py`](../tools/prism_parser.py) | 코드 추출 및 구조화 파서 헬퍼 |
| [`tools/prism_hash.py`](../tools/prism_hash.py) | SHA-256 무결성 헬퍼 (독립/체인 해시) |
| [`docs/integration_guide.md`](./integration_guide.md) | 제공자별 통합 가이드 |

---

## 라이선스 및 면책

MIT. 사용, 수정, 상업적 임베딩 모두 자유. [LICENSE](../LICENSE) 참조.

**중요:** 본 표준은 기술 명세이며 법률 자문이 아닙니다. 사용이 특정 규제 준수를 보장하지 않습니다. 전체 범위와 한계는 [DISCLAIMER.md](../DISCLAIMER.md) 참조.

출처 표시는 권장되지만 필수는 아닙니다.

---

## 연락처

- 이슈/제안: GitHub 이슈 등록
- 상업적 문의: 2sk@aioq.org
- 웹사이트: [aioq.org](https://aioq.org)

---

English docs: [README.md](../README.md)
