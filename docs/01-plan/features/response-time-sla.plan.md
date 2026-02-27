# [Plan] response-time-sla

> **조회(READ) API** 응답 시간 2초 이내 보장 — 결제·주문 생성 등 비동기 처리는 제외

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 기능명 | Response Time SLA (응답 시간 서비스 수준 협약) |
| 연관 프로젝트 | Saemaul Chonggak Shopping Server |
| 핵심 요구사항 | **조회(READ) API 응답은 2초(2000ms) 이내** |
| 우선순위 | High — 사용자 이탈률 직결 |
| **적용 범위** | **조회 REST API** (상품/카테고리/배너/검색/장바구니/주문내역/포인트 등) |
| **제외 범위** | **결제, 주문 생성, 푸시 알림 등 외부 API 연동·비동기 처리** |

---

## 2. 요구사항 분석

### 2.1 SLA 목표

**적용 대상: 조회(READ) API 전용**

| 구분 | 목표 | 비고 |
|------|------|------|
| 조회 API Hard Limit | **p99 < 2000ms** | 조회 API 절대 상한선 |
| 일반 조회 API (상품/목록/카테고리) | p99 < 300ms | Redis 캐시 활용 |
| 검색 API (MySQL FULLTEXT) | p99 < 500ms | 초기, 쿼리 최적화 |
| 인증 API (JWT 발급) | p99 < 200ms | 캐시 우선 처리 |
| 장바구니 조회 | p99 < 300ms | Redis 캐시 활용 |

**2초 SLA 제외 대상 (비동기/외부 연동)**

| 구분 | 처리 방식 | 비고 |
|------|---------|------|
| 결제 API (토스페이먼츠) | UX "처리 중" 표시 + 웹훅 결과 수신 | 외부 PG사 응답 시간 보장 불가 |
| 주문 생성 | 비동기 이벤트 처리 + 상태 폴링 | 분산 트랜잭션 포함 |
| 푸시 알림 발송 | 완전 비동기 (FCM) | 응답 지연 없이 즉시 반환 |
| 쿠폰/포인트 적용 (결제 시) | Redis Lua Script 원자 처리 | 결제 흐름 일부, SLA 별도 |

> **2초 기준 근거**: Google Research — 페이지 로드 3초 초과 시 모바일 이탈률 53% 증가. 조회 API 응답 기준 2초는 UI 렌더링 여유를 포함한 UX 최소 기준.

### 2.2 현재 계획 대비 변경 사항

기존 `shopping-server.plan.md`의 비기능 요구사항:
- 일반 API p99 < 500ms ✅ (2초 내 포함)
- Elasticsearch p99 < 200ms ✅ (2초 내 포함)

**추가/강화 항목**:
- 결제/주문 등 외부 API 연동 포함 hard limit 2초 명시
- 타임아웃 정책 수립 (2초 초과 시 처리 방안)
- 성능 모니터링 체계 구축

---

## 3. 기능 범위 (Scope)

### 3.1 포함 (In-Scope) — 조회 API 2초 보장 대상

- [ ] **Redis 캐싱 전략**: 반복 조회 API 캐시 적용
  - 상품 목록/상세: TTL 10분
  - 카테고리 목록: TTL 1시간
  - 배너 목록: TTL 30분
- [ ] **DB 쿼리 최적화**: N+1 방지, 인덱스 설계 (조회 성능)
- [ ] **검색 쿼리 최적화**: MySQL FULLTEXT 튜닝
- [ ] **비동기 처리 분리**: 조회 응답에 포함되지 않는 작업 완전 비동기화 (푸시 알림, 이벤트 발행)
- [ ] **성능 모니터링**: Actuator + Micrometer 기반 응답 시간 메트릭 수집 (조회 API 전용)
- [ ] **타임아웃 정책**: 외부 API 호출 타임아웃 설정 (조회 흐름에서 외부 의존 제거 목적)
  - Kakao/Naver OAuth (인증): 연결 1초, 읽기 1초
  - Firebase FCM: 완전 비동기 (조회 응답과 무관)
- [ ] **Circuit Breaker**: 외부 서비스 장애 시 빠른 실패 처리 (Resilience4j) — 인증 흐름 보호

### 3.2 제외 (Out-of-Scope) — 2초 SLA 미적용

- **결제 API**: 토스페이먼츠 외부 응답 포함 → UX "처리 중" 상태 표시로 대응
- **주문 생성**: 분산 트랜잭션(재고/쿠폰/포인트) 포함 → 비동기 처리 + 폴링
- **푸시 알림 발송**: 완전 비동기, FCM 처리 시간 서버 응답과 무관
- 인프라 확장 (서버 스케일 아웃)
- 배치/리포트성 API (관리자 대용량 조회)

---

