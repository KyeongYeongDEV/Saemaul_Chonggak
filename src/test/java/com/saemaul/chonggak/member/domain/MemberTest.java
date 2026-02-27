package com.saemaul.chonggak.member.domain;

import com.saemaul.chonggak.member.domain.vo.AgreementType;
import com.saemaul.chonggak.member.domain.vo.MemberRole;
import com.saemaul.chonggak.member.domain.vo.MemberStatus;
import com.saemaul.chonggak.member.domain.vo.OAuthProvider;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Member 도메인 테스트")
class MemberTest {

    @Test
    @DisplayName("로컬 회원 생성 - 초기 상태는 ACTIVE, 포인트 0")
    void createLocalMember() {
        Member member = Member.createLocalMember("test@email.com", "encodedPw", "닉네임");

        assertThat(member.getEmail()).isEqualTo("test@email.com");
        assertThat(member.getNickname()).isEqualTo("닉네임");
        assertThat(member.getOauthProvider()).isEqualTo(OAuthProvider.LOCAL);
        assertThat(member.getRole()).isEqualTo(MemberRole.USER);
        assertThat(member.getStatus()).isEqualTo(MemberStatus.ACTIVE);
        assertThat(member.getPointBalance()).isZero();
        assertThat(member.isActive()).isTrue();
    }

    @Test
    @DisplayName("OAuth 회원 생성")
    void createOAuthMember() {
        Member member = Member.createOAuthMember(OAuthProvider.KAKAO, "kakao-123", "oauth@email.com", "카카오유저");

        assertThat(member.getOauthProvider()).isEqualTo(OAuthProvider.KAKAO);
        assertThat(member.getOauthId()).isEqualTo("kakao-123");
        assertThat(member.getPassword()).isNull();
        assertThat(member.isActive()).isTrue();
    }

    @Test
    @DisplayName("포인트 적립 - 잔액 증가")
    void addPoints() {
        Member member = Member.createLocalMember("a@b.com", "pw", "닉");
        member.addPoints(1000L);
        assertThat(member.getPointBalance()).isEqualTo(1000L);

        member.addPoints(500L);
        assertThat(member.getPointBalance()).isEqualTo(1500L);
    }

    @Test
    @DisplayName("포인트 차감 - 정상 차감")
    void deductPoints_success() {
        Member member = Member.createLocalMember("a@b.com", "pw", "닉");
        member.addPoints(1000L);
        member.deductPoints(300L);
        assertThat(member.getPointBalance()).isEqualTo(700L);
    }

    @Test
    @DisplayName("포인트 차감 - 잔액 부족 시 예외")
    void deductPoints_insufficientBalance() {
        Member member = Member.createLocalMember("a@b.com", "pw", "닉");
        member.addPoints(100L);

        assertThatThrownBy(() -> member.deductPoints(200L))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("부족");
    }

    @Test
    @DisplayName("약관 동의 추가 및 업데이트")
    void setAgreement() {
        Member member = Member.createLocalMember("a@b.com", "pw", "닉");

        // 최초 동의
        member.setAgreement(AgreementType.MARKETING_PUSH, true);
        assertThat(member.getAgreements()).hasSize(1);
        assertThat(member.getAgreements().get(0).isAgreed()).isTrue();

        // 동의 철회 (업데이트)
        member.setAgreement(AgreementType.MARKETING_PUSH, false);
        assertThat(member.getAgreements()).hasSize(1); // 중복 추가 아님
        assertThat(member.getAgreements().get(0).isAgreed()).isFalse();
    }

    @Test
    @DisplayName("회원 탈퇴 - 상태 WITHDRAWN")
    void withdraw() {
        Member member = Member.createLocalMember("a@b.com", "pw", "닉");
        member.withdraw();

        assertThat(member.getStatus()).isEqualTo(MemberStatus.WITHDRAWN);
        assertThat(member.isActive()).isFalse();
    }

    @Test
    @DisplayName("회원 정지 - 상태 SUSPENDED")
    void suspend() {
        Member member = Member.createLocalMember("a@b.com", "pw", "닉");
        member.suspend();

        assertThat(member.getStatus()).isEqualTo(MemberStatus.SUSPENDED);
        assertThat(member.isActive()).isFalse();
    }
}
