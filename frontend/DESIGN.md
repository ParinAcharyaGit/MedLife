---
name: Clinical Precision
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#424752'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#727784'
  outline-variant: '#c2c6d4'
  surface-tint: '#115cb9'
  primary: '#003f87'
  on-primary: '#ffffff'
  primary-container: '#0056b3'
  on-primary-container: '#bbd0ff'
  inverse-primary: '#acc7ff'
  secondary: '#006e25'
  on-secondary: '#ffffff'
  secondary-container: '#80f98b'
  on-secondary-container: '#007327'
  tertiary: '#88001c'
  on-tertiary: '#ffffff'
  tertiary-container: '#b10f2b'
  on-tertiary-container: '#ffc0bf'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d7e2ff'
  primary-fixed-dim: '#acc7ff'
  on-primary-fixed: '#001a40'
  on-primary-fixed-variant: '#004491'
  secondary-fixed: '#83fc8e'
  secondary-fixed-dim: '#66df75'
  on-secondary-fixed: '#002106'
  on-secondary-fixed-variant: '#00531a'
  tertiary-fixed: '#ffdad9'
  tertiary-fixed-dim: '#ffb3b2'
  on-tertiary-fixed: '#410008'
  on-tertiary-fixed-variant: '#92001f'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
  headline-md-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 0.25rem
  sm: 0.5rem
  md: 1rem
  lg: 1.5rem
  xl: 2.5rem
  gutter: 1rem
  margin-mobile: 1rem
  margin-desktop: 2rem
---

## Brand & Style

This design system is engineered for high-stakes medical environments where clarity, speed of recognition, and trust are paramount. The brand personality is **authoritative yet accessible**, leaning into a **Modern Corporate** aesthetic with a strong emphasis on **Minimalism**. 

The UI prioritizes "information density without clutter," utilizing generous whitespace to reduce cognitive load during inventory audits. The emotional response should be one of calm reliability—ensuring that healthcare professionals feel the system is a silent, efficient partner in patient care. Visual flourishes are stripped away in favor of functional clarity, using subtle structural lines and a disciplined color application to guide the user's eye to critical data points.

## Colors

The palette is rooted in clinical standards to ensure instant semantic recognition.
- **Primary (#0056b3):** Used for primary actions, navigation states, and brand presence. It conveys stability and professional trust.
- **Success (#28a745):** Specifically reserved for "In Stock" indicators, completed shipments, and positive system confirmations.
- **Warning/Danger (#dc3545):** Utilized exclusively for low-stock alerts, expired medication warnings, and critical system errors.
- **Neutral (#f8f9fa):** A range of cool grays used for backgrounds and subtle borders to maintain a clean, sterile environment that prevents eye fatigue.

Color should be used sparingly: backgrounds remain predominantly white (#FFFFFF) to maximize contrast and readability.

## Typography

**Inter** is selected for its exceptional legibility in data-heavy contexts and its neutral, systematic tone. 
- **Headlines:** Use semi-bold weights with slight negative letter spacing to create a sturdy, professional appearance.
- **Body:** Standardized at 14px for density, ensuring large tables remain readable.
- **Labels:** Uppercase styles are used for table headers and category tags to differentiate metadata from primary content.
- **Numerical Data:** Tabular numerals should be enabled where possible to ensure that quantities and SKU numbers align perfectly in vertical lists.

## Layout & Spacing

This design system utilizes a **Fixed Grid** philosophy for the main content area (max-width: 1440px) to ensure consistent data scanning patterns on wide medical monitors.
- **Grid:** A 12-column system with 16px (1rem) gutters.
- **Spacing Rhythm:** Based on a 4px baseline. Most internal padding for cards and containers should utilize `md` (16px) or `lg` (24px).
- **Mobile Adaptivity:** On devices smaller than 768px, the layout collapses to a single column with 16px side margins. Data tables should transition to a "card-list" format to maintain legibility of SKU details and expiration dates.

## Elevation & Depth

To maintain a "clinical" and "organized" feel, the system avoids heavy shadows. 
- **Low-contrast outlines:** Primary containers (tables, inventory cards) are defined by 1px solid borders in a soft gray (#E9ECEF) rather than shadows.
- **Tonal Layers:** The main application background is a very light neutral (#F8F9FA), while the primary content surfaces (cards, whiteboards) are pure white (#FFFFFF). This creates "stacking" through color rather than depth.
- **Interactions:** Subtle, low-opacity shadows (0px 2px 4px rgba(0,0,0,0.05)) are permitted only for active dropdowns or modals to lift them from the primary plane.

## Shapes

The shape language is **Soft (0.25rem)**. This slight rounding takes the edge off a purely "industrial" look, making the software feel modern and accessible without losing its professional rigor. 
- **Buttons and Inputs:** Use the base 4px (0.25rem) radius.
- **Large Containers:** Use 8px (0.5rem) for main dashboard cards.
- **Status Pills:** Use a full pill-shape (100px) for status indicators (e.g., "In Stock") to distinguish them clearly from interactive buttons.

## Components

- **Buttons:** Primary buttons use the medical blue background with white text. Ghost buttons (blue outline) are used for secondary actions like "Export" or "Print."
- **Input Fields:** Use 1px borders. Focus states must use the primary blue for the border with a subtle 2px outer glow to indicate activity.
- **Inventory Cards:** Must feature a clear "Status Badge" in the top right. Content should be grouped logically: SKU, Name, and Quantity in a hierarchy.
- **Data Tables:** These are the heart of the system. Use alternating row stripes (zebra striping) in the lightest neutral color to aid horizontal tracking.
- **Alert Banners:** Positioned at the top of the viewport for critical stock warnings. Red backgrounds should be softened (tinted) to ensure white text remains readable, or use a left-border "accent" style on a light red background.
- **Stock Indicators:** Vertical "thermometer" bars should be used for visual representation of stock levels relative to reorder points.