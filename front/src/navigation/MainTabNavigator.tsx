import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import type {
  MainTabParamList,
  HomeStackParamList,
  ProductStackParamList,
  CartStackParamList,
  MyPageStackParamList,
} from './types';
import { colors } from '../utils/theme';
import { useCartStore } from '../store/useCartStore';

// Screens
import HomeScreen from '../screens/Home/HomeScreen';
import ProductListScreen from '../screens/Product/ProductListScreen';
import ProductDetailScreen from '../screens/Product/ProductDetailScreen';
import SearchScreen from '../screens/Product/SearchScreen';
import CartScreen from '../screens/Cart/CartScreen';
import CheckoutScreen from '../screens/Order/CheckoutScreen';
import OrderCompleteScreen from '../screens/Order/OrderCompleteScreen';
import MyPageScreen from '../screens/MyPage/MyPageScreen';
import OrderListScreen from '../screens/Order/OrderListScreen';
import OrderDetailScreen from '../screens/Order/OrderDetailScreen';
import AddressScreen from '../screens/MyPage/AddressScreen';
import CouponScreen from '../screens/MyPage/CouponScreen';
import PointScreen from '../screens/MyPage/PointScreen';
import SettingsScreen from '../screens/MyPage/SettingsScreen';
import ReviewFormScreen from '../screens/CS/ReviewFormScreen';
import InquiryListScreen from '../screens/CS/InquiryListScreen';
import InquiryFormScreen from '../screens/CS/InquiryFormScreen';
import FaqScreen from '../screens/CS/FaqScreen';
import NoticeScreen from '../screens/CS/NoticeScreen';

const Tab = createBottomTabNavigator<MainTabParamList>();
const HomeStack = createNativeStackNavigator<HomeStackParamList>();
const ProductStack = createNativeStackNavigator<ProductStackParamList>();
const CartStack = createNativeStackNavigator<CartStackParamList>();
const MyPageStack = createNativeStackNavigator<MyPageStackParamList>();

function HomeStackNav() {
  return (
    <HomeStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.primary },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <HomeStack.Screen
        name="Home"
        component={HomeScreen}
        options={({ navigation }) => ({
          title: '새마을총각',
          headerRight: () => (
            <TouchableOpacity
              onPress={() => (navigation as any).getParent()?.jumpTo('ProductTab', { screen: 'Search' })}
              style={{ marginRight: 4 }}
            >
              <Text style={{ fontSize: 22 }}>🔍</Text>
            </TouchableOpacity>
          ),
        })}
      />
      <HomeStack.Screen name="ProductDetail" component={ProductDetailScreen} options={{ title: '상품 상세' }} />
    </HomeStack.Navigator>
  );
}

function ProductStackNav() {
  return (
    <ProductStack.Navigator>
      <ProductStack.Screen name="ProductList" component={ProductListScreen} options={{ title: '상품' }} />
      <ProductStack.Screen name="ProductDetail" component={ProductDetailScreen} options={{ title: '상품 상세' }} />
      <ProductStack.Screen name="Search" component={SearchScreen} options={{ title: '검색' }} />
    </ProductStack.Navigator>
  );
}

function CartStackNav() {
  return (
    <CartStack.Navigator>
      <CartStack.Screen name="Cart" component={CartScreen} options={{ title: '장바구니' }} />
      <CartStack.Screen name="Checkout" component={CheckoutScreen} options={{ title: '주문서 작성' }} />
      <CartStack.Screen name="OrderComplete" component={OrderCompleteScreen} options={{ headerShown: false }} />
    </CartStack.Navigator>
  );
}

function MyPageStackNav() {
  return (
    <MyPageStack.Navigator>
      <MyPageStack.Screen name="MyPage" component={MyPageScreen} options={{ title: '마이페이지' }} />
      <MyPageStack.Screen name="OrderList" component={OrderListScreen} options={{ title: '주문 내역' }} />
      <MyPageStack.Screen name="OrderDetail" component={OrderDetailScreen} options={{ title: '주문 상세' }} />
      <MyPageStack.Screen name="Address" component={AddressScreen} options={{ title: '배송지 관리' }} />
      <MyPageStack.Screen name="Coupon" component={CouponScreen} options={{ title: '쿠폰함' }} />
      <MyPageStack.Screen name="Point" component={PointScreen} options={{ title: '적립금' }} />
      <MyPageStack.Screen name="ReviewForm" component={ReviewFormScreen} options={{ title: '리뷰 작성' }} />
      <MyPageStack.Screen name="InquiryList" component={InquiryListScreen} options={{ title: '1:1 문의' }} />
      <MyPageStack.Screen name="InquiryForm" component={InquiryFormScreen} options={{ title: '문의 작성' }} />
      <MyPageStack.Screen name="Faq" component={FaqScreen} options={{ title: 'FAQ' }} />
      <MyPageStack.Screen name="Notice" component={NoticeScreen} options={{ title: '공지사항' }} />
      <MyPageStack.Screen name="Settings" component={SettingsScreen} options={{ title: '설정' }} />
    </MyPageStack.Navigator>
  );
}

function CartTabIcon({ focused }: { focused: boolean }) {
  const itemCount = useCartStore((s) => s.itemCount);
  return (
    <View>
      <Text style={{ fontSize: 22 }}>{focused ? '🛒' : '🛒'}</Text>
      {itemCount > 0 && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{itemCount > 99 ? '99+' : itemCount}</Text>
        </View>
      )}
    </View>
  );
}

export default function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          borderTopWidth: 1,
          borderTopColor: colors.divider,
          height: 58,
          paddingBottom: 6,
          paddingTop: 4,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: '500' },
        headerShown: false,
      }}
    >
      <Tab.Screen
        name="HomeTab"
        component={HomeStackNav}
        options={{
          tabBarLabel: '홈',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ fontSize: size, color }}>🏠</Text>
          ),
        }}
      />
      <Tab.Screen
        name="ProductTab"
        component={ProductStackNav}
        options={{
          tabBarLabel: '상품',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ fontSize: size, color }}>🌿</Text>
          ),
        }}
      />
      <Tab.Screen
        name="CartTab"
        component={CartStackNav}
        options={{
          tabBarLabel: '장바구니',
          tabBarIcon: ({ focused }) => <CartTabIcon focused={focused} />,
        }}
      />
      <Tab.Screen
        name="MyPageTab"
        component={MyPageStackNav}
        options={{
          tabBarLabel: '마이페이지',
          tabBarIcon: ({ color, size }) => (
            <Text style={{ fontSize: size, color }}>👤</Text>
          ),
        }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  badge: {
    position: 'absolute',
    top: -4,
    right: -8,
    backgroundColor: colors.secondary,
    borderRadius: 9999,
    minWidth: 18,
    height: 18,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 3,
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
});
