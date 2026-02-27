# [Plan] shopping-server

> 쇼핑 앱용 Spring Boot Java 백엔드 서버

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | Saemaul Chonggak Shopping Server |
| 기술 스택 | Spring Boot 3.x (Java 21), AWS RDS MySQL 8.0, Redis, Firebase |
| 예상 규모 | 초기 2만명, 확장 대비 설계 |
| 프로젝트 구조 | 단일 모듈 (패키지 기반 레이어 분리) |
| 아키텍처 | **Layered Architecture + DDD** (presentation / application / domain / infra) |
| 개발 방법론 | TDD (Red-Green-Refactor) |
| 결제 | 토스페이먼츠 연동 |
| 분산 트랜잭션 | Redis + Lua Script (결제, 쿠폰, 재고) |
| 이미지 저장 | AWS S3 |
| 배포 | AWS EC2 + Docker-compose (Nginx 로드밸런서 포함) |
| CI/CD | GitHub Actions (무중단 Blue-Green 배포) |
| API 문서 | SpringDoc OpenAPI (Swagger) — 한글 설명 필수 |

---

## 2. 기능 범위 (Scope)

### 2.1 인증 및 회원 관리
- [ ] **SSO 로그인**: 카카오, 네이버 OAuth2 소셜 로그인
  - [ ] **JWT 인증**: Access Token + Refresh Token 발급/갱신/폐기
  - [ ] **이용약관 동의 관리**: 필수/선택 약관 동의 여부 저장 및 조회
  - [ ] **개인정보 동의 관리**: 개인정보 수집·이용 동의 관리
  - [ ] **푸시알림 동의 관리**: 마케팅/서비스 푸시 수신 동의 설정
  - [ ] **적립금(포인트) 관리**: 적립/차감/조회/사용 이력 관리

### 2.2 상품
- [ ] **카테고리별 상품 노출**: 신상품, 베스트셀러, 특가 등 분류별 목록
  - [ ] **상품 검색**: MySQL FULLTEXT 검색 + QueryDSL 복합 필터/정렬 (초기), 추후 Elasticsearch 도입 예정
  - [ ] **홈 화면 배너 관리**: 배너 등록/수정/삭제/순서 관리 (관리자 API `/admin/**`)

### 2.3 장바구니
- [ ] **장바구니 CRUD**: 상품 추가/수량 변경/삭제
  - [ ] **장바구니 조회**: 현재 담긴 상품 및 금액 계산
  - [ ] **실시간 재고 연동**: 장바구니 담기 시 Redis 재고 수량 확인 및 선점

### 2.4 결제
- [ ] **토스페이먼츠 연동**: 결제 요청/승인/취소 API 연동
  - [ ] **결제 원자성 보장**: Redis Lua Script 기반 분산 트랜잭션
  - [ ] **쿠폰 시스템**: 쿠폰 발행/적용/사용 처리
  - [ ] **쿠폰 원자성 보장**: Redis Lua Script 기반 중복 사용 방지

### 2.5 주문
- [ ] **주문 생성 및 상태 추적**: 입금전 → 결제완료 → 배송준비 → 배송중 → 배송완료
  - [ ] **취소 신청 및 처리**: 주문 취소 요청/승인/환불
  - [ ] **교환 신청 및 조회**: 교환 요청/상태 추적
  - [ ] **반품 신청 및 조회**: 반품 요청/상태 추적

### 2.6 고객 서비스 (CS)
- [ ] **리뷰 시스템**: 상품 리뷰 작성/수정/삭제/조회, 평점 집계
  - [ ] **1:1 문의**: 문의 등록/조회/답변 (사용자 ↔ 관리자)
  - [ ] **FAQ**: 자주 묻는 질문 카테고리별 관리 및 조회
  - [ ] **공지사항**: 게시글 형태 공지 등록/수정/삭제/조회

### 2.7 알림
- [ ] **푸시 알림 발송**: Firebase FCM 연동, 주문 상태 변경/마케팅 발송

### 2.8 관리자 (Admin) — 전용 사이트에서 로그인 후 사용
- [ ] **관리자 로그인**: 이메일/비밀번호 로그인 (ROLE_ADMIN 계정, 자동 가입 불가)
  - [ ] **상품 관리**: 상품 등록/수정/삭제, 카테고리 관리
  - [ ] **배너 관리**: 홈 배너 등록/수정/삭제/순서
  - [ ] **주문 관리**: 주문 목록 조회, 상태 변경 (배송 처리 등)
  - [ ] **쿠폰 관리**: 쿠폰 발행/만료/목록 조회
  - [ ] **회원 관리**: 회원 목록 조회, 회원 정지/탈퇴 처리
  - [ ] **1:1 문의 답변**: 문의 조회 및 답변 등록
  - [ ] **공지/FAQ 관리**: 공지사항·FAQ 등록/수정/삭제

