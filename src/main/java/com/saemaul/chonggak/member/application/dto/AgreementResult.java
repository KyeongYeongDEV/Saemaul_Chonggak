package com.saemaul.chonggak.member.application.dto;

import com.saemaul.chonggak.member.domain.MemberAgreement;
import com.saemaul.chonggak.member.domain.vo.AgreementType;

import java.time.LocalDateTime;

public record AgreementResult(
        AgreementType agreementType,
        boolean agreed,
        LocalDateTime agreedAt
) {
    public static AgreementResult from(MemberAgreement agreement) {
        return new AgreementResult(
                agreement.getAgreementType(),
                agreement.isAgreed(),
                agreement.getAgreedAt()
        );
    }
}
