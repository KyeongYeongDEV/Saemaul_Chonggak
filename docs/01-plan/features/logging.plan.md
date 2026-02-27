# [Plan] logging

> 개발자를 위한 로그 전략 — `log.info` / `log.debug` / `log.warn` / `log.error` 사용 규약

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 피처명 | logging |
| 라이브러리 | SLF4J + Logback (Spring Boot 기본 내장) |
| 어노테이션 | Lombok `@Slf4j` (전 클래스 통일) |
| 적용 범위 | presentation / application / infra 레이어 (domain 레이어 제외) |
| 관련 문서 | `shopping-server.plan.md`, `clean-code.plan.md` |

> **Domain 레이어는 로그 미적용**: 순수 Java 규칙 유지 (Spring/Lombok 의존 금지)

---

## 2. 현황 분석

| 파일 | 현재 상태 |
|------|-----------|
| `GlobalExceptionHandler` | `@Slf4j` + `log.warn/error` 사용 ✅ |
| `JwtAuthenticationFilter` | `@Slf4j` 있지만 로그 미사용 ⚠️ |
| `AuthService` | 로그 전혀 없음 ❌ |
| `LocalSignupService` | 로그 전혀 없음 ❌ |
| `MemberService` | 로그 전혀 없음 ❌ |

---

## 3. 로그 레벨 전략

### 3.1 레벨별 사용 기준

| 레벨 | 사용 기준 | 예시 |
|------|----------|------|
| `log.debug(...)` | 개발 중 상세 흐름 추적. **로컬에서만 출력** | 파라미터 값, SQL 파라미터, 캐시 key |
| `log.info(...)` | 비즈니스 이벤트 완료. **로컬+운영 모두 출력** | 회원 가입 완료, 주문 생성, 결제 승인 |
| `log.warn(...)` | 예상 가능한 비정상 상황. 즉시 장애는 아님 | 쿠폰 이미 사용, 재고 부족, 유효하지 않은 토큰 |
| `log.error(...)` | 처리 불가 오류. 즉각 확인 필요 | 외부 API 실패, DB 연결 오류, 예상치 못한 예외 |

### 3.2 환경별 로그 레벨 설정

```yaml
# application-local.yml
logging:
  level:
    com.saemaul.chonggak: DEBUG   # 로컬: 전 레벨 출력
    org.hibernate.SQL: DEBUG       # SQL 쿼리 출력
    org.hibernate.orm.jdbc.bind: TRACE  # SQL 파라미터 출력

# application-prod.yml
logging:
  level:
    com.saemaul.chonggak: INFO    # 운영: INFO 이상만 출력
    org.hibernate.SQL: WARN       # SQL 로그 최소화
```

---

## 4. 레이어별 로그 포인트

### 4.1 Application Service — 비즈니스 이벤트 중심

**언제**: UseCase 완료 시점, 중요 분기 발생 시

```java
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    public TokenPair localLogin(LocalLoginCommand command) {
        // ... 비즈니스 로직 ...
        log.info("[AUTH] 로컬 로그인 성공: userId={}, deviceId={}", member.getId(), command.deviceId());
        return issueTokenPair(member, command.deviceId());
    }

    public TokenPair reissue(String refreshToken, Long userId, String deviceId) {
        if (!stored.equals(refreshToken)) {
            log.warn("[AUTH] RT 불일치 감지, 전체 토큰 삭제 (탈취 의심): userId={}", userId);
            refreshTokenRepository.deleteAll(userId);
            throw new BusinessException(ErrorCode.INVALID_REFRESH_TOKEN);
        }
        log.info("[AUTH] 토큰 재발급 완료 (RT Rotation): userId={}, deviceId={}", userId, deviceId);
        return issueTokenPair(member, deviceId);
    }

    public void logout(String accessToken, Long userId, String deviceId) {
        // ...
        log.info("[AUTH] 로그아웃: userId={}, deviceId={}", userId, deviceId);
    }
}
```

**로그 패턴**: `[{도메인}] {이벤트명}: {핵심 식별자}={값}`

### 4.2 Infrastructure Layer — 외부 연동 및 Mock