---

## 3. 아키텍처 설계 원칙

### 3.1 레이어드 아키텍처 + DDD 패키지 구조

```
src/main/java/com/saemaul/chonggak/
│
├── domain/                              ← [Domain Layer] DDD 핵심
│   ├── member/
│   │   ├── Member.java                  (Aggregate Root)
│   │   ├── MemberRepository.java        (Repository Interface)
│   │   ├── vo/                          (Value Object: Email, PhoneNumber)
│   │   ├── event/                       (Domain Event: MemberRegisteredEvent)
│   │   └── service/                     (Domain Service: 도메인 순수 로직)
│   ├── product/
│   │   ├── Product.java                 (Aggregate Root)
│   │   ├── ProductRepository.java
│   │   ├── vo/                          (Money, ProductCategory)
│   │   └── service/                     (StockDomainService)
│   ├── order/
│   │   ├── Order.java                   (Aggregate Root)
│   │   ├── OrderItem.java               (Entity, Order 내부)
│   │   ├── OrderRepository.java
│   │   ├── vo/                          (OrderStatus, DeliveryInfo)
│   │   └── event/                       (OrderPlacedEvent, OrderCancelledEvent)
│   ├── payment/
│   │   ├── Payment.java                 (Aggregate Root)
│   │   ├── PaymentRepository.java
│   │   └── event/                       (PaymentCompletedEvent)
│   ├── coupon/
│   │   ├── Coupon.java                  (Aggregate Root)
│   │   ├── UserCoupon.java              (Entity)
│   │   ├── CouponRepository.java
│   │   └── service/                     (CouponDomainService)
│   └── ...
│
├── application/                         ← [Application Layer] UseCase 조율
│   ├── member/
│   │   ├── MemberService.java           (회원 가입/로그인/탈퇴 오케스트레이션)
│   │   └── dto/                         (SignupCommand, MemberResult)
│   ├── product/
│   │   ├── ProductService.java
│   │   └── dto/
│   ├── order/
│   │   ├── OrderService.java            (주문 생성/취소/교환/반품)
│   │   └── dto/
│   ├── payment/
│   │   ├── PaymentService.java          (결제 요청/승인/환불)
│   │   └── dto/
│   └── ...
│
├── infra/                               ← [Infrastructure Layer] 외부 구현체
│   ├── persistence/
│   │   ├── member/                      (MemberJpaRepository, MemberRepositoryImpl)
│   │   ├── product/
│   │   └── order/
│   ├── redis/
│   │   ├── StockRedisRepository.java    (실시간 재고, Lua Script)
│   │   └── CacheRepository.java        (상품/카테고리 캐시)
│   ├── s3/
│   │   └── S3ImageUploader.java        (Presigned URL)
│   ├── payment/
│   │   └── TossPaymentClient.java      (토스페이먼츠 API)
│   ├── oauth/
│   │   └── KakaoOAuthClient.java       (Kakao/Naver OAuth2)
│   └── fcm/
│       └── FcmPushSender.java          (Firebase FCM)
│
├── presentation/                        ← [Presentation Layer] Controller
│   ├── member/
│   │   ├── MemberController.java
│   │   └── dto/                         (Request/Response DTO)
│   ├── product/
│   ├── order/
│   ├── admin/
│   │   ├── AdminProductController.java
│   │   └── AdminOrderController.java
│   └── ...
│
└── global/                              ← 공통 설정/유틸
    ├── config/                          (SecurityConfig, SwaggerConfig, RedisConfig)
    ├── exception/                       (GlobalExceptionHandler, ErrorCode, BusinessException)
    └── response/                        (ApiResponse<T>)
```

**레이어 의존성 방향**:
```
presentation → application → domain ← infra
                   ↑                      ↑
               global/exception       global/config
```

### 3.2 DDD 핵심 개념 적용

