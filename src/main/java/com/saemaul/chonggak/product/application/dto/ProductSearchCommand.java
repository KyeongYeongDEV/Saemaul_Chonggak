package com.saemaul.chonggak.product.application.dto;

import com.saemaul.chonggak.product.domain.vo.SortType;

public record ProductSearchCommand(
        String keyword,
        Long categoryId,
        SortType sortType,
        int page,
        int size
) {}
