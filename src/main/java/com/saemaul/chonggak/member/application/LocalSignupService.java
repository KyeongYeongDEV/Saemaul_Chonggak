package com.saemaul.chonggak.member.application;

import com.saemaul.chonggak.member.domain.Member;
import com.saemaul.chonggak.member.domain.MemberRepository;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Profile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Profile({"local", "test"})
@RequiredArgsConstructor
public class LocalSignupService {

    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public Member signup(String email, String rawPassword, String nickname) {
        if (memberRepository.existsByEmail(email)) {
            throw new BusinessException(ErrorCode.MEMBER_ALREADY_EXISTS);
        }
        Member member = Member.createLocalMember(email, passwordEncoder.encode(rawPassword), nickname);
        return memberRepository.save(member);
    }
}
