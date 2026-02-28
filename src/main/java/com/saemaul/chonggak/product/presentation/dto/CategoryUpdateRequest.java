package com.saemaul.chonggak.product.presentation.dto;

import com.saemaul.chonggak.product.application.dto.CategoryUpdateCommand;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record CategoryUpdateRequest(
        @NotBlank String name,
        String description,
        @NotNull int displayOrder
) {
    public CategoryUpdateCommand toCommand() {
        return new CategoryUpdateCommand(name, description, displayOrder);
    }
}
