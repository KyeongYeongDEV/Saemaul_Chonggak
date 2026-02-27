package com.saemaul.chonggak.member.domain;

import com.saemaul.chonggak.member.domain.vo.AgreementType;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "member_agreements",
        uniqueConstraints = @UniqueConstraint(name = "uk_member_agreement", columnNames = {"member_id", "agreement_type"}))
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class MemberAgreement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    @Column(name = "agreement_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private AgreementType agreementType;

    @Column(nullable = false)
    private boolean agreed;

    private LocalDateTime agreedAt;

    static MemberAgreement of(Member member, AgreementType type, boolean agreed) {
        MemberAgreement a = new MemberAgreement();
        a.member = member;
        a.agreementType = type;
        a.agreed = agreed;
        a.agreedAt = agreed ? LocalDateTime.now() : null;
        return a;
    }

    void update(boolean agreed) {
        this.agreed = agreed;
        this.agreedAt = agreed ? LocalDateTime.now() : null;
    }
}
