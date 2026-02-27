package com.saemaul.chonggak.product.domain;

import java.util.List;
import java.util.Optional;

public interface CategoryRepository {
    Optional<ProductCategory> findById(Long id);
    List<ProductCategory> findAllActive();
    ProductCategory save(ProductCategory category);
}
