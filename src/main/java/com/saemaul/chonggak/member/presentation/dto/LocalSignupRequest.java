package com.saemaul.chonggak.member.presentation.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

@Schema(description = "로컬 회원가입 요청 (개발 환경 전용)")
public record LocalSignupRequest(

        @Schema(description = "이메일", example = "test@example.com")
        @Email @NotBlank
        String email,

        @Schema(description = "비밀번호 (8자 이상)", example = "password123!")
        @NotBlank @Size(min = 8)
        String password,

        @Schema(description = "닉네임", example = "테스터")
        @NotBlank @Size(min = 2, max = 20)
        String nickname
) {}
