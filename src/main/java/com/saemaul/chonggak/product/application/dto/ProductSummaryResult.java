package com.saemaul.chonggak.product.application.dto;

import com.saemaul.chonggak.product.domain.Product;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;

public record ProductSummaryResult(
        Long id,
        String name,
        long salePrice,
        String imageUrl,
        ProductStatus status
) {
    public static ProductSummaryResult from(Product product) {
        return new ProductSummaryResult(
                product.getId(),
                product.getName(),
                product.getSalePrice().getAmount(),
                product.getImageUrl(),
                product.getStatus()
        );
    }
}
