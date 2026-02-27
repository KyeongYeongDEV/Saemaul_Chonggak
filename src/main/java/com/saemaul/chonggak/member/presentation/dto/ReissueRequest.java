package com.saemaul.chonggak.member.presentation.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Schema(description = "토큰 재발급 요청")
public record ReissueRequest(

        @Schema(description = "Refresh Token")
        @NotBlank
        String refreshToken,

        @Schema(description = "회원 ID")
        @NotNull
        Long userId,

        @Schema(description = "기기 식별자", example = "device-001")
        String deviceId
) {
    public String resolvedDeviceId() {
        return (deviceId != null && !deviceId.isBlank()) ? deviceId : "default";
    }
}
