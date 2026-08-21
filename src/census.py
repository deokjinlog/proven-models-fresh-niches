#!/usr/bin/env python3
"""
니치 미개척도(신선도)를 감(感)이 아니라 데이터로 잰다.

story 도메인의 census.py(WikiPlots 11만편에서 배경 등장수를 셈)를
사업 도메인에 이식한 것 — 여기선 YC 공개 회사 코퍼스(~6,200개사)에서
각 니치에 이미 몇 개 회사가 있나(혼잡도)를 직접 센다.

혼잡도 ↓ = 미개척 = 신선도 ↑.

산출물:
  data/census.json        감사용 전체 결과(코퍼스 크기·니치별 count·샘플)
  data/niche_block.js     index.html에 붙일 NICHE={...} 리터럴(census.py가 소유)

한계(정직하게):
  - YC = 글로벌/미국 스타트업. 한국 시장 혼잡도가 아니라 "가장 큰 생태계에서도
    얼마나 붐비나"의 프록시. 그래도 여기서조차 비어있으면 진짜 미개척이다.
  - 매칭은 영어 키워드 기반 → 실제보다 적게 잡히는 하한(下限)이다. 그래서
    raw count와 샘플 회사명을 같이 남겨 누구나 검수할 수 있게 한다.

실행:  ~/.local/bin/uv run python src/census.py
"""
import json, re, math, sys, time, urllib.request, urllib.error
from datetime import date
from pathlib import Path

API = "https://api.ycombinator.com/v0.1/companies"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"; DATA.mkdir(exist_ok=True)

