package com.saemaul.chonggak.member.presentation;

import com.saemaul.chonggak.member.application.MemberService;
import com.saemaul.chonggak.member.application.dto.AgreementResult;
import com.saemaul.chonggak.member.application.dto.MemberResult;
import com.saemaul.chonggak.member.application.dto.PointHistoryResult;
import com.saemaul.chonggak.member.presentation.dto.AgreementUpdateRequest;
import com.saemaul.chonggak.shared.response.ApiResponse;
import com.saemaul.chonggak.shared.security.UserPrincipal;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "회원", description = "회원 정보 조회/수정 및 약관, 포인트 관리")
@RestController
@RequestMapping("/api/v1/members")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
public class MemberController {

    private final MemberService memberService;

    @Operation(summary = "내 프로필 조회", description = "로그인한 회원의 프로필 정보를 조회합니다.")
    @GetMapping("/me")
    public ResponseEntity<ApiResponse<MemberResult>> getMyProfile(
            @AuthenticationPrincipal UserPrincipal principal) {
        MemberResult result = memberService.getMyProfile(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @Operation(summary = "회원 탈퇴", description = "로그인한 회원 계정을 탈퇴 처리합니다. 모든 기기에서 로그아웃됩니다.")
    @DeleteMapping("/me")
    public ResponseEntity<ApiResponse<Void>> withdraw(
            @AuthenticationPrincipal UserPrincipal principal) {
        memberService.withdraw(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @Operation(summary = "약관 동의 목록 조회", description = "회원이 동의/비동의한 약관 목록을 조회합니다.")
    @GetMapping("/me/agreements")
    public ResponseEntity<ApiResponse<List<AgreementResult>>> getMyAgreements(
            @AuthenticationPrincipal UserPrincipal principal) {
        List<AgreementResult> result = memberService.getMyAgreements(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @Operation(summary = "약관 동의 수정", description = "특정 약관의 동의 여부를 변경합니다. 필수 약관(TERMS_OF_SERVICE, PRIVACY_POLICY)도 수정 가능하나 비동의 시 서비스 이용이 제한될 수 있습니다.")
    @PutMapping("/me/agreements")
    public ResponseEntity<ApiResponse<Void>> updateAgreement(
            @AuthenticationPrincipal UserPrincipal principal,
            @Valid @RequestBody AgreementUpdateRequest request) {
        memberService.updateAgreement(principal.getUserId(), request.toCommand());
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @Operation(summary = "포인트 잔액 조회", description = "현재 보유한 포인트 잔액을 조회합니다.")
    @GetMapping("/me/points")
    public ResponseEntity<ApiResponse<Long>> getMyPointBalance(
            @AuthenticationPrincipal UserPrincipal principal) {
        long balance = memberService.getMyPointBalance(principal.getUserId());
        return ResponseEntity.ok(ApiResponse.success(balance));
    }

    @Operation(summary = "포인트 내역 조회", description = "포인트 적립/사용/만료 내역을 페이지네이션으로 조회합니다.")
    @GetMapping("/me/points/history")
    public ResponseEntity<ApiResponse<Page<PointHistoryResult>>> getPointHistory(
            @AuthenticationPrincipal UserPrincipal principal,
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC) Pageable pageable) {
        Page<PointHistoryResult> result = memberService.getPointHistory(principal.getUserId(), pageable);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
}
