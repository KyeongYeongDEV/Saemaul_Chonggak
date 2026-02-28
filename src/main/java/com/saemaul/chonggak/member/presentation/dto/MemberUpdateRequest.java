package com.saemaul.chonggak.member.presentation.dto;

import com.saemaul.chonggak.member.application.dto.MemberUpdateCommand;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record MemberUpdateRequest(
        @NotBlank(message = "닉네임은 필수입니다.")
        @Size(max = 50, message = "닉네임은 50자 이하여야 합니다.")
        String nickname
) {
    public MemberUpdateCommand toCommand() {
        return new MemberUpdateCommand(nickname);
    }
}
