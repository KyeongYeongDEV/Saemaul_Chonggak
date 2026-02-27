package com.saemaul.chonggak.shared.security;

import com.saemaul.chonggak.member.domain.vo.MemberRole;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import static org.assertj.core.api.Assertions.*;

@DisplayName("JwtProvider 테스트")
class JwtProviderTest {

    private JwtProvider jwtProvider;

    @BeforeEach
    void setUp() {
        jwtProvider = new JwtProvider();
        ReflectionTestUtils.setField(jwtProvider, "secret",
                "test-secret-key-must-be-at-least-32-characters-long");
        ReflectionTestUtils.setField(jwtProvider, "accessTokenExpiry", 3600L);
        jwtProvider.init();
    }

    @Test
    @DisplayName("Access Token 생성 - userId, role 클레임 포함")
    void createAccessToken() {
        String token = jwtProvider.createAccessToken(1L, MemberRole.USER);

        assertThat(token).isNotBlank();

        Claims claims = jwtProvider.parseAndValidate(token);
        assertThat(claims.getSubject()).isEqualTo("1");
        assertThat(claims.get("role", String.class)).isEqualTo("USER");
        assertThat(claims.getId()).isNotBlank(); // jti 존재
    }

    @Test
    @DisplayName("유효한 토큰 파싱 성공")
    void parseAndValidate_validToken() {
        String token = jwtProvider.createAccessToken(42L, MemberRole.ADMIN);
        Claims claims = jwtProvider.parseAndValidate(token);

        assertThat(claims.getSubject()).isEqualTo("42");
        assertThat(claims.get("role", String.class)).isEqualTo("ADMIN");
    }

    @Test
    @DisplayName("잘못된 토큰 → INVALID_TOKEN 예외")
    void parseAndValidate_invalidToken() {
        assertThatThrownBy(() -> jwtProvider.parseAndValidate("invalid.token.here"))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_TOKEN));
    }

    @Test
    @DisplayName("만료된 토큰 → EXPIRED_TOKEN 예외")
    void parseAndValidate_expiredToken() {
        // expiry=0으로 즉시 만료 토큰 생성
        JwtProvider shortLived = new JwtProvider();
        ReflectionTestUtils.setField(shortLived, "secret",
                "test-secret-key-must-be-at-least-32-characters-long");
        ReflectionTestUtils.setField(shortLived, "accessTokenExpiry", 0L);
        shortLived.init();

        String token = shortLived.createAccessToken(1L, MemberRole.USER);

        assertThatThrownBy(() -> jwtProvider.parseAndValidate(token))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.EXPIRED_TOKEN));
    }

    @Test
    @DisplayName("만료 토큰에서 Claims 추출 (parseIgnoreExpiry)")
    void parseIgnoreExpiry_extractsClaimsFromExpiredToken() {
        JwtProvider shortLived = new JwtProvider();
        ReflectionTestUtils.setField(shortLived, "secret",
                "test-secret-key-must-be-at-least-32-characters-long");
        ReflectionTestUtils.setField(shortLived, "accessTokenExpiry", 0L);
        shortLived.init();

        String token = shortLived.createAccessToken(5L, MemberRole.USER);

        Claims claims = jwtProvider.parseIgnoreExpiry(token);
        assertThat(claims.getSubject()).isEqualTo("5");
    }

    @Test
    @DisplayName("남은 만료 시간 계산 - 유효한 토큰은 양수 반환")
    void getRemainingSeconds_returnsPositive() {
        String token = jwtProvider.createAccessToken(1L, MemberRole.USER);
        Claims claims = jwtProvider.parseAndValidate(token);

        long remaining = jwtProvider.getRemainingSeconds(claims);
        assertThat(remaining).isPositive().isLessThanOrEqualTo(3600L);
    }
}
