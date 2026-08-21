/* engine.js 단위 테스트 — node engine.test.js (byte-identical 사본이라 두 repo 공용).
   매칭·점수·순위 불변식을 고정한다. 실패 시 비정상 종료. */
var Engine = require('./engine.js');
var pass = 0, fail = 0;
function ok(cond, msg) { if (cond) { pass++; } else { fail++; console.error('  ✗ ' + msg); } }
function eq(a, b, msg) { ok(JSON.stringify(a) === JSON.stringify(b), msg + ' (got ' + JSON.stringify(a) + ')'); }

// match: 요구 ⊆ 보유
var m1 = Engine.match(['A', 'B'], ['A', 'B', 'C']);
ok(m1.fit === true, 'req⊆affords → fit');
eq(m1.miss, [], 'fit이면 miss 없음');
ok(m1.rate === 1, 'fit rate=1');
var m2 = Engine.match(['A', 'B'], ['A']);
ok(m2.fit === false, '부족하면 fit=false');
eq(m2.met, ['A'], 'met=충족분');
eq(m2.miss, ['B'], 'miss=부족분');
ok(Math.abs(m2.rate - 0.5) < 1e-9, 'rate=0.5');
eq(Engine.match([], ['X']).rate, 0, 'req 비면 rate=0');

// score: proven × fresh, 완전 적합만
ok(Engine.score(10, 0.5, true) === 5, 'score=proven×fresh');
ok(Engine.score(10, 0.5, false) === 0, '부적합이면 score=0');
ok(Engine.round1(6.04) === 6, 'round1 내림');
ok(Engine.round1(6.06) === 6.1, 'round1 올림');

// rank: score 내림차순, 완전적합만 점수, 동점은 rate
var items = ['big', 'small', 'nofit'];
var meta = { big:  { req: ['A'], proven: 9, fresh: 1 },
             small:{ req: ['A'], proven: 3, fresh: 1 },
             nofit:{ req: ['A', 'Z'], proven: 99, fresh: 1 } };
var r = Engine.rank(items, ['A'], {
  req: function (k) { return meta[k].req; },
  proven: function (k) { return meta[k].proven; },
  fresh: function (k) { return meta[k].fresh; } });
eq(r.map(function (x) { return x.item; }), ['big', 'small', 'nofit'], '순위: 검증 높은 fit 먼저, 부적합 꼴찌');
ok(r[2].score === 0, '부적합(nofit)은 proven 99여도 score 0');
ok(r[0].score === 9 && r[1].score === 3, 'fit 점수=proven×fresh');

// combos: 완전 적합 조합만
var cb = Engine.combos(['k1'], ['s1', 's2'], {
  req: function () { return ['A', 'B']; },
  affords: function (s) { return s === 's1' ? ['A', 'B', 'C'] : ['A']; },
  proven: function () { return 5; },
  fresh: function () { return 0.8; } });
ok(cb.length === 1 && cb[0].context === 's1', 'combos: 완전적합(s1)만');
ok(Math.abs(cb[0].score - 4) < 1e-9, 'combos score=5×0.8');

console.log((fail === 0 ? '✓ ' : '✗ ') + pass + ' passed, ' + fail + ' failed');
process.exit(fail === 0 ? 0 : 1);
