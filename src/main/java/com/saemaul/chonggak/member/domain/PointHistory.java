package com.saemaul.chonggak.member.domain;

import com.saemaul.chonggak.member.domain.vo.PointType;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "point_histories",
        indexes = @Index(name = "idx_point_member_id", columnList = "member_id"))
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class PointHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "member_id", nullable = false)
    private Long memberId;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private PointType pointType;

    @Column(nullable = false)
    private long amount;  // 양수: 적립, 음수: 사용/만료

    @Column(nullable = false)
    private long balance;  // 이 거래 후 잔액

    @Column(length = 200)
    private String description;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    private PointHistory(Long memberId, PointType pointType, long amount,
                         long balance, String description) {
        this.memberId = memberId;
        this.pointType = pointType;
        this.amount = amount;
        this.balance = balance;
        this.description = description;
        this.createdAt = LocalDateTime.now();
    }
}
