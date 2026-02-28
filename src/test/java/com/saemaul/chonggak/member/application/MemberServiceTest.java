package com.saemaul.chonggak.member.application;

import com.saemaul.chonggak.member.application.dto.*;
import com.saemaul.chonggak.member.domain.*;
import com.saemaul.chonggak.member.domain.vo.AgreementType;
import com.saemaul.chonggak.member.domain.vo.PointType;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.BDDMockito.*;

@DisplayName("MemberService 테스트")
@ExtendWith(MockitoExtension.class)
class MemberServiceTest {

    @InjectMocks MemberService memberService;

    @Mock MemberRepository memberRepository;
    @Mock PointHistoryRepository pointHistoryRepository;
    @Mock RefreshTokenPort refreshTokenPort;

    private Member activeMember() {
        Member m = Member.createLocalMember("test@email.com", "encodedPw", "닉네임");
        ReflectionTestUtils.setField(m, "id", 1L);
        return m;
    }

    @Test
    @DisplayName("내 프로필 조회 성공")
    void getMyProfile_success() {
        Member member = activeMember();
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));

        MemberResult result = memberService.getMyProfile(1L);

        assertThat(result.id()).isEqualTo(1L);
        assertThat(result.email()).isEqualTo("test@email.com");
        assertThat(result.nickname()).isEqualTo("닉네임");
    }

    @Test
    @DisplayName("존재하지 않는 회원 조회 → MEMBER_NOT_FOUND")
    void getMyProfile_notFound() {
        given(memberRepository.findById(anyLong())).willReturn(Optional.empty());

        assertThatThrownBy(() -> memberService.getMyProfile(999L))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.MEMBER_NOT_FOUND));
    }

    @Test
    @DisplayName("정지된 회원 프로필 조회 → MEMBER_SUSPENDED")
    void getMyProfile_suspended() {
        Member member = activeMember();
        member.suspend();
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));

        assertThatThrownBy(() -> memberService.getMyProfile(1L))
                .isInstanceOf(BusinessException.class)
                .satisfies(e -> assertThat(((BusinessException) e).getErrorCode())
                        .isEqualTo(ErrorCode.MEMBER_SUSPENDED));
    }

    @Test
    @DisplayName("내 프로필 수정 - 닉네임 변경")
    void updateMyProfile_success() {
        Member member = activeMember();
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));
        given(memberRepository.save(any())).willReturn(member);

        MemberResult result = memberService.updateMyProfile(1L, new MemberUpdateCommand("새닉네임"));

        assertThat(result.nickname()).isEqualTo("새닉네임");
        then(memberRepository).should().save(member);
    }

    @Test
    @DisplayName("약관 동의 목록 조회")
    void getMyAgreements_success() {
        Member member = activeMember();
        member.setAgreement(AgreementType.TERMS_OF_SERVICE, true);
        member.setAgreement(AgreementType.MARKETING_PUSH, false);
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));

        List<AgreementResult> results = memberService.getMyAgreements(1L);

        assertThat(results).hasSize(2);
        assertThat(results).anyMatch(r -> r.agreementType() == AgreementType.TERMS_OF_SERVICE && r.agreed());
        assertThat(results).anyMatch(r -> r.agreementType() == AgreementType.MARKETING_PUSH && !r.agreed());
    }

    @Test
    @DisplayName("약관 동의 수정")
    void updateAgreement_success() {
        Member member = activeMember();
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));
        given(memberRepository.save(any())).willReturn(member);

        memberService.updateAgreement(1L, new AgreementUpdateCommand(AgreementType.MARKETING_PUSH, true));

        assertThat(member.getAgreements()).hasSize(1);
        assertThat(member.getAgreements().get(0).isAgreed()).isTrue();
        then(memberRepository).should().save(member);
    }

    @Test
    @DisplayName("포인트 잔액 조회")
    void getMyPointBalance_success() {
        Member member = activeMember();
        member.addPoints(5000L);
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));

        long balance = memberService.getMyPointBalance(1L);

        assertThat(balance).isEqualTo(5000L);
    }

    @Test
    @DisplayName("포인트 내역 조회 - 페이지네이션")
    void getPointHistory_success() {
        PointHistory history = PointHistory.builder()
                .memberId(1L)
                .pointType(PointType.EARNED)
                .amount(1000L)
                .balance(1000L)
                .description("구매 적립")
                .build();
        ReflectionTestUtils.setField(history, "id", 1L);
        ReflectionTestUtils.setField(history, "createdAt", LocalDateTime.now());

        Page<PointHistory> page = new PageImpl<>(List.of(history));
        given(pointHistoryRepository.findByMemberId(eq(1L), any())).willReturn(page);

        Page<PointHistoryResult> result = memberService.getPointHistory(1L, PageRequest.of(0, 20));

        assertThat(result.getContent()).hasSize(1);
        assertThat(result.getContent().get(0).amount()).isEqualTo(1000L);
        assertThat(result.getContent().get(0).pointType()).isEqualTo(PointType.EARNED);
    }

    @Test
    @DisplayName("회원 탈퇴 - 상태 변경 + 전체 RT 삭제")
    void withdraw_success() {
        Member member = activeMember();
        given(memberRepository.findById(1L)).willReturn(Optional.of(member));
        given(memberRepository.save(any())).willReturn(member);

        memberService.withdraw(1L);

        assertThat(member.isActive()).isFalse();
        then(refreshTokenPort).should().deleteAll(1L);
        then(memberRepository).should().save(member);
    }
}
