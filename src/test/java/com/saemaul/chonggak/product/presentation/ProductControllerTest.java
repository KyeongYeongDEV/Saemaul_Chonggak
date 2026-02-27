package com.saemaul.chonggak.product.presentation;

import com.saemaul.chonggak.product.application.ProductService;
import com.saemaul.chonggak.product.application.dto.*;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.PageImpl;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.BDDMockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ProductController.class)
@ActiveProfiles("test")
@DisplayName("ProductController 테스트")
class ProductControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean ProductService productService;

    private ProductResult sampleProductResult() {
        return new ProductResult(1L, null, null, "테스트 상품", "설명",
                10000L, 9000L, "http://img.jpg", 10, ProductStatus.ACTIVE, LocalDateTime.now());
    }

    @Test
    @WithMockUser
    @DisplayName("상품 상세 조회 → 200")
    void getProduct_success() throws Exception {
        given(productService.getProduct(1L)).willReturn(sampleProductResult());

        mockMvc.perform(get("/api/v1/products/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"))
                .andExpect(jsonPath("$.data.name").value("테스트 상품"))
                .andExpect(jsonPath("$.data.salePrice").value(9000));
    }

    @Test
    @WithMockUser
    @DisplayName("없는 상품 조회 → 404")
    void getProduct_notFound() throws Exception {
        given(productService.getProduct(anyLong()))
                .willThrow(new BusinessException(ErrorCode.PRODUCT_NOT_FOUND));

        mockMvc.perform(get("/api/v1/products/999"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value("PRODUCT_NOT_FOUND"));
    }

    @Test
    @WithMockUser
    @DisplayName("상품 목록 검색 → 200")
    void searchProducts_success() throws Exception {
        ProductSummaryResult summary = new ProductSummaryResult(1L, "상품A", 9000L, "http://img.jpg", ProductStatus.ACTIVE);
        given(productService.searchProducts(any())).willReturn(new PageImpl<>(List.of(summary)));

        mockMvc.perform(get("/api/v1/products").param("keyword", "상품").param("page", "0").param("size", "20"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.content").isArray())
                .andExpect(jsonPath("$.data.content.length()").value(1));
    }

    @Test
    @WithMockUser
    @DisplayName("베스트셀러 조회 → 200")
    void getBestSellers_success() throws Exception {
        ProductSummaryResult summary = new ProductSummaryResult(1L, "베스트상품", 15000L, "http://img.jpg", ProductStatus.ACTIVE);
        given(productService.getBestSellers()).willReturn(List.of(summary));

        mockMvc.perform(get("/api/v1/products/bestseller"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data.length()").value(1));
    }

    @Test
    @WithMockUser
    @DisplayName("카테고리 목록 조회 → 200")
    void getCategories_success() throws Exception {
        given(productService.getCategories()).willReturn(
                List.of(new CategoryResult(1L, "의류", "의류 카테고리", null, 1))
        );

        mockMvc.perform(get("/api/v1/categories"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data[0].name").value("의류"));
    }

    @Test
    @WithMockUser
    @DisplayName("배너 목록 조회 → 200")
    void getActiveBanners_success() throws Exception {
        given(productService.getActiveBanners()).willReturn(
                List.of(new BannerResult(1L, "메인 배너", "http://img.jpg", "http://link", 1))
        );

        mockMvc.perform(get("/api/v1/banners"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data[0].title").value("메인 배너"));
    }
}
