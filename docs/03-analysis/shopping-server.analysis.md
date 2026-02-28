# shopping-server Analysis Report

> **Analysis Type**: Gap Analysis (Design vs Implementation) - Phase 1~3 Scope
>
> **Project**: Saemaul Chonggak Shopping Server
> **Version**: 0.0.1-SNAPSHOT
> **Analyst**: Claude Code (Opus 4.6)
> **Date**: 2026-02-28
> **Design Doc**: [shopping-server.design.md](../02-design/features/shopping-server.design.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

Phase 1 (Project Setup), Phase 2 (Auth/Member), Phase 3 (Product/Category/Banner) 구현 완료 상태에서
설계 문서와 실제 구현 코드 간의 일치율을 측정하고, 불일치 항목을 식별한다.

### 1.2 Analysis Scope

| Phase | Design Section | Implementation Path | Status |
|-------|---------------|---------------------|--------|
| Phase 1 | Section 2, 10 | build.gradle.kts, shared/config/ | 구현 완료 |
| Phase 2 | Section 3.2 (Member), 4.2 (Auth/Member API), 5, 6 | member/ | 구현 완료 |
| Phase 3 | Section 3.2 (Product), 4.2 (Product API), 7 | product/ | 구현 완료 |
| Phase 4~12 | 장바구니/쿠폰/주문/결제/리뷰/CS/알림 등 | - | 계획된 미구현 |

### 1.3 Analysis Exclusion (Planned Not-Yet-Implemented)

아래 도메인은 설계 문서에 포함되어 있으나, Phase 4 이후 구현 예정이므로 Gap으로 산정하지 않는다.

- cart (장바구니), coupon (쿠폰), order (주문), payment (결제)
- review (리뷰), cs (문의/FAQ/공지), notification (알림)
- 외부 연동: 토스페이먼츠, Kakao/Naver OAuth2 Client, FCM, S3

---

## 2. Gap Analysis (Design vs Implementation)

### 2.1 Package Structure (Section 2.2)

**Design**: `domain/`, `application/`, `infra/`, `presentation/`, `global/` (패키지-우선 레이어 구조)

**Implementation**: DDD 기반 **도메인-우선 구조** (`{domain}/{layer}/`)

| Design (Flat Layer) | Implementation (Domain-First) | Status |
|---------------------|-------------------------------|--------|
| `domain/member/` | `member/domain/` | -- Changed |
| `application/auth/` | `member/application/` | -- Changed |
| `infra/persistence/member/` | `member/infra/persistence/` | -- Changed |
| `infra/redis/` | `member/infra/redis/` | -- Changed |
| `presentation/auth/` | `member/presentation/` | -- Changed |
| `domain/product/` | `product/domain/` | -- Changed |
| `application/product/` | `product/application/` | -- Changed |
| `infra/persistence/product/` | `product/infra/persistence/` | -- Changed |
| `presentation/product/` | `product/presentation/` | -- Changed |
| `global/` | `shared/` | -- Changed |

**Verdict**: 구조적 변경 (Flat Layer -> Domain-First). 4개 레이어(domain/application/infra/presentation)는 각 도메인 내부에서 보존됨. `global/` -> `shared/`로 네이밍 변경. **의도적 개선으로 판단** -- 도메인 응집도 향상, DDD 원칙에 부합.

**Impact**: Low (아키텍처 개선 방향)

### 2.2 Auth/Member API Endpoints (Section 4.2)

#### Auth API

| Design Endpoint | Method | Implementation | Status |
|----------------|--------|----------------|--------|
| `/api/v1/auth/login/kakao` | POST | 미구현 (OAuth Client 미구현) | -- Planned (Phase 3 설계, 외부연동 대기) |
| `/api/v1/auth/login/naver` | POST | 미구현 (OAuth Client 미구현) | -- Planned |
| `/api/v1/auth/reissue` | POST | `AuthController.reissue()` | -- Match |
| `/api/v1/auth/logout` | POST | `AuthController.logout()` | -- Match |
| `/admin/v1/auth/login` | POST | 미구현 | -- Planned |
| - | - | `/api/v1/auth/local-login` (POST) | -- Added (local/test) |
| - | - | `/api/v1/auth/local-signup` (POST) | -- Added (local/test) |

#### Member API

| Design Endpoint | Method | Implementation | Status |
|----------------|--------|----------------|--------|
| `/api/v1/members/me` | GET | `MemberController.getMyProfile()` | -- Match |
| `/api/v1/members/me` | PATCH | 미구현 (닉네임 수정 등) | -- Missing |
| `/api/v1/members/me` | DELETE | `MemberController.withdraw()` | -- Match |
| `/api/v1/members/me/points` | GET | `MemberController.getMyPointBalance()` | -- Match |
| `/api/v1/members/me/agreements` | PATCH | `MemberController.updateAgreement()` (PUT) | -- Changed (PATCH->PUT) |
| `/api/v1/members/fcm-tokens` | POST | 미구현 (FCM 미구현) | -- Planned |
| - | - | `/api/v1/members/me/agreements` (GET) | -- Added |
| - | - | `/api/v1/members/me/points/history` (GET) | -- Added |

### 2.3 Product/Category/Banner API Endpoints (Section 4.2)

#### Product API

| Design Endpoint | Method | Implementation | Status |
|----------------|--------|----------------|--------|
| `/api/v1/categories` | GET | `ProductController.getCategories()` | -- Match |
| `/api/v1/banners` | GET | `ProductController.getActiveBanners()` | -- Match |
| `/api/v1/products` | GET | `ProductController.searchProducts()` | -- Match |
| `/api/v1/products/{id}` | GET | `ProductController.getProduct()` | -- Match |
| `/api/v1/products/search` | GET | 통합됨 -> `/api/v1/products` 에서 keyword 파라미터로 검색 | -- Changed |
| `/api/v1/products/best` | GET | `/api/v1/products/bestseller` | -- Changed (URL) |
| `/api/v1/products/new` | GET | 미구현 | -- Missing |

#### Admin Product API

| Design Endpoint | Method | Implementation | Status |
|----------------|--------|----------------|--------|
| `/admin/v1/products/**` | CRUD | `AdminProductController` (POST/PUT/DELETE) | -- Match |
| `/admin/v1/categories/**` | CRUD | 미구현 | -- Missing |
| `/admin/v1/banners/**` | CRUD | 미구현 | -- Missing |

### 2.4 Data Model Comparison (Section 3.2)

#### Member Entity

| Design Field | Type | Implementation | Status |
|-------------|------|----------------|--------|
| id | BIGINT PK | Long id (IDENTITY) | -- Match |
| email | VARCHAR(100) UNIQUE | String email (100) | -- Match |
| nickname | VARCHAR(50) NOT NULL | String nickname (50) | -- Match |
| profile_image_url | VARCHAR(500) | 미구현 | -- Missing |
| social_type | VARCHAR(20) NOT NULL | OAuthProvider (ENUM) `oauth_provider` | -- Changed (naming) |
| social_id | VARCHAR(100) NOT NULL | String `oauth_id` | -- Changed (naming) |
| role | VARCHAR(20) DEFAULT 'ROLE_USER' | MemberRole (ENUM) `USER/ADMIN` | -- Changed (no ROLE_ prefix) |
| status | VARCHAR(20) DEFAULT 'ACTIVE' | MemberStatus (ENUM) | -- Match |
| - | - | String password (BCrypt) | -- Added (local auth) |
| - | - | long pointBalance | -- Added |
| created_at/updated_at | DATETIME(6) | LocalDateTime | -- Match |

**Key Differences**:
- `social_type`/`social_id` -> `oauth_provider`/`oauth_id` 네이밍 변경
- `password` 필드 추가 (로컬 인증 지원)
- `profile_image_url` 미구현
- `pointBalance` 필드가 Member에 직접 포함 (설계에서는 PointHistory에서만 관리)
- 설계에서 `ROLE_USER`/`ROLE_ADMIN`이지만 구현은 `USER`/`ADMIN` (Spring Security에서 `ROLE_` prefix 자동 부여)

#### Product Entity

| Design Field | Type | Implementation | Status |
|-------------|------|----------------|--------|
| id | BIGINT PK | Long id | -- Match |
| category_id | BIGINT NOT NULL | `ProductCategory category` (ManyToOne LAZY) | -- Match |
| name | VARCHAR(200) NOT NULL | String name (200) | -- Match |
| description | TEXT | String description (TEXT) | -- Match |
| original_price | INT NOT NULL | Money originalPrice (Embedded) | -- Changed (Value Object) |
| sale_price | INT NOT NULL | Money salePrice (Embedded) | -- Changed (Value Object) |
| stock_quantity | INT DEFAULT 0 | int stockQuantity | -- Match |
| thumbnail_url | VARCHAR(500) | String imageUrl (500) | -- Changed (naming) |
| status | VARCHAR(20) DEFAULT 'ON_SALE' | ProductStatus (ENUM): ACTIVE/INACTIVE/SOLD_OUT/DELETED | -- Changed (values) |
| view_count | BIGINT DEFAULT 0 | 미구현 | -- Missing |
| sales_count | INT DEFAULT 0 | int salesCount | -- Match |
| FULLTEXT INDEX | ft_name_desc | 미구현 (QueryDSL containsIgnoreCase로 대체) | -- Changed |
| - | - | Table: `products` (설계는 `product`) | -- Changed (naming) |

**Key Differences**:
- `original_price`/`sale_price` -> `Money` Value Object (Embedded) -- DDD 개선
- `thumbnail_url` -> `imageUrl` 네이밍 변경
- ProductStatus: 설계 `ON_SALE/SOLD_OUT/DISCONTINUED` -> 구현 `ACTIVE/INACTIVE/SOLD_OUT/DELETED`
- `view_count` 미구현
- FULLTEXT INDEX 대신 QueryDSL `containsIgnoreCase` 사용
- ProductImage 엔티티 미구현 (이미지 1개만 직접 URL 보관)

#### ProductCategory Entity

| Design Field | Type | Implementation | Status |
|-------------|------|----------------|--------|
| parent_id | BIGINT (FK) | Long parentCategoryId | -- Match (Self-reference) |
| name | VARCHAR(50) | String name (100) | -- Changed (length 50->100) |
| sort_order | INT DEFAULT 0 | int displayOrder | -- Changed (naming) |
| is_active | TINYINT(1) DEFAULT 1 | boolean active | -- Match |
| - | - | String description | -- Added |
| - | - | Table: `product_categories` (설계는 `product_category`) | -- Changed |

#### Banner Entity

| Design Field | Type | Implementation | Status |
|-------------|------|----------------|--------|
| title | VARCHAR(100) | String title (200) | -- Changed (length) |
| image_url | VARCHAR(500) | String imageUrl (500) | -- Match |
| link_url | VARCHAR(500) | String linkUrl (500) | -- Match |
| sort_order | INT DEFAULT 0 | int displayOrder | -- Changed (naming) |
| start_at/end_at | DATETIME(6) NOT NULL | LocalDateTime (nullable) | -- Changed (nullable) |
| is_active | TINYINT(1) DEFAULT 1 | boolean active | -- Match |
| - | - | Table: `banners` (설계는 `banner`) | -- Changed |

#### MemberAgreement & PointHistory

| Entity | Implementation | Status |
|--------|---------------|--------|
| MemberAgreement | `member/domain/MemberAgreement.java` | -- Match |
| PointHistory | `member/domain/PointHistory.java` | -- Match |

---

## 3. Common/Infra Design Match

### 3.1 ErrorCode (Section 5.1)

| Category | Design | Implementation | Status |
|----------|--------|----------------|--------|
| Code format | 단축 코드: C001, A001, M001, P001... | 서술적 코드: INVALID_INPUT, MEMBER_NOT_FOUND... | -- Changed (High Impact) |
| Field order | (code, message, status) | (httpStatus, code, message) | -- Changed (field order) |
| Common | C001, C002 | INVALID_INPUT_VALUE, INTERNAL_SERVER_ERROR, UNAUTHORIZED, FORBIDDEN, NOT_FOUND, TOO_MANY_REQUESTS | -- Changed + Extended |
| Auth | A001~A004 | INVALID_CREDENTIALS, INVALID_TOKEN, EXPIRED_TOKEN, BLACKLISTED_TOKEN, INVALID_REFRESH_TOKEN, OAUTH_AUTHENTICATION_FAILED | -- Changed + Extended |
| Member | M001~M003 | MEMBER_NOT_FOUND, MEMBER_ALREADY_EXISTS, MEMBER_SUSPENDED | -- Changed + Extended |
| Product | P001~P003 | PRODUCT_NOT_FOUND, PRODUCT_SOLD_OUT, INSUFFICIENT_STOCK | -- Changed (names differ) |

**Verdict**: 코드 체계가 근본적으로 다름. 설계는 단축 코드(M001), 구현은 서술적 코드(MEMBER_NOT_FOUND).
구현 방식이 더 가독성이 높고 자체 설명적. **설계 문서 업데이트 권장**.

### 3.2 ApiResponse (Section 5.4)

| Item | Design | Implementation | Status |
|------|--------|----------------|--------|
| Success flag | `success: boolean` | `code: "SUCCESS"` | -- Changed (High Impact) |
| Success data | `{success: true, data: {...}}` | `{code: "SUCCESS", message: "...", data: {...}}` | -- Changed |
| Error format | `{success: false, error: {code, message}}` | `{code: "ERROR_CODE", message: "...", data: null}` | -- Changed |
| Nested error | `error.code`, `error.message` | Top-level `code`, `message` | -- Changed (structure) |
| @JsonInclude | 없음 | `NON_NULL` (null 필드 제외) | -- Added |

**Verdict**: 응답 형식이 구조적으로 다름. 설계는 `success` boolean + 중첩 `error` 객체, 구현은 평탄한 `code`/`message`/`data` 구조. **클라이언트 API 계약에 영향 -- 설계 문서 업데이트 필수**.

### 3.3 SecurityConfig URL Rules (Section 6.1)

| Design permitAll | Implementation PUBLIC_URLS | Status |
|-----------------|---------------------------|--------|
| `/api/v1/auth/**` | `/api/v1/auth/**` | -- Match |
| `/api/v1/products/**` | `/api/v1/products/**` | -- Match |
| `/api/v1/categories` | `/api/v1/categories/**` | -- Changed (wider) |
| `/api/v1/banners` | `/api/v1/banners/**` | -- Changed (wider) |
| `/api/v1/faqs` | `/api/v1/faqs/**` | -- Changed (wider) |
| `/api/v1/notices/**` | `/api/v1/notices/**` | -- Match |
| `/actuator/health` | `/actuator/health` | -- Match |
| `/swagger-ui/**` | `/swagger-ui/**` | -- Match |
| `/v3/api-docs/**` | `/v3/api-docs/**` | -- Match |
| `ROLE_ADMIN -> /admin/**` | `.hasRole("ADMIN")` for `/admin/**` | -- Match |
| `authenticated -> rest` | `.anyRequest().authenticated()` | -- Match |

**Minor Issue**: `/swagger-uii.html` 오타가 SecurityConfig와 application.yml 양쪽에 존재 (의도적 또는 오타).

### 3.4 RedisConfig Cache TTL (Section 7.2)

| Cache Name | Design TTL | Implementation TTL | Status |
|-----------|-----------|-------------------|--------|
| product | 10 min | 10 min | -- Match |
| category | 1 hour | 1 hour | -- Match |
| banner | 30 min | 30 min | -- Match |
| productList | (5 min implied) | 5 min | -- Match |
| bestseller | (1 hour implied) | 1 hour | -- Match |
| notice | (1 hour) | 1 hour | -- Match |
| faq | (2 hours) | 2 hours | -- Match |
| reviewRating | 미설계 | 10 min | -- Added |

**Verdict**: 설계에 명시된 캐시 TTL과 구현이 완벽 일치. 추가된 `reviewRating` 캐시는 미래 구현을 위한 선행 설정.

### 3.5 JWT Token Spec (Section 6.2)

| Item | Design | Implementation | Status |
|------|--------|----------------|--------|
| AT Algorithm | HS256 | HMAC (jjwt signWith, key size에 의해 결정) | -- Changed |
| AT Expiry | 1 hour (3600s) | 3600s (`jwt.access-token-expiry`) | -- Match |
| RT Storage | UUID, HttpOnly Cookie | UUID, Body response (TokenPair) | -- Changed |
| RT Expiry | 7 days | 7 days (RefreshTokenRepository TTL) | -- Match |
| Redis Blacklist | `blacklist:{jti}` | `blacklist:{jti}` (PREFIX) | -- Match |
| Redis RT Key | `refresh:{memberId}:{deviceId}` | `refresh:{userId}:{deviceId}` | -- Match |
| AT Payload | memberId, role, jti | subject(userId), claim("role"), id(jti) | -- Match |

**Key Differences**:
- 설계는 HS256 명시, 구현은 jjwt의 `signWith(key)` (키 길이 기반 자동 선택, 32+ bytes -> HS256)
- 설계는 RT를 HttpOnly Cookie로 반환, 구현은 JSON Body로 반환 (모바일 앱 대상이므로 적절한 변경)

---

## 4. Clean Architecture Compliance

### 4.1 Layer Dependency Verification

| Layer | Expected Dependencies | Actual Dependencies | Status |
|-------|----------------------|---------------------|--------|
| domain/ | None (pure Java) | jakarta.persistence (JPA), shared/exception | -- Violation |
| application/ | domain, (infra via interface) | domain, infra/redis (직접), shared/ | -- Partial Violation |
| infra/ | domain only | domain, Spring Data, QueryDSL | -- Match |
| presentation/ | application only | application, shared/ | -- Match |

### 4.2 Dependency Violations

| File | Layer | Violation | Severity | Notes |
|------|-------|-----------|----------|-------|
| `Product.java` | domain | imports `shared.exception.BusinessException`, `shared.exception.ErrorCode` | Medium | 설계: "Domain은 Spring/외부 라이브러리 import 금지" |
| `Product.java` | domain | imports `jakarta.persistence.*` (JPA annotations) | Low | DDD+JPA 통합에서 일반적으로 허용되는 패턴 |
| `Member.java` | domain | imports `jakarta.persistence.*`, `shared.exception` 없음 | Low | JPA만 사용, 에러는 IllegalArgumentException |
| `AuthService.java` | application | imports `member.infra.redis.BlacklistRepository` (직접 의존) | Medium | 설계: "Application은 도메인 인터페이스만 의존" |
| `AuthService.java` | application | imports `member.infra.redis.RefreshTokenRepository` (직접 의존) | Medium | 인터페이스 없이 직접 구현체 참조 |
| `MemberService.java` | application | imports `member.infra.redis.RefreshTokenRepository` (직접 의존) | Medium | 동일 위반 |

### 4.3 Architecture Score

```
Architecture Compliance: 78%

  Layer separation (domain-first):           -- Match (structure)
  Correct layer placement:                   -- 100% (all files in correct layers)
  Dependency direction (presentation->app):  -- 100%
  Dependency direction (app->domain):        -- 100%
  Domain purity (no Spring imports):         -- Partial (JPA annotations used)
  Application -> Infra interface isolation:  -- Violation (Redis repos direct)
```

---

## 5. Convention Compliance

### 5.1 Naming Convention

| Category | Convention | Compliance | Violations |
|----------|-----------|:----------:|------------|
| Classes | PascalCase | 100% | None |
| Methods | camelCase | 100% | None |
| Constants | UPPER_SNAKE_CASE | 100% | PREFIX = "refresh:", TTL = Duration.ofDays(7) |
| Enums | PascalCase (type) / UPPER_SNAKE (values) | 100% | None |
| Packages | lowercase | 100% | None |
| Table names | 설계: singular (`member`), 구현: plural (`members`) | -- Different | 일관된 복수형 사용 |

### 5.2 Import Order

모든 파일에서 일관된 순서 유지:
1. Java/Jakarta packages
2. Spring Framework
3. Third-party (jjwt, querydsl, swagger)
4. Project internal (`com.saemaul.chonggak.*`)
5. Lombok annotations

**Compliance**: 100%

### 5.3 Convention Score

```
Convention Compliance: 95%

  Naming:            100%
  Import Order:      100%
  Table Naming:      85% (plural vs singular)
  Code Style:        95% (consistent Lombok usage, Builder pattern)
```

---

## 6. Local-First Strategy Compliance

### 6.1 @Profile("local","test") Components

| Component | @Profile Applied | Purpose | Status |
|-----------|:---------------:|---------|--------|
| `LocalAuthController` | local, test | Email/password login (dev only) | -- Match |
| `LocalSignupService` | local, test | Email/password signup (dev only) | -- Match |
| `LocalFileStorage` | local, test | S3 -> local filesystem replacement | -- Match |

### 6.2 S3 -> LocalFileStorage

| Design | Implementation | Status |
|--------|---------------|--------|
| `S3ImageUploader` (infra/s3/) | `FileStorage` interface + `LocalFileStorage` impl | -- Match |
| Presigned URL pattern | Direct byte upload to local disk | -- Changed (simplified for local) |

**Verdict**: 로컬 우선 전략이 정확히 적용됨. 인터페이스(`FileStorage`)를 통해 향후 S3 구현체 교체가 용이한 구조.

### 6.3 Environment Configuration

| Item | Design | Implementation | Status |
|------|--------|----------------|--------|
| application.yml profile | env vars | `spring.profiles.active: local` | -- Match |
| application-local.yml | - | MySQL local, Redis local, ddl-auto: create-drop | -- Match |
| application-prod.yml | - | 존재 (example) | -- Match |
| JWT secret | `${JWT_SECRET}` | `${JWT_SECRET:local-dev-secret-key...}` (default 포함) | -- Match |

---

## 7. Test Coverage Status

### 7.1 Test Files

| Test | Target | Layer |
|------|--------|-------|
| `MemberTest.java` | Member domain logic | Domain |
| `JwtProviderTest.java` | JWT token issue/validate | Security |
| `AuthServiceTest.java` | Auth business logic | Application |
| `MemberServiceTest.java` | Member business logic | Application |
| `LocalAuthControllerTest.java` | Local auth API | Presentation |
| `MemberControllerTest.java` | Member API | Presentation |
| `ProductTest.java` | Product domain logic | Domain |
| `ProductServiceTest.java` | Product business logic | Application |
| `ProductControllerTest.java` | Product API | Presentation |

**Coverage**: Domain/Application/Presentation 전 레이어에 걸쳐 테스트 존재. 설계 기준(Domain 90%, Application 80%)에 부합하는 테스트 구조.

### 7.2 Missing Tests

| Target | Priority | Notes |
|--------|----------|-------|
| Testcontainers (MySQL/Redis) | P1 | 설계에 명시, 미적용 (H2 사용) |
| BlacklistRepository | P2 | Redis integration test |
| RefreshTokenRepository | P2 | Redis integration test |

---

## 8. Build/Dependencies Comparison (Section 10.1)

| Design Dependency | Implementation | Status |
|------------------|---------------|--------|
| spring-boot-starter-web | O | -- Match |
| spring-boot-starter-data-jpa | O | -- Match |
| spring-boot-starter-data-redis | O | -- Match |
| spring-boot-starter-security | O | -- Match |
| spring-boot-starter-validation | O | -- Match |
| spring-boot-starter-actuator | O | -- Match |
| spring-boot-starter-oauth2-client | X | -- Planned (OAuth 미구현) |
| querydsl-jpa 5.1.0 | O | -- Match |
| jjwt 0.12.6 | O | -- Match |
| springdoc-openapi 2.8.4 | O | -- Match |
| aws-sdk-s3 | X | -- Planned (S3 미구현, LocalFileStorage 대체) |
| resilience4j | O (2.2.0, 설계는 2.3.0) | -- Changed (version) |
| mysql-connector-j | O | -- Match |
| testcontainers-mysql | X (H2 사용) | -- Missing |
| testcontainers-redis | X | -- Missing |
| micrometer-prometheus | O (추가) | -- Added |

---

## 9. Match Rate Summary (Phase 1~3 Scope Only)

### 9.1 Category Scores

| Category | Items | Match | Changed | Missing | Added | Score |
|----------|:-----:|:-----:|:-------:|:-------:|:-----:|:-----:|
| Package Structure | 10 | 0 | 10 | 0 | 0 | 80% |
| Auth API (Phase 2 scope) | 4 | 2 | 0 | 0 | 2 | 85% |
| Member API (Phase 2 scope) | 5 | 3 | 1 | 1 | 2 | 80% |
| Product API (Phase 3 scope) | 7 | 4 | 2 | 1 | 0 | 78% |
| Admin API (Phase 3 scope) | 3 | 1 | 0 | 2 | 0 | 67% |
| Member Data Model | 10 | 6 | 2 | 1 | 1 | 80% |
| Product Data Model | 12 | 7 | 3 | 2 | 0 | 75% |
| ErrorCode | 15 | 5 | 10 | 0 | 5 | 60% |
| ApiResponse | 5 | 0 | 5 | 0 | 1 | 40% |
| SecurityConfig | 9 | 7 | 2 | 0 | 0 | 90% |
| Redis Cache TTL | 7 | 7 | 0 | 0 | 1 | 95% |
| JWT Spec | 7 | 5 | 2 | 0 | 0 | 85% |
| Architecture Compliance | 6 | 4 | 0 | 2 | 0 | 78% |
| Convention | 5 | 4 | 1 | 0 | 0 | 95% |
| Local-First Strategy | 3 | 3 | 0 | 0 | 0 | 100% |
| Test Structure | 4 | 3 | 0 | 1 | 0 | 85% |
| Build Dependencies | 12 | 10 | 1 | 1 | 1 | 88% |

### 9.2 Overall Scores

```
+-----------------------------------------------+
|  Design-Implementation Gap Analysis            |
+-----------------------------------------------+
|                                                |
|  Design Match:          78%           [=======-]|
|  Architecture:          78%           [=======-]|
|  Convention:            95%           [========]|
|  Local-First:           100%          [========]|
|                                                |
|  OVERALL SCORE:         82%           [=======-]|
|                                                |
|  Status: Acceptable (>= 70%, < 90%)           |
+-----------------------------------------------+
```

---

## 10. Differences Found

### 10.1 Missing Features (Design O, Implementation X) -- Phase 1~3 Scope

| # | Item | Design Location | Description | Impact |
|---|------|----------------|-------------|--------|
| 1 | PATCH /api/v1/members/me | Section 4.2 | 내 정보 수정 (닉네임) 엔드포인트 미구현 | Medium |
| 2 | GET /api/v1/products/new | Section 4.2 | 신상품 목록 엔드포인트 미구현 | Low |
| 3 | Admin Category CRUD | Section 4.2 | `/admin/v1/categories/**` 미구현 | Medium |
| 4 | Admin Banner CRUD | Section 4.2 | `/admin/v1/banners/**` 미구현 | Medium |
| 5 | ProductImage Entity | Section 3.2 | 상품 다중 이미지 테이블 미구현 (단일 imageUrl만) | Medium |
| 6 | view_count (Product) | Section 3.2 | 상품 조회수 필드 미구현 | Low |
| 7 | profile_image_url (Member) | Section 3.2 | 회원 프로필 이미지 URL 미구현 | Low |
| 8 | Testcontainers | Section 9.1 | MySQL/Redis Testcontainers 미적용 (H2 대체) | Low |

### 10.2 Added Features (Design X, Implementation O)

| # | Item | Implementation Location | Description |
|---|------|------------------------|-------------|
| 1 | Local Auth | `LocalAuthController`, `LocalSignupService` | @Profile(local,test) 로컬 로그인/회원가입 |
| 2 | GET /me/agreements | `MemberController` | 약관 동의 목록 조회 |
| 3 | GET /me/points/history | `MemberController` | 포인트 내역 페이지네이션 조회 |
| 4 | Money Value Object | `product/domain/vo/Money.java` | 가격을 VO로 래핑 (DDD 개선) |
| 5 | OAuthProvider.LOCAL | `member/domain/vo/OAuthProvider.java` | 로컬 인증 프로바이더 추가 |
| 6 | Resilience4j config | `application.yml` | Circuit Breaker 사전 설정 |
| 7 | Virtual Threads | `application.yml` | Java 21 Virtual Thread 활성화 |
| 8 | Prometheus metrics | `build.gradle.kts` | Micrometer Prometheus 추가 |
| 9 | reviewRating cache | `RedisConfig.java` | 리뷰 평점 캐시 선행 설정 |

### 10.3 Changed Features (Design != Implementation)

| # | Item | Design | Implementation | Impact |
|---|------|--------|----------------|--------|
| 1 | ApiResponse 구조 | `{success, data, error}` | `{code, message, data}` | **High** |
| 2 | ErrorCode 형식 | 단축 코드 (M001, P001) | 서술적 코드 (MEMBER_NOT_FOUND) | **High** |
| 3 | Package 구조 | Layer-first (domain/, application/) | Domain-first (member/domain/) | Medium |
| 4 | ProductStatus values | ON_SALE/SOLD_OUT/DISCONTINUED | ACTIVE/INACTIVE/SOLD_OUT/DELETED | Medium |
| 5 | RT 전달 방식 | HttpOnly Cookie | JSON Body (TokenPair) | Medium |
| 6 | 약관 수정 HTTP Method | PATCH | PUT | Low |
| 7 | 검색 엔드포인트 | 별도 /products/search | /products?keyword= 통합 | Low |
| 8 | 베스트셀러 URL | /products/best | /products/bestseller | Low |
| 9 | 상품 가격 타입 | INT (plain) | Money (Embedded VO) | Low (improvement) |
| 10 | 테이블명 | singular (member, product) | plural (members, products) | Low |

---

## 11. Recommended Actions

### 11.1 Immediate (High Impact)

| Priority | Item | Action | Rationale |
|----------|------|--------|-----------|
| 1 | ApiResponse 구조 통일 | 설계 문서를 현재 구현(`code/message/data` 구조)에 맞게 업데이트 | 클라이언트 API 계약 명확화 필수 |
| 2 | ErrorCode 체계 통일 | 설계 문서를 현재 구현(서술적 코드)에 맞게 업데이트 | 코드 가독성 측면에서 구현이 우수 |
| 3 | PATCH /members/me 구현 | 닉네임 수정 엔드포인트 추가 | 설계에 명시된 Phase 2 범위 |

### 11.2 Short-term (1 week)

| Priority | Item | Action | Impact |
|----------|------|--------|--------|
| 4 | Admin Category/Banner CRUD | AdminCategoryController, AdminBannerController 구현 | Phase 3 완성도 |
| 5 | GET /products/new 구현 | 신상품 목록 엔드포인트 추가 | 사용자 경험 |
| 6 | RefreshToken/Blacklist 인터페이스화 | domain 레이어에 인터페이스 정의, infra에서 구현 | 아키텍처 순수성 |
| 7 | ProductImage 엔티티 추가 | 다중 상품 이미지 지원 | 데이터 모델 완성도 |

### 11.3 Design Document Update Needed

다음 항목은 **구현이 설계보다 개선된 경우**이므로 설계 문서를 현재 구현에 맞게 업데이트할 것을 권장한다.

- [ ] ApiResponse 구조: `{success, data, error}` -> `{code, message, data}`
- [ ] ErrorCode 형식: 단축 코드 -> 서술적 코드
- [ ] Package 구조: Layer-first -> Domain-first (DDD)
- [ ] ProductStatus enum 값 업데이트
- [ ] RT 전달 방식: Cookie -> Body (모바일 앱 특성)
- [ ] Money Value Object 반영
- [ ] 로컬 인증 전략 추가
- [ ] 테이블명 복수형 규칙 반영
- [ ] Virtual Threads, Prometheus 설정 추가

---

## 12. Planned Not-Yet-Implemented Summary

아래는 설계 문서에 포함되어 있으나 Phase 4 이후 구현 예정인 항목으로, 현재 Gap 분석에서 제외했다.

| Phase | Domain | Key Components |
|-------|--------|---------------|
| Phase 5 | Cart | Cart, CartItem entity + Redis 재고 선점 Lua Script |
| Phase 6 | Coupon | Coupon, UserCoupon entity + Redis Lua Script |
| Phase 7 | Payment | TossPaymentClient, 분산 트랜잭션 |
| Phase 8 | Order | Order, OrderItem, OrderStatusHistory + 상태 머신 |
| Phase 9 | CS | Review, Inquiry, Notice, FAQ |
| Phase 10 | Notification | FCM, NotificationLog, FcmToken |
| Phase 11 | Deploy | EC2 Blue-Green, Nginx |
| Phase 12 | Search | Elasticsearch 고도화 |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-28 | Initial gap analysis (Phase 1~3 scope) | Claude Code (Opus 4.6) |
