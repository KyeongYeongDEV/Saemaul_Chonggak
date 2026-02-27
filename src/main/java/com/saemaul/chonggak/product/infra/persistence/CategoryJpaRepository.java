package com.saemaul.chonggak.product.infra.persistence;

import com.saemaul.chonggak.product.domain.ProductCategory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

interface CategoryJpaRepository extends JpaRepository<ProductCategory, Long> {
    List<ProductCategory> findAllByActiveTrueOrderByDisplayOrderAsc();
}
