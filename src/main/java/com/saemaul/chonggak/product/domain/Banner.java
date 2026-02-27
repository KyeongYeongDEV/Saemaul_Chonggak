package com.saemaul.chonggak.product.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "banners")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Banner {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false, length = 500)
    private String imageUrl;

    @Column(length = 500)
    private String linkUrl;

    @Column(nullable = false)
    private boolean active = true;

    @Column(nullable = false)
    private int displayOrder;

    @Column
    private LocalDateTime startAt;

    @Column
    private LocalDateTime endAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    public static Banner create(String title, String imageUrl, String linkUrl,
                                int displayOrder, LocalDateTime startAt, LocalDateTime endAt) {
        Banner banner = new Banner();
        banner.title = title;
        banner.imageUrl = imageUrl;
        banner.linkUrl = linkUrl;
        banner.displayOrder = displayOrder;
        banner.startAt = startAt;
        banner.endAt = endAt;
        banner.createdAt = LocalDateTime.now();
        banner.updatedAt = LocalDateTime.now();
        return banner;
    }

    public boolean isCurrentlyActive() {
        if (!active) return false;
        LocalDateTime now = LocalDateTime.now();
        if (startAt != null && now.isBefore(startAt)) return false;
        if (endAt != null && now.isAfter(endAt)) return false;
        return true;
    }

    public void deactivate() {
        this.active = false;
        this.updatedAt = LocalDateTime.now();
    }
}
