package com.saemaul.chonggak.product.presentation;

import com.saemaul.chonggak.product.application.ProductService;
import com.saemaul.chonggak.product.application.dto.ProductCreateCommand;
import com.saemaul.chonggak.product.application.dto.ProductResult;
import com.saemaul.chonggak.product.application.dto.ProductUpdateCommand;
import com.saemaul.chonggak.product.presentation.dto.ProductCreateRequest;
import com.saemaul.chonggak.product.presentation.dto.ProductUpdateRequest;
import com.saemaul.chonggak.shared.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/v1/products")
@RequiredArgsConstructor
@Tag(name = "Admin - Product", description = "관리자 상품 관리 API")
@SecurityRequirement(name = "bearerAuth")
public class AdminProductController {

    private final ProductService productService;

    @Operation(summary = "상품 등록")
    @PostMapping
    public ApiResponse<ProductResult> createProduct(@Valid @RequestBody ProductCreateRequest request) {
        ProductCreateCommand command = new ProductCreateCommand(
                request.categoryId(), request.name(), request.description(),
                request.originalPrice(), request.salePrice(),
                request.imageUrl(), request.stockQuantity()
        );
        return ApiResponse.success(productService.createProduct(command));
    }

    @Operation(summary = "상품 수정")
    @PutMapping("/{productId}")
    public ApiResponse<ProductResult> updateProduct(
            @PathVariable Long productId,
            @Valid @RequestBody ProductUpdateRequest request
    ) {
        ProductUpdateCommand command = new ProductUpdateCommand(
                request.name(), request.description(),
                request.originalPrice(), request.salePrice(), request.imageUrl()
        );
        return ApiResponse.success(productService.updateProduct(productId, command));
    }

    @Operation(summary = "상품 삭제")
    @DeleteMapping("/{productId}")
    public ApiResponse<Void> deleteProduct(@PathVariable Long productId) {
        productService.deleteProduct(productId);
        return ApiResponse.success(null);
    }
}
