package com.saemaul.chonggak.product.presentation.dto;

import com.saemaul.chonggak.product.application.dto.BannerUpdateCommand;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

public record BannerUpdateRequest(
        @NotBlank String title,
        @NotBlank String imageUrl,
        String linkUrl,
        @NotNull int displayOrder,
        LocalDateTime startAt,
        LocalDateTime endAt
) {
    public BannerUpdateCommand toCommand() {
        return new BannerUpdateCommand(title, imageUrl, linkUrl, displayOrder, startAt, endAt);
    }
}