| DDD 개념 | 적용 위치 | 예시 |
|---------|---------|------|
| **Aggregate Root** | `domain/{도메인}/{도메인}.java` | `Member`, `Order`, `Product` |
| **Value Object** | `domain/{도메인}/vo/` | `Money(금액)`, `OrderStatus`, `Email` |
| **Domain Event** | `domain/{도메인}/event/` | `OrderPlacedEvent`, `PaymentCompletedEvent` |
| **Domain Service** | `domain/{도메인}/service/` | `StockDomainService`, `CouponDomainService` |
| **Repository (Interface)** | `domain/{도메인}/` | `OrderRepository` (인터페이스만) |
| **Repository (Impl)** | `infra/persistence/` | `OrderRepositoryImpl` |
| **Application Service** | `application/{도메인}/` | `OrderService` (트랜잭션, 오케스트레이션) |

**DDD 규칙**:
- Aggregate Root를 통해서만 내부 Entity 접근 (Order → OrderItem)
- Value Object는 불변(Immutable), `equals()`/`hashCode()` 재정의
- Domain Layer는 순수 Java — Spring 어노테이션 최소화, 외부 라이브러리 금지
- Domain Event는 `ApplicationEventPublisher`로 발행 → 비동기 처리

### 3.3 관리자 API 분리 전략

**방식**: `presentation/admin/` 패키지 내 `/admin/**` 경로 분리 (역할 기반 엔드포인트)

```
일반 사용자 API: /api/v1/**     ← 일반 사용자 앱에서 호출
관리자 API:     /admin/v1/**   ← 관리자 전용 사이트(별도 프론트엔드)에서 호출
```

**접근 제어**:
- 관리자 전용 사이트에서 이메일/비밀번호 로그인
- `ROLE_ADMIN` 계정으로만 로그인 가능 (사용자 ROLE_USER와 분리)
- Spring Security `hasRole('ADMIN')` + `@PreAuthorize` 어노테이션으로 API 보호
- 관리자 계정은 DB에서 직접 생성/관리 (자동 가입 불가)

### 3.4 명명 규칙
- Aggregate/Entity: 명사 단수형 → `Member`, `Order`, `OrderItem`
- Value Object: 의미 있는 명사 → `Money`, `OrderStatus`, `Email`
- Domain Service: `{도메인}DomainService` → `StockDomainService`
- Application Service: `{도메인}Service` → `OrderService`, `PaymentService`
- Repository Interface: `{Aggregate}Repository` → domain 레이어에 위치
- 메소드: 읽자마자 이해 가능한 동사+명사 → `findAvailableCouponsByUserId()`, `decreaseStockWithLuaScript()`

---

## 4. 기술 스택

| 분류 | 기술 | 용도 |
|------|------|------|
| Language | Java 21 | 메인 언어 (Virtual Thread 활용) |
| Framework | Spring Boot 3.x | 서버 프레임워크 |
| ORM | Spring Data JPA + QueryDSL | DB 접근 |
| DB | AWS RDS MySQL 8.0 (db.t3.medium) | 주 데이터베이스 |
| Cache/Lock | Redis 7.x | 캐싱, 분산 락, Lua Script, 실시간 재고 |
| Search | MySQL FULLTEXT + QueryDSL | 상품 검색 (초기), 추후 Elasticsearch 도입 예정 |
| Auth | Spring Security + OAuth2 + JWT | 인증/인가 |
| Payment | 토스페이먼츠 API | 결제 |
| Push | Firebase FCM | 푸시 알림 |
| Storage | AWS S3 | 이미지/파일 저장 |
| Infra | AWS EC2 | 서버 배포 |
| LB | Nginx (Docker container) | 로드밸런서, SSL 종료, /admin 접근 제어 |
| Container | Docker + Docker-compose | 컨테이너화 및 로컬/서버 환경 통일 |
| CI/CD | GitHub Actions | 자동 빌드/테스트/무중단 배포 |
| Test | JUnit 5 + Mockito + Testcontainers | TDD |
| Docs | SpringDoc OpenAPI (Swagger) + 한글 설명 | API 문서 (전 엔드포인트 한글 설명 필수) |
| Build | Gradle (Kotlin DSL) | 빌드 |

---

## 5. 확장성 고려사항

### 5.1 2만명 → 이후 확장 대비
- **Connection Pool**: HikariCP 최적화 (초기 max 50, 확장 시 100+)
- **Redis Cluster 준비**: 단일 Redis → 클러스터 전환 용이하도록 추상화
- **검색 단계별 확장**: MySQL FULLTEXT(초기) → Elasticsearch 도입(트래픽 증가 시) 용이하게 `SearchRepository` 인터페이스 추상화
- **이벤트 기반 비동기**: `ApplicationEventPublisher` → 추후 Kafka 전환 용이하게 설계
- **RDS 확장 경로**: db.t3.medium → db.t3.large → db.r6g.large (읽기 레플리카 추가)
- **인덱스 전략**: 자주 조회되는 컬럼 (user_id, order_status, product_category 등) 인덱스 적용

