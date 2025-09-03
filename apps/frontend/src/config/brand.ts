/**
 * Another Doctor Brand Configuration
 * Design tokens and branding constants extracted from https://another.doctor
 */

export const brandColors = {
  // Primary brand colors
  primary: {
    teal: '#287a7d',
    coral: '#eb7d68',
  },
  
  // Text colors
  text: {
    dark: '#1a1a1a',
    gray: '#6b7280',
    light: '#9ca3af',
  },
  
  // Background colors
  background: {
    light: '#f8fafb',
    white: '#ffffff',
    gradient: {
      from: '#f0f9ff',
      to: '#fef3f2',
    },
  },
  
  // Semantic colors
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
} as const;

export const brandTypography = {
  // Font families
  fonts: {
    primary: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    mono: ['SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'monospace'],
  },
  
  // Font sizes
  sizes: {
    xs: '0.75rem',     // 12px
    sm: '0.875rem',    // 14px
    base: '1rem',      // 16px
    lg: '1.125rem',    // 18px
    xl: '1.25rem',     // 20px
    '2xl': '1.5rem',   // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
  },
  
  // Line heights
  lineHeights: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.6',
    loose: '2',
  },
  
  // Font weights
  weights: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
} as const;

export const brandSpacing = {
  // Container max widths
  container: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1200px',
  },
  
  // Common spacing values
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
  },
} as const;

export const brandComponents = {
  // Button variants
  button: {
    primary: {
      bg: brandColors.primary.teal,
      text: brandColors.background.white,
      hover: '#1e6b6e', // Darker teal
    },
    secondary: {
      bg: brandColors.primary.coral,
      text: brandColors.background.white,
      hover: '#d66b56', // Darker coral
    },
    outline: {
      bg: 'transparent',
      text: brandColors.primary.teal,
      border: brandColors.primary.teal,
      hover: brandColors.primary.teal,
    },
  },
  
  // Card styles
  card: {
    bg: brandColors.background.white,
    border: '#e5e7eb',
    shadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    shadowHover: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  },
  
  // Navigation
  nav: {
    height: '4rem', // 64px
    logoHeight: '45px',
    bg: brandColors.background.white,
    borderBottom: '#e5e7eb',
  },
} as const;

export const brandAssets = {
  // Logo paths
  logo: {
    primary: '/another-doctor-logo.png',
    concept: '/another-doctor-concept.pdf',
    mediaKit: '/another-doctor-media-kit.png',
  },
  
  // Logo dimensions
  logoSizes: {
    nav: { width: 'auto', height: '45px' },
    hero: { width: 'auto', height: '60px' },
    footer: { width: 'auto', height: '36px' },
  },
} as const;

export const brandAnimations = {
  // Transition durations
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },
  
  // Easing functions
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

// Export as default brand config
export const brand = {
  colors: brandColors,
  typography: brandTypography,
  spacing: brandSpacing,
  components: brandComponents,
  assets: brandAssets,
  animations: brandAnimations,
} as const;

export default brand;