# proven-models-fresh-niches

> **“될 만한 사업 아이디어 줘”** 라고 하면 모델은 학습에서 흔한 쪽 — 이미 붉은 바다 — 으로 회귀한다.
> 이 도구는 **실제로 검증된 비즈니스 구조**를 **아직 아무도 안 판 니치**에 얹고, *왜 신선한지 데이터로* 남긴다.
> 무엇을 조합할지는 **코드가 결정**(취향 0)하고, 표현만 모델이 쓴다.

한 번 발명한 엔진 — **검증된 구조 × 안 써본 맥락 + 데이터 근거 → 결정적 매칭** — 을 세 번째 도메인(사업 아이디어)에 인스턴스화한 것.
[design-explosion](#)(디자인)·[classic-bones-modern-fusion](https://deokjinlog.github.io/classic-bones-modern-fusion/)(이야기)과 **같은 엔진**이다.

## 바로 보기 (레포에서 바로 열림)

- 💡 **아이디어 엔진**: <https://deokjinlog.github.io/proven-models-fresh-niches/> — 검증된 비즈니스 구조 14종 × 안 파인 니치 21종, 신선순 랭킹 + 근거
- 🔩 **프레임워크 허브** (하나의 엔진, 세 번 증명): <https://deokjinlog.github.io/proven-models-fresh-niches/framework.html>

## 어떻게 동작하나

| 층 | 내용 |
|---|---|
| **검증된 구조** | 반복 검증돼 살아남은 비즈니스 모델 14종 (마켓플레이스·수직SaaS·애그리게이터·데이터플라이휠·긴급전문 온디맨드·공동구매 등, 각 `req`+`proven`+성공사례) |
| **조건 스키마** | 그 모델이 **요구**하는 조건의 공통 어휘 B1–B12 (분절공급·신뢰문제·반복니즈·유휴자산·산업워크플로 등) |
| **안 파인 니치** | 이식할 현대 시장 21종 (반려장례·소상공인폐업·프리랜서세무·특수교육·이민자행정·장애인접근성 등), 어떤 조건을 **보유**하는지 태깅 |

- 매칭 = `모델의 요구 ⊆ 니치의 보유` — 집합 연산이라 **취향 0 · 재현 가능**.
- 점수 = 신선도(niche.fresh) × 검증도(model.proven). ★ 딥 아이디어 패킷 7개는 가설·comp·왜 되나·리스크까지.
- 정적 웹에서 API·키 없이 돈다 — 매칭·근거는 LLM이 필요 없다.

## 왜 데이터를 세나 — 신선도는 감이 아니다

story 도메인이 WikiPlots 11만편에서 배경 등장수를 세듯([classic-bones의 census](https://deokjinlog.github.io/classic-bones-modern-fusion/)), 여기선 **YC 공개 회사 ~6,200개사**(`api.ycombinator.com/v0.1`)에서 각 니치에 **이미 몇 개 회사가 있나(혼잡도)**를 직접 센다 — `src/census.py`. 혼잡도 ↓ = 미개척 = 신선도 ↑.

결과가 **손감을 뒤집었다**: 감으로 "신선하다" 여긴 **이민자 행정(27개사)·시니어 돌봄(19)·집수리(36)** 가 실측에선 가장 붐볐고, **반려동물 장례(0)·아마추어 리그(0)·중고 유아용품(1)** 이 진짜로 비어있었다. 21개 중 12개의 손감이 20%p 이상 틀렸다 — *"신선한 걸 줘"가 흔한 쪽으로 회귀한다*는 걸 도구가 자기 데이터로 증명한 셈. 매 회사 샘플명을 UI에 공개해 누구나 검수할 수 있다.

**한계(정직하게)**: YC = 글로벌/미국 스타트업이라 **한국 시장 혼잡도가 아니다**(가장 큰 생태계에서조차 비었나의 프록시). 영어 키워드 매칭이라 실제보다 적게 잡히는 **하한**이다. 그래서 raw count와 샘플 회사명을 같이 남긴다. 진짜 시장 규모·경쟁 밀도 데이터를 붙이는 건 향후.

## 왜 세 번째 도메인인가

세 번을 만들고 나서야 보였다 — 이 방법은 이야기의 성질도, 디자인의 성질도, 사업의 성질도 아닌 **도메인 불변의 엔진**이다.
자세히: **[프레임워크 허브](https://deokjinlog.github.io/proven-models-fresh-niches/framework.html)**.

## 레포 구조

| 경로 | 내용 |
|---|---|
| `index.html` | 아이디어 엔진 (조건 B1–B12 · 구조 14 · 니치 21 · 딥 패킷 7, `engine.js` 로드) |
| `engine.js` · `engine.test.js` · `verify-engine.sh` · `engine.sha256` | 도메인 불변 매칭 엔진 — 요구 ⊆ 보유 · `score = proven × fresh` · 순위. `classic-bones-modern-fusion`과 **byte-identical**(canonical은 거기, 여기선 사본). `bash verify-engine.sh` = 해시 고정 + 17개 불변식 게이트(사본이 어긋나면 실패) |
| `framework.html` | "하나의 엔진, 세 번 증명" 포폴 허브 |
| `src/census.py` | YC ~6,200개사에서 니치별 혼잡도 실측 → 신선도. `data/census.json`(감사)·`data/niche_block.js`(index.html용 NICHE 리터럴) 생성 |
| `data/census.json` | 코퍼스 크기·니치별 count·샘플 회사명 (재현·검수용) |

재실행: `~/.local/bin/uv run python src/census.py` (키·라이브러리 불필요, stdlib만).

포트폴리오·비상업.