### 5.2 Redis 캐싱 전략 (Cache-Aside 패턴 기본)

> **원칙**: 읽기 빈도 높음 + 쓰기 빈도 낮음 + 실시간성 불필요 → 캐시 우선 적용

#### 5.2.1 도메인별 캐싱 전략표

| 도메인 | 캐시 대상 | 패턴 | TTL | Redis Key | 무효화 트리거 |
|--------|---------|------|-----|-----------|--------------|
| **상품** | 상품 상세 | Cache-Aside | 10분 | `product:{id}` | 상품 수정/삭제 |
| **상품** | 카테고리별 목록 (1페이지) | Cache-Aside | 5분 | `product:list:{category}:{page}` | 상품 등록/수정/삭제 |
| **상품** | 베스트셀러 목록 | 주기적 갱신 | 1시간 | `product:bestseller` | 스케줄러 갱신 |
| **상품** | 신상품 목록 | Cache-Aside | 10분 | `product:new` | 상품 등록 |
| **카테고리** | 전체 카테고리 트리 | Cache-Aside | 1시간 | `category:all` | 카테고리 변경 |
| **배너** | 홈 배너 목록 | Cache-Aside | 30분 | `banner:home` | 배너 수정/삭제 |
| **인증** | Refresh Token | Write-Through | 7일 | `refresh:{userId}` | 로그아웃/탈퇴 |
| **인증** | Access Token 블랙리스트 | Write-Through | AT 만료까지 | `blacklist:{token}` | 로그아웃 |
| **검색** | 인기 검색어 Top10 | 주기적 갱신 | 1시간 | `search:popular` | 스케줄러 갱신 |
| **재고** | 실시간 재고 수량 | Write-Through | 영구 | `stock:{productId}` | 결제/취소 (Lua Script) |
| **쿠폰** | 쿠폰 사용 가능 여부 | Write-Through | 쿠폰 만료까지 | `coupon:{couponId}:{userId}` | 쿠폰 사용 (Lua Script) |
| **장바구니** | 장바구니 (비로그인) | TTL 기반 | 3일 | `cart:guest:{sessionId}` | 로그인 시 DB 이전 |
| **적립금** | 사용자 포인트 잔액 | Cache-Aside | 5분 | `point:{userId}` | 적립/차감 시 |
| **공지/FAQ** | 공지사항 목록 | Cache-Aside | 1시간 | `notice:list:{page}` | 공지 등록/수정 |
| **공지/FAQ** | FAQ 카테고리별 목록 | Cache-Aside | 2시간 | `faq:list:{category}` | FAQ 변경 |
| **Rate Limit** | API 요청 횟수 | Atomic INCR | 1분 | `ratelimit:{ip}:{api}` | TTL 만료 자동 |

#### 5.2.2 패턴별 구현 방식

**Cache-Aside (Lazy Loading)** — 기본 패턴:
```
요청 → Redis 조회
  ├── HIT: Redis에서 반환 (DB 조회 없음)
  └── MISS: DB 조회 → Redis 저장 → 반환
변경 시: DB 업데이트 → Redis 키 삭제 (다음 요청에서 재생성)
```
```java
// @Cacheable (Spring Cache + Redis)
@Cacheable(value = "product", key = "#id")
public ProductDto getProduct(Long id) { ... }

@CacheEvict(value = "product", key = "#id")
public void updateProduct(Long id, ...) { ... }
```

**Write-Through** — 인증/재고/쿠폰:
```
쓰기 → DB 저장 + Redis 동시 갱신 (항상 일관성 유지)
```

**주기적 갱신 (Scheduled)** — 베스트셀러/인기 검색어:
```
매 1시간마다 스케줄러 실행:
  1. DB에서 최근 7일 판매량 집계
  2. Redis bestseller 키 갱신 (SETEX)
```

**Lua Script (Atomic)** — 재고/쿠폰:
```lua
-- 재고 차감 (음수 방지)
local stock = redis.call('GET', KEYS[1])
if tonumber(stock) < tonumber(ARGV[1]) then
    return -1  -- 재고 부족
end
return redis.call('DECRBY', KEYS[1], ARGV[1])
```

#### 5.2.3 캐시 적용 우선순위

