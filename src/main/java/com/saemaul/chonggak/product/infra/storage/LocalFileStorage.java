package com.saemaul.chonggak.product.infra.storage;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Slf4j
@Component
@Profile({"local", "test"})
public class LocalFileStorage implements FileStorage {

    @Value("${file.upload-dir:./uploads}")
    private String uploadDir;

    @Override
    public String upload(String folder, String filename, byte[] data, String contentType) {
        try {
            Path dir = Paths.get(uploadDir, folder);
            Files.createDirectories(dir);
            Path filePath = dir.resolve(filename);
            Files.write(filePath, data);
            log.info("[LocalFileStorage] 파일 저장: {}", filePath);
            return "/files/" + folder + "/" + filename;
        } catch (IOException e) {
            throw new RuntimeException("파일 저장 실패: " + filename, e);
        }
    }

    @Override
    public void delete(String fileUrl) {
        try {
            String relativePath = fileUrl.replaceFirst("^/files/", "");
            Path filePath = Paths.get(uploadDir, relativePath);
            Files.deleteIfExists(filePath);
            log.info("[LocalFileStorage] 파일 삭제: {}", filePath);
        } catch (IOException e) {
            log.warn("[LocalFileStorage] 파일 삭제 실패: {}", fileUrl, e);
        }
    }
}
