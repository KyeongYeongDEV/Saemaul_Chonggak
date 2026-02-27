package com.saemaul.chonggak;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class SaemaulChonggakApplication {

    public static void main(String[] args) {
        SpringApplication.run(SaemaulChonggakApplication.class, args);
    }
}