| 우선순위 | 대상 | 이유 |
|---------|------|------|
| P0 | 재고/쿠폰 (Lua Script) | 동시성 제어 필수 |
| P0 | Refresh Token 저장 | 인증 보안 필수 |
| P1 | 상품 상세/목록 | 가장 빈번한 읽기 요청 |
| P1 | 카테고리 트리 | 전 페이지 공통 호출 |
| P1 | 배너 목록 | 홈 진입 시 매번 호출 |
| P2 | 베스트셀러/신상품 | 집계 쿼리 부담 감소 |
| P2 | 포인트 잔액 | 주문/결제 흐름에서 반복 조회 |
| P3 | 공지/FAQ | 읽기 多, 변경 少 |
| P3 | 인기 검색어 | UX 향상 |
| P4 | Rate Limiting | API 남용 방지 |

#### 5.2.4 캐시 일관성 보장

- **TTL 기반 만료**: 최악의 경우에도 TTL 후 자동 최신화
- **명시적 무효화**: 데이터 변경 시 즉시 `@CacheEvict` 또는 Redis DEL
- **정합성 검증**: 결제 완료 후 재고/포인트 DB↔Redis 동기화 스케줄러 실행 (1분 주기)

#### 5.2.5 Redis 토큰 관리 전략 (인증)

**토큰 구조**:

| 토큰 | 저장 위치 | 만료 | 용도 |
|------|---------|------|------|
| Access Token (JWT) | 클라이언트 메모리 | 1시간 | API 인증 (stateless) |
| Refresh Token | **Redis** (서버) | 7일 | Access Token 재발급 |
| AT 블랙리스트 | **Redis** (서버) | AT 잔여 만료까지 | 로그아웃된 AT 무효화 |

**Redis Key 구조**:
```
refresh:{userId}:{deviceId}   → Refresh Token 값  (TTL: 7일)
blacklist:{jti}               → "logout"           (TTL: AT 잔여 만료 시간)
```
> `{deviceId}`: 다중 기기 로그인 지원. 단일 기기면 `refresh:{userId}` 사용

---

**① 로그인 흐름**:
```
[클라이언트] → POST /api/v1/auth/login
       │
[서버]  1. 사용자 인증 (DB 조회 + 비밀번호 검증 또는 OAuth2)
        2. Access Token 생성 (JWT, exp: 1h, jti 포함)
        3. Refresh Token 생성 (UUID)
        4. Redis SET: refresh:{userId}:{deviceId} = RT값  (EX 604800)
        5. AT → 응답 Body, RT → HttpOnly Cookie 반환
```

**② API 요청 흐름 (AT 검증)**:
```
[클라이언트] → Authorization: Bearer {AT}
       │
[서버]  1. JWT 서명 검증
        2. Redis GET: blacklist:{jti} → 존재하면 401 반환
        3. 정상이면 요청 처리
```

**③ Access Token 재발급 (RT 사용)**:
```
[클라이언트] → POST /api/v1/auth/reissue  (쿠키에 RT 포함)
       │
[서버]  1. 쿠키에서 RT 추출
        2. Redis GET: refresh:{userId}:{deviceId} → 저장된 RT와 비교
        3. 일치하면 새 AT 발급 + 새 RT 발급
        4. Redis 업데이트: 새 RT 저장 (RT Rotation)
        5. 새 AT → Body, 새 RT → HttpOnly Cookie 반환
        (불일치 → RT 삭제 + 401: 토큰 탈취 의심)
```

**④ 로그아웃 흐름**:
```
[클라이언트] → POST /api/v1/auth/logout  (AT + RT 쿠키)
       │
[서버]  1. Redis DEL: refresh:{userId}:{deviceId}  (RT 즉시 무효화)
        2. AT의 남은 만료 시간 계산 (remainingTtl = exp - now)
        3. Redis SET: blacklist:{jti} = "logout"  (EX remainingTtl)
        4. RT 쿠키 삭제 지시 응답
```

**⑤ 전체 기기 강제 로그아웃** (보안 이슈 발생 시):
```
[서버]  Redis KEYS refresh:{userId}:* → 모두 DEL
        → 모든 기기에서 다음 AT 만료 시 자동 로그아웃
        → AT 블랙리스트는 기기별로 등록 (즉시 차단 필요 시)
```

**보안 원칙**:
- RT는 반드시 `HttpOnly + Secure` 쿠키 (XSS 탈취 방지)
- AT는 응답 Body → 클라이언트 메모리 저장 (localStorage 금지)
- RT Rotation: 재발급 시 기존 RT 즉시 폐기 → 탈취 RT 재사용 불가
- AT `jti` 클레임 필수: 블랙리스트 조회 key로 사용

