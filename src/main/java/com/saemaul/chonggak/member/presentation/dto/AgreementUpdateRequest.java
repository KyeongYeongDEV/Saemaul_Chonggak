package com.saemaul.chonggak.member.presentation.dto;

import com.saemaul.chonggak.member.application.dto.AgreementUpdateCommand;
import com.saemaul.chonggak.member.domain.vo.AgreementType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotNull;

@Schema(description = "약관 동의 수정 요청")
public record AgreementUpdateRequest(

        @Schema(description = "약관 종류", example = "MARKETING_PUSH")
        @NotNull
        AgreementType agreementType,

        @Schema(description = "동의 여부", example = "true")
        boolean agreed
) {
    public AgreementUpdateCommand toCommand() {
        return new AgreementUpdateCommand(agreementType, agreed);
    }
}
