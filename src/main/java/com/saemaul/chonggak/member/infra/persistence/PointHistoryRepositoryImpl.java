package com.saemaul.chonggak.member.infra.persistence;

import com.saemaul.chonggak.member.domain.PointHistory;
import com.saemaul.chonggak.member.domain.PointHistoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class PointHistoryRepositoryImpl implements PointHistoryRepository {

    private final PointHistoryJpaRepository jpaRepository;

    @Override
    public PointHistory save(PointHistory pointHistory) {
        return jpaRepository.save(pointHistory);
    }

    @Override
    public Page<PointHistory> findByMemberId(Long memberId, Pageable pageable) {
        return jpaRepository.findByMemberIdOrderByCreatedAtDesc(memberId, pageable);
    }
}
