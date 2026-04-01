import React, { useRef, useState } from 'react';
import {
  View, Text, ScrollView, Image, TouchableOpacity,
  StyleSheet, Dimensions, NativeSyntheticEvent, NativeScrollEvent,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { HomeStackParamList } from '../../navigation/types';
import { colors, spacing, fontSize, borderRadius, shadow } from '../../utils/theme';
import { formatPrice, formatCountdown } from '../../utils/format';
import { useBanners, useTimeSale, useProductList, useCategories } from '../../hooks/useProducts';
import Loading from '../../components/common/Loading';
import ProductCard from '../../components/product/ProductCard';

type Nav = NativeStackNavigationProp<HomeStackParamList, 'Home'>;
const { width } = Dimensions.get('window');

const CATEGORY_ICONS: Record<string, string> = {
  '상추 모종': '🥬',
  '토마토 모종': '🍅',
  '고추·가지 모종': '🌶️',
  '오이·호박 모종': '🥒',
  '허브 모종': '🌿',
  '딸기 모종': '🍓',
  '배추·무 모종': '🥦',
  '파·양파 모종': '🧅',
  '화훼 모종': '🌸',
  '원예용품': '🪴',
  '농업용 비료': '🌱',
  '씨앗': '🌾',
  '과채 모종': '🍆',
  '산나물 모종': '🌾',
  '기타': '🌻',
};

export default function HomeScreen() {
  const navigation = useNavigation<Nav>();
  const { data: banners } = useBanners();
  const { data: timeSaleItems } = useTimeSale();
  const { data: newProducts } = useProductList({ sort: 'latest', size: 6 });
  const { data: bestProducts } = useProductList({ sort: 'latest', size: 6 });
  const { data: categories } = useCategories();
  const [bannerIndex, setBannerIndex] = useState(0);
  const bannerRef = useRef<ScrollView>(null);

  const goToDetail = (productId: number) =>
    navigation.navigate('ProductDetail', { productId });

  const goToList = (categoryId?: number) =>
    (navigation as any).getParent()?.jumpTo('ProductTab', { categoryId });

  const onBannerScroll = (e: NativeSyntheticEvent<NativeScrollEvent>) => {
    const idx = Math.round(e.nativeEvent.contentOffset.x / width);
    setBannerIndex(idx);
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>

      {/* ── 배너 ── */}
      {banners && banners.length > 0 && (
        <View style={styles.bannerWrapper}>
          <ScrollView
            ref={bannerRef}
            horizontal
            pagingEnabled
            showsHorizontalScrollIndicator={false}
            onMomentumScrollEnd={onBannerScroll}
          >
            {banners.map((banner) => (
              <View key={banner.id} style={styles.bannerItem}>
                <Image
                  source={{ uri: banner.image_url }}
                  style={styles.bannerImage}
                  resizeMode="cover"
                />
                <View style={styles.bannerOverlay}>
                  <Text style={styles.bannerTitle}>{banner.title}</Text>
                </View>
              </View>
            ))}
          </ScrollView>
          {/* dots */}
          <View style={styles.dotsRow}>
            {banners.map((_, i) => (
              <View
                key={i}
                style={[styles.dot, i === bannerIndex && styles.dotActive]}
              />
            ))}
          </View>
        </View>
      )}

      {/* ── 카테고리 ── */}
      {categories && categories.length > 0 && (
        <View style={styles.categorySection}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.categoryList}>
            {categories.map((cat) => (
              <TouchableOpacity
                key={cat.id}
                style={styles.categoryItem}
                onPress={() => goToList(cat.id)}
                activeOpacity={0.75}
              >
                <View style={styles.categoryIconBox}>
                  <Text style={styles.categoryIcon}>
                    {CATEGORY_ICONS[cat.name] ?? '🌱'}
                  </Text>
                </View>
                <Text style={styles.categoryName} numberOfLines={2}>{cat.name}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* ── 타임세일 ── */}
      {timeSaleItems && timeSaleItems.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitleRow}>
              <View style={styles.sectionAccent} />
              <Text style={styles.sectionTitle}>타임세일</Text>
            </View>
            {timeSaleItems[0].time_sale_end && (
              <View style={styles.countdownBadge}>
                <Text style={styles.countdownText}>
                  {formatCountdown(timeSaleItems[0].time_sale_end)}
                </Text>
              </View>
            )}
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.horizontalList}
          >
            {timeSaleItems.map((product) => (
              <TouchableOpacity
                key={product.id}
                style={styles.timeSaleCard}
                onPress={() => goToDetail(product.id)}
                activeOpacity={0.85}
              >
                {product.thumbnail_url ? (
                  <Image
                    source={{ uri: product.thumbnail_url }}
                    style={styles.timeSaleImage}
                    resizeMode="cover"
                  />
                ) : (
                  <View style={[styles.timeSaleImage, styles.imageFallback]}>
                    <Text style={{ fontSize: 32 }}>🌱</Text>
                  </View>
                )}
                <View style={styles.timeSaleBadgeAbsolute}>
                  <Text style={styles.timeSaleBadgeText}>SALE</Text>
                </View>
                <View style={styles.timeSaleInfo}>
                  <Text style={styles.timeSaleName} numberOfLines={1}>{product.name}</Text>
                  <Text style={styles.timeSalePrice}>
                    {formatPrice(product.time_sale_price ?? product.price)}
                  </Text>
                  {product.price !== (product.time_sale_price ?? product.price) && (
                    <Text style={styles.timeSaleOriginal}>{formatPrice(product.price)}</Text>
                  )}
                </View>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* ── 지금 심기 딱 좋은 모종 ── */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={styles.sectionTitleRow}>
            <View style={styles.sectionAccent} />
            <Text style={styles.sectionTitle}>지금 심기 딱 좋은 모종</Text>
          </View>
          <TouchableOpacity onPress={() => goToList()}>
            <Text style={styles.sectionMore}>더보기 ›</Text>
          </TouchableOpacity>
        </View>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.horizontalList}
        >
          {newProducts?.items.slice(0, 5).map((product) => (
            <TouchableOpacity
              key={product.id}
              style={styles.horizontalCard}
              onPress={() => goToDetail(product.id)}
              activeOpacity={0.85}
            >
              {product.thumbnail_url ? (
                <Image
                  source={{ uri: product.thumbnail_url }}
                  style={styles.horizontalImage}
                  resizeMode="cover"
                />
              ) : (
                <View style={[styles.horizontalImage, styles.imageFallback]}>
                  <Text style={{ fontSize: 28 }}>🌱</Text>
                </View>
              )}
              <View style={styles.horizontalInfo}>
                <Text style={styles.horizontalName} numberOfLines={2}>{product.name}</Text>
                <Text style={styles.horizontalPrice}>{formatPrice(product.sale_price ?? product.price)}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* ── 베스트셀러 ── */}
      <View style={[styles.section, styles.sectionGreen]}>
        <View style={styles.sectionHeader}>
          <View style={styles.sectionTitleRow}>
            <View style={[styles.sectionAccent, { backgroundColor: '#fff' }]} />
            <Text style={[styles.sectionTitle, { color: '#fff' }]}>베스트셀러</Text>
          </View>
          <TouchableOpacity onPress={() => goToList()}>
            <Text style={[styles.sectionMore, { color: 'rgba(255,255,255,0.8)' }]}>더보기 ›</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.gridWrap}>
          {bestProducts?.items.slice(0, 4).map((product) => (
            <View key={product.id} style={styles.gridCol}>
              <ProductCard product={product} onPress={() => goToDetail(product.id)} />
            </View>
          ))}
        </View>
      </View>

      {/* ── 신상품 ── */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <View style={styles.sectionTitleRow}>
            <View style={styles.sectionAccent} />
            <Text style={styles.sectionTitle}>신상품</Text>
          </View>
          <TouchableOpacity onPress={() => goToList()}>
            <Text style={styles.sectionMore}>더보기 ›</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.gridWrap}>
          {newProducts?.items.map((product) => (
            <View key={product.id} style={styles.gridCol}>
              <ProductCard product={product} onPress={() => goToDetail(product.id)} />
            </View>
          ))}
        </View>
      </View>

      <View style={{ height: spacing.xl }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },

  /* 배너 */
  bannerWrapper: { position: 'relative' },
  bannerItem: { width, height: 220 },
  bannerImage: { width: '100%', height: '100%' },
  bannerOverlay: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    paddingHorizontal: spacing.lg, paddingVertical: spacing.md,
    backgroundColor: 'rgba(0,0,0,0.28)',
  },
  bannerTitle: {
    color: '#fff', fontSize: fontSize.xl, fontWeight: 'bold',
  },
  dotsRow: {
    flexDirection: 'row', justifyContent: 'center',
    paddingVertical: spacing.sm, gap: 6,
    backgroundColor: colors.surface,
  },
  dot: {
    width: 7, height: 7, borderRadius: 4,
    backgroundColor: colors.border,
  },
  dotActive: {
    width: 18, backgroundColor: colors.primary,
  },

  /* 카테고리 */
  categorySection: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.divider,
  },
  categoryList: { paddingHorizontal: spacing.md, gap: spacing.md },
  categoryItem: { alignItems: 'center', width: 64 },
  categoryIconBox: {
    width: 52, height: 52,
    borderRadius: 26,
    backgroundColor: '#f0f8f2',
    alignItems: 'center', justifyContent: 'center',
    marginBottom: spacing.xs,
    borderWidth: 1,
    borderColor: '#d4edd9',
  },
  categoryIcon: { fontSize: 24 },
  categoryName: {
    fontSize: 11, color: colors.text,
    textAlign: 'center', lineHeight: 15,
  },

  /* 섹션 공통 */
  section: {
    paddingTop: spacing.lg,
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.md,
    backgroundColor: colors.surface,
    marginBottom: spacing.sm,
  },
  sectionGreen: {
    backgroundColor: colors.primary,
  },
  sectionHeader: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: spacing.md,
  },
  sectionTitleRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  sectionAccent: {
    width: 4, height: 20, borderRadius: 2,
    backgroundColor: colors.primary,
  },
  sectionTitle: {
    fontSize: fontSize.lg, fontWeight: '700', color: colors.text,
  },
  sectionMore: {
    fontSize: fontSize.sm, color: colors.textSecondary,
  },

  /* 가로 스크롤 리스트 */
  horizontalList: { paddingRight: spacing.md, gap: spacing.sm },

  /* 타임세일 카드 */
  timeSaleCard: {
    width: 140,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    overflow: 'hidden',
    ...shadow.sm,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  timeSaleImage: { width: 140, height: 140 },
  imageFallback: {
    backgroundColor: colors.divider,
    alignItems: 'center', justifyContent: 'center',
  },
  timeSaleBadgeAbsolute: {
    position: 'absolute', top: spacing.xs, left: spacing.xs,
    backgroundColor: colors.timeSale,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.sm, paddingVertical: 2,
  },
  timeSaleBadgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  timeSaleInfo: { padding: spacing.sm },
  timeSaleName: { fontSize: fontSize.xs, color: colors.text, marginBottom: 2 },
  timeSalePrice: { fontSize: fontSize.sm, fontWeight: 'bold', color: colors.timeSale },
  timeSaleOriginal: {
    fontSize: 10, color: colors.textDisabled,
    textDecorationLine: 'line-through', marginTop: 1,
  },

  /* 가로 스크롤 상품 카드 */
  horizontalCard: {
    width: 130,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    overflow: 'hidden',
    ...shadow.sm,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  horizontalImage: { width: 130, height: 130 },
  horizontalInfo: { padding: spacing.sm },
  horizontalName: { fontSize: fontSize.xs, color: colors.text, marginBottom: 4, lineHeight: 16 },
  horizontalPrice: { fontSize: fontSize.sm, fontWeight: 'bold', color: colors.text },

  /* 그리드 */
  gridWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  gridCol: { width: '48.5%' },
});
