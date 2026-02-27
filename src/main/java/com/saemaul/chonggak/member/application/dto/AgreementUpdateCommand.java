package com.saemaul.chonggak.member.application.dto;

import com.saemaul.chonggak.member.domain.vo.AgreementType;

public record AgreementUpdateCommand(AgreementType agreementType, boolean agreed) {
}
