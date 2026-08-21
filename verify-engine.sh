#!/usr/bin/env bash
# engine.js 무결성 게이트.
#   1) engine.js 가 커밋된 canonical 해시(engine.sha256)와 일치하는가
#   2) 단위 불변식(engine.test.js)이 통과하는가
# 이 스크립트와 engine.js·engine.sha256 은 classic-bones-modern-fusion ↔
# proven-models-fresh-niches 두 repo에서 byte-identical 이어야 한다.
# 한쪽 engine.js 를 고치면 반대편에 복사하지 않는 한 이 게이트가 어긋남을 잡는다.
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c engine.sha256          # canonical 해시와 일치?
node engine.test.js                  # 매칭·점수·순위 불변식
echo "✓ engine.js 무결 — canonical 해시 일치 + 단위테스트 통과"
