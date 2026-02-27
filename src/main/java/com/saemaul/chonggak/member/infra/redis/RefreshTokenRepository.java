package com.saemaul.chonggak.member.infra.redis;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.util.Optional;
import java.util.Set;

@Repository
@RequiredArgsConstructor
public class RefreshTokenRepository {

    private static final String PREFIX = "refresh:";
    private static final Duration TTL = Duration.ofDays(7);

    private final StringRedisTemplate redisTemplate;

    private String key(Long userId, String deviceId) {
        return PREFIX + userId + ":" + deviceId;
    }

    public void save(Long userId, String deviceId, String token) {
        redisTemplate.opsForValue().set(key(userId, deviceId), token, TTL);
    }

    public Optional<String> find(Long userId, String deviceId) {
        return Optional.ofNullable(redisTemplate.opsForValue().get(key(userId, deviceId)));
    }

    public void delete(Long userId, String deviceId) {
        redisTemplate.delete(key(userId, deviceId));
    }

    /** 전체 기기 강제 로그아웃 */
    public void deleteAll(Long userId) {
        Set<String> keys = redisTemplate.keys(PREFIX + userId + ":*");
        if (keys != null && !keys.isEmpty()) {
            redisTemplate.delete(keys);
        }
    }
}
