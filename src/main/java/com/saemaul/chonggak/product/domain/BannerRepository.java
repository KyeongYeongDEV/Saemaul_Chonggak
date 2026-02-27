package com.saemaul.chonggak.product.domain;

import java.util.List;

public interface BannerRepository {
    List<Banner> findAllActive();
    Banner save(Banner banner);
}
