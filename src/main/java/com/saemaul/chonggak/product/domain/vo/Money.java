package com.saemaul.chonggak.product.domain.vo;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Embeddable
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Money {

    @Column(nullable = false)
    private long amount;

    public static Money of(long amount) {
        if (amount < 0) throw new IllegalArgumentException("금액은 0 이상이어야 합니다.");
        Money money = new Money();
        money.amount = amount;
        return money;
    }
}
