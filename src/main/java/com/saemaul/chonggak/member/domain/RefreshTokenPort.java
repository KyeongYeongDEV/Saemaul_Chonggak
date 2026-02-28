package com.saemaul.chonggak.member.domain;

import java.util.Optional;

/**
 * Refresh Token 저장소 포트 (Hexagonal Architecture).
 * Application 레이어는 이 인터페이스에만 의존하며, 실제 구현(Redis 등)은 infra 레이어에서 담당한다.
 */
public interface RefreshTokenPort {
    void save(Long userId, String deviceId, String token);
    Optional<String> find(Long userId, String deviceId);
    void delete(Long userId, String deviceId);
    void deleteAll(Long userId);
}
