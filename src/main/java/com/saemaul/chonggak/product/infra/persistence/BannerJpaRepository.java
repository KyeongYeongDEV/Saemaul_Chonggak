package com.saemaul.chonggak.product.infra.persistence;

import com.saemaul.chonggak.product.domain.Banner;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

interface BannerJpaRepository extends JpaRepository<Banner, Long> {
    List<Banner> findAllByActiveTrueOrderByDisplayOrderAsc();
}
