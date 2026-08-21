/*!
 * engine.js — 도메인 불변 매칭 엔진.
 *
 * "검증된 구조 × 안 써본 맥락": 요구(req) ⊆ 보유(affords) 집합 매칭 →
 * score = 검증도(proven) × 신선도(fresh), 완전 적합만 후보, score 내림차순 순위.
 * 취향 0 · 재현 가능. 무엇을 고를지는 이 코드가 결정하고, 표현(바·패킷·문장)만 각 사이트 몫.
 *
 * 이 파일은 두 라이브 사이트가 그대로(byte-identical) 로드한다 —
 *   classic-bones-modern-fusion  (고전 이야기 뼈대 × 현대 세팅)
 *   proven-models-fresh-niches   (검증된 비즈니스 구조 × 안 파인 니치)
 * "하나의 엔진, 세 번"을 서사가 아니라 코드로도 참이게. 두 도메인은 proven/fresh를
 * 어디서 얻느냐만 다르고(아이템 vs 맥락), 매칭·점수·순위 알고리즘은 같다.
 *
 * canonical: classic-bones-modern-fusion/engine.js  (proven-models 의 사본과 sha 동일)
 * classic <script> 로 로드 → file:// 에서도 돈다(ES module import는 file://에서 막힘).
 */
(function (root) {
  var Engine = {
    // 요구 ⊆ 보유 인가. met=충족 코드, miss=부족 코드, fit=완전적합, rate=충족률.
    match: function (req, affords) {
      var A = affords || [];
      var met = req.filter(function (c) { return A.indexOf(c) !== -1; });
      var miss = req.filter(function (c) { return A.indexOf(c) === -1; });
      return { met: met, miss: miss, fit: met.length === req.length,
               rate: req.length ? met.length / req.length : 0 };
    },
    // 점수 = 검증도 × 신선도. 완전 적합이 아니면 0. 반올림은 표시 몫(round1).
    score: function (proven, fresh, fit) { return fit ? proven * fresh : 0; },
    round1: function (x) { return +(+x).toFixed(1); },

    // 한 맥락(affords)에 아이템들을 평가·정렬.
    // get = { req(item), proven(item), fresh(item) } 접근자.
    // 반환: [{item, met, miss, fit, rate, proven, fresh, score}] — score 내림차순, 동점은 rate.
    rank: function (items, affords, get) {
      return items.map(function (it) {
        var m = Engine.match(get.req(it), affords);
        var proven = get.proven(it), fresh = get.fresh(it);
        return { item: it, met: m.met, miss: m.miss, fit: m.fit, rate: m.rate,
                 proven: proven, fresh: fresh, score: Engine.score(proven, fresh, m.fit) };
      }).sort(function (a, b) { return (b.score - a.score) || (b.rate - a.rate); });
    },

    // 아이템 × 맥락 전 조합 중 완전 적합만(디스커버리용).
    // get = { req(item), affords(context), proven(item), fresh(item, context) }.
    combos: function (items, contexts, get) {
      var out = [];
      items.forEach(function (it) {
        contexts.forEach(function (cx) {
          var m = Engine.match(get.req(it), get.affords(cx));
          if (!m.fit) return;
          var proven = get.proven(it), fresh = get.fresh(it, cx);
          out.push({ item: it, context: cx, proven: proven, fresh: fresh,
                     score: Engine.score(proven, fresh, true), met: m.met });
        });
      });
      return out;
    }
  };

  root.Engine = Engine;
  if (typeof module !== 'undefined' && module.exports) module.exports = Engine;
})(typeof self !== 'undefined' ? self : this);
