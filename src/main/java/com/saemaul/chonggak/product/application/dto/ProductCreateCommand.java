package com.saemaul.chonggak.product.application.dto;

public record ProductCreateCommand(
        Long categoryId,
        String name,
        String description,
        long originalPrice,
        long salePrice,
        String imageUrl,
        int stockQuantity
) {}
