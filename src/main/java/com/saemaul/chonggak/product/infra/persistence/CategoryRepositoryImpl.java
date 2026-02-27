package com.saemaul.chonggak.product.infra.persistence;

import com.saemaul.chonggak.product.domain.CategoryRepository;
import com.saemaul.chonggak.product.domain.ProductCategory;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class CategoryRepositoryImpl implements CategoryRepository {

    private final CategoryJpaRepository categoryJpaRepository;

    @Override
    public Optional<ProductCategory> findById(Long id) {
        return categoryJpaRepository.findById(id);
    }

    @Override
    public List<ProductCategory> findAllActive() {
        return categoryJpaRepository.findAllByActiveTrueOrderByDisplayOrderAsc();
    }

    @Override
    public ProductCategory save(ProductCategory category) {
        return categoryJpaRepository.save(category);
    }
}
