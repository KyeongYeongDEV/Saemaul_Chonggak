package com.saemaul.chonggak.product.domain;

import java.util.List;
import java.util.Optional;

public interface BannerRepository {
    Optional<Banner> findById(Long id);
    List<Banner> findAllActive();
    Banner save(Banner banner);
}
