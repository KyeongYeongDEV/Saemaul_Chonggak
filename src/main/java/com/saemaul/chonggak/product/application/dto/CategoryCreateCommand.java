package com.saemaul.chonggak.product.application.dto;

public record CategoryCreateCommand(
        String name,
        String description,
        Long parentCategoryId,
        int displayOrder
) {
}
