import { useState, useEffect } from 'react'

/* ── Breakpoints (must match responsive.css) ── */
export const BP = {
  sm:  480,
  md:  768,
  lg: 1024,
}

/**
 * Returns the current window width, updated on resize.
 * Debounced by one animation frame to avoid excessive re-renders.
 */
export function useWindowWidth() {
  const [width, setWidth] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth : BP.lg
  )

  useEffect(() => {
    let raf = null

    const handler = () => {
      if (raf) cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => setWidth(window.innerWidth))
    }

    window.addEventListener('resize', handler)
    return () => {
      window.removeEventListener('resize', handler)
      if (raf) cancelAnimationFrame(raf)
    }
  }, [])

  return width
}

/**
 * Convenience booleans for the most common breakpoint checks.
 *
 * Usage:
 *   const { isMobile, isTablet, isDesktop } = useIsMobile()
 *
 *   isMobile  → true when width < 768  (phones)
 *   isTablet  → true when width < 1024 (tablets + phones)
 *   isDesktop → true when width >= 1024
 *   isSmall   → true when width < 480  (small phones)
 */
export function useIsMobile() {
  const width = useWindowWidth()

  return {
    width,
    isSmall:   width < BP.sm,   // < 480px
    isMobile:  width < BP.md,   // < 768px  ← most common check
    isTablet:  width < BP.lg,   // < 1024px
    isDesktop: width >= BP.lg,  // >= 1024px
  }
}

/**
 * Returns a value based on screen size.
 * Useful for picking between two inline-style values.
 *
 * Usage:
 *   const padding = useResponsiveValue({ mobile: 12, desktop: 24 })
 *   const cols    = useResponsiveValue({ mobile: 1, tablet: 2, desktop: 3 })
 */
export function useResponsiveValue({ mobile, tablet, desktop }) {
  const { isDesktop, isMobile } = useIsMobile()

  if (isDesktop && desktop !== undefined) return desktop
  if (!isMobile  && tablet  !== undefined) return tablet
  return mobile
}