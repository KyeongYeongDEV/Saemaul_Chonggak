package com.saemaul.chonggak.product.presentation;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.saemaul.chonggak.product.application.ProductService;
import com.saemaul.chonggak.product.application.dto.BannerResult;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.BDDMockito.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(AdminBannerController.class)
@ActiveProfiles("test")
@DisplayName("AdminBannerController 테스트")
class AdminBannerControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;
    @MockBean ProductService productService;

    private BannerResult sampleBannerResult() {
        return new BannerResult(1L, "메인 배너", "http://img.jpg", "http://link", 1);
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("배너 등록 → 200")
    void createBanner_success() throws Exception {
        given(productService.createBanner(any())).willReturn(sampleBannerResult());

        mockMvc.perform(post("/admin/v1/banners")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "title", "메인 배너",
                                "imageUrl", "http://img.jpg",
                                "linkUrl", "http://link",
                                "displayOrder", 1
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"))
                .andExpect(jsonPath("$.data.title").value("메인 배너"));
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("배너 수정 → 200")
    void updateBanner_success() throws Exception {
        given(productService.updateBanner(anyLong(), any())).willReturn(sampleBannerResult());

        mockMvc.perform(put("/admin/v1/banners/1")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "title", "메인 배너",
                                "imageUrl", "http://img.jpg",
                                "linkUrl", "http://link",
                                "displayOrder", 1
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.title").value("메인 배너"));
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("배너 비활성화 → 200")
    void deactivateBanner_success() throws Exception {
        willDoNothing().given(productService).deactivateBanner(1L);

        mockMvc.perform(delete("/admin/v1/banners/1").with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"));
    }
}
