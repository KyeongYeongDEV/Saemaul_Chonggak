package com.saemaul.chonggak.product.presentation;

import com.saemaul.chonggak.product.application.ProductService;
import com.saemaul.chonggak.product.application.dto.BannerResult;
import com.saemaul.chonggak.product.presentation.dto.BannerCreateRequest;
import com.saemaul.chonggak.product.presentation.dto.BannerUpdateRequest;
import com.saemaul.chonggak.shared.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/v1/banners")
@RequiredArgsConstructor
@Tag(name = "Admin - Banner", description = "관리자 배너 관리 API")
@SecurityRequirement(name = "bearerAuth")
public class AdminBannerController {

    private final ProductService productService;

    @Operation(summary = "배너 등록")
    @PostMapping
    public ApiResponse<BannerResult> createBanner(@Valid @RequestBody BannerCreateRequest request) {
        return ApiResponse.success(productService.createBanner(request.toCommand()));
    }

    @Operation(summary = "배너 수정")
    @PutMapping("/{bannerId}")
    public ApiResponse<BannerResult> updateBanner(
            @PathVariable Long bannerId,
            @Valid @RequestBody BannerUpdateRequest request) {
        return ApiResponse.success(productService.updateBanner(bannerId, request.toCommand()));
    }

    @Operation(summary = "배너 비활성화")
    @DeleteMapping("/{bannerId}")
    public ApiResponse<Void> deactivateBanner(@PathVariable Long bannerId) {
        productService.deactivateBanner(bannerId);
        return ApiResponse.success(null);
    }
}
