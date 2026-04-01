# 프론트엔드 규칙 (React Native)

## 상태관리: Zustand
- Context API 사용 금지
- 전역 상태는 `store/` 에 도메인별 분리
- 예: `store/useCartStore.ts`, `store/useAuthStore.ts`

## API 호출: react-query
- `useQuery` / `useMutation` 사용
- 컴포넌트에서 직접 `axios.get()` 호출 금지
- 반드시 `api/` 폴더의 함수를 통해 호출

```typescript
// 금지
const res = await axios.get('/products');

// 권장
const { data } = useQuery(['products'], () => productApi.getList());
```

## API 함수 위치

```
api/
  products.ts   ← 상품 관련 API
  orders.ts     ← 주문 관련 API
  auth.ts       ← 인증 관련 API
  index.ts      ← axios 인스턴스 (baseURL, interceptor)
```

## 스타일
- `StyleSheet.create` 사용
- 인라인 스타일 최소화
- 테마 색상은 `utils/theme.ts` 에서 관리 (하드코딩 금지)

## 네비게이션
- `react-navigation` 사용
- 파라미터 타입 정의 필수 (TypeScript)

```typescript
type RootStackParamList = {
  Home: undefined;
  ProductDetail: { productId: number };
  Order: { orderId: string };
};
```

## 결제 (토스페이먼츠)
- 결제 금액을 직접 서버로 보내지 말 것
- 서버에서 생성한 `orderNo`를 TossPayments SDK에 전달
- 결제 완료 후 `paymentKey`만 서버로 전달 → 서버에서 검증

## Firebase Analytics 필수 이벤트

```typescript
// 상품 상세 진입
analytics().logViewItem({...})

// 장바구니 추가
analytics().logAddToCart({...})

// 결제 완료
analytics().logPurchase({ transaction_id: orderNo, ... })
```

## Sentry 에러 캡처
- 결제 오류는 반드시 Sentry 캡처
- `extra`에 orderId, amount 포함 (개인정보 제외)
