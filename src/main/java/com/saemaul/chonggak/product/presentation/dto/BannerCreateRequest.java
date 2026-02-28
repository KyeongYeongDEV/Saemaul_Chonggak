package com.saemaul.chonggak.product.presentation.dto;

import com.saemaul.chonggak.product.application.dto.BannerCreateCommand;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

public record BannerCreateRequest(
        @NotBlank String title,
        @NotBlank String imageUrl,
        String linkUrl,
        @NotNull int displayOrder,
        LocalDateTime startAt,
        LocalDateTime endAt
) {
    public BannerCreateCommand toCommand() {
        return new BannerCreateCommand(title, imageUrl, linkUrl, displayOrder, startAt, endAt);
    }
}
