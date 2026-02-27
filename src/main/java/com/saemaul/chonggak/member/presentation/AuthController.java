package com.saemaul.chonggak.member.presentation;

import com.saemaul.chonggak.member.application.AuthService;
import com.saemaul.chonggak.member.application.dto.TokenPair;
import com.saemaul.chonggak.member.presentation.dto.LogoutRequest;
import com.saemaul.chonggak.member.presentation.dto.ReissueRequest;
import com.saemaul.chonggak.shared.response.ApiResponse;
import com.saemaul.chonggak.shared.security.UserPrincipal;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

@Tag(name = "인증", description = "토큰 재발급 및 로그아웃")
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @Operation(summary = "Access Token 재발급", description = "Refresh Token으로 Access Token을 재발급합니다. RT Rotation 적용.")
    @PostMapping("/reissue")
    public ResponseEntity<ApiResponse<TokenPair>> reissue(@Valid @RequestBody ReissueRequest request) {
        TokenPair tokenPair = authService.reissue(
                request.refreshToken(), request.userId(), request.resolvedDeviceId()
        );
        return ResponseEntity.ok(ApiResponse.success(tokenPair));
    }

    @Operation(summary = "로그아웃", description = "Access Token을 블랙리스트에 등록하고 Refresh Token을 삭제합니다.",
            security = @SecurityRequirement(name = "bearerAuth"))
    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<Void>> logout(
            @RequestHeader("Authorization") String bearerToken,
            @AuthenticationPrincipal UserPrincipal principal,
            @RequestBody(required = false) LogoutRequest request) {

        String accessToken = bearerToken.substring(7);
        String deviceId = (request != null) ? request.resolvedDeviceId() : "default";
        authService.logout(accessToken, principal.getUserId(), deviceId);
        return ResponseEntity.ok(ApiResponse.success(null));
    }
}