**언제**: 외부 API 호출 전후, Mock 동작 시

```java
@Slf4j
@Component
@Profile({"local", "test"})
public class MockPaymentGateway implements PaymentGateway {

    public PaymentResult approve(PaymentRequest request) {
        log.info("[MOCK][PAYMENT] 결제 승인 시뮬레이션: orderId={}, amount={}",
                 request.orderId(), request.amount());
        return PaymentResult.success("mock-key-" + UUID.randomUUID());
    }
}

@Slf4j
@Component
@Profile("prod")
public class TossPaymentGateway implements PaymentGateway {

    public PaymentResult approve(PaymentRequest request) {
        log.debug("[PAYMENT] 토스페이먼츠 요청: orderId={}", request.orderId());
        try {
            PaymentResult result = tossClient.approve(request);
            log.info("[PAYMENT] 결제 승인 완료: orderId={}, paymentKey={}", request.orderId(), result.paymentKey());
            return result;
        } catch (Exception e) {
            log.error("[PAYMENT] 결제 승인 실패: orderId={}, error={}", request.orderId(), e.getMessage(), e);
            throw new BusinessException(ErrorCode.PAYMENT_FAILED);
        }
    }
}
```

### 4.3 Security / Filter — 보안 이벤트

**언제**: 인증 실패, 블랙리스트 감지

```java
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    protected void doFilterInternal(...) {
        if (blacklistRepository.isBlacklisted(jti)) {
            log.warn("[SECURITY] 블랙리스트 토큰 접근 차단: jti={}, uri={}", jti, request.getRequestURI());
            writeErrorResponse(response, ErrorCode.BLACKLISTED_TOKEN);
            return;
        }
        log.debug("[SECURITY] 토큰 인증 완료: userId={}", userId);
    }
}
```

### 4.4 Redis 캐시 — 캐시 hit/miss 추적 (Debug)

```java
@Slf4j
@Service
public class ProductService {

    public ProductDto getProduct(Long productId) {
        String cacheKey = "product:" + productId;
        ProductDto cached = redisCache.get(cacheKey, ProductDto.class);
        if (cached != null) {
            log.debug("[CACHE] HIT: key={}", cacheKey);
            return cached;
        }
        log.debug("[CACHE] MISS: key={}, DB 조회 시작", cacheKey);
        ProductDto result = fetchFromDb(productId);
        redisCache.set(cacheKey, result, Duration.ofMinutes(10));
        return result;
    }
}
```

---

## 5. 로그 포맷 규약

### 5.1 메시지 형식

```
[{PREFIX}] {이벤트}: {key1}={value1}, {key2}={value2}
```

| PREFIX 예시 | 의미 |
|------------|------|
| `[AUTH]` | 인증/인가 관련 |
| `[PAYMENT]` | 결제 관련 |
| `[ORDER]` | 주문 관련 |
| `[STOCK]` | 재고 관련 |
| `[COUPON]` | 쿠폰 관련 |
| `[CACHE]` | Redis 캐시 |
| `[SECURITY]` | 보안 이벤트 |
| `[MOCK]` | Mock 구현체 동작 |
| `[ASYNC]` | 비동기 이벤트 처리 |

### 5.2 금지 사항

```java
// ❌ 문자열 연결 (성능 손해: 로그 비활성화돼도 연산 발생)
log.debug("회원 로그인 시도: " + email);

// ✅ 파라미터 바인딩 (로그 레벨 비활성화 시 연산 스킵)
log.debug("[AUTH] 로그인 시도: email={}", email);

// ❌ 개인정보 직접 노출
log.info("로그인: email={}, password={}", email, password);

// ✅ 개인정보 마스킹 또는 ID만 노출
log.info("[AUTH] 로그인 성공: userId={}", member.getId());
```

### 5.3 개인정보 로그 금지 목록

아래 항목은 절대 로그에 출력하지 않는다:
- 비밀번호 (평문 / 해시 모두)
- 이메일 주소 (식별자로 userId 사용)
- 전화번호
- 주소
- 카드 번호 / 결제 정보 전체
- Access Token / Refresh Token 전체 값

---

