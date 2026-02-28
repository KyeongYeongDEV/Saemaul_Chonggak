package com.saemaul.chonggak.product.application.dto;

import java.time.LocalDateTime;

public record BannerUpdateCommand(
        String title,
        String imageUrl,
        String linkUrl,
        int displayOrder,
        LocalDateTime startAt,
        LocalDateTime endAt
) {
}
