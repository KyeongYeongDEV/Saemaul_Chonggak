# [Plan] clean-code

> 모든 비즈니스 로직은 책임 분리가 잘 되어야 한다.
> 메인이 되는 메소드는 코드 형식보단 메소드명이 읽히며 가독성이 좋아야 한다.

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 피처명 | clean-code |
| 적용 범위 | 전 도메인 `application/`, `domain/` 레이어 |
| 핵심 가치 | 책임 분리(SRP) + 읽히는 코드(Readable Facade) |
| 관련 문서 | `project-architecture.plan.md`, `shopping-server.plan.md` |

---

## 2. 핵심 원칙

### 원칙 1: 책임 분리 (Separation of Concerns)

> "모든 비즈니스 로직은 책임 분리가 잘 되어야 한다."

각 클래스·메소드는 **단 하나의 이유**로만 변경된다.

| 레이어 | 책임 | 하지 않는 것 |
|--------|------|-------------|
| `presentation` | HTTP 요청/응답 변환, 입력 유효성 검사 | 비즈니스 판단 |
| `application` | UseCase 조율 (트랜잭션, 흐름 제어) | 세부 도메인 로직 |
| `domain` | 순수 비즈니스 규칙, 불변식 보장 | Spring/JPA 의존 |
| `infra` | DB/Redis/외부 API 실제 구현 | 비즈니스 판단 |

### 원칙 2: 읽히는 메소드 (Readable Facade Method)

> "메인이 되는 메소드는 코드 형식보단 메소드명이 읽히며 가독성이 좋아야 한다."

Application Service의 **퍼블릭 메소드(UseCase 진입점)** 는 비즈니스 흐름을 산문처럼 읽을 수 있어야 한다.
세부 구현은 **프라이빗 메소드로 위임**하여 메인 메소드를 의도 전달에만 집중시킨다.

---

## 3. 코드 설계 규칙

### 3.1 Application Service — Readable Facade 패턴

```java
// ✅ GOOD: 메인 메소드가 비즈니스 흐름으로 읽힌다
@Transactional
public OrderResult placeOrder(PlaceOrderCommand command) {
    validateStock(command);
    applyCouponIfPresent(command);
    deductPoints(command);
    Payment payment = processPayment(command);
    Order order = createOrder(command, payment);
    notifyOrderPlaced(order);
    return OrderResult.from(order);
}

// ❌ BAD: 메인 메소드에 세부 코드가 뒤섞여 흐름이 보이지 않는다
@Transactional
public OrderResult placeOrder(PlaceOrderCommand command) {
    Long stock = redisTemplate.opsForValue().get("stock:" + command.productId());
    if (stock == null || stock < command.quantity()) {
        throw new BusinessException(ErrorCode.OUT_OF_STOCK);
    }
    if (command.couponId() != null) {
        UserCoupon coupon = couponRepository.findById(command.couponId())
            .orElseThrow(() -> new BusinessException(ErrorCode.COUPON_NOT_FOUND));
        // ... 수십 줄 ...
    }
    // ... 계속 ...
}
```

### 3.2 책임 위임 계층

```
Application Service (퍼블릭 메소드)
  └─ 비즈니스 흐름만 기술, 각 단계를 프라이빗 메소드로 위임
       ├─ private void validateStock(command)
       ├─ private void applyCouponIfPresent(command)
       ├─ private Payment processPayment(command)
       └─ private void notifyOrderPlaced(order)
            └─ 복잡한 로직은 Domain Service 또는 전용 클래스로 추가 위임
```

### 3.3 메소드 명명 규칙

| 종류 | 패턴 | 예시 |
|------|------|------|
| 조회 | `find{대상}By{조건}()` | `findAvailableCouponsByUserId()` |
| 검증 | `validate{대상}()` | `validateStock()`, `validateCouponOwnership()` |
| 적용/처리 | `apply{행위}()` | `applyCouponIfPresent()`, `applyPointDiscount()` |
| 생성 | `create{대상}()` | `createOrder()`, `createPaymentRecord()` |
| 발행/발송 | `notify{이벤트}()` | `notifyOrderPlaced()`, `notifyPaymentFailed()` |
| 차감/증가 | `deduct{대상}()` / `credit{대상}()` | `deductPoints()`, `creditRefundAmount()` |