## 6. 주요 로그 포인트 목록

### 6.1 인증/회원 도메인

| 이벤트 | 레벨 | 로그 내용 |
|--------|------|----------|
| 회원 가입 완료 | INFO | `[AUTH] 회원 가입: userId={}, provider=LOCAL` |
| 로컬 로그인 성공 | INFO | `[AUTH] 로컬 로그인 성공: userId={}, deviceId={}` |
| 로그인 실패 (비밀번호 불일치) | WARN | `[AUTH] 로그인 실패 (비밀번호 불일치): 입력 email 마스킹` |
| RT 재발급 완료 | INFO | `[AUTH] 토큰 재발급: userId={}, deviceId={}` |
| RT 불일치 (탈취 의심) | WARN | `[AUTH] RT 불일치 감지: userId={}` |
| 로그아웃 | INFO | `[AUTH] 로그아웃: userId={}, deviceId={}` |
| 블랙리스트 차단 | WARN | `[SECURITY] 블랙리스트 토큰 차단: jti={}` |

### 6.2 결제/주문 도메인 (추후 구현)

| 이벤트 | 레벨 | 로그 내용 |
|--------|------|----------|
| 결제 승인 완료 | INFO | `[PAYMENT] 승인 완료: orderId={}, paymentKey={}` |
| 결제 승인 실패 | ERROR | `[PAYMENT] 승인 실패: orderId={}, error={}` |
| 재고 부족 | WARN | `[STOCK] 재고 부족: productId={}, 요청={}, 현재={}` |
| 쿠폰 이미 사용됨 | WARN | `[COUPON] 중복 사용 시도: couponId={}, userId={}` |
| 주문 생성 완료 | INFO | `[ORDER] 주문 생성: orderId={}, userId={}, amount={}` |

### 6.3 Mock 구현체 (로컬 개발)

| 이벤트 | 레벨 | 로그 내용 |
|--------|------|----------|
| Mock 결제 승인 | INFO | `[MOCK][PAYMENT] 결제 시뮬레이션: orderId={}` |
| Mock 푸시 발송 | INFO | `[MOCK][FCM] 푸시 시뮬레이션: userId={}, title={}` |
| Mock 파일 저장 | INFO | `[MOCK][STORAGE] 로컬 저장: path={}` |

---

## 7. application.yml 로그 설정 추가 계획

```yaml
# application-local.yml 추가 내용
logging:
  level:
    com.saemaul.chonggak: DEBUG
    org.hibernate.SQL: DEBUG
    org.hibernate.orm.jdbc.bind: TRACE
  pattern:
    console: "%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"

# application-prod.yml 추가 내용
logging:
  level:
    com.saemaul.chonggak: INFO
    org.hibernate.SQL: WARN
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"
```

---

## 8. 성공 기준 (Success Criteria)

- [ ] 전 Application Service에 `@Slf4j` + 비즈니스 이벤트 `log.info` 적용
- [ ] 보안 이벤트 (토큰 재발급, 블랙리스트 차단 등) `log.warn` 적용
- [ ] 외부 API 호출 (결제, FCM) 성공/실패 `log.info/error` 적용
- [ ] Mock 구현체에 `[MOCK]` 접두사 `log.info` 적용
- [ ] 개인정보(비밀번호, 이메일, 카드번호) 로그 미노출 확인
- [ ] `application-local.yml` DEBUG 레벨 설정 적용
- [ ] `application-prod.yml` INFO 레벨 설정 적용
- [ ] 문자열 연결 방식 로그 미사용 (파라미터 바인딩만 사용)

---

## 9. 미결 사항 (Open Questions)

- [ ] MDC(Mapped Diagnostic Context)로 requestId, userId 자동 주입 여부 (Phase 3 이후 고려)
- [ ] 로그 파일 출력 + 로테이션 정책 (운영 배포 단계에서 결정)
- [ ] 구조화 로그(JSON 포맷) vs 텍스트 포맷 — 초기: 텍스트, 운영 고도화 시 JSON 전환 검토

---

**작성일**: 2026-02-28
**작성자**: Claude Code (Sonnet 4.6)
**상태**: Draft
