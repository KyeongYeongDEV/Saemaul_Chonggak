package com.saemaul.chonggak.member.infra.persistence;

import com.saemaul.chonggak.member.domain.Member;
import com.saemaul.chonggak.member.domain.vo.OAuthProvider;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

interface MemberJpaRepository extends JpaRepository<Member, Long> {

    Optional<Member> findByEmail(String email);

    Optional<Member> findByOauthProviderAndOauthId(OAuthProvider oauthProvider, String oauthId);

    boolean existsByEmail(String email);
}
