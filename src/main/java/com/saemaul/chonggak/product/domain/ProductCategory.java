package com.saemaul.chonggak.product.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "product_categories")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProductCategory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(length = 500)
    private String description;

    @Column
    private Long parentCategoryId;

    @Column(nullable = false)
    private int displayOrder;

    @Column(nullable = false)
    private boolean active = true;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    public static ProductCategory create(String name, String description,
                                         Long parentCategoryId, int displayOrder) {
        ProductCategory cat = new ProductCategory();
        cat.name = name;
        cat.description = description;
        cat.parentCategoryId = parentCategoryId;
        cat.displayOrder = displayOrder;
        cat.createdAt = LocalDateTime.now();
        cat.updatedAt = LocalDateTime.now();
        return cat;
    }

    public void update(String name, String description, int displayOrder) {
        this.name = name;
        this.description = description;
        this.displayOrder = displayOrder;
        this.updatedAt = LocalDateTime.now();
    }

    public void deactivate() {
        this.active = false;
        this.updatedAt = LocalDateTime.now();
    }
}
