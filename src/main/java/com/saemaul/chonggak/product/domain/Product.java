package com.saemaul.chonggak.product.domain;

import com.saemaul.chonggak.product.domain.vo.Money;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "products")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private ProductCategory category;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Embedded
    @AttributeOverrides({
            @AttributeOverride(name = "amount", column = @Column(name = "original_price", nullable = false))
    })
    private Money originalPrice;

    @Embedded
    @AttributeOverrides({
            @AttributeOverride(name = "amount", column = @Column(name = "sale_price", nullable = false))
    })
    private Money salePrice;

    @Column(length = 500)
    private String imageUrl;

    @Column(nullable = false)
    private int stockQuantity;

    @Column(nullable = false)
    private int salesCount = 0;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private ProductStatus status = ProductStatus.ACTIVE;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    public static Product create(ProductCategory category, String name, String description,
                                 long originalPrice, long salePrice,
                                 String imageUrl, int stockQuantity) {
        Product product = new Product();
        product.category = category;
        product.name = name;
        product.description = description;
        product.originalPrice = Money.of(originalPrice);
        product.salePrice = Money.of(salePrice);
        product.imageUrl = imageUrl;
        product.stockQuantity = stockQuantity;
        product.createdAt = LocalDateTime.now();
        product.updatedAt = LocalDateTime.now();
        return product;
    }

    public void decreaseStock(int quantity) {
        if (this.stockQuantity < quantity) {
            throw new BusinessException(ErrorCode.INSUFFICIENT_STOCK);
        }
        this.stockQuantity -= quantity;
        this.salesCount += quantity;
        if (this.stockQuantity == 0) {
            this.status = ProductStatus.SOLD_OUT;
        }
        this.updatedAt = LocalDateTime.now();
    }

    public void increaseStock(int quantity) {
        this.stockQuantity += quantity;
        if (this.status == ProductStatus.SOLD_OUT && this.stockQuantity > 0) {
            this.status = ProductStatus.ACTIVE;
        }
        this.updatedAt = LocalDateTime.now();
    }

    public void updateInfo(String name, String description,
                           long originalPrice, long salePrice, String imageUrl) {
        this.name = name;
        this.description = description;
        this.originalPrice = Money.of(originalPrice);
        this.salePrice = Money.of(salePrice);
        if (imageUrl != null) {
            this.imageUrl = imageUrl;
        }
        this.updatedAt = LocalDateTime.now();
    }

    public void changeStatus(ProductStatus status) {
        this.status = status;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isActive() {
        return this.status == ProductStatus.ACTIVE;
    }
}
