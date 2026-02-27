package com.saemaul.chonggak.member.infra.persistence;

import com.saemaul.chonggak.member.domain.PointHistory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

interface PointHistoryJpaRepository extends JpaRepository<PointHistory, Long> {

    Page<PointHistory> findByMemberIdOrderByCreatedAtDesc(Long memberId, Pageable pageable);
}