### 5.3 분산 트랜잭션 전략
```
결제 흐름:
1. Redis Lua Script로 쿠폰/적립금/재고 선점 (원자적 차감)
2. 토스페이먼츠 결제 승인 요청
3. 성공 → DB 커밋 + Redis 확정
   실패 → Redis 롤백 (Lua Script) + 보상 트랜잭션
```

---

## 6. 인프라 및 배포 아키텍처

### 6.1 전체 인프라 구성

```
[Internet]
    │  :80 / :443
    ▼
┌─────────────────────────────────────┐
│         EC2 t3.medium               │
│  Docker-compose                     │
│  ┌────────────────────────────┐     │
│  │  Nginx (port 80/443)       │     │  ← 로드밸런서, SSL 종료
│  │  - upstream: app_blue      │     │  ← Rate Limiting, SSL 종료
│  │  - upstream: app_green     │     │
│  └────────┬──────────┬────────┘     │
│           │          │              │
│  ┌────────▼──┐  ┌────▼──────┐      │
│  │ app_blue  │  │ app_green │      │  ← Blue-Green 중 1개만 활성
│  │  :8080    │  │  :8081    │      │
│  └───────────┘  └───────────┘      │
│                                     │
│  ┌──────────────────┐               │
│  │  Redis 7.x :6379 │               │
│  └──────────────────┘               │
└─────────────────────────────────────┘

[AWS 관리형 서비스]
  ├── AWS RDS MySQL 8.0 (db.t3.medium, Single-AZ)  ← 주 DB
  └── AWS S3  ← 이미지/파일 저장

[외부 서비스]
  ├── Firebase FCM — 푸시 알림
  ├── 토스페이먼츠 — 결제
  └── Kakao/Naver OAuth2 — 소셜 로그인

EC2 인스턴스 타입 선정 근거:
- 초기 2만명 MAU → 동시 접속 추정 500~1,000명
- t3.medium (2 vCPU / 4GB): Nginx + Spring Boot × 1 + Redis 조합 충분
- 트래픽 증가 시 t3.large (2 vCPU / 8GB) → 멀티 EC2로 수평 확장

Nginx 역할:
- 로드밸런서 (app_blue / app_green 간 upstream 전환으로 Blue-Green)
- SSL 종료 (HTTPS, Let's Encrypt)
- **Rate Limiting** — IP당 과도한 요청 차단 (limit_req 모듈)
- 정적 파일 서빙 (필요 시)
```

### 6.2 Docker-compose 구성

**운영** `docker-compose.yml`:
```yaml
services:
  nginx:      # Nginx — port 80, 443 (로드밸런서)
  app_blue:   # Spring Boot Blue — port 8080
  app_green:  # Spring Boot Green — port 8081 (배포 시 교체)
  redis:      # Redis 7.x — port 6379 (AOF 영속성 활성화: appendonly yes)
```

> **Redis 배포 방식**: Docker 내 단일 Redis (초기 추천)
> - 이유: 초기 2만명 규모에서 별도 EC2는 비용/관리 오버헤드가 큼
> - 컨테이너 내부 통신으로 네트워크 지연 최소화
> - `appendonly yes` 설정으로 AOF 영속성 보장 (EC2 재시작 시 데이터 복구)
> - 확장 시점: Redis 메모리 사용량 70% 초과 또는 MAU 10만 이상 → 별도 EC2 또는 ElastiCache 이전

