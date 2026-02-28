package com.saemaul.chonggak.product.presentation;

import com.saemaul.chonggak.product.application.ProductService;
import com.saemaul.chonggak.product.application.dto.CategoryResult;
import com.saemaul.chonggak.product.presentation.dto.CategoryCreateRequest;
import com.saemaul.chonggak.product.presentation.dto.CategoryUpdateRequest;
import com.saemaul.chonggak.shared.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/v1/categories")
@RequiredArgsConstructor
@Tag(name = "Admin - Category", description = "관리자 카테고리 관리 API")
@SecurityRequirement(name = "bearerAuth")
public class AdminCategoryController {

    private final ProductService productService;

    @Operation(summary = "카테고리 등록")
    @PostMapping
    public ApiResponse<CategoryResult> createCategory(@Valid @RequestBody CategoryCreateRequest request) {
        return ApiResponse.success(productService.createCategory(request.toCommand()));
    }

    @Operation(summary = "카테고리 수정")
    @PutMapping("/{categoryId}")
    public ApiResponse<CategoryResult> updateCategory(
            @PathVariable Long categoryId,
            @Valid @RequestBody CategoryUpdateRequest request) {
        return ApiResponse.success(productService.updateCategory(categoryId, request.toCommand()));
    }

    @Operation(summary = "카테고리 삭제 (비활성화)")
    @DeleteMapping("/{categoryId}")
    public ApiResponse<Void> deleteCategory(@PathVariable Long categoryId) {
        productService.deleteCategory(categoryId);
        return ApiResponse.success(null);
    }
}
