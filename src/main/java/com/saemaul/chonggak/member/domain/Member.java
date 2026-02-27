package com.saemaul.chonggak.member.domain;

import com.saemaul.chonggak.member.domain.vo.AgreementType;
import com.saemaul.chonggak.member.domain.vo.MemberRole;
import com.saemaul.chonggak.member.domain.vo.MemberStatus;
import com.saemaul.chonggak.member.domain.vo.OAuthProvider;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Entity
@Table(name = "members",
        uniqueConstraints = {
                @UniqueConstraint(name = "uk_email", columnNames = "email"),
                @UniqueConstraint(name = "uk_oauth", columnNames = {"oauth_provider", "oauth_id"})
        })
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Member {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "oauth_provider")
    @Enumerated(EnumType.STRING)
    private OAuthProvider oauthProvider;  // null이면 로컬 계정

    @Column(name = "oauth_id")
    private String oauthId;

    @Column(nullable = false, length = 100)
    private String email;

    @Column
    private String password;  // BCrypt. OAuth 사용자는 null

    @Column(nullable = false, length = 50)
    private String nickname;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private MemberRole role;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private MemberStatus status;

    @Column(nullable = false)
    private long pointBalance;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "member", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<MemberAgreement> agreements = new ArrayList<>();

    @Builder
    private Member(OAuthProvider oauthProvider, String oauthId, String email,
                   String password, String nickname, MemberRole role) {
        this.oauthProvider = oauthProvider;
        this.oauthId = oauthId;
        this.email = email;
        this.password = password;
        this.nickname = nickname;
        this.role = role;
        this.status = MemberStatus.ACTIVE;
        this.pointBalance = 0L;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    // === 팩토리 메서드 ===

    public static Member createLocalMember(String email, String encodedPassword, String nickname) {
        return Member.builder()
                .oauthProvider(OAuthProvider.LOCAL)
                .email(email)
                .password(encodedPassword)
                .nickname(nickname)
                .role(MemberRole.USER)
                .build();
    }

    public static Member createOAuthMember(OAuthProvider provider, String oauthId,
                                           String email, String nickname) {
        return Member.builder()
                .oauthProvider(provider)
                .oauthId(oauthId)
                .email(email)
                .nickname(nickname)
                .role(MemberRole.USER)
                .build();
    }

    // === 도메인 행위 ===

    public void updateNickname(String nickname) {
        this.nickname = nickname;
        this.updatedAt = LocalDateTime.now();
    }

    public void suspend() {
        this.status = MemberStatus.SUSPENDED;
        this.updatedAt = LocalDateTime.now();
    }

    public void withdraw() {
        this.status = MemberStatus.WITHDRAWN;
        this.updatedAt = LocalDateTime.now();
    }

    public void addPoints(long amount) {
        this.pointBalance += amount;
        this.updatedAt = LocalDateTime.now();
    }

    public void deductPoints(long amount) {
        if (this.pointBalance < amount) {
            throw new IllegalArgumentException("포인트 잔액이 부족합니다.");
        }
        this.pointBalance -= amount;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isActive() {
        return this.status == MemberStatus.ACTIVE;
    }

    public void setAgreement(AgreementType type, boolean agreed) {
        Optional<MemberAgreement> existing = agreements.stream()
                .filter(a -> a.getAgreementType() == type)
                .findFirst();

        if (existing.isPresent()) {
            existing.get().update(agreed);
        } else {
            agreements.add(MemberAgreement.of(this, type, agreed));
        }
        this.updatedAt = LocalDateTime.now();
    }
}
