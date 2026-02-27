package com.saemaul.chonggak.product.infra.persistence;

import com.saemaul.chonggak.product.domain.Product;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

interface ProductJpaRepository extends JpaRepository<Product, Long> {
    Optional<Product> findByIdAndStatus(Long id, ProductStatus status);
}
