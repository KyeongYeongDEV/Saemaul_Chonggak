package com.saemaul.chonggak.member.domain;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface PointHistoryRepository {

    PointHistory save(PointHistory pointHistory);

    Page<PointHistory> findByMemberId(Long memberId, Pageable pageable);
}
