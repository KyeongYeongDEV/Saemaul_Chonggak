# [Design] shopping-server

> **요약**: Layered Architecture + DDD 기반 쇼핑 앱 Spring Boot 백엔드 서버 상세 설계
>
> **Project**: Saemaul Chonggak Shopping Server
> **Author**: Claude Code (Sonnet 4.6)
> **Date**: 2026-02-28
> **Status**: Draft
> **Planning Doc**: [shopping-server.plan.md](../01-plan/features/shopping-server.plan.md)

---

## 1. 설계 개요

### 1.1 설계 목표

| 목표 | 달성 방법 |
|------|---------|
| 조회 API p99 < 300ms | Redis Cache-Aside 패턴, 인덱스 최적화 |
| 도메인 순수성 보장 | Domain Layer = 순수 Java (Spring 어노테이션 금지) |
| 무중단 배포 | Nginx Blue-Green + GitHub Actions |
| 결제/재고 원자성 100% | Redis Lua Script 분산 트랜잭션 |
| 유지보수성 | Layered + DDD, 단방향 의존성, 명확한 패키지 경계 |

### 1.2 설계 원칙

- **도메인 우선**: Aggregate Root를 통해서만 내부 Entity 접근
- **의존성 방향 엄수**: `presentation → application → domain ← infra`
- **캐시 우선 조회**: Redis HIT → DB 조회 없이 즉시 반환
- **외부 격리**: 토스페이먼츠/FCM/S3/OAuth 클라이언트는 모두 `infra` 레이어에 격리
- **일관된 에러 처리**: `ErrorCode enum + BusinessException → GlobalExceptionHandler`

---

## 2. 아키텍처

### 2.1 시스템 컴포넌트 다이어그램

```
[Mobile App]        [Admin Web (별도 프론트)]
      │                       │
      └───────────┬───────────┘
                  │ HTTPS :443 / :80
                  ▼
     ┌─────────────────────────────────┐
     │  EC2 t3.medium (Docker-compose)  │
     │                                  │
     │  ┌──────────────────────────┐    │
     │  │  Nginx :80/:443          │    │  ← Rate Limiting, SSL, Blue-Green
     │  └──────┬───────────────────┘    │
     │         │                        │
     │  ┌──────▼──────┐ ┌───────────┐   │
     │  │  app_blue   │ │ app_green │   │  ← 1개만 활성
     │  │  :8080      │ │  :8081    │   │
     │  └──────┬──────┘ └───────────┘   │
     │         │                        │
     │  ┌──────▼──────────────────┐     │
     │  │    Redis 7.x :6379      │     │  ← 캐시/토큰/재고/Rate Limit
     │  └─────────────────────────┘     │
     └─────────────────────────────────┘
               │
     ┌─────────┴─────────────────────────┐
     │  AWS 관리형 서비스                  │
     │  ├── RDS MySQL 8.0 (db.t3.medium) │
     │  └── S3 (이미지/파일)              │
     └───────────────────────────────────┘

[외부 서비스]
  ├── 토스페이먼츠 API
  ├── Kakao/Naver OAuth2
  └── Firebase FCM
```

### 2.2 패키지 구조

```
src/main/java/com/saemaul/chonggak/
│
├── domain/                              ← [Domain Layer] 순수 Java
│   ├── member/
│   │   ├── Member.java                  (Aggregate Root)
│   │   ├── MemberRepository.java        (Repository Interface)
│   │   ├── vo/                          (Email, PhoneNumber)
│   │   └── event/                       (MemberWithdrawnEvent)
│   ├── product/
│   │   ├── Product.java
│   │   ├── ProductRepository.java
│   │   ├── vo/                          (Money, ProductStatus)
│   │   └── service/                     (StockDomainService)
│   ├── order/
│   │   ├── Order.java
│   │   ├── OrderItem.java
│   │   ├── OrderRepository.java
│   │   ├── vo/                          (OrderStatus, DeliveryInfo)
│   │   └── event/                       (OrderPlacedEvent, OrderCancelledEvent)
│   ├── payment/
│   │   ├── Payment.java
│   │   ├── PaymentRepository.java
│   │   └── event/                       (PaymentCompletedEvent)
│   ├── coupon/
│   │   ├── Coupon.java
│   │   ├── UserCoupon.java
│   │   ├── CouponRepository.java
│   │   └── service/                     (CouponDomainService)
│   ├── cart/
│   │   ├── Cart.java
│   │   ├── CartItem.java
│   │   └── CartRepository.java
│   └── review/
│       ├── Review.java
│       └── ReviewRepository.java
│
├── application/                         ← [Application Layer] UseCase 조율
│   ├── auth/
│   │   ├── AuthService.java
│   │   └── dto/                         (SocialLoginCommand, TokenResult)
│   ├── member/
│   │   ├── MemberService.java
│   │   └── dto/
│   ├── product/
│   │   ├── ProductService.java
│   │   └── dto/
│   ├── cart/
│   │   ├── CartService.java
│   │   └── dto/
│   ├── order/
│   │   ├── OrderService.java
│   │   └── dto/
│   ├── payment/
│   │   ├── PaymentService.java
│   │   └── dto/
│   ├── coupon/
│   │   ├── CouponService.java
│   │   └── dto/
│   └── notification/
│       ├── NotificationService.java
│       └── dto/
│
├── infra/                               ← [Infrastructure Layer] 외부 구현체
│   ├── persistence/
│   │   ├── member/                      (MemberJpaRepository, MemberRepositoryImpl)
│   │   ├── product/
│   │   ├── order/
│   │   └── ...
│   ├── redis/
│   │   ├── TokenRedisRepository.java    (RT 저장/조회/삭제)
│   │   ├── StockRedisRepository.java    (재고 Lua Script)
│   │   └── CouponRedisRepository.java   (쿠폰 Lua Script)
│   ├── s3/
│   │   └── S3ImageUploader.java
│   ├── payment/
│   │   └── TossPaymentClient.java
│   ├── oauth/
│   │   ├── KakaoOAuthClient.java
│   │   └── NaverOAuthClient.java
│   └── fcm/
│       └── FcmPushSender.java
│
├── presentation/                        ← [Presentation Layer] Controller + DTO
│   ├── auth/
│   │   ├── AuthController.java
│   │   └── dto/
│   ├── member/
│   ├── product/
│   ├── cart/
│   ├── order/
│   ├── payment/
│   ├── coupon/
│   ├── cs/                              (문의/FAQ/공지)
│   ├── notification/
│   └── admin/
│       ├── AdminProductController.java
│       ├── AdminOrderController.java
│       ├── AdminMemberController.java
│       └── ...
│
└── global/                              ← 공통
    ├── config/
    │   ├── SecurityConfig.java
    │   ├── SwaggerConfig.java
    │   ├── RedisConfig.java
    │   ├── JpaConfig.java
    │   └── S3Config.java
    ├── exception/
    │   ├── GlobalExceptionHandler.java
    │   ├── BusinessException.java
    │   └── ErrorCode.java
    ├── response/
    │   └── ApiResponse.java
    └── security/
        ├── JwtTokenProvider.java
        ├── JwtAuthenticationFilter.java
        └── CustomUserDetails.java
```

