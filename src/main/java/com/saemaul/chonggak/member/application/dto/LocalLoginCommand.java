package com.saemaul.chonggak.member.application.dto;

public record LocalLoginCommand(String email, String password, String deviceId) {
}
