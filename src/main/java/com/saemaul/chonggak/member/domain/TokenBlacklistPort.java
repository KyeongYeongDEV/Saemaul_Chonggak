package com.saemaul.chonggak.member.domain;

/**
 * AT 블랙리스트 저장소 포트 (Hexagonal Architecture).
 * Application 레이어는 이 인터페이스에만 의존하며, 실제 구현(Redis 등)은 infra 레이어에서 담당한다.
 */
public interface TokenBlacklistPort {
    void add(String jti, long remainingSeconds);
    boolean isBlacklisted(String jti);
}
