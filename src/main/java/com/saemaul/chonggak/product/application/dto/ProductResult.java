package com.saemaul.chonggak.product.application.dto;

import com.saemaul.chonggak.product.domain.Product;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;

import java.time.LocalDateTime;

public record ProductResult(
        Long id,
        Long categoryId,
        String categoryName,
        String name,
        String description,
        long originalPrice,
        long salePrice,
        String imageUrl,
        int stockQuantity,
        ProductStatus status,
        LocalDateTime createdAt
) {
    public static ProductResult from(Product product) {
        return new ProductResult(
                product.getId(),
                product.getCategory() != null ? product.getCategory().getId() : null,
                product.getCategory() != null ? product.getCategory().getName() : null,
                product.getName(),
                product.getDescription(),
                product.getOriginalPrice().getAmount(),
                product.getSalePrice().getAmount(),
                product.getImageUrl(),
                product.getStockQuantity(),
                product.getStatus(),
                product.getCreatedAt()
        );
    }
}
