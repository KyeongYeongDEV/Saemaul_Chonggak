package com.saemaul.chonggak.member.infra.redis;

import com.saemaul.chonggak.member.domain.TokenBlacklistPort;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;

@Repository
@RequiredArgsConstructor
public class BlacklistRepository implements TokenBlacklistPort {

    private static final String PREFIX = "blacklist:";

    private final StringRedisTemplate redisTemplate;

    public void add(String jti, long remainingSeconds) {
        if (remainingSeconds > 0) {
            redisTemplate.opsForValue().set(PREFIX + jti, "logout", Duration.ofSeconds(remainingSeconds));
        }
    }

    public boolean isBlacklisted(String jti) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(PREFIX + jti));
    }
}
