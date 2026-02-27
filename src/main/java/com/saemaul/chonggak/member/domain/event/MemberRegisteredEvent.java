package com.saemaul.chonggak.member.domain.event;

public record MemberRegisteredEvent(Long memberId, String email, String nickname) {
}
