package com.saemaul.chonggak.member.presentation;

import com.saemaul.chonggak.member.application.AuthService;
import com.saemaul.chonggak.member.application.LocalSignupService;
import com.saemaul.chonggak.member.application.dto.LocalLoginCommand;
import com.saemaul.chonggak.member.application.dto.TokenPair;
import com.saemaul.chonggak.member.presentation.dto.LocalLoginRequest;
import com.saemaul.chonggak.member.presentation.dto.LocalSignupRequest;
import com.saemaul.chonggak.shared.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Profile;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Tag(name = "로컬 인증 (개발 전용)", description = "개발 환경에서만 사용 가능한 이메일/비밀번호 회원가입 및 로그인")
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Profile({"local", "test"})
public class LocalAuthController {

    private final AuthService authService;
    private final LocalSignupService localSignupService;

    @Operation(summary = "로컬 회원가입 (개발 전용)", description = "이메일/비밀번호로 회원을 등록합니다. 운영 환경에서는 비활성화됩니다.")
    @PostMapping("/local-signup")
    public ResponseEntity<ApiResponse<Void>> localSignup(@Valid @RequestBody LocalSignupRequest request) {
        localSignupService.signup(request.email(), request.password(), request.nickname());
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @Operation(summary = "로컬 로그인 (개발 전용)", description = "이메일/비밀번호로 로그인합니다. 운영 환경에서는 비활성화됩니다.")
    @PostMapping("/local-login")
    public ResponseEntity<ApiResponse<TokenPair>> localLogin(@Valid @RequestBody LocalLoginRequest request) {
        LocalLoginCommand command = new LocalLoginCommand(
                request.email(), request.password(), request.resolvedDeviceId()
        );
        TokenPair tokenPair = authService.localLogin(command);
        return ResponseEntity.ok(ApiResponse.success(tokenPair));
    }
}
