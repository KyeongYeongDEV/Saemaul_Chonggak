package com.saemaul.chonggak.member.domain.vo;

public enum PointType {
    EARNED,           // 적립 (구매, 이벤트 등)
    SPENT,            // 사용 (주문 시)
    EXPIRED,          // 만료
    ADMIN_ADJUSTED    // 관리자 조정
}
