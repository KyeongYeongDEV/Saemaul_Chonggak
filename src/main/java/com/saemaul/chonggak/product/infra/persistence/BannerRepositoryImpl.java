package com.saemaul.chonggak.product.infra.persistence;

import com.saemaul.chonggak.product.domain.Banner;
import com.saemaul.chonggak.product.domain.BannerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
@RequiredArgsConstructor
public class BannerRepositoryImpl implements BannerRepository {

    private final BannerJpaRepository bannerJpaRepository;

    @Override
    public List<Banner> findAllActive() {
        return bannerJpaRepository.findAllByActiveTrueOrderByDisplayOrderAsc();
    }

    @Override
    public Banner save(Banner banner) {
        return bannerJpaRepository.save(banner);
    }
}
