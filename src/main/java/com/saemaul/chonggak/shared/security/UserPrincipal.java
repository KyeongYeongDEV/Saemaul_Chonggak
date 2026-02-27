package com.saemaul.chonggak.shared.security;

import com.saemaul.chonggak.member.domain.vo.MemberRole;
import lombok.Getter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;

@Getter
public class UserPrincipal implements UserDetails {

    private final Long userId;
    private final MemberRole role;
    private final String jti;

    public UserPrincipal(Long userId, MemberRole role, String jti) {
        this.userId = userId;
        this.role = role;
        this.jti = jti;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_" + role.name()));
    }

    @Override
    public String getPassword() { return null; }

    @Override
    public String getUsername() { return String.valueOf(userId); }
}
