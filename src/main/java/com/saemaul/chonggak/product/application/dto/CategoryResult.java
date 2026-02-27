package com.saemaul.chonggak.product.application.dto;

import com.saemaul.chonggak.product.domain.ProductCategory;

public record CategoryResult(
        Long id,
        String name,
        String description,
        Long parentCategoryId,
        int displayOrder
) {
    public static CategoryResult from(ProductCategory category) {
        return new CategoryResult(
                category.getId(),
                category.getName(),
                category.getDescription(),
                category.getParentCategoryId(),
                category.getDisplayOrder()
        );
    }
}
