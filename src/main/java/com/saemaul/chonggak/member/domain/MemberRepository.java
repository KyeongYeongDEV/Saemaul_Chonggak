package com.saemaul.chonggak.member.domain;

import com.saemaul.chonggak.member.domain.vo.OAuthProvider;

import java.util.Optional;

public interface MemberRepository {

    Member save(Member member);

    Optional<Member> findById(Long id);

    Optional<Member> findByEmail(String email);

    Optional<Member> findByOAuthProviderAndOAuthId(OAuthProvider provider, String oauthId);

    boolean existsByEmail(String email);
}
