package com.saemaul.chonggak.product.domain;

import com.saemaul.chonggak.product.domain.vo.ProductStatus;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Product 도메인 테스트")
class ProductTest {

    private Product sampleProduct(int stock) {
        return Product.create(null, "테스트 상품", "설명", 10000L, 9000L, "http://img.jpg", stock);
    }

    @Test
    @DisplayName("상품 생성 성공")
    void create_success() {
        Product product = sampleProduct(10);

        assertThat(product.getName()).isEqualTo("테스트 상품");
        assertThat(product.getOriginalPrice().getAmount()).isEqualTo(10000L);
        assertThat(product.getSalePrice().getAmount()).isEqualTo(9000L);
        assertThat(product.getStockQuantity()).isEqualTo(10);
        assertThat(product.getStatus()).isEqualTo(ProductStatus.ACTIVE);
    }

    @Test
    @DisplayName("음수 가격으로 생성 시 예외")
    void create_negativePrice_throws() {
        assertThatThrownBy(() -> Product.create(null, "상품", "설명", -1L, 9000L, null, 10))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    @DisplayName("재고 차감 성공")
    void decreaseStock_success() {
        Product product = sampleProduct(10);

        product.decreaseStock(3);

        assertThat(product.getStockQuantity()).isEqualTo(7);
        assertThat(product.getSalesCount()).isEqualTo(3);
        assertThat(product.getStatus()).isEqualTo(ProductStatus.ACTIVE);
    }

    @Test
    @DisplayName("재고 전량 차감 시 SOLD_OUT 전환")
    void decreaseStock_soldOut() {
        Product product = sampleProduct(5);

        product.decreaseStock(5);

        assertThat(product.getStockQuantity()).isEqualTo(0);
        assertThat(product.getStatus()).isEqualTo(ProductStatus.SOLD_OUT);
    }

    @Test
    @DisplayName("재고 부족 시 INSUFFICIENT_STOCK 예외")
    void decreaseStock_insufficient() {
        Product product = sampleProduct(2);

        assertThatThrownBy(() -> product.decreaseStock(5))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.INSUFFICIENT_STOCK));
    }

    @Test
    @DisplayName("재고 추가 시 SOLD_OUT → ACTIVE 복구")
    void increaseStock_restoresActive() {
        Product product = sampleProduct(1);
        product.decreaseStock(1); // SOLD_OUT 상태로 만들기

        product.increaseStock(10);

        assertThat(product.getStockQuantity()).isEqualTo(10);
        assertThat(product.getStatus()).isEqualTo(ProductStatus.ACTIVE);
    }

    @Test
    @DisplayName("상품 정보 수정")
    void updateInfo_success() {
        Product product = sampleProduct(10);

        product.updateInfo("수정된 상품명", "수정된 설명", 20000L, 18000L, "http://new-img.jpg");

        assertThat(product.getName()).isEqualTo("수정된 상품명");
        assertThat(product.getOriginalPrice().getAmount()).isEqualTo(20000L);
        assertThat(product.getSalePrice().getAmount()).isEqualTo(18000L);
    }

    @Test
    @DisplayName("상태 변경 - DELETED")
    void changeStatus_deleted() {
        Product product = sampleProduct(10);

        product.changeStatus(ProductStatus.DELETED);

        assertThat(product.getStatus()).isEqualTo(ProductStatus.DELETED);
        assertThat(product.isActive()).isFalse();
    }
}
