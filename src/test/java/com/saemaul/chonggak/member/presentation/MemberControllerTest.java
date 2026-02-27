package com.saemaul.chonggak.member.presentation;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.saemaul.chonggak.member.application.MemberService;
import com.saemaul.chonggak.member.application.dto.*;
import com.saemaul.chonggak.member.domain.vo.*;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import com.saemaul.chonggak.shared.security.UserPrincipal;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.PageImpl;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(MemberController.class)
@ActiveProfiles("test")
@DisplayName("MemberController 테스트")
class MemberControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;

    @MockBean MemberService memberService;

    private void authenticateAs(Long userId) {
        UserPrincipal principal = new UserPrincipal(userId, MemberRole.USER, "jti-123");
        SecurityContextHolder.getContext().setAuthentication(
                new UsernamePasswordAuthenticationToken(principal, null, principal.getAuthorities())
        );
    }

    private MemberResult sampleMemberResult() {
        return new MemberResult(1L, "test@email.com", "닉네임",
                OAuthProvider.LOCAL, MemberRole.USER, MemberStatus.ACTIVE, 0L, LocalDateTime.now());
    }

    @Test
    @DisplayName("내 프로필 조회 - 인증된 사용자 → 200")
    void getMyProfile_authenticated() throws Exception {
        authenticateAs(1L);
        given(memberService.getMyProfile(1L)).willReturn(sampleMemberResult());

        mockMvc.perform(get("/api/v1/members/me"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"))
                .andExpect(jsonPath("$.data.email").value("test@email.com"))
                .andExpect(jsonPath("$.data.nickname").value("닉네임"));
    }

    @Test
    @DisplayName("내 프로필 조회 - 비인증 → 401")
    void getMyProfile_unauthenticated() throws Exception {
        SecurityContextHolder.clearContext();

        mockMvc.perform(get("/api/v1/members/me"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("약관 동의 목록 조회")
    void getMyAgreements_success() throws Exception {
        authenticateAs(1L);
        List<AgreementResult> agreements = List.of(
                new AgreementResult(AgreementType.TERMS_OF_SERVICE, true, LocalDateTime.now()),
                new AgreementResult(AgreementType.MARKETING_PUSH, false, null)
        );
        given(memberService.getMyAgreements(1L)).willReturn(agreements);

        mockMvc.perform(get("/api/v1/members/me/agreements"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data.length()").value(2));
    }

    @Test
    @DisplayName("약관 동의 수정 - 성공 → 200")
    void updateAgreement_success() throws Exception {
        authenticateAs(1L);
        willDoNothing().given(memberService).updateAgreement(eq(1L), any());

        mockMvc.perform(put("/api/v1/members/me/agreements")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "agreementType", "MARKETING_PUSH",
                                "agreed", true
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"));
    }

    @Test
    @DisplayName("포인트 잔액 조회")
    void getMyPointBalance_success() throws Exception {
        authenticateAs(1L);
        given(memberService.getMyPointBalance(1L)).willReturn(3000L);

        mockMvc.perform(get("/api/v1/members/me/points"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").value(3000));
    }

    @Test
    @DisplayName("포인트 내역 조회 - 빈 페이지")
    void getPointHistory_empty() throws Exception {
        authenticateAs(1L);
        given(memberService.getPointHistory(eq(1L), any())).willReturn(new PageImpl<>(List.of()));

        mockMvc.perform(get("/api/v1/members/me/points/history"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.content").isArray())
                .andExpect(jsonPath("$.data.totalElements").value(0));
    }

    @Test
    @DisplayName("회원 탈퇴 → 200")
    void withdraw_success() throws Exception {
        authenticateAs(1L);
        willDoNothing().given(memberService).withdraw(1L);

        mockMvc.perform(delete("/api/v1/members/me").with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"));
    }

    @Test
    @DisplayName("회원 탈퇴 - 이미 탈퇴한 회원 → 403 (MEMBER_SUSPENDED 상황)")
    void withdraw_alreadyWithdrawn() throws Exception {
        authenticateAs(1L);
        willThrow(new BusinessException(ErrorCode.MEMBER_SUSPENDED))
                .given(memberService).withdraw(1L);

        mockMvc.perform(delete("/api/v1/members/me").with(csrf()))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.code").value("MEMBER_SUSPENDED"));
    }
}
