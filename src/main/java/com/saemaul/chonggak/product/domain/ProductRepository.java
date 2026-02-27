package com.saemaul.chonggak.product.domain;

import com.saemaul.chonggak.product.domain.vo.SortType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.Optional;

public interface ProductRepository {
    Optional<Product> findById(Long id);
    Optional<Product> findActiveById(Long id);
    Page<Product> search(String keyword, Long categoryId, SortType sortType, Pageable pageable);
    Page<Product> findBestSellers(Pageable pageable);
    Product save(Product product);
}
