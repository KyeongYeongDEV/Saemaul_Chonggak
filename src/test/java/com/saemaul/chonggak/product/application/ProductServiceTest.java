package com.saemaul.chonggak.product.application;

import com.saemaul.chonggak.product.application.dto.*;
import com.saemaul.chonggak.product.domain.*;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;
import com.saemaul.chonggak.product.domain.vo.SortType;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.BDDMockito.*;

@DisplayName("ProductService 테스트")
@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @InjectMocks ProductService productService;

    @Mock ProductRepository productRepository;
    @Mock CategoryRepository categoryRepository;
    @Mock BannerRepository bannerRepository;

    private Product sampleProduct() {
        Product p = Product.create(null, "테스트 상품", "설명", 10000L, 9000L, "http://img.jpg", 10);
        ReflectionTestUtils.setField(p, "id", 1L);
        return p;
    }

    @Test
    @DisplayName("상품 상세 조회 성공")
    void getProduct_success() {
        given(productRepository.findActiveById(1L)).willReturn(Optional.of(sampleProduct()));

        ProductResult result = productService.getProduct(1L);

        assertThat(result.id()).isEqualTo(1L);
        assertThat(result.name()).isEqualTo("테스트 상품");
        assertThat(result.salePrice()).isEqualTo(9000L);
    }

    @Test
    @DisplayName("없는 상품 조회 → PRODUCT_NOT_FOUND")
    void getProduct_notFound() {
        given(productRepository.findActiveById(anyLong())).willReturn(Optional.empty());

        assertThatThrownBy(() -> productService.getProduct(999L))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.PRODUCT_NOT_FOUND));
    }

    @Test
    @DisplayName("상품 검색 - 키워드 없음")
    void searchProducts_noKeyword() {
        ProductSearchCommand command = new ProductSearchCommand(null, null, SortType.LATEST, 0, 20);
        given(productRepository.search(null, null, SortType.LATEST, PageRequest.of(0, 20)))
                .willReturn(new PageImpl<>(List.of(sampleProduct())));

        var result = productService.searchProducts(command);

        assertThat(result.getContent()).hasSize(1);
        assertThat(result.getContent().get(0).name()).isEqualTo("테스트 상품");
    }

    @Test
    @DisplayName("베스트셀러 조회")
    void getBestSellers_success() {
        given(productRepository.findBestSellers(any())).willReturn(new PageImpl<>(List.of(sampleProduct())));

        List<ProductSummaryResult> result = productService.getBestSellers();

        assertThat(result).hasSize(1);
    }

    @Test
    @DisplayName("카테고리 목록 조회")
    void getCategories_success() {
        ProductCategory cat = ProductCategory.create("의류", "의류 카테고리", null, 1);
        ReflectionTestUtils.setField(cat, "id", 1L);
        given(categoryRepository.findAllActive()).willReturn(List.of(cat));

        List<CategoryResult> result = productService.getCategories();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).name()).isEqualTo("의류");
    }

    @Test
    @DisplayName("배너 목록 조회 - 활성 배너만")
    void getActiveBanners_success() {
        Banner banner = Banner.create("메인 배너", "http://img.jpg", "http://link", 1, null, null);
        ReflectionTestUtils.setField(banner, "id", 1L);
        given(bannerRepository.findAllActive()).willReturn(List.of(banner));

        List<BannerResult> result = productService.getActiveBanners();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).title()).isEqualTo("메인 배너");
    }

    @Test
    @DisplayName("상품 등록 성공")
    void createProduct_success() {
        ProductCreateCommand command = new ProductCreateCommand(
                null, "새 상품", "설명", 20000L, 18000L, "http://img.jpg", 50);
        Product saved = sampleProduct();
        given(productRepository.save(any())).willReturn(saved);

        ProductResult result = productService.createProduct(command);

        assertThat(result.name()).isEqualTo("테스트 상품");
        then(productRepository).should().save(any(Product.class));
    }

    @Test
    @DisplayName("상품 수정 성공")
    void updateProduct_success() {
        Product product = sampleProduct();
        given(productRepository.findActiveById(1L)).willReturn(Optional.of(product));
        given(productRepository.save(any())).willReturn(product);

        ProductUpdateCommand command = new ProductUpdateCommand("수정명", "수정 설명", 15000L, 13000L, null);
        productService.updateProduct(1L, command);

        assertThat(product.getName()).isEqualTo("수정명");
        then(productRepository).should().save(product);
    }

    @Test
    @DisplayName("상품 삭제 - 상태 DELETED 변경")
    void deleteProduct_success() {
        Product product = sampleProduct();
        given(productRepository.findById(1L)).willReturn(Optional.of(product));
        given(productRepository.save(any())).willReturn(product);

        productService.deleteProduct(1L);

        assertThat(product.getStatus()).isEqualTo(ProductStatus.DELETED);
        then(productRepository).should().save(product);
    }
}
