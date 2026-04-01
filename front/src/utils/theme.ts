export const colors = {
  primary: '#0b5a2c',
  primaryLight: '#1a7a3e',
  primaryDark: '#073d1e',
  secondary: '#FF6B35',
  secondaryLight: '#FF8A65',
  background: '#F5F5F5',
  surface: '#FFFFFF',
  text: '#1A1A1A',
  textSecondary: '#666666',
  textDisabled: '#BBBBBB',
  border: '#E0E0E0',
  divider: '#F0F0F0',
  error: '#D32F2F',
  success: '#388E3C',
  warning: '#F57C00',
  info: '#1976D2',
  overlay: 'rgba(0, 0, 0, 0.5)',
  timeSale: '#E53935',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const fontSize = {
  xs: 11,
  sm: 13,
  md: 15,
  lg: 17,
  xl: 20,
  xxl: 24,
  title: 28,
} as const;

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
} as const;

export const shadow = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 4,
    elevation: 4,
  },
} as const;
