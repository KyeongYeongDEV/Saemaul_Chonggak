package com.saemaul.chonggak.product.application;

import com.saemaul.chonggak.product.application.dto.*;
import com.saemaul.chonggak.product.domain.*;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;
import com.saemaul.chonggak.product.domain.vo.SortType;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.Caching;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;
    private final BannerRepository bannerRepository;

    @Cacheable(value = "product", key = "#productId")
    public ProductResult getProduct(Long productId) {
        Product product = productRepository.findActiveById(productId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND));
        return ProductResult.from(product);
    }

    public Page<ProductSummaryResult> searchProducts(ProductSearchCommand command) {
        SortType sortType = command.sortType() != null ? command.sortType() : SortType.LATEST;
        PageRequest pageable = PageRequest.of(command.page(), command.size());
        return productRepository.search(command.keyword(), command.categoryId(), sortType, pageable)
                .map(ProductSummaryResult::from);
    }

    @Cacheable(value = "bestseller", key = "'top20'")
    public List<ProductSummaryResult> getBestSellers() {
        return productRepository.findBestSellers(PageRequest.of(0, 20))
                .map(ProductSummaryResult::from)
                .getContent();
    }

    @Cacheable(value = "category", key = "'all'")
    public List<CategoryResult> getCategories() {
        return categoryRepository.findAllActive().stream()
                .map(CategoryResult::from)
                .toList();
    }

    @Cacheable(value = "banner", key = "'active'")
    public List<BannerResult> getActiveBanners() {
        return bannerRepository.findAllActive().stream()
                .filter(Banner::isCurrentlyActive)
                .map(BannerResult::from)
                .toList();
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(value = "productList", allEntries = true),
            @CacheEvict(value = "bestseller", allEntries = true)
    })
    public ProductResult createProduct(ProductCreateCommand command) {
        ProductCategory category = null;
        if (command.categoryId() != null) {
            category = categoryRepository.findById(command.categoryId())
                    .orElseThrow(() -> new BusinessException(ErrorCode.NOT_FOUND));
        }
        Product product = Product.create(category, command.name(), command.description(),
                command.originalPrice(), command.salePrice(),
                command.imageUrl(), command.stockQuantity());
        return ProductResult.from(productRepository.save(product));
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(value = "product", key = "#productId"),
            @CacheEvict(value = "productList", allEntries = true),
            @CacheEvict(value = "bestseller", allEntries = true)
    })
    public ProductResult updateProduct(Long productId, ProductUpdateCommand command) {
        Product product = productRepository.findActiveById(productId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND));
        product.updateInfo(command.name(), command.description(),
                command.originalPrice(), command.salePrice(), command.imageUrl());
        return ProductResult.from(productRepository.save(product));
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(value = "product", key = "#productId"),
            @CacheEvict(value = "productList", allEntries = true),
            @CacheEvict(value = "bestseller", allEntries = true)
    })
    public void deleteProduct(Long productId) {
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND));
        product.changeStatus(ProductStatus.DELETED);
        productRepository.save(product);
    }
}
