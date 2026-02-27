package com.saemaul.chonggak.product.presentation.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ProductCreateRequest(
        Long categoryId,
        @NotBlank String name,
        String description,
        @NotNull @Min(0) Long originalPrice,
        @NotNull @Min(0) Long salePrice,
        String imageUrl,
        @NotNull @Min(0) Integer stockQuantity
) {}
