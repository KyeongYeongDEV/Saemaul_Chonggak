# 관리자 웹 규칙 (React + Vite + Ant Design)

## UI 컴포넌트
- Ant Design 컴포넌트 최우선 사용
- 커스텀 컴포넌트는 Ant Design으로 해결 안 될 때만

## API
- `back/` 서버와 동일 FastAPI 사용 (`/api/v1/admin/*`)
- 관리자 전용 엔드포인트는 `/admin/` prefix 필수

## 배포
- Vercel 자동 배포 (`vercel.json` 설정 유지)
- 환경변수: `VITE_API_BASE_URL` (Vercel 대시보드에서 관리)

## 빌드
- `npm run build` → `dist/` 폴더

## 주요 페이지 위치

```
pages/
  Dashboard.tsx      ← MAU/매출/주문 현황
  Orders/
    OrderList.tsx    ← 기간별 주문 조회 (DateRangePicker + Table)
    OrderDetail.tsx  ← 주문 상세 + 상태 변경
  Products/
    ProductList.tsx
    ProductForm.tsx
  Users/
    UserList.tsx
```

## 관리자 권한 주의
- 관리자 API 호출 시 JWT 토큰 자동 포함 (axios interceptor)
- 403 응답 시 로그인 페이지로 리다이렉트
