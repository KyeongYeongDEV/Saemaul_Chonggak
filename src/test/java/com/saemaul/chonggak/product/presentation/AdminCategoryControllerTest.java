package com.saemaul.chonggak.product.presentation;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.saemaul.chonggak.product.application.ProductService;
import com.saemaul.chonggak.product.application.dto.CategoryResult;
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

@WebMvcTest(AdminCategoryController.class)
@ActiveProfiles("test")
@DisplayName("AdminCategoryController 테스트")
class AdminCategoryControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;
    @MockBean ProductService productService;

    private CategoryResult sampleCategoryResult() {
        return new CategoryResult(1L, "전자기기", "전자기기 카테고리", null, 1);
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("카테고리 등록 → 200")
    void createCategory_success() throws Exception {
        given(productService.createCategory(any())).willReturn(sampleCategoryResult());

        mockMvc.perform(post("/admin/v1/categories")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "name", "전자기기",
                                "description", "전자기기 카테고리",
                                "displayOrder", 1
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"))
                .andExpect(jsonPath("$.data.name").value("전자기기"));
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("카테고리 수정 → 200")
    void updateCategory_success() throws Exception {
        given(productService.updateCategory(anyLong(), any())).willReturn(sampleCategoryResult());

        mockMvc.perform(put("/admin/v1/categories/1")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "name", "전자기기",
                                "description", "전자기기 카테고리",
                                "displayOrder", 1
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.name").value("전자기기"));
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("카테고리 삭제 → 200")
    void deleteCategory_success() throws Exception {
        willDoNothing().given(productService).deleteCategory(1L);

        mockMvc.perform(delete("/admin/v1/categories/1").with(csrf()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SUCCESS"));
    }
}
