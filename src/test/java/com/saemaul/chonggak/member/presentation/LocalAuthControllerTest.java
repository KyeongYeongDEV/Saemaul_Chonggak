package com.saemaul.chonggak.member.presentation;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.saemaul.chonggak.member.application.AuthService;
import com.saemaul.chonggak.member.application.LocalSignupService;
import com.saemaul.chonggak.member.application.dto.LocalLoginCommand;
import com.saemaul.chonggak.member.application.dto.TokenPair;
import com.saemaul.chonggak.member.domain.Member;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(LocalAuthController.class)
@ActiveProfiles("test")
@DisplayName("LocalAuthController 테스트")
class LocalAuthControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;

    @MockBean AuthService authService;
    @MockBean LocalSignupService localSignupService;

    @Test
    @WithMockUser
    @DisplayName("로컬 회원가입 성공 → 200")
    void localSignup_success() throws Exception {
        given(localSignupService.signup(anyString(), anyString(), anyString()))
                .willReturn(mock(Member.class));

        mockMvc.perform(post("/api/v1/auth/local-signup")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "email", "test@example.com",
                                "password", "password1234",
                                "nickname", "테스터"
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"));
    }

    @Test
    @WithMockUser
    @DisplayName("이미 가입된 이메일로 회원가입 → 409")
    void localSignup_duplicateEmail() throws Exception {
        given(localSignupService.signup(anyString(), anyString(), anyString()))
                .willThrow(new BusinessException(ErrorCode.MEMBER_ALREADY_EXISTS));

        mockMvc.perform(post("/api/v1/auth/local-signup")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "email", "test@example.com",
                                "password", "password1234",
                                "nickname", "테스터"
                        ))))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("MEMBER_ALREADY_EXISTS"));
    }

    @Test
    @WithMockUser
    @DisplayName("로컬 로그인 성공 → AT/RT 반환")
    void localLogin_success() throws Exception {
        TokenPair tokenPair = new TokenPair("access.token.here", "refresh-uuid");
        given(authService.localLogin(any(LocalLoginCommand.class))).willReturn(tokenPair);

        mockMvc.perform(post("/api/v1/auth/local-login")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "email", "test@example.com",
                                "password", "password1234",
                                "deviceId", "device-001"
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"))
                .andExpect(jsonPath("$.data.accessToken").value("access.token.here"))
                .andExpect(jsonPath("$.data.refreshToken").value("refresh-uuid"));
    }

    @Test
    @WithMockUser
    @DisplayName("잘못된 비밀번호 로그인 → 401")
    void localLogin_wrongPassword() throws Exception {
        given(authService.localLogin(any(LocalLoginCommand.class)))
                .willThrow(new BusinessException(ErrorCode.INVALID_CREDENTIALS));

        mockMvc.perform(post("/api/v1/auth/local-login")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "email", "test@example.com",
                                "password", "wrongpassword",
                                "deviceId", "device-001"
                        ))))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.code").value("INVALID_CREDENTIALS"));
    }

    @Test
    @WithMockUser
    @DisplayName("유효성 검사 실패 - 이메일 형식 오류 → 400")
    void localLogin_invalidEmail() throws Exception {
        mockMvc.perform(post("/api/v1/auth/local-login")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "email", "not-an-email",
                                "password", "password1234"
                        ))))
                .andExpect(status().isBadRequest());
    }
}
