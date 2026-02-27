# project-architecture Planning Document

> **Summary**: Saemaul Chonggak 쇼핑 서버의 프로젝트 루트 구조 — DDD 우선, 그 안에 Layered Architecture 적용
>
> **Project**: saemaul_chonggak
> **Version**: 1.0.0
> **Author**: Claude Code (Sonnet 4.6)
> **Date**: 2026-02-28
> **Status**: Confirmed

---

## 1. Overview

### 1.1 Purpose

Spring Boot 기반 쇼핑 서버의 폴더 구조 규약을 명확히 정의한다.
**DDD를 먼저 적용** (도메인별 최상위 패키지), 그 **안에 Layered Architecture** 적용 (domain/application/presentation/infra).
공통 파일은 `shared/` 패키지로 관리한다.

### 1.2 핵심 원칙

- **DDD 우선**: 최상위 패키지 분리 기준은 **도메인** (member, product, order 등)
- **레이어드 내부**: 각 도메인 패키지 안에 `domain`, `application`, `presentation`, `infra` 레이어 존재
- **shared**: 전 도메인에서 공통으로 사용하는 설정/유틸 → `shared/` 패키지

### 1.3 Related Documents

- `docs/01-plan/features/shopping-server.plan.md`
- `docs/01-plan/features/response-time-sla.plan.md`

---

## 2. 프로젝트 폴더 구조

### 2.1 전체 구조 (루트)

```
saemaul_chonggak/                              ← 프로젝트 루트 폴더
│
src/main/java/com/saemaul/chonggak/
│
├── member/                                    ← [DDD] 회원 도메인
│   ├── domain/                                ← 도메인 레이어
│   ├── application/                           ← 애플리케이션 레이어
│   ├── presentation/                          ← 프레젠테이션 레이어
│   └── infra/                                 ← 인프라 레이어
│
├── product/                                   ← [DDD] 상품 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
├── order/                                     ← [DDD] 주문 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
├── payment/                                   ← [DDD] 결제 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
├── coupon/                                    ← [DDD] 쿠폰 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
├── cart/                                      ← [DDD] 장바구니 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
├── review/                                    ← [DDD] 리뷰 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
├── cs/                                        ← [DDD] 고객서비스 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
├── notification/                              ← [DDD] 알림 도메인
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── infra/
│
└── shared/                                    ← 공통 모듈 (전 도메인 참조 가능)
    ├── config/
    ├── exception/
    ├── response/
    ├── security/
    └── util/
```

### 2.2 도메인 내부 레이어 상세 (예: member)

```
member/
├── domain/                                    ← 순수 Java, Spring 어노테이션 금지
│   ├── Member.java                            (Aggregate Root)
│   ├── MemberRepository.java                  (Repository Interface)
│   ├── vo/                                    (Value Object — 불변)
│   │   ├── Email.java
│   │   └── OAuthProvider.java
│   ├── event/                                 (Domain Event)
│   │   └── MemberRegisteredEvent.java
│   └── service/                               (Domain Service — 순수 도메인 로직)
│       └── MemberDomainService.java
│
├── application/                               ← @Service, @Transactional, UseCase 조율
│   ├── MemberService.java
│   └── dto/
│       ├── MemberLoginCommand.java            (입력 Command)
│       └── MemberResult.java                  (출력 Result)
│
├── presentation/                              ← @RestController, HTTP DTO
│   ├── MemberController.java
│   └── dto/
│       ├── MemberLoginRequest.java            (HTTP Request DTO)
│       └── MemberResponse.java                (HTTP Response DTO)
│
└── infra/                                     ← JPA 구현체, Redis, 외부 API 클라이언트
    ├── MemberJpaRepository.java               (extends JpaRepository)
    ├── MemberRepositoryImpl.java              (implements domain/MemberRepository)
    └── oauth/
        ├── KakaoOAuthClient.java
        └── NaverOAuthClient.java
```

### 2.3 shared/ 상세 구조

```
shared/
├── config/                                    ← Spring 설정 클래스
│   ├── SecurityConfig.java
│   ├── RedisConfig.java
│   ├── SwaggerConfig.java
│   └── AsyncConfig.java
│
├── exception/                                 ← 예외 처리
│   ├── BusinessException.java
│   ├── ErrorCode.java
│   └── GlobalExceptionHandler.java
│
├── response/                                  ← 공통 응답 형식
│   └── ApiResponse.java
│
├── security/                                  ← JWT, 인증 필터 (Phase 2)
│   ├── JwtProvider.java
│   ├── JwtAuthenticationFilter.java
│   └── UserPrincipal.java
│
└── util/                                      ← 공통 유틸
    └── (필요 시 추가)
```

---

## 3. 레이어 의존성 방향

```
presentation → application → domain ← infra
      ↓              ↓                    ↓
    shared         shared              shared
```

**규칙**:
- 각 도메인 내 `presentation` → `application` → `domain` ← `infra`
- `domain`은 어떤 것도 의존하지 않음 (순수 Java)
- `infra`는 `domain`의 Repository Interface 구현 (DIP)
- `shared`는 모든 레이어에서 단방향 참조만 허용
- 도메인 간 참조: `application` → 타 도메인 `domain`의 Repository만 허용

---

## 4. 도메인 목록

| 도메인 | 패키지 | 주요 Aggregate |
|--------|--------|----------------|
| 회원 | `member/` | Member, MemberAgreement, PointHistory |
| 상품 | `product/` | Product, ProductCategory, Banner |
| 장바구니 | `cart/` | Cart, CartItem |
| 주문 | `order/` | Order, OrderItem |
| 결제 | `payment/` | Payment |
| 쿠폰 | `coupon/` | Coupon, UserCoupon |
| 리뷰 | `review/` | Review, ReviewImage |
| CS | `cs/` | Inquiry, FAQ, Notice |
| 알림 | `notification/` | NotificationLog, FcmToken |

---

## 5. API 경로 규약

```
일반 사용자: /api/v1/{도메인}/**
관리자:      /admin/v1/{도메인}/**
```

관리자 컨트롤러는 각 도메인의 `presentation/` 안에 `Admin{도메인}Controller.java`로 위치.

---

## 6. Success Criteria

- [x] DDD 우선 + Layered 내부 구조 Plan 문서 완성
- [ ] 기존 잘못된 폴더 구조 삭제 및 신규 구조로 재편
- [ ] `shared/` 공통 파일 마이그레이션 완료
- [ ] 레이어 의존성 방향 준수

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-28 | Initial draft — DDD 우선 구조 확정 | Claude Code (Sonnet 4.6) |
| 1.1 | 2026-02-28 | 레이어드-먼저 구조 폐기, DDD-먼저 구조로 수정 | Claude Code (Sonnet 4.6) |
