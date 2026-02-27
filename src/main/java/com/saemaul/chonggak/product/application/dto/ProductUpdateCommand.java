package com.saemaul.chonggak.product.application.dto;

public record ProductUpdateCommand(
        String name,
        String description,
        long originalPrice,
        long salePrice,
        String imageUrl
) {}