**Nginx 설정** `nginx/nginx.conf`:
```nginx
# ─── Rate Limiting Zone 정의 (IP 기준) ───────────────────────────────
# binary_remote_addr: IP당 7byte, 10MB = 약 80만 IP 추적 가능
limit_req_zone $binary_remote_addr zone=general:10m  rate=20r/s;
limit_req_zone $binary_remote_addr zone=auth:10m     rate=5r/s;
limit_req_zone $binary_remote_addr zone=payment:10m  rate=2r/s;
limit_req_zone $binary_remote_addr zone=search:10m   rate=30r/s;

upstream backend {
    server app_blue:8080;   # 배포 시 app_green:8081 으로 교체
}

server {
    listen 80;

    # ─── 인증 API (로그인/회원가입) — 브루트포스 방지 ───────────────
    # 5r/s: 초당 5회, burst=10: 순간 최대 10개 큐잉, nodelay: 초과 즉시 429
    location ~* ^/api/v1/(auth|members/signup|members/login) {
        limit_req zone=auth burst=10 nodelay;
        limit_req_status 429;
        proxy_pass http://backend;
    }

    # ─── 결제 API — 가장 엄격 ────────────────────────────────────────
    location /api/v1/payments/ {
        limit_req zone=payment burst=5 nodelay;
        limit_req_status 429;
        proxy_pass http://backend;
    }

    # ─── 검색 API — 여유 있게 ────────────────────────────────────────
    location /api/v1/products/search {
        limit_req zone=search burst=50 nodelay;
        limit_req_status 429;
        proxy_pass http://backend;
    }

    # ─── 일반 API ────────────────────────────────────────────────────
    location /api/ {
        limit_req zone=general burst=40 nodelay;
        limit_req_status 429;
        proxy_pass http://backend;
    }

    location / {
        proxy_pass http://backend;
    }

    # ─── 429 응답 커스텀 메시지 ──────────────────────────────────────
    error_page 429 /429.json;
    location = /429.json {
        default_type application/json;
        return 429 '{"code":"TOO_MANY_REQUESTS","message":"요청이 너무 많습니다. 잠시 후 다시 시도해주세요."}';
    }
}
```

**Rate Limiting 전략표**:

