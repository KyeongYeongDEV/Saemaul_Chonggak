package com.saemaul.chonggak.product.presentation.dto;

import com.saemaul.chonggak.product.application.dto.CategoryCreateCommand;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record CategoryCreateRequest(
        @NotBlank String name,
        String description,
        Long parentCategoryId,
        @NotNull int displayOrder
) {
    public CategoryCreateCommand toCommand() {
        return new CategoryCreateCommand(name, description, parentCategoryId, displayOrder);
    }
}
