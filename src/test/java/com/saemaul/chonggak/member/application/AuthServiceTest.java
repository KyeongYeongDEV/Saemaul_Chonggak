package com.saemaul.chonggak.member.application;

import com.saemaul.chonggak.member.application.dto.LocalLoginCommand;
import com.saemaul.chonggak.member.application.dto.TokenPair;
import com.saemaul.chonggak.member.domain.Member;
import com.saemaul.chonggak.member.domain.MemberRepository;
import com.saemaul.chonggak.member.domain.RefreshTokenPort;
import com.saemaul.chonggak.member.domain.TokenBlacklistPort;
import com.saemaul.chonggak.member.domain.vo.MemberRole;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import com.saemaul.chonggak.shared.security.JwtProvider;
import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.*;

@DisplayName("AuthService 테스트")
@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @InjectMocks AuthService authService;

    @Mock MemberRepository memberRepository;
    @Mock RefreshTokenPort refreshTokenPort;
    @Mock TokenBlacklistPort tokenBlacklistPort;
    @Mock JwtProvider jwtProvider;
    @Mock PasswordEncoder passwordEncoder;

    private Member activeMember() {
        Member m = Member.createLocalMember("test@email.com", "encodedPw", "닉네임");
        ReflectionTestUtils.setField(m, "id", 1L);
        return m;
    }

    // ─── localLogin ───────────────────────────────────────────────

    @Test
    @DisplayName("로컬 로그인 성공 - AT/RT 반환")
    void localLogin_success() {
        Member member = activeMember();
        given(memberRepository.findByEmail("test@email.com")).willReturn(Optional.of(member));
        given(passwordEncoder.matches("rawPw", "encodedPw")).willReturn(true);
        given(jwtProvider.createAccessToken(1L, MemberRole.USER)).willReturn("accessToken");

        TokenPair result = authService.localLogin(new LocalLoginCommand("test@email.com", "rawPw", "device-1"));

        assertThat(result.accessToken()).isEqualTo("accessToken");
        assertThat(result.refreshToken()).isNotBlank();
        then(refreshTokenPort).should().save(eq(1L), eq("device-1"), anyString());
    }

    @Test
    @DisplayName("존재하지 않는 이메일 → INVALID_CREDENTIALS")
    void localLogin_emailNotFound() {
        given(memberRepository.findByEmail(anyString())).willReturn(Optional.empty());

        assertThatThrownBy(() ->
                authService.localLogin(new LocalLoginCommand("none@email.com", "pw", "d")))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_CREDENTIALS));
    }

    @Test
    @DisplayName("비밀번호 불일치 → INVALID_CREDENTIALS")
    void localLogin_wrongPassword() {
        Member member = activeMember();
        given(memberRepository.findByEmail(anyString())).willReturn(Optional.of(member));
        given(passwordEncoder.matches(anyString(), anyString())).willReturn(false);

        assertThatThrownBy(() ->
                authService.localLogin(new LocalLoginCommand("test@email.com", "wrongPw", "d")))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_CREDENTIALS));
    }

    @Test
    @DisplayName("정지된 회원 로그인 → MEMBER_SUSPENDED")
    void localLogin_suspendedMember() {
        Member member = activeMember();
        member.suspend();
        given(memberRepository.findByEmail(anyString())).willReturn(Optional.of(member));
        given(passwordEncoder.matches(anyString(), anyString())).willReturn(true);

        assertThatThrownBy(() ->
                authService.localLogin(new LocalLoginCommand("test@email.com", "pw", "d")))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.MEMBER_SUSPENDED));
    }

    // ─── reissue ──────────────────────────────────────────────────

    @Test
    @DisplayName("토큰 재발급 성공 - RT Rotation")
    void reissue_success() {
        Member member = activeMember();
        given(refreshTokenPort.find(1L, "device-1")).willReturn(Optional.of("stored-rt"));
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));
        given(jwtProvider.createAccessToken(1L, MemberRole.USER)).willReturn("newAT");

        TokenPair result = authService.reissue("stored-rt", 1L, "device-1");

        assertThat(result.accessToken()).isEqualTo("newAT");
        assertThat(result.refreshToken()).isNotBlank();
        then(refreshTokenPort).should().delete(1L, "device-1");       // 기존 RT 삭제
        then(refreshTokenPort).should().save(eq(1L), eq("device-1"), anyString()); // 새 RT 저장
    }

    @Test
    @DisplayName("RT 불일치 → INVALID_REFRESH_TOKEN + 전체 RT 삭제 (탈취 의심)")
    void reissue_mismatchRT_deletesAll() {
        given(refreshTokenPort.find(1L, "device-1")).willReturn(Optional.of("stored-rt"));

        assertThatThrownBy(() -> authService.reissue("other-rt", 1L, "device-1"))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_REFRESH_TOKEN));

        then(refreshTokenPort).should().deleteAll(1L); // 전체 기기 RT 삭제
    }

    @Test
    @DisplayName("RT 없음 (이미 로그아웃) → INVALID_REFRESH_TOKEN")
    void reissue_rtNotFound() {
        given(refreshTokenPort.find(anyLong(), anyString())).willReturn(Optional.empty());

        assertThatThrownBy(() -> authService.reissue("rt", 1L, "device-1"))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INVALID_REFRESH_TOKEN));
    }

    // ─── logout ───────────────────────────────────────────────────

    @Test
    @DisplayName("로그아웃 - AT 블랙리스트 등록 + RT 삭제")
    void logout_success() {
        Claims claims = mock(Claims.class);
        given(claims.getId()).willReturn("jti-123");
        given(jwtProvider.parseIgnoreExpiry("accessToken")).willReturn(claims);
        given(jwtProvider.getRemainingSeconds(claims)).willReturn(1800L);

        authService.logout("accessToken", 1L, "device-1");

        then(tokenBlacklistPort).should().add("jti-123", 1800L);
        then(refreshTokenPort).should().delete(1L, "device-1");
    }
}
