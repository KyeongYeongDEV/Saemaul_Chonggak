package com.saemaul.chonggak.member.application;

import com.saemaul.chonggak.member.application.dto.LocalLoginCommand;
import com.saemaul.chonggak.member.application.dto.TokenPair;
import com.saemaul.chonggak.member.domain.Member;
import com.saemaul.chonggak.member.domain.MemberRepository;
import com.saemaul.chonggak.member.domain.RefreshTokenPort;
import com.saemaul.chonggak.member.domain.TokenBlacklistPort;
import com.saemaul.chonggak.shared.exception.BusinessException;
import com.saemaul.chonggak.shared.exception.ErrorCode;
import com.saemaul.chonggak.shared.security.JwtProvider;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final MemberRepository memberRepository;
    private final RefreshTokenPort refreshTokenPort;
    private final TokenBlacklistPort tokenBlacklistPort;
    private final JwtProvider jwtProvider;
    private final PasswordEncoder passwordEncoder;

    /**
     * 로컬 이메일/비밀번호 로그인 (개발 환경용)
     */
    @Transactional(readOnly = true)
    public TokenPair localLogin(LocalLoginCommand command) {
        Member member = memberRepository.findByEmail(command.email())
                .orElseThrow(() -> new BusinessException(ErrorCode.INVALID_CREDENTIALS));

        if (!passwordEncoder.matches(command.password(), member.getPassword())) {
            throw new BusinessException(ErrorCode.INVALID_CREDENTIALS);
        }

        if (!member.isActive()) {
            if (member.getStatus().name().equals("SUSPENDED")) {
                throw new BusinessException(ErrorCode.MEMBER_SUSPENDED);
            }
            throw new BusinessException(ErrorCode.MEMBER_NOT_FOUND);
        }

        return issueTokenPair(member, command.deviceId());
    }

    /**
     * Refresh Token으로 Access Token 재발급 (RT Rotation)
     */
    @Transactional
    public TokenPair reissue(String refreshToken, Long userId, String deviceId) {
        String stored = refreshTokenPort.find(userId, deviceId)
                .orElseThrow(() -> new BusinessException(ErrorCode.INVALID_REFRESH_TOKEN));

        if (!stored.equals(refreshToken)) {
            // RT 불일치 → 탈취 의심 → 전체 RT 삭제
            refreshTokenPort.deleteAll(userId);
            throw new BusinessException(ErrorCode.INVALID_REFRESH_TOKEN);
        }

        Member member = memberRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.MEMBER_NOT_FOUND));

        if (!member.isActive()) {
            throw new BusinessException(ErrorCode.MEMBER_SUSPENDED);
        }

        // 기존 RT 삭제 후 새 토큰 발급
        refreshTokenPort.delete(userId, deviceId);
        return issueTokenPair(member, deviceId);
    }

    /**
     * 로그아웃: AT 블랙리스트 등록 + RT 삭제
     */
    @Transactional
    public void logout(String accessToken, Long userId, String deviceId) {
        Claims claims = jwtProvider.parseIgnoreExpiry(accessToken);
        String jti = claims.getId();
        long remainingSeconds = jwtProvider.getRemainingSeconds(claims);

        tokenBlacklistPort.add(jti, remainingSeconds);
        refreshTokenPort.delete(userId, deviceId);
    }

    private TokenPair issueTokenPair(Member member, String deviceId) {
        String accessToken = jwtProvider.createAccessToken(member.getId(), member.getRole());
        String refreshToken = UUID.randomUUID().toString();
        refreshTokenPort.save(member.getId(), deviceId, refreshToken);
        return new TokenPair(accessToken, refreshToken);
    }
}
