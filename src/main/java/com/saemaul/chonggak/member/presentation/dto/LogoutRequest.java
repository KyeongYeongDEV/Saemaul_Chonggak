package com.saemaul.chonggak.member.presentation.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotNull;

@Schema(description = "로그아웃 요청")
public record LogoutRequest(

        @Schema(description = "기기 식별자", example = "device-001")
        String deviceId
) {
    public String resolvedDeviceId() {
        return (deviceId != null && !deviceId.isBlank()) ? deviceId : "default";
    }
}