### 3.4 레이어별 책임 예시 (주문 생성)

```
[presentation]  OrderController.placeOrder(request)
                  → 입력 검증 + Command 생성
                  → orderService.placeOrder(command) 호출

[application]   OrderService.placeOrder(command)       ← Readable Facade
                  ① validateStock(command)              ← private
                  ② applyCouponIfPresent(command)       ← private
                  ③ deductPoints(command)               ← private
                  ④ processPayment(command)             ← private
                  ⑤ createOrder(command, payment)       ← private
                  ⑥ notifyOrderPlaced(order)            ← private

[domain]        Order.place(items, coupon, payment)
                  → 도메인 불변식 검증 (금액 검증, 상태 전이)
                  → OrderPlacedEvent 발행

[infra]         OrderRepositoryImpl, StockRedisRepository (Lua Script)
```

### 3.5 단일 책임 위반 시그널 (Code Smell)

아래 징후가 보이면 **책임 분리가 필요**하다는 신호다:

| 시그널 | 조치 |
|--------|------|
| 서비스 메소드 50줄 초과 | 프라이빗 메소드로 분리 |
| `if` 중첩 3단계 이상 | 전용 Validator 또는 도메인 메소드 추출 |
| 메소드명이 `And`로 연결 | 두 개의 책임이 섞인 것 → 분리 |
| 주석으로 구역 구분 (`// 1단계`, `// 2단계`) | 각 구역을 프라이빗 메소드로 추출 |
| Repository + 비즈니스 로직 혼재 | 도메인 서비스로 비즈니스 로직 이동 |

---

## 4. 도메인별 적용 지침

### 4.1 Application Service 퍼블릭 메소드 길이 기준

| 기준 | 목표 |
|------|------|
| 퍼블릭 메소드(UseCase 진입점) | **10줄 이내** (비즈니스 흐름만) |
| 프라이빗 메소드(세부 처리) | **20줄 이내** (단일 책임) |
| Domain Service 메소드 | **15줄 이내** (순수 비즈니스 규칙) |

> 길이는 절대 기준이 아니라 **분리 필요성을 감지하는 신호**로 사용한다.

### 4.2 이벤트 기반 후처리 분리

주문 완료 후 알림·포인트 적립 등 **핵심 흐름과 무관한 후처리**는 Domain Event로 분리한다.

```java
// application: 핵심 흐름에만 집중
@Transactional
public OrderResult placeOrder(PlaceOrderCommand command) {
    // ...
    Order order = createOrder(command, payment);
    eventPublisher.publishEvent(new OrderPlacedEvent(order.getId()));  // 후처리는 이벤트로
    return OrderResult.from(order);
}

// 이벤트 리스너: 알림, 적립금 등 후처리 책임 분리
@EventListener
@Async
public void onOrderPlaced(OrderPlacedEvent event) {
    sendOrderConfirmationNotification(event.orderId());
    creditWelcomePoints(event.orderId());
}
```

---

## 5. 성공 기준 (Success Criteria)

- [ ] 전 도메인 Application Service의 퍼블릭 UseCase 메소드가 Readable Facade 형태
- [ ] 퍼블릭 메소드에 비즈니스 구현 코드(if/for/직접 쿼리 등)가 직접 노출되지 않음
- [ ] 메소드명만 읽어도 비즈니스 흐름 파악 가능
- [ ] 단일 책임 위반 시그널(3.5) 해당 코드 부재
- [ ] Domain Layer에 Spring 어노테이션(`@Service`, `@Repository` 등) 미사용

---

## 6. 미결 사항 (Open Questions)

- [ ] 퍼블릭 메소드 길이 기준(10줄)이 프로젝트 특성상 너무 엄격할 경우 조정 가능
- [ ] 외부 API 호출(결제, 푸시)을 프라이빗 메소드로 감쌀 때 예외 처리 위치 기준 확정 필요

---

**작성일**: 2026-02-28
**작성자**: Claude Code (Sonnet 4.6)
**상태**: Draft
