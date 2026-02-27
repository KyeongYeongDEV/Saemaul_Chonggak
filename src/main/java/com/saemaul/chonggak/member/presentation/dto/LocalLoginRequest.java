package com.saemaul.chonggak.member.presentation.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

@Schema(description = "로컬 로그인 요청 (개발 환경 전용)")
public record LocalLoginRequest(

        @Schema(description = "이메일", example = "test@example.com")
        @Email @NotBlank
        String email,

        @Schema(description = "비밀번호", example = "password123!")
        @NotBlank
        String password,

        @Schema(description = "기기 식별자 (없으면 'default' 사용)", example = "device-001")
        String deviceId
) {
    public String resolvedDeviceId() {
        return (deviceId != null && !deviceId.isBlank()) ? deviceId : "default";
    }
}
