package com.saemaul.chonggak.member.application;

import com.saemaul.chonggak.member.application.dto.*;
import com.saemaul.chonggak.member.domain.Member;
import com.saemaul.chonggak.member.domain.MemberRepository;
import com.saemaul.chonggak.member.domain.PointHistory;
import com.saemaul.chonggak.member.domain.PointHistoryRepository;
import com.saemaul.chonggak.member.infra.redis.RefreshTokenRepository;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MemberService {

    private final MemberRepository memberRepository;
    private final PointHistoryRepository pointHistoryRepository;
    private final RefreshTokenRepository refreshTokenRepository;

    @Transactional(readOnly = true)
    public MemberResult getMyProfile(Long memberId) {
        Member member = findActiveMember(memberId);
        return MemberResult.from(member);
    }

    @Transactional(readOnly = true)
    public List<AgreementResult> getMyAgreements(Long memberId) {
        Member member = findActiveMember(memberId);
        return member.getAgreements().stream()
                .map(AgreementResult::from)
                .toList();
    }

    @Transactional
    public void updateAgreement(Long memberId, AgreementUpdateCommand command) {
        Member member = findActiveMember(memberId);
        member.setAgreement(command.agreementType(), command.agreed());
        memberRepository.save(member);
    }

    @Transactional(readOnly = true)
    public long getMyPointBalance(Long memberId) {
        return findActiveMember(memberId).getPointBalance();
    }

    @Transactional(readOnly = true)
    public Page<PointHistoryResult> getPointHistory(Long memberId, Pageable pageable) {
        return pointHistoryRepository.findByMemberId(memberId, pageable)
                .map(PointHistoryResult::from);
    }

    @Transactional
    public void withdraw(Long memberId) {
        Member member = findActiveMember(memberId);
        member.withdraw();
        memberRepository.save(member);
        refreshTokenRepository.deleteAll(memberId);
    }

    private Member findActiveMember(Long memberId) {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new BusinessException(ErrorCode.MEMBER_NOT_FOUND));
        if (!member.isActive()) {
            throw new BusinessException(ErrorCode.MEMBER_SUSPENDED);
        }
        return member;
    }
}
