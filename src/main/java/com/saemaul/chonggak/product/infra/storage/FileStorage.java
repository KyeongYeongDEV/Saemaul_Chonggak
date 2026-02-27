package com.saemaul.chonggak.product.infra.storage;

public interface FileStorage {
    String upload(String folder, String filename, byte[] data, String contentType);
    void delete(String fileUrl);
}