| Zone | 적용 경로 | 기본 속도 | Burst | 목적 |
|------|---------|---------|-------|------|
| `auth` | 로그인, 회원가입 | 5 req/s | 10 | 브루트포스/크리덴셜 스터핑 방지 |
| `payment` | 결제 API | 2 req/s | 5 | 중복 결제 시도 방지 |
| `search` | 상품 검색 | 30 req/s | 50 | 검색 봇 완화, 여유 있게 |
| `general` | 나머지 /api/** | 20 req/s | 40 | 전반적 서버 보호 |

> **burst**: 순간 트래픽 허용 큐 크기. 정상 사용자는 burst 내에서 처리되고, 초과 시 즉시 `429 Too Many Requests` 반환.
> **nodelay**: burst 내 요청을 지연 없이 처리 (UX 보호). 없으면 요청이 큐에서 천천히 처리됨.

**로컬 개발** `docker-compose.local.yml`:
```yaml
services:
  nginx:
  app_blue:
  redis:
  mysql:  # RDS 대체용 로컬 MySQL 8.0
```

> 운영 배포: `docker-compose up -d` → Nginx + app_blue + Redis 실행
> Blue-Green: app_green 배포 후 nginx.conf upstream 변경 → `docker exec nginx nginx -s reload`

### 6.3 무중단 CI/CD (Blue-Green 배포)

```
[GitHub Push → main]
        │
        ▼
[GitHub Actions]
  1. Gradle 빌드 + 테스트
  2. Docker 이미지 빌드 → DockerHub / ECR 푸시
  3. EC2에 SSH 접속
  4. app_green 컨테이너에 새 이미지 배포 (docker-compose pull app_green && up)
  5. app_green 헬스체크 통과 확인 (/actuator/health)
  6. nginx.conf upstream → app_green으로 변경
  7. docker exec nginx nginx -s reload  (Nginx 무중단 재시작)
  8. app_blue 컨테이너 정지 (다음 배포 시 역할 전환)
```

**무중단 보장**: Nginx `reload`는 기존 커넥션 유지 → 새 요청만 app_green으로 → 다운타임 0초

### 6.4 AWS S3 이미지 관리

| 항목 | 내용 |
|------|------|
| Presigned URL | 클라이언트 직접 업로드 (서버 부하 최소화) |
| 버킷 구조 | `saemaul-chonggak/{env}/products/`, `users/`, `banners/` |
| 접근 제어 | Private 버킷, CloudFront CDN으로 이미지 서빙 |
| 허용 타입 | jpg, png, webp — 최대 10MB |

### 6.5 실시간 재고 관리 (Redis)

```
재고 관리 흐름:
1. 상품 등록 시 → Redis에 재고 수량 초기화 (HASH: stock:{productId})
2. 장바구니 담기 → Redis DECRBY로 수량 선점 (음수 방지: Lua Script)
3. 결제 완료 → DB에 재고 최종 반영 + Redis 동기화
4. 결제 실패/취소 → Redis INCRBY로 재고 복구
5. 주기적 DB↔Redis 정합성 검증 (스케줄러)
```

**동시성 제어**: Redis Lua Script로 원자적 재고 차감 → 초과 판매 방지

---

## 7. 도메인 목록

| 도메인 | 주요 엔티티 |
|--------|-------------|
| Member | Member, MemberAgreement, PointHistory |
| Product | Product, ProductCategory, Banner |
| Cart | Cart, CartItem |
| Order | Order, OrderItem, OrderStatusHistory |
| Payment | Payment, PaymentHistory |
| Coupon | Coupon, UserCoupon, CouponUsageHistory |
| Review | Review, ReviewImage |
| CS | Inquiry, InquiryAnswer, FAQ, Notice |
| Notification | NotificationLog, FcmToken |

---

## 8. 비기능 요구사항

| 항목 | 목표 |
|------|------|
| **조회 API 응답 시간** | **Hard Limit p99 < 2000ms** (상품/카테고리/검색/장바구니 등 READ API) |
| 일반 조회 API | p99 < 300ms (Redis 캐시 활용) |
| 검색 API | MySQL FULLTEXT p99 < 500ms (초기), ES 도입 후 p99 < 200ms |
| **결제/주문 생성** | **2초 SLA 제외** — 외부 PG사 응답 포함, UX로 처리 중 상태 표시 |
| **기타 비동기 처리** | **2초 SLA 제외** — 푸시 알림 발송, 분산 트랜잭션 등 비동기 작업 |
| 결제 처리 | 분산 트랜잭션 완결성 100% |
| 재고 정합성 | Redis ↔ DB 동기화 99.99% (보상 트랜잭션) |
| 코드 커버리지 | Unit Test 80% 이상 (TDD 준수) |
| API 문서 | **Swagger 전 엔드포인트 한글 설명 100%** |
| 무중단 배포 | Blue-Green 전환 다운타임 0초 |

---

## 9. 개발 순서 (추천)

1. **Phase 1**: 프로젝트 기반 설정 (패키지 구조, Layered+DDD 뼈대, Docker-compose, CI/CD, RDS 연결)
2. **Phase 2**: 인증/회원 도메인 (SSO, JWT, 약관, 적립금)
3. **Phase 3**: 상품/카테고리/배너/검색 (S3 이미지, MySQL FULLTEXT 검색)
4. **Phase 4**: 장바구니 (Redis 실시간 재고 연동)
5. **Phase 5**: 쿠폰 시스템 (Redis Lua Script)
6. **Phase 6**: 결제 (토스페이먼츠 + 분산 트랜잭션)
7. **Phase 7**: 주문/취소/교환/반품
8. **Phase 8**: CS (리뷰, 1:1문의, FAQ, 공지사항)
9. **Phase 9**: 푸시 알림 (Firebase FCM)
10. **Phase 10**: 운영 배포 (EC2 + ALB + Blue-Green CI/CD)
11. **Phase 11 (추후)**: Elasticsearch 도입 — 검색 품질 고도화

---

## 10. 미결 사항 (Open Questions)

- [x] ~~멀티모듈 구조~~ → **단일 모듈 확정** (Layered Architecture + DDD, 패키지 기반 레이어 분리)
- [x] ~~이미지 저장 방식~~ → **AWS S3 확정** (Presigned URL + CloudFront)
- [x] ~~관리자 API 분리~~ → **역할 기반 `/admin/**` 엔드포인트 확정** (관리자 전용 사이트 로그인 + Spring Security ADMIN 역할)
- [x] ~~실시간 재고 관리~~ → **Redis Lua Script 확정**
- [x] ~~배포 환경~~ → **AWS EC2 t3.medium + Docker-compose (Nginx + app_blue/green + Redis) + GitHub Actions Blue-Green 확정**
- [x] ~~DB~~ → **AWS RDS MySQL 8.0 (db.t3.medium) 확정**
- [x] ~~EC2 인스턴스 타입~~ → **t3.medium 확정** (초기 2만명 규모 적합, 업그레이드 경로 수립)
- [x] ~~Elasticsearch~~ → **초기 미도입 확정**, MySQL FULLTEXT로 시작 후 추후 도입
- [ ] RDS Multi-AZ 전환 시점 (트래픽 기준 정의 필요)
- [x] ~~관리자 허용 IP~~ → **관리자 전용 사이트 로그인으로 대체** (IP 제한 없음)

---

**작성일**: 2026-02-27
**최종 수정**: 2026-02-27 (Layered+DDD, RDS MySQL, ES 미도입, EC2 t3.medium, Docker Nginx LB, Blue-Green 확정)
**작성자**: Claude Code (Sonnet 4.6)
**상태**: Draft