## 4. 기술 전략

### 4.1 레이어별 최적화 포인트

```
[Presentation Layer]
  - Response Compression (gzip)
  - Connection Keep-Alive 설정
  - Virtual Thread 활용 (Java 21)

[Application Layer]
  - 비동기 이벤트 처리 (ApplicationEventPublisher)
  - 외부 API 호출 병렬화 (CompletableFuture)

[Domain Layer]
  - 도메인 로직 경량화

[Infrastructure Layer]
  - Redis 캐싱 (Cache-Aside 패턴)
  - HikariCP 커넥션 풀 최적화
  - Elasticsearch 쿼리 최적화
  - 외부 API 타임아웃 + Circuit Breaker
```

### 4.2 캐싱 전략

| API | 캐시 대상 | TTL | 무효화 트리거 |
|-----|----------|-----|--------------|
| 상품 목록 | Redis | 5min | 상품 수정/삭제 |
| 상품 상세 | Redis | 5min | 상품 수정/삭제 |
| 카테고리 | Redis | 1hr | 카테고리 변경 |
| 배너 | Redis | 30min | 배너 수정 |
| JWT 검증 | Redis | Access Token 만료까지 | 로그아웃/탈퇴 |

### 4.3 타임아웃 정책

```
전체 API 응답 = DB 쿼리 + 캐시 + 외부 API + 비즈니스 로직
                              ≤ 2000ms (hard limit)

외부 API 타임아웃 설정:
- 토스페이먼츠: connectTimeout=1000ms, readTimeout=1500ms
- OAuth2 (Kakao/Naver): connectTimeout=1000ms, readTimeout=1000ms
- FCM: connectTimeout=500ms, readTimeout=1000ms (비동기 처리)
```

### 4.4 Circuit Breaker (Resilience4j)

```
외부 API 장애 시:
1. 임계치 도달 (실패율 50% 이상) → Circuit Open
2. Circuit Open → 즉시 fallback 응답 (2초 대기 없음)
3. 30초 후 Half-Open → 정상 여부 확인
```

---

## 5. 성능 측정 방안

### 5.1 로컬 측정

```bash
# Spring Actuator 메트릭
GET /actuator/metrics/http.server.requests

# 부하 테스트 (k6 또는 Gatling)
- 동시 사용자: 100명
- 지속 시간: 5분
- 목표: p99 < 2000ms
```

### 5.2 모니터링 메트릭

| 메트릭 | 수집 도구 | 임계 알람 |
|--------|----------|----------|
| 응답 시간 p99 | Micrometer | > 1500ms 경고, > 2000ms 알람 |
| DB 커넥션 풀 | HikariCP | 사용률 > 80% 경고 |
| Redis 히트율 | Redis INFO | < 70% 경고 |
| ES 검색 시간 | ES Slowlog | > 300ms 로깅 |

---

## 6. 도메인별 위험 분석

| 도메인 | 잠재적 지연 원인 | 대응 방안 |
|--------|----------------|----------|
| 결제 | 토스페이먼츠 외부 API | 타임아웃 + Circuit Breaker |
| 검색 | ES 복잡한 쿼리 | 쿼리 최적화 + 캐싱 |
| 주문 생성 | 재고 차감 + 분산 트랜잭션 | Redis Lua Script (단일 네트워크 왕복) |
| 인증 | DB 조회 반복 | Redis JWT 캐싱 |
| 장바구니 | 상품 가격 재계산 | 캐시된 상품 정보 활용 |

---

## 7. 구현 우선순위

1. **P0 (즉시)**: 타임아웃 정책 전면 적용 (외부 API 무한 대기 방지)
2. **P1 (1주차)**: Redis 캐싱 — 상품/카테고리/배너
3. **P1 (1주차)**: Circuit Breaker — 결제/OAuth2
4. **P2 (2주차)**: DB 쿼리 최적화 (N+1, 인덱스)
5. **P2 (2주차)**: Elasticsearch 쿼리 튜닝
6. **P3 (3주차)**: 성능 모니터링 대시보드 구축

---

## 8. 미결 사항 (Open Questions)

- [ ] 결제 API는 외부 PG사 응답 시간 보장 불가 → 사용자에게 "처리 중" UI 피드백으로 UX 보완 여부
- [ ] 비동기 처리 시 WebFlux 도입 검토 여부 (Spring MVC 유지 vs 전환)
- [ ] APM 도구 연동 여부 (Elastic APM, Datadog 등)
- [ ] 2초 초과 시 API 응답 정책 — 에러 반환 vs 처리 계속 후 알림

---

**작성일**: 2026-02-27
**작성자**: Claude Code (Sonnet 4.6)
**상태**: Draft
**연관 플랜**: shopping-server.plan.md (비기능 요구사항 섹션 7)
