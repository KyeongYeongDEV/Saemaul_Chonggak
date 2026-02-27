package com.saemaul.chonggak.product.application.dto;

import com.saemaul.chonggak.product.domain.Banner;

public record BannerResult(
        Long id,
        String title,
        String imageUrl,
        String linkUrl,
        int displayOrder
) {
    public static BannerResult from(Banner banner) {
        return new BannerResult(
                banner.getId(),
                banner.getTitle(),
                banner.getImageUrl(),
                banner.getLinkUrl(),
                banner.getDisplayOrder()
        );
    }
}
