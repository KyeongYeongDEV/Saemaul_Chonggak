# 백엔드 규칙

## 아키텍처: DDD + 4계층 + 약식 헥사고날
- domain/        → 순수 Python. Entity, Value Object, Repository ABC, Domain Service
- application/   → UseCase (단일 책임). Command/Query 패턴
- infrastructure/→ SQLAlchemy Repository 구현, 외부 API Adapter (토스, FCM, S3)
- presentation/  → FastAPI Router. 비즈니스 로직 없음

## 도메인 레이어 규칙 (STRICT)
- `import sqlalchemy` 금지
- `import redis` 금지
- `import requests` / `import httpx` 금지
- `from app.infrastructure.*` 금지
- 허용: `dataclasses`, `abc`, `typing`, `datetime`, `enum`, `uuid`

## Redis 캐시 패턴
- Cache-Aside: 조회 시 Redis 먼저 → Miss 시 DB → Redis 저장
- 캐시 무효화: 상품 수정 시 관련 키 즉시 삭제
- 타임세일 재고: Redis Lua Script (Atomic DECR)
- TTL: 상품목록 5분, 상품상세 10분, 배너 1시간

## 에러 처리
- 도메인 예외: `domain/{domain}/exceptions.py` 정의
- HTTP 변환: `presentation/middleware/error_handler.py`
- 공통 HTTP 예외: `core/exceptions.py`

## UseCase 작성 규칙
- 클래스 1개 = 메서드 1개 (execute)
- 생성자에서 Repository/Port DI
- 트랜잭션 경계는 UseCase에서 관리

## 보안
- 관리자 API: `Depends(require_admin)` 필수
- 관리자 모든 행동: audit_logs 테이블 기록
- 결제 금액: DB 조회값만 사용 (클라이언트 값 무시)
- 비밀번호: bcrypt (rounds=12)
