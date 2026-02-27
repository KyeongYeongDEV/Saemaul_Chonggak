package com.saemaul.chonggak.member.application.dto;

import com.saemaul.chonggak.member.domain.Member;
import com.saemaul.chonggak.member.domain.vo.MemberRole;
import com.saemaul.chonggak.member.domain.vo.MemberStatus;
import com.saemaul.chonggak.member.domain.vo.OAuthProvider;

import java.time.LocalDateTime;

public record MemberResult(
        Long id,
        String email,
        String nickname,
        OAuthProvider oauthProvider,
        MemberRole role,
        MemberStatus status,
        long pointBalance,
        LocalDateTime createdAt
) {
    public static MemberResult from(Member member) {
        return new MemberResult(
                member.getId(),
                member.getEmail(),
                member.getNickname(),
                member.getOauthProvider(),
                member.getRole(),
                member.getStatus(),
                member.getPointBalance(),
                member.getCreatedAt()
        );
    }
}
