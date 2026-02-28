package com.saemaul.chonggak.product.application.dto;

public record CategoryUpdateCommand(
        String name,
        String description,
        int displayOrder
) {
}