# ── 니치: index.html에서 이관 + census용 영어 키워드(정규식) ──────────────
# hunch = 기존 손감(感) fresh 값(대조용으로 보존). kw = 이 니치에 실제 영업 중인
# 회사를 식별하는 패턴. 오탐을 줄이려 짧고 모호한 토큰은 \b 경계/문맥을 건다.
NICHES = {
 "pet_funeral":   dict(name="반려동물 장례", gloss="파편화·불투명·감정재",
    affords=["B1","B3","B5"], hunch=.85,
    kw=[r"pet\s*(loss|funeral|cremation|memorial|death|grief|end[- ]of[- ]life|hospice)",
        r"(dog|cat|pet)[^.]{0,25}(euthan|cremat|memorial|after[- ]?life)"]),
 "freelance_tax": dict(name="프리랜서 세무·정산", gloss="수기·전문성·반복",
    affords=["B8","B11","B4","B3"], hunch=.7,
    kw=[r"freelanc\w*[^.]{0,25}(tax|account|bookkeep|invoic|finance)",
        r"\b1099\b", r"self[- ]employed[^.]{0,25}(tax|account|finance)",
        r"gig\s*worker[^.]{0,25}(tax|finance|benefit|pay)",
        r"(independent )?contractor[^.]{0,20}(tax|account|payroll)"]),
 "solo_mfg":      dict(name="1인 제조업(스마트공장 미만)", gloss="엑셀·파편·데이터부재",
    affords=["B8","B12","B1"], hunch=.8,
    kw=[r"(small|smb|micro)[^.]{0,20}manufactur", r"job\s*shop", r"machine\s*shop",
        r"shop\s*floor", r"contract manufactur", r"factory[^.]{0,20}(small|smb)"]),
 "special_ed":    dict(name="특수교육 학부모", gloss="정보난·또래필요·전문성",
    affords=["B7","B9","B3","B11"], hunch=.85,
    kw=[r"special\s*(education|needs|ed)", r"\biep\b", r"autis", r"\badhd\b",
        r"learning\s*(disabilit|difference|disorder)", r"neurodiver",
        r"dyslex", r"speech\s*therap"]),
 "local_smb_mkt": dict(name="동네 소상공인 마케팅", gloss="수기·발견난·흩어진수요",
    affords=["B8","B7","B2"], hunch=.6,
    kw=[r"(local|small)\s*business[^.]{0,25}(marketing|advertis|reviews|reputation|leads)",
        r"\bsmb\b[^.]{0,20}(marketing|advertis|growth)",
        r"local\s*merchant", r"main\s*street\s*business"]),
 "midlife_job":   dict(name="중장년 재취업", gloss="흩어진수요·발견난·불신",
    affords=["B2","B7","B3"], hunch=.75,
    kw=[r"career\s*(change|transition|switch|pivot)", r"reskill", r"upskill",
        r"second\s*career", r"older\s*(worker|adult)[^.]{0,20}(job|work|career)",
        r"return(ship| to work)", r"mid[- ]?career"]),
 "plant_care":    dict(name="반려식물 케어", gloss="선택난·반복·커뮤니티",
    affords=["B7","B4","B9"], hunch=.8,
    kw=[r"house\s*plant", r"indoor\s*plant", r"plant\s*care", r"gardening",
        r"\bplant\s*(parent|app|shop|deliver)"]),
 "creator_tax":   dict(name="크리에이터 정산·세금", gloss="수기·전문성·반복",
    affords=["B8","B11","B4"], hunch=.8,
    kw=[r"creator[^.]{0,25}(tax|account|finance|payout|payment|monet|bank)",
        r"influencer[^.]{0,25}(tax|finance|payment|payout)",
        r"(youtuber|streamer|content creator)[^.]{0,25}(tax|finance|income|pay)"]),
 "immigrant_admin":dict(name="이민자·유학생 행정", gloss="규제·불신·정보난·즉시",
    affords=["B11","B3","B7","B5"], hunch=.85,
    kw=[r"immigrat", r"immigrant", r"\bvisa\b", r"green\s*card", r"work\s*permit",
        r"international\s*student", r"expat", r"newcomer[^.]{0,20}(settle|bank|admin)"]),
 "used_baby":     dict(name="중고 유아용품 순환", gloss="유휴자산·흩어진수요·불신",
    affords=["B6","B2","B3"], hunch=.7,
    kw=[r"(baby|infant|kids|children|toddler)[^.]{0,25}(resale|resell|second[- ]?hand|used|reuse|rental|hand[- ]me[- ]down|circular)",
        r"(resale|second[- ]?hand|circular)[^.]{0,20}(baby|kids|children|maternity)"]),
 "farm_direct":   dict(name="소규모 농가 직거래", gloss="파편공급·흩어진수요·불신",
    affords=["B1","B2","B3"], hunch=.7,
    kw=[r"farm(er)?[- ]?to[- ]?(table|door|consumer|fork)", r"farmer\w*\s*(direct|market)",
        r"local\s*farm", r"(agricultur|produce)[^.]{0,20}(marketplace|direct|farmer)",
        r"csa\s*box", r"local\s*produce"]),
 "senior_digital":dict(name="시니어 디지털 돌봄", gloss="즉시·불신·반복",
    affords=["B5","B3","B4"], hunch=.85,
    kw=[r"senior\s*(care|living|health)", r"elder(ly|care)", r"aging[^.]{0,20}(parent|adult|care|place)",
        r"older\s*adult", r"caregiv", r"in[- ]home\s*care"]),
 "home_repair":   dict(name="동네 수리기사(집수리)", gloss="파편·불신·즉시·유휴",
    affords=["B1","B3","B5","B6"], hunch=.75,
    kw=[r"home\s*(repair|service|maintenance|improvement|reno)", r"handyman",
        r"home\s*(pro|contractor)", r"(plumb|electric|hvac)[^.]{0,20}(book|marketplace|service)"]),
 "indie_shop":    dict(name="독립서점·로컬상점", gloss="발견난·커뮤니티·흩어진수요",
    affords=["B7","B9","B2"], hunch=.7,
    kw=[r"(independent|indie|local)\s*book\s*(store|shop)", r"\bbookshop\b",
        r"(independent|indie|boutique)\s*(retail|store|shop|brand)er?",
        r"brick[- ]and[- ]mortar\s*(retail|store|shop|boutique)",
        r"neighborhood\s*(store|shop|boutique)"]),
 "amateur_league":dict(name="아마추어 스포츠 리그", gloss="네트워크·발견난·흩어진수요",
    affords=["B9","B7","B2"], hunch=.8,
    kw=[r"amateur\s*(sport|league|athlet)", r"recreational\s*(league|sport)",
        r"pickup\s*(game|sport|soccer|basketball)", r"local\s*sports\s*(league|team)",
        r"grassroots\s*sport", r"rec\s*league"]),
}

