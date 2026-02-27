package com.saemaul.chonggak.product.infra.persistence;

import com.querydsl.core.BooleanBuilder;
import com.querydsl.core.types.OrderSpecifier;
import com.querydsl.jpa.impl.JPAQueryFactory;
import com.saemaul.chonggak.product.domain.Product;
import com.saemaul.chonggak.product.domain.ProductRepository;
import com.saemaul.chonggak.product.domain.QProduct;
import com.saemaul.chonggak.product.domain.vo.ProductStatus;
import com.saemaul.chonggak.product.domain.vo.SortType;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class ProductRepositoryImpl implements ProductRepository {

    private final ProductJpaRepository productJpaRepository;
    private final JPAQueryFactory queryFactory;

    @Override
    public Optional<Product> findById(Long id) {
        return productJpaRepository.findById(id);
    }

    @Override
    public Optional<Product> findActiveById(Long id) {
        return productJpaRepository.findByIdAndStatus(id, ProductStatus.ACTIVE);
    }

    @Override
    public Page<Product> search(String keyword, Long categoryId, SortType sortType, Pageable pageable) {
        QProduct product = QProduct.product;
        BooleanBuilder where = new BooleanBuilder();
        where.and(product.status.eq(ProductStatus.ACTIVE));

        if (keyword != null && !keyword.isBlank()) {
            where.and(product.name.containsIgnoreCase(keyword)
                    .or(product.description.containsIgnoreCase(keyword)));
        }
        if (categoryId != null) {
            where.and(product.category.id.eq(categoryId));
        }

        OrderSpecifier<?> order = switch (sortType) {
            case PRICE_ASC -> product.salePrice.amount.asc();
            case PRICE_DESC -> product.salePrice.amount.desc();
            case POPULAR -> product.salesCount.desc();
            default -> product.createdAt.desc();
        };

        List<Product> content = queryFactory.selectFrom(product)
                .where(where)
                .orderBy(order)
                .offset(pageable.getOffset())
                .limit(pageable.getPageSize())
                .fetch();

        Long total = queryFactory.select(product.count())
                .from(product)
                .where(where)
                .fetchOne();

        return new PageImpl<>(content, pageable, total != null ? total : 0L);
    }

    @Override
    public Page<Product> findBestSellers(Pageable pageable) {
        QProduct product = QProduct.product;

        List<Product> content = queryFactory.selectFrom(product)
                .where(product.status.eq(ProductStatus.ACTIVE))
                .orderBy(product.salesCount.desc())
                .offset(pageable.getOffset())
                .limit(pageable.getPageSize())
                .fetch();

        Long total = queryFactory.select(product.count())
                .from(product)
                .where(product.status.eq(ProductStatus.ACTIVE))
                .fetchOne();

        return new PageImpl<>(content, pageable, total != null ? total : 0L);
    }

    @Override
    public Product save(Product product) {
        return productJpaRepository.save(product);
    }
}