### 2.3 레이어 의존성 규칙

```
presentation → application → domain ← infra

규칙:
- Domain은 Spring/외부 라이브러리 import 금지
- Application은 도메인 인터페이스만 의존 (infra 직접 의존 불가)
- Presentation은 Application DTO만 받아 Response DTO로 변환
- Infra는 Domain Repository 인터페이스를 구현 (의존 역전)
```

---

## 3. 데이터 모델

### 3.1 엔티티 관계 요약

```
Member ──N── MemberAgreement
Member ──N── PointHistory
Member ──1── Cart ──N── CartItem ──N─── Product
Member ──N── Order ──N── OrderItem ──N── Product
              Order ──1── Payment
              Order ──N─1── UserCoupon ──N─1── Coupon
Member ──N── UserCoupon
Product ──N─1── ProductCategory
Product ──N── ProductImage
Product ──N── Review ──N─1── Member
Member ──N── Inquiry ──N── InquiryAnswer
Member ──N── NotificationLog
Member ──N── FcmToken
```

### 3.2 핵심 테이블 DDL

#### Member 도메인

```sql
CREATE TABLE member (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(100) UNIQUE,
    nickname    VARCHAR(50)  NOT NULL,
    profile_image_url VARCHAR(500),
    social_type VARCHAR(20)  NOT NULL COMMENT 'KAKAO | NAVER',
    social_id   VARCHAR(100) NOT NULL,
    role        VARCHAR(20)  NOT NULL DEFAULT 'ROLE_USER' COMMENT 'ROLE_USER | ROLE_ADMIN',
    status      VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE | SUSPENDED | WITHDRAWN',
    created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY uq_social (social_type, social_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE member_agreement (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id      BIGINT       NOT NULL,
    agreement_type VARCHAR(50)  NOT NULL COMMENT 'TERMS_OF_SERVICE | PRIVACY | MARKETING_PUSH',
    is_agreed      TINYINT(1)   NOT NULL DEFAULT 0,
    agreed_at      DATETIME(6),
    INDEX idx_member (member_id),
    FOREIGN KEY (member_id) REFERENCES member(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE point_history (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id   BIGINT       NOT NULL,
    type        VARCHAR(20)  NOT NULL COMMENT 'EARN | USE | EXPIRE',
    amount      INT          NOT NULL,
    balance     INT          NOT NULL,
    description VARCHAR(200),
    created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_member_created (member_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Product 도메인

```sql
CREATE TABLE product_category (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    parent_id  BIGINT       COMMENT '최상위 카테고리는 NULL',
    name       VARCHAR(50)  NOT NULL,
    sort_order INT          NOT NULL DEFAULT 0,
    is_active  TINYINT(1)   NOT NULL DEFAULT 1,
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE product (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    category_id     BIGINT         NOT NULL,
    name            VARCHAR(200)   NOT NULL,
    description     TEXT,
    original_price  INT            NOT NULL,
    sale_price      INT            NOT NULL,
    stock_quantity  INT            NOT NULL DEFAULT 0,
    thumbnail_url   VARCHAR(500),
    status          VARCHAR(20)    NOT NULL DEFAULT 'ON_SALE' COMMENT 'ON_SALE | SOLD_OUT | DISCONTINUED',
    view_count      BIGINT         NOT NULL DEFAULT 0,
    sales_count     INT            NOT NULL DEFAULT 0,
    created_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      DATETIME(6)    NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FULLTEXT INDEX ft_name_desc (name, description) WITH PARSER ngram,
    INDEX idx_category_status (category_id, status),
    INDEX idx_status_sales (status, sales_count),
    INDEX idx_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE product_image (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id  BIGINT       NOT NULL,
    image_url   VARCHAR(500) NOT NULL,
    sort_order  INT          NOT NULL DEFAULT 0,
    INDEX idx_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE banner (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    image_url   VARCHAR(500) NOT NULL,
    link_url    VARCHAR(500),
    sort_order  INT          NOT NULL DEFAULT 0,
    start_at    DATETIME(6)  NOT NULL,
    end_at      DATETIME(6)  NOT NULL,
    is_active   TINYINT(1)   NOT NULL DEFAULT 1,
    INDEX idx_active_date (is_active, start_at, end_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Cart 도메인

```sql
CREATE TABLE cart (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id   BIGINT      NOT NULL UNIQUE,
    created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cart_item (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    cart_id     BIGINT      NOT NULL,
    product_id  BIGINT      NOT NULL,
    quantity    INT         NOT NULL DEFAULT 1,
    created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_cart (cart_id),
    UNIQUE KEY uq_cart_product (cart_id, product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Order 도메인

```sql
CREATE TABLE `order` (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id        BIGINT        NOT NULL,
    order_number     VARCHAR(30)   NOT NULL UNIQUE COMMENT 'ORD-YYYYMMDD-UUID6자리',
    status           VARCHAR(30)   NOT NULL DEFAULT 'PENDING_PAYMENT'
                     COMMENT 'PENDING_PAYMENT | PAYMENT_DONE | PREPARING | SHIPPING | DELIVERED | CANCELLED | EXCHANGE_REQUESTED | RETURN_REQUESTED',
    total_price      INT           NOT NULL COMMENT '정가 합계',
    discount_price   INT           NOT NULL DEFAULT 0 COMMENT '쿠폰/포인트 할인',
    final_price      INT           NOT NULL COMMENT '최종 결제 금액',
    recipient_name   VARCHAR(50)   NOT NULL,
    recipient_phone  VARCHAR(20)   NOT NULL,
    zip_code         VARCHAR(10)   NOT NULL,
    address          VARCHAR(200)  NOT NULL,
    address_detail   VARCHAR(200),
    delivery_message VARCHAR(200),
    ordered_at       DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_member_ordered (member_id, ordered_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE order_item (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id       BIGINT       NOT NULL,
    product_id     BIGINT       NOT NULL,
    product_name   VARCHAR(200) NOT NULL COMMENT '주문 시점 상품명 스냅샷',
    product_price  INT          NOT NULL COMMENT '주문 시점 가격 스냅샷',
    quantity       INT          NOT NULL,
    total_price    INT          NOT NULL,
    INDEX idx_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE order_status_history (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id    BIGINT       NOT NULL,
    status      VARCHAR(30)  NOT NULL,
    changed_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    note        VARCHAR(200),
    INDEX idx_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Payment 도메인

```sql
CREATE TABLE payment (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id     BIGINT        NOT NULL UNIQUE,
    payment_key  VARCHAR(200)  COMMENT '토스페이먼츠 paymentKey',
    method       VARCHAR(30)   COMMENT 'CARD | VIRTUAL_ACCOUNT | MOBILE_PHONE',
    amount       INT           NOT NULL,
    status       VARCHAR(30)   NOT NULL DEFAULT 'READY'
                 COMMENT 'READY | DONE | CANCELED | PARTIAL_CANCELED | ABORTED',
    paid_at      DATETIME(6),
    canceled_at  DATETIME(6),
    created_at   DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Coupon 도메인

```sql
CREATE TABLE coupon (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    code                VARCHAR(50)   NOT NULL UNIQUE,
    name                VARCHAR(100)  NOT NULL,
    type                VARCHAR(20)   NOT NULL COMMENT 'PERCENT | FIXED',
    discount_value      INT           NOT NULL COMMENT 'PERCENT: %, FIXED: 원',
    min_order_amount    INT           NOT NULL DEFAULT 0,
    max_discount_amount INT           COMMENT 'PERCENT 타입에만 적용',
    total_quantity      INT           NOT NULL COMMENT '-1이면 무제한',
    issued_quantity     INT           NOT NULL DEFAULT 0,
    start_at            DATETIME(6)   NOT NULL,
    end_at              DATETIME(6)   NOT NULL,
    is_active           TINYINT(1)    NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE user_coupon (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id   BIGINT      NOT NULL,
    coupon_id   BIGINT      NOT NULL,
    order_id    BIGINT      COMMENT '사용된 주문 ID',
    status      VARCHAR(20) NOT NULL DEFAULT 'UNUSED' COMMENT 'UNUSED | USED | EXPIRED',
    issued_at   DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    used_at     DATETIME(6),
    UNIQUE KEY uq_member_coupon (member_id, coupon_id),
    INDEX idx_member_status (member_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Review/CS 도메인

```sql
CREATE TABLE review (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id     BIGINT      NOT NULL,
    product_id    BIGINT      NOT NULL,
    order_item_id BIGINT      NOT NULL UNIQUE COMMENT '주문 항목당 1개만',
    rating        TINYINT     NOT NULL COMMENT '1~5',
    content       TEXT        NOT NULL,
    is_deleted    TINYINT(1)  NOT NULL DEFAULT 0,
    created_at    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_product_rating (product_id, is_deleted, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE inquiry (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id   BIGINT       NOT NULL,
    product_id  BIGINT       COMMENT '상품 문의면 product_id 존재',
    category    VARCHAR(50)  NOT NULL COMMENT 'ORDER | PRODUCT | DELIVERY | ETC',
    title       VARCHAR(200) NOT NULL,
    content     TEXT         NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING | ANSWERED',
    created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_member (member_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE notice (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    content     TEXT         NOT NULL,
    is_pinned   TINYINT(1)   NOT NULL DEFAULT 0,
    view_count  INT          NOT NULL DEFAULT 0,
    created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_pinned_created (is_pinned, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 4. API 명세

### 4.1 공통 응답 형식

```java
// 성공
{"success": true, "data": { ... }}

// 목록 (페이지네이션)
{
  "success": true,
  "data": {
    "content": [ ... ],
    "page": 0,
    "size": 20,
    "totalElements": 100,
    "totalPages": 5,
    "last": false
  }
}

// 실패
{"success": false, "error": {"code": "M001", "message": "존재하지 않는 회원입니다."}}
```

### 4.2 전체 엔드포인트 목록

#### 인증 (Auth)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| POST | /api/v1/auth/login/kakao | 카카오 소셜 로그인 | 불필요 |
| POST | /api/v1/auth/login/naver | 네이버 소셜 로그인 | 불필요 |
| POST | /api/v1/auth/reissue | Access Token 재발급 | RT 쿠키 |
| POST | /api/v1/auth/logout | 로그아웃 | AT 필수 |
| POST | /admin/v1/auth/login | 관리자 로그인 | 불필요 |

#### 회원 (Member)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | /api/v1/members/me | 내 정보 조회 | AT 필수 |
| PATCH | /api/v1/members/me | 내 정보 수정 | AT 필수 |
| DELETE | /api/v1/members/me | 회원 탈퇴 | AT 필수 |
| GET | /api/v1/members/me/points | 포인트 내역 | AT 필수 |
| PATCH | /api/v1/members/me/agreements | 동의 항목 수정 | AT 필수 |
| POST | /api/v1/members/fcm-tokens | FCM 토큰 등록 | AT 필수 |

#### 상품 (Product)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | /api/v1/categories | 전체 카테고리 트리 | 불필요 |
| GET | /api/v1/banners | 홈 배너 목록 | 불필요 |
| GET | /api/v1/products | 상품 목록 (카테고리/정렬/페이지) | 불필요 |
| GET | /api/v1/products/{id} | 상품 상세 | 불필요 |
| GET | /api/v1/products/search | 상품 검색 (키워드/필터) | 불필요 |
| GET | /api/v1/products/best | 베스트셀러 목록 | 불필요 |
| GET | /api/v1/products/new | 신상품 목록 | 불필요 |

#### 장바구니 (Cart)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | /api/v1/cart | 장바구니 조회 | AT 필수 |
| POST | /api/v1/cart/items | 상품 추가 | AT 필수 |
| PATCH | /api/v1/cart/items/{itemId} | 수량 변경 | AT 필수 |
| DELETE | /api/v1/cart/items/{itemId} | 상품 제거 | AT 필수 |
| DELETE | /api/v1/cart | 장바구니 전체 비우기 | AT 필수 |

#### 쿠폰 (Coupon)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | /api/v1/coupons | 내 쿠폰 목록 | AT 필수 |
| POST | /api/v1/coupons/issue | 쿠폰 코드로 발급 | AT 필수 |

#### 주문 (Order)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| POST | /api/v1/orders | 주문 생성 | AT 필수 |
| GET | /api/v1/orders | 주문 목록 | AT 필수 |
| GET | /api/v1/orders/{orderId} | 주문 상세 | AT 필수 |
| POST | /api/v1/orders/{orderId}/cancel | 주문 취소 | AT 필수 |
| POST | /api/v1/orders/{orderId}/exchange | 교환 신청 | AT 필수 |
| POST | /api/v1/orders/{orderId}/return | 반품 신청 | AT 필수 |

#### 결제 (Payment)

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| POST | /api/v1/payments/prepare | 결제 준비 (orderId 검증) | AT 필수 |
| POST | /api/v1/payments/confirm | 결제 승인 (토스 callback) | AT 필수 |
| POST | /api/v1/payments/{paymentId}/cancel | 결제 취소/환불 | AT 필수 |
| POST | /api/v1/payments/webhook | 토스 웹훅 수신 | 토스 서명 검증 |

#### 리뷰/CS

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | /api/v1/products/{productId}/reviews | 상품 리뷰 목록 | 불필요 |
| POST | /api/v1/reviews | 리뷰 작성 | AT 필수 |
| PATCH | /api/v1/reviews/{reviewId} | 리뷰 수정 | AT 필수 |
| DELETE | /api/v1/reviews/{reviewId} | 리뷰 삭제 | AT 필수 |
| GET | /api/v1/inquiries | 내 문의 목록 | AT 필수 |
| POST | /api/v1/inquiries | 문의 등록 | AT 필수 |
| GET | /api/v1/inquiries/{id} | 문의 상세 | AT 필수 |
| GET | /api/v1/faqs | FAQ 목록 | 불필요 |
| GET | /api/v1/notices | 공지사항 목록 | 불필요 |
| GET | /api/v1/notices/{id} | 공지사항 상세 | 불필요 |

#### 알림

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | /api/v1/notifications | 알림 목록 | AT 필수 |
| PATCH | /api/v1/notifications/{id}/read | 읽음 처리 | AT 필수 |
| PATCH | /api/v1/notifications/read-all | 전체 읽음 | AT 필수 |

#### 관리자 API (/admin/v1/**)

| Method | Path | 설명 |
|--------|------|------|
| GET/POST/PATCH/DELETE | /admin/v1/products/** | 상품 관리 |
| GET/POST/PATCH/DELETE | /admin/v1/categories/** | 카테고리 관리 |
| GET/POST/PATCH/DELETE | /admin/v1/banners/** | 배너 관리 |
| GET/PATCH | /admin/v1/orders/** | 주문/배송 상태 관리 |
| GET/POST/DELETE | /admin/v1/coupons/** | 쿠폰 발행/관리 |
| GET/PATCH | /admin/v1/members/** | 회원 조회/정지/탈퇴 처리 |
| GET/POST | /admin/v1/inquiries/** | 문의 조회/답변 |
| GET/POST/PATCH/DELETE | /admin/v1/notices/** | 공지사항 관리 |
| GET/POST/PATCH/DELETE | /admin/v1/faqs/** | FAQ 관리 |

### 4.3 주요 API 상세

#### POST /api/v1/auth/login/kakao

**Request:**
```json
{
  "authorizationCode": "카카오에서 받은 인가 코드"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "tokenType": "Bearer",
    "expiresIn": 3600,
    "memberId": 1,
    "nickname": "홍길동",
    "isNewMember": true
  }
}
```
> Refresh Token은 `Set-Cookie: refreshToken=...; HttpOnly; Secure; Path=/api/v1/auth/reissue` 로 반환

---

#### GET /api/v1/products?category=1&sort=LATEST&page=0&size=20

**Query Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| category | Long | - | 카테고리 ID (없으면 전체) |
| sort | String | LATEST | LATEST \| BEST \| PRICE_ASC \| PRICE_DESC |
| page | int | 0 | 페이지 번호 |
| size | int | 20 | 페이지 크기 (max 100) |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 1,
        "name": "프리미엄 티셔츠",
        "originalPrice": 39000,
        "salePrice": 29000,
        "discountRate": 26,
        "thumbnailUrl": "https://cdn.example.com/products/1/thumb.webp",
        "status": "ON_SALE",
        "salesCount": 152
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 150,
    "totalPages": 8,
    "last": false
  }
}
```

---

#### POST /api/v1/payments/prepare

**Request:**
```json
{
  "orderId": 42,
  "amount": 58000
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "orderId": 42,
    "orderNumber": "ORD-20260228-A3F9B2",
    "amount": 58000,
    "orderName": "프리미엄 티셔츠 외 1건",
    "customerName": "홍길동",
    "successUrl": "https://app.example.com/payment/success",
    "failUrl": "https://app.example.com/payment/fail"
  }
}
```
> 클라이언트는 이 정보로 토스페이먼츠 SDK를 호출. 결제 완료 후 `/api/v1/payments/confirm` 호출.

---

#### POST /api/v1/payments/confirm

**Request:**
```json
{
  "paymentKey": "5zJ4xY7m0kODnyRpQWGrN2eqXgQVLKad60GnT1SNwvO",
  "orderId": "ORD-20260228-A3F9B2",
  "amount": 58000
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "paymentId": 7,
    "status": "DONE",
    "method": "CARD",
    "amount": 58000,
    "paidAt": "2026-02-28T14:30:00+09:00"
  }
}
```

---

## 5. 공통 설계

### 5.1 에러 코드 정의 (ErrorCode)

```java
@Getter
@RequiredArgsConstructor
public enum ErrorCode {

    // ─── 공통 ───────────────────────────────────────────────
    INVALID_INPUT("C001", "입력값이 올바르지 않습니다.", HttpStatus.BAD_REQUEST),
    INTERNAL_SERVER_ERROR("C002", "서버 오류가 발생했습니다.", HttpStatus.INTERNAL_SERVER_ERROR),

    // ─── 인증/인가 ──────────────────────────────────────────
    INVALID_TOKEN("A001", "유효하지 않은 토큰입니다.", HttpStatus.UNAUTHORIZED),
    EXPIRED_TOKEN("A002", "만료된 토큰입니다.", HttpStatus.UNAUTHORIZED),
    ACCESS_DENIED("A003", "접근 권한이 없습니다.", HttpStatus.FORBIDDEN),
    OAUTH_LOGIN_FAILED("A004", "소셜 로그인에 실패했습니다.", HttpStatus.BAD_GATEWAY),

    // ─── 회원 ───────────────────────────────────────────────
    MEMBER_NOT_FOUND("M001", "존재하지 않는 회원입니다.", HttpStatus.NOT_FOUND),
    MEMBER_SUSPENDED("M002", "정지된 계정입니다.", HttpStatus.FORBIDDEN),
    MEMBER_WITHDRAWN("M003", "탈퇴한 회원입니다.", HttpStatus.FORBIDDEN),

    // ─── 상품 ───────────────────────────────────────────────
    PRODUCT_NOT_FOUND("P001", "존재하지 않는 상품입니다.", HttpStatus.NOT_FOUND),
    OUT_OF_STOCK("P002", "재고가 부족합니다.", HttpStatus.CONFLICT),
    PRODUCT_DISCONTINUED("P003", "판매 종료된 상품입니다.", HttpStatus.CONFLICT),

    // ─── 주문 ───────────────────────────────────────────────
    ORDER_NOT_FOUND("O001", "존재하지 않는 주문입니다.", HttpStatus.NOT_FOUND),
    ORDER_CANCEL_NOT_ALLOWED("O002", "취소할 수 없는 주문입니다.", HttpStatus.CONFLICT),
    ORDER_ACCESS_DENIED("O003", "본인 주문만 조회할 수 있습니다.", HttpStatus.FORBIDDEN),

    // ─── 결제 ───────────────────────────────────────────────
    PAYMENT_FAILED("PA001", "결제에 실패했습니다.", HttpStatus.BAD_GATEWAY),
    PAYMENT_AMOUNT_MISMATCH("PA002", "결제 금액이 일치하지 않습니다.", HttpStatus.CONFLICT),
    PAYMENT_NOT_FOUND("PA003", "결제 정보를 찾을 수 없습니다.", HttpStatus.NOT_FOUND),

    // ─── 쿠폰 ───────────────────────────────────────────────
    COUPON_NOT_FOUND("CP001", "존재하지 않는 쿠폰입니다.", HttpStatus.NOT_FOUND),
    COUPON_ALREADY_USED("CP002", "이미 사용된 쿠폰입니다.", HttpStatus.CONFLICT),
    COUPON_EXPIRED("CP003", "만료된 쿠폰입니다.", HttpStatus.CONFLICT),
    COUPON_OUT_OF_STOCK("CP004", "쿠폰 수량이 소진되었습니다.", HttpStatus.CONFLICT),
    COUPON_ALREADY_ISSUED("CP005", "이미 발급된 쿠폰입니다.", HttpStatus.CONFLICT),

    // ─── 장바구니 ────────────────────────────────────────────
    CART_ITEM_NOT_FOUND("CA001", "장바구니에 없는 상품입니다.", HttpStatus.NOT_FOUND);

    private final String code;
    private final String message;
    private final HttpStatus status;
}
```

### 5.2 BusinessException

```java
@Getter
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }
}
```

### 5.3 GlobalExceptionHandler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 비즈니스 예외 처리
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
        ErrorCode code = e.getErrorCode();
        return ResponseEntity.status(code.getStatus())
            .body(ApiResponse.error(code));
    }

    // 입력값 검증 실패 (@Valid)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
            .map(FieldError::getDefaultMessage)
            .findFirst()
            .orElse(ErrorCode.INVALID_INPUT.getMessage());
        return ResponseEntity.badRequest()
            .body(ApiResponse.error(ErrorCode.INVALID_INPUT, message));
    }

    // 미처리 예외
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        log.error("Unhandled exception", e);
        return ResponseEntity.internalServerError()
            .body(ApiResponse.error(ErrorCode.INTERNAL_SERVER_ERROR));
    }
}
```

### 5.4 ApiResponse

```java
@Getter
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
public class ApiResponse<T> {
    private final boolean success;
    private final T data;
    private final ErrorInfo error;

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(true, data, null);
    }

    public static ApiResponse<Void> ok() {
        return new ApiResponse<>(true, null, null);
    }

    public static ApiResponse<Void> error(ErrorCode errorCode) {
        return new ApiResponse<>(false, null,
            new ErrorInfo(errorCode.getCode(), errorCode.getMessage()));
    }

    public static ApiResponse<Void> error(ErrorCode errorCode, String message) {
        return new ApiResponse<>(false, null,
            new ErrorInfo(errorCode.getCode(), message));
    }

    public record ErrorInfo(String code, String message) {}
}
```

---

## 6. 보안 설계

### 6.1 Spring Security 설정

```
인증 흐름:
  1. JwtAuthenticationFilter: 모든 요청에서 AT 추출 및 검증
  2. AT 유효 → SecurityContext에 CustomUserDetails 설정
  3. 컨트롤러 접근 전 @PreAuthorize 체크

URL 접근 규칙:
  permitAll()  → /api/v1/auth/**, /api/v1/products/**, /api/v1/categories,
                 /api/v1/banners, /api/v1/faqs, /api/v1/notices/**,
                 /actuator/health, /swagger-ui/**, /v3/api-docs/**
  ROLE_ADMIN   → /admin/**
  authenticated → 나머지 /api/v1/**
```

### 6.2 JWT 토큰 스펙

| 항목 | Access Token | Refresh Token |
|------|-------------|---------------|
| 알고리즘 | HS256 | UUID (랜덤) |
| 만료 | 1시간 | 7일 |
| 저장 위치 | 응답 Body | HttpOnly Cookie |
| Redis 저장 | 블랙리스트만 (로그아웃 시) | 항상 저장 |
| Payload | memberId, role, jti | 없음 (Redis value로 사용) |

### 6.3 Redis 토큰 키 구조

```
refresh:{memberId}:{deviceId}  → RT 값       (EX 604800 = 7일)
blacklist:{jti}                → "logout"   (EX AT 잔여 만료 시간)
```

---

## 7. Redis 상세 설계

### 7.1 전체 키 구조

```
# 캐싱
product:{id}                   → ProductDetailDto (JSON)     TTL: 10분
product:list:{category}:{page}:{sort}
                               → PageDto<ProductSummaryDto>  TTL: 5분
product:bestseller             → List<ProductSummaryDto>     TTL: 1시간
product:new                    → List<ProductSummaryDto>     TTL: 10분
category:all                   → List<CategoryDto>           TTL: 1시간
banner:home                    → List<BannerDto>             TTL: 30분
notice:list:{page}             → PageDto<NoticeDto>          TTL: 1시간
faq:list:{category}            → List<FaqDto>                TTL: 2시간
search:popular                 → List<String>                TTL: 1시간
point:{memberId}               → Long (잔액)                 TTL: 5분

# 인증
refresh:{memberId}:{deviceId}  → RT 문자열                  TTL: 7일
blacklist:{jti}                → "logout"                   TTL: AT 잔여

# 재고/쿠폰 (Write-Through, 영구)
stock:{productId}              → Integer (재고 수량)         영구
coupon:{couponId}:{memberId}   → "USED" / 없으면 미사용      TTL: 쿠폰 만료일

# Rate Limiting
ratelimit:{ip}:{apiZone}       → 요청 횟수 (INCR)           TTL: 1분
```

### 7.2 Redis 직렬화 설정

```java
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);

        // Key: StringSerializer
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());

        // Value: Jackson2JsonRedisSerializer
        Jackson2JsonRedisSerializer<Object> jsonSerializer =
            new Jackson2JsonRedisSerializer<>(Object.class);
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);

        return template;
    }

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));

        return RedisCacheManager.builder(factory)
            .withCacheConfiguration("product",
                config.entryTtl(Duration.ofMinutes(10)))
            .withCacheConfiguration("category",
                config.entryTtl(Duration.ofHours(1)))
            .withCacheConfiguration("banner",
                config.entryTtl(Duration.ofMinutes(30)))
            .build();
    }
}
```

### 7.3 재고 차감 Lua Script

```lua
-- stock_deduct.lua
-- KEYS[1]: stock:{productId}
-- ARGV[1]: 차감 수량
local stock = redis.call('GET', KEYS[1])
if stock == false then
    return -2  -- 키 없음 (Redis 초기화 필요)
end
if tonumber(stock) < tonumber(ARGV[1]) then
    return -1  -- 재고 부족
end
return redis.call('DECRBY', KEYS[1], ARGV[1])
```

```lua
-- coupon_issue.lua (중복 발급 방지 + 수량 차감 원자적 처리)
-- KEYS[1]: coupon:issued:{couponId}:{memberId}
-- KEYS[2]: coupon:quantity:{couponId}
-- ARGV[1]: memberId
local alreadyIssued = redis.call('EXISTS', KEYS[1])
if alreadyIssued == 1 then
    return -2  -- 이미 발급됨
end
local remaining = redis.call('GET', KEYS[2])
if remaining == false or tonumber(remaining) <= 0 then
    return -1  -- 수량 소진
end
redis.call('DECR', KEYS[2])
redis.call('SET', KEYS[1], '1', 'EX', 2592000)  -- 30일 TTL
return 1  -- 성공
```

---

## 8. 외부 연동 설계

### 8.1 토스페이먼츠

```
흐름:
  1. [클라이언트] 결제 버튼 클릭
  2. [서버] POST /api/v1/payments/prepare → orderId, amount 검증 후 응답
  3. [클라이언트] 토스페이먼츠 SDK 호출 (카드 선택 등)
  4. [토스] 결제 완료 후 successUrl redirect (paymentKey, orderId, amount 포함)
  5. [클라이언트] POST /api/v1/payments/confirm 호출
  6. [서버] 금액 검증 → 토스 승인 API 호출 → Redis 재고/쿠폰 확정 → DB 저장

타임아웃: connectTimeout=1000ms, readTimeout=1500ms
```

### 8.2 Kakao/Naver OAuth2

```
흐름:
  1. [앱] 소셜 SDK로 authorizationCode 발급
  2. [서버] authorizationCode → 액세스 토큰 교환 (Kakao/Naver API)
  3. [서버] 액세스 토큰으로 사용자 정보 조회 (이메일, nickname, profileImage)
  4. [서버] social_type + social_id 기준 member 조회 → 신규면 자동 가입
  5. [서버] AT + RT 발급 후 응답

타임아웃: connectTimeout=1000ms, readTimeout=1000ms
```

### 8.3 AWS S3 이미지 업로드

```
흐름 (Presigned URL 방식):
  1. [앱] POST /api/v1/files/presigned-url?type=PRODUCT (파일명, 확장자 전달)
  2. [서버] S3 Presigned URL 생성 (유효시간 5분) + S3 키 반환
  3. [앱] Presigned URL로 S3에 직접 PUT (서버 경유 없음)
  4. [앱] 업로드 완료 후 S3 키를 상품 등록 API에 포함

버킷 구조: saemaul-chonggak/{env}/products/ | users/ | banners/ | reviews/
CDN: CloudFront 배포 (이미지 서빙 URL: https://cdn.saemaul.com/{key})
허용 타입: jpg, jpeg, png, webp (최대 10MB)
```

### 8.4 Firebase FCM

```
비동기 전용 (절대 동기 호출 금지):
  - 주문 상태 변경 → ApplicationEventPublisher.publishEvent(OrderStatusChangedEvent)
  - 이벤트 리스너 @Async → FCM API 호출
  - 실패 시 재시도 3회 (지수 백오프), 최종 실패는 로그만

타임아웃: connectTimeout=500ms, readTimeout=1000ms
```

---

## 9. 테스트 전략

### 9.1 테스트 도구

| 구분 | 도구 | 목적 |
|------|------|------|
| Unit Test | JUnit 5 + Mockito | 도메인/서비스 비즈니스 로직 |
| Integration Test | @SpringBootTest + Testcontainers | API E2E, DB/Redis 연동 |
| DB 테스트 | Testcontainers (MySQL 8.0) | 실제 MySQL 환경 재현 |
| Redis 테스트 | Testcontainers (Redis) | Lua Script 등 Redis 연동 |
| API 문서 | SpringDoc OpenAPI | Swagger UI 자동 생성 |

### 9.2 TDD 적용 원칙

```
Red → Green → Refactor

우선 대상:
  1. Domain 로직 (StockDomainService, CouponDomainService)
  2. Application Service (OrderService, PaymentService)
  3. Lua Script 실행 결과 (재고 차감, 쿠폰 중복 방지)
  4. JWT 토큰 발급/검증 로직
```

### 9.3 주요 테스트 케이스

```java
// 도메인 Unit Test 예시
@Test
void 재고가_부족하면_OutOfStockException_발생() {
    Product product = createProductWithStock(5);
    assertThatThrownBy(() -> product.decreaseStock(6))
        .isInstanceOf(BusinessException.class)
        .extracting("errorCode").isEqualTo(ErrorCode.OUT_OF_STOCK);
}

// Integration Test 예시 (Testcontainers)
@Test
void 주문_생성_시_Redis_재고가_차감된다() {
    // given: Redis에 재고 10 세팅
    stockRedisRepository.init(productId, 10);
    // when: 주문 생성 (수량 3)
    orderService.createOrder(createOrderCommand(productId, 3));
    // then: Redis 재고 7 확인
    assertThat(stockRedisRepository.getStock(productId)).isEqualTo(7);
}
```

### 9.4 커버리지 목표

| 레이어 | 목표 | 우선순위 |
|--------|------|---------|
| Domain | 90% 이상 | P0 |
| Application (Service) | 80% 이상 | P0 |
| Infrastructure | 통합 테스트로 커버 | P1 |
| Presentation | API 통합 테스트로 커버 | P1 |

---

## 10. 구현 가이드

### 10.1 Gradle 의존성 (`build.gradle.kts`)

```kotlin
dependencies {
    // Spring Boot
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-data-redis")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-oauth2-client")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-actuator")

    // QueryDSL
    implementation("com.querydsl:querydsl-jpa:5.1.0:jakarta")
    annotationProcessor("com.querydsl:querydsl-apt:5.1.0:jakarta")
    annotationProcessor("jakarta.annotation:jakarta.annotation-api")
    annotationProcessor("jakarta.persistence:jakarta.persistence-api")

    // JWT
    implementation("io.jsonwebtoken:jjwt-api:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.6")

    // API Docs
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.4")

    // AWS S3
    implementation("software.amazon.awssdk:s3:2.29.0")

    // Resilience4j (Circuit Breaker)
    implementation("io.github.resilience4j:resilience4j-spring-boot3:2.3.0")

    // DB
    runtimeOnly("com.mysql:mysql-connector-j")

    // Test
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.security:spring-security-test")
    testImplementation("org.testcontainers:mysql:1.20.4")
    testImplementation("org.testcontainers:junit-jupiter:1.20.4")
    testImplementation("com.redis:testcontainers-redis:2.2.2")
}
```

### 10.2 핵심 설정 파일 (`application.yml`)

```yaml
spring:
  datasource:
    url: jdbc:mysql://${DB_HOST}:3306/${DB_NAME}?useSSL=true&serverTimezone=Asia/Seoul
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 50
      minimum-idle: 10
      connection-timeout: 3000
  jpa:
    hibernate:
      ddl-auto: validate  # 운영: validate, 개발: update
    properties:
      hibernate:
        format_sql: false
        default_batch_fetch_size: 100  # N+1 방지
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: 6379
      lettuce:
        pool:
          max-active: 20
          min-idle: 5

jwt:
  secret: ${JWT_SECRET}
  access-expiry: 3600     # 1시간 (초)
  refresh-expiry: 604800  # 7일 (초)

toss:
  secret-key: ${TOSS_SECRET_KEY}
  base-url: https://api.tosspayments.com/v1

cloud:
  aws:
    s3:
      bucket: saemaul-chonggak
    region:
      static: ap-northeast-2

management:
  endpoints:
    web:
      exposure:
        include: health, metrics, prometheus
  endpoint:
    health:
      show-details: when-authorized
```

### 10.3 구현 순서

| 단계 | 작업 | 비고 |
|------|------|------|
| Phase 1 | 프로젝트 기반 설정 | 패키지 구조, Docker-compose, CI/CD |
| Phase 2 | Global 공통 설정 | SecurityConfig, GlobalExceptionHandler, ApiResponse |
| Phase 3 | 인증/회원 | OAuth2 로그인, JWT, Redis 토큰 관리 |
| Phase 4 | 상품/카테고리/배너 | Redis 캐싱, S3 연동, FULLTEXT 검색 |
| Phase 5 | 장바구니 | Redis 재고 선점 (Lua Script) |
| Phase 6 | 쿠폰 | Redis Lua Script 원자성 보장 |
| Phase 7 | 결제 | 토스페이먼츠 연동, 분산 트랜잭션 |
| Phase 8 | 주문 | 주문 생성/상태 변경/취소/교환/반품 |
| Phase 9 | CS | 리뷰, 1:1 문의, FAQ, 공지사항 |
| Phase 10 | 알림 | Firebase FCM 비동기 처리 |
| Phase 11 | 운영 배포 | EC2 Blue-Green, 성능 모니터링 |
| Phase 12 (추후) | Elasticsearch | 검색 고도화 |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-02-28 | Initial draft | Claude Code (Sonnet 4.6) |