def fetch_all():
    comps, url, seen = [], API, 0
    while url:
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"census/1.0 (portfolio; +deokjinlog)"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    d = json.loads(r.read().decode())
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                if attempt == 3:
                    print(f"  ! give up on {url}: {e}", file=sys.stderr); return comps
                time.sleep(1.5*(attempt+1))
        comps.extend(d.get("companies", []))
        url = d.get("nextPage")
        seen += 1
        if seen % 40 == 0:
            print(f"  … page {d.get('page')}/{d.get('totalPages')} ({len(comps)} companies)", file=sys.stderr)
    return comps

def blob(c):
    parts = [c.get("name"), c.get("oneLiner"), c.get("longDescription")]
    parts += c.get("tags") or []
    parts += c.get("industries") or []
    return " ".join(p for p in parts if p).lower()

def main():
    print("YC 코퍼스 수집 중…", file=sys.stderr)
    comps = fetch_all()
    N = len(comps)
    if N < 500:
        print(f"코퍼스가 너무 작다({N}). 네트워크 확인.", file=sys.stderr); sys.exit(1)
    blobs = [(c.get("name","?"), blob(c)) for c in comps]

    # 니치별 매칭 카운트 + 샘플
    res = {}
    for key, n in NICHES.items():
        pats = [re.compile(p, re.I) for p in n["kw"]]
        hits = [name for name, b in blobs if any(p.search(b) for p in pats)]
        res[key] = {"count": len(hits), "samples": hits[:4]}

    maxc = max(r["count"] for r in res.values()) or 1
    lm = math.log10(maxc+1)
    for key, r in res.items():
        # 혼잡도 → 신선도: log 역스케일(카운트 편차가 커서 선형이면 뭉갬)
        mf = 1 - math.log10(r["count"]+1)/lm
        r["mfresh"] = max(0.10, min(0.95, round(mf, 2)))

    # ── 감사용 census.json ──
    audit = {
        "corpus": "YC companies (api.ycombinator.com/v0.1)",
        "corpus_size": N,
        "fetched": date.today().isoformat(),
        "note": "count=이 니치에 이미 영업 중인 회사 수(영어 키워드 매칭 하한). mfresh=log 역스케일 신선도.",
        "niches": {k: {"name": NICHES[k]["name"], "hunch": NICHES[k]["hunch"], **res[k]} for k in NICHES},
    }
    (DATA/"census.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2))

    # ── index.html에 붙일 NICHE 리터럴 ──
    lines = ["// AUTO-GENERATED by src/census.py — 손대지 말 것(census 재실행으로 갱신).",
             f"// corpus: YC {N}개사 · fetched {date.today().isoformat()}",
             "const NICHE={"]
    order = sorted(NICHES, key=lambda k: -res[k]["mfresh"])  # 신선순
    for k in order:
        n, r = NICHES[k], res[k]
        aff = ",".join(f'"{a}"' for a in n["affords"])
        ex = ",".join(json.dumps(s, ensure_ascii=False) for s in r["samples"])
        lines.append(
            f' {k}:{{name:{json.dumps(n["name"],ensure_ascii=False)},'
            f'gloss:{json.dumps(n["gloss"],ensure_ascii=False)},'
            f'affords:[{aff}],fresh:{r["mfresh"]},hunch:{n["hunch"]},'
            f'census:{r["count"]},exc:[{ex}]}},')
    lines[-1] = lines[-1].rstrip(",")
    lines.append("};")
    lines.append(f"const CENSUS_N={N}; // YC 코퍼스 크기")
    (DATA/"niche_block.js").write_text("\n".join(lines)+"\n")

    # ── 콘솔 리포트: 감 vs 실측 델타 ──
    print(f"\n코퍼스 {N}개사. 니치별 혼잡도(count) → 실측 신선도(mfresh) vs 손감(hunch):\n", file=sys.stderr)
    print(f"  {'니치':<22}{'count':>6}  {'실측':>5}  {'감':>5}  델타", file=sys.stderr)
    for k in sorted(NICHES, key=lambda k: res[k]["count"]):
        n, r = NICHES[k], res[k]
        d = r["mfresh"] - n["hunch"]
        flag = "  ←감이 틀림" if abs(d) >= .2 else ""
        print(f"  {n['name']:<22}{r['count']:>6}  {r['mfresh']*100:>4.0f}%  {n['hunch']*100:>4.0f}%  {d*100:+5.0f}%{flag}", file=sys.stderr)
    print(f"\n→ data/census.json, data/niche_block.js 갱신 완료.", file=sys.stderr)

if __name__ == "__main__":
    main()
