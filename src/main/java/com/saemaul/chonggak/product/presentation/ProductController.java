package com.saemaul.chonggak.product.presentation;

import com.saemaul.chonggak.product.application.ProductService;
import com.saemaul.chonggak.product.application.dto.*;
import com.saemaul.chonggak.product.domain.vo.SortType;
import com.saemaul.chonggak.shared.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Tag(name = "Product", description = "상품 API")
public class ProductController {

    private final ProductService productService;

    @Operation(summary = "상품 상세 조회")
    @GetMapping("/products/{productId}")
    public ApiResponse<ProductResult> getProduct(@PathVariable Long productId) {
        return ApiResponse.success(productService.getProduct(productId));
    }

    @Operation(summary = "상품 목록 검색")
    @GetMapping("/products")
    public ApiResponse<Page<ProductSummaryResult>> searchProducts(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) SortType sortType,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        ProductSearchCommand command = new ProductSearchCommand(keyword, categoryId, sortType, page, size);
        return ApiResponse.success(productService.searchProducts(command));
    }

    @Operation(summary = "베스트셀러 조회")
    @GetMapping("/products/bestseller")
    public ApiResponse<List<ProductSummaryResult>> getBestSellers() {
        return ApiResponse.success(productService.getBestSellers());
    }

    @Operation(summary = "카테고리 목록 조회")
    @GetMapping("/categories")
    public ApiResponse<List<CategoryResult>> getCategories() {
        return ApiResponse.success(productService.getCategories());
    }

    @Operation(summary = "배너 목록 조회")
    @GetMapping("/banners")
    public ApiResponse<List<BannerResult>> getActiveBanners() {
        return ApiResponse.success(productService.getActiveBanners());
    }
}
