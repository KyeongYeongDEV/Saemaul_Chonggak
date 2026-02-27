package com.saemaul.chonggak.member.application.dto;

import com.saemaul.chonggak.member.domain.PointHistory;
import com.saemaul.chonggak.member.domain.vo.PointType;

import java.time.LocalDateTime;

public record PointHistoryResult(
        Long id,
        PointType pointType,
        long amount,
        long balance,
        String description,
        LocalDateTime createdAt
) {
    public static PointHistoryResult from(PointHistory history) {
        return new PointHistoryResult(
                history.getId(),
                history.getPointType(),
                history.getAmount(),
                history.getBalance(),
                history.getDescription(),
                history.getCreatedAt()
        );
    }
}
