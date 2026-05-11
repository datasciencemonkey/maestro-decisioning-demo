# Beat 1 — Fluttershy Flutter Web Storefront

**Date:** 2026-05-10
**Status:** Approved
**Scope:** Beat 1 only — Cindy's e-commerce browser journey
**Platform:** Flutter Web only

---

## 1. Purpose

Build a conference-grade Flutter web app that simulates a Shutterfly-like photo book shopping experience. The app follows customer "Cindy" as she browses pet photo book templates, uploads a reference photo of her kitten Whiskers, receives AI-powered recommendations, adds a product to cart, and abandons — firing the `cart_abandoned` event that triggers Beat 2's agentic reasoning.

This is the demo's opening act (3 minutes). It must look like a real, premium e-commerce site — not a prototype. Marketing leaders watch e-commerce sites daily; they will spot anything fake.

## 2. Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Platform | Flutter Web only | Beat 1 simulates a browser session; web is the natural target |
| Design direction | Hybrid Premium | Real shopping UX mechanics with elevated brand tone |
| Brand identity | Soft Modern | Warm chocolate + cream + gold gradients, rounded geometry, conference-projector friendly |
| Interactivity | Interactive + guided rails | 3 modes: freeform, guided, auto-pilot. Covers every presentation context |
| Architecture | GoRouter shell + DemoOrchestrator | Real routes for credibility, orchestrator for demo reliability |
| Upload | Preset Unsplash images (click to simulate) | No file picker needed; 4 preset tabby kitten photos |
| Products/recs | Static mock data | No backend needed for product catalog or initial recommendations |
| NBA re-rank | Simple backend endpoint | Coalesces with existing Maestro API at `../src/maestro/` |
| Cart abandon trigger | "Launch Beat 2" button | Dark-themed demo control in cart drawer; fires `cart_abandoned` event |
| Imagery | Unsplash cat/pet photos | Free, high-quality, real-looking |

## 3. Brand Identity — Soft Modern

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Espresso | `#2c1810` | Primary text, nav icons, dark accents |
| Mocha | `#7c6353` | Secondary text, gradient starts, button fills |
| Brushed Gold | `#c4a87a` | Accent color, badges, highlights, links |
| Warm Cream | `#ede4d8` | Card backgrounds, hero gradients |
| Linen | `#faf8f6` | Page background |
| White | `#ffffff` | Card surfaces, nav bar |

### Typography

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Headings | DM Serif Display | 400 | Hero text, section titles, product names (large) |
| Body | Inter | 400, 500, 600, 700 | Everything else — nav, labels, prices, buttons |

### Design Tokens

- Border radius (cards): 14px
- Border radius (buttons): 8-12px
- Border radius (badges): 8px
- Shadow (cards): `0 2px 12px rgba(44, 24, 16, 0.06)`
- Shadow (elevated): `0 4px 24px rgba(44, 24, 16, 0.10)`
- Gradient (buttons): `linear-gradient(135deg, #7c6353, #a08468)`
- Gradient (gold badge): `linear-gradient(135deg, #c4a87a, #dbc09e)`
- Gradient (promo bar): `linear-gradient(90deg, #7c6353, #a08468)`

## 4. Page Architecture

5 screens connected by GoRouter. The DemoOrchestrator guides Cindy through this path:

### 4.1 Home (`/`)

- Hero banner: full-bleed pet photography (Unsplash), "Welcome Home Collection" headline
- Category tiles: Photo Books, Cards, Prints, Gifts
- Featured products row: 4 product cards
- "New Arrivals" section

### 4.2 Category — Pet Photo Books (`/photo-books`)

This is where most of the action happens. Three-column layout:

**Left — Filter Sidebar (~200px)**
- Pet Type filter chips (Cats selected, Dogs, All)
- Book Size checkboxes (8x8, 10x10, 12x12)
- Price range slider
- **"Match My Pet" upload trigger** — dashed-border card with camera icon. Clicking opens overlay with 4 preset Unsplash tabby kitten photos.

**Center — Product Grid (flexible)**
- Sort bar: "Showing N pet photo books" + sort dropdown (Recommended, Price, Rating)
- 3-column responsive grid of product cards
- Each card: product image, title, subtitle, star rating, price, "Add to Cart" button
- Badges: BESTSELLER (gold gradient), NEW (red), TABBY MATCH (gold, appears after upload)

**Right — NBA Recommendations Panel (~220px)**
- Green dot + "AI RECOMMENDATIONS" header
- Customer card: "Welcome, Cindy" with profile snippet (repeat buyer, cat parent, Whiskers)
- "PICKED FOR YOU" section with 3 recommendation items, each showing match percentage
- "Powered by Mosaic AI · Real-time" footer
- Updates live after photo "upload" with re-ranked recommendations

### 4.3 Upload Modal (overlay on Category)

Not a separate route — modal overlay so the grid re-rank animation plays in context.

- 4 preset Unsplash tabby kitten photos in a 2x2 grid
- Click one to "upload" → triggers AI matching animation sequence:
  1. Sparkle burst on selected photo (600ms)
  2. "Analyzing..." pulse ring animation
  3. Product grid re-sorts with staggered slide animation (800ms)
  4. TABBY MATCH badges appear on matching products (scale-in + gold shimmer)
  5. NBA panel updates with new match percentages

### 4.4 Product Detail (`/product/:id`)

- Large product image (photo book cover with cat imagery)
- Product title, price, star rating, review count
- Customization options: size selector, cover type, page count
- "Add to Cart" primary CTA button
- "You might also like" recommendations row

### 4.5 Cart Drawer (slide-in overlay)

Not a route — slides in from right on any page when cart icon clicked or item added.

- Header: "Your Cart" with close button
- Cart item: product thumbnail, title, subtitle, quantity, price
- Subtotal, shipping (FREE with paw emoji), estimated delivery
- Total prominently displayed
- "Proceed to Checkout" primary button
- "Continue Shopping" text link
- **Demo Control** (dark-themed section at bottom):
  - "DEMO CONTROL" label in gold
  - **"Abandon Cart → Launch Beat 2"** button
  - "Fires cart_abandoned event to agent" caption

## 5. DemoOrchestrator

Top-level `InheritedWidget` wrapping the app. Three modes:

### 5.1 Freeform Mode (default)

Full interactive browsing. Narrator strip shows contextual hints but doesn't drive navigation.

### 5.2 Guided Mode

Narrator advances scene-by-scene. Highlights next interactive element with a pulsing spotlight ring (FlutterFX glow). User clicks the highlighted element to advance.

### 5.3 Auto-pilot Mode

Runs Cindy's full journey hands-free with realistic timing:
- 800ms–2000ms between clicks
- Smooth scrolls to target elements
- Simulated hover effects before clicks

### 5.4 Scene Sequence

| # | Scene | Action | Narrator Text |
|---|-------|--------|---------------|
| 1 | Home landing | Page loads with hero animation | "Meet Cindy — back on Fluttershy for her kitten Whiskers" |
| 2 | Browse photo books | Navigate to /photo-books | "She's browsing cat-themed photo book templates" |
| 3 | Upload pet photo | Click "Match My Pet" → select Whiskers | "She uploads a reference photo of Whiskers" |
| 4 | AI matching | Watch grid re-rank | "NBA panel updates live with cat-matched recommendations" |
| 5 | View product | Click "Welcome Home 24pg" | "Tabby-pattern templates surface to the top" |
| 6 | Add to cart | Click "Add to Cart" | "She adds the Welcome Home template to cart" |
| 7 | Cart abandon | Click "Launch Beat 2" | "She abandons cart — triggering the agent..." |

### 5.5 Narrator Strip

Persistent bottom bar across all screens:
- Left: Scene label + progress dots (7 total)
- Center: Narrator text / spoken line preview
- Right: Mode toggle (Freeform / Guided / Auto-pilot)
- Visual: Semi-transparent dark background, gold accents, 48px height

## 6. Animation Spec (FlutterFX + Custom)

| Moment | Type | Duration | Detail |
|--------|------|----------|--------|
| Page transitions | Shared-axis horizontal | 350ms | Slide + fade via GoRouter transitions |
| Product card hover | Lift + shadow | 200ms | translateY(-4px), shadow expands |
| Hero banner load | Parallax fade-in | 600ms | Image scales from 1.05 to 1.0 + text fades up |
| "Match My Pet" click | Sparkle burst | 600ms | FlutterFX particle effect on selected photo |
| Grid re-rank | Staggered sort | 800ms | Cards slide to new positions, 100ms stagger |
| TABBY MATCH badge | Scale-in + shimmer | 400ms | Scale 0→1 with gold shimmer sweep |
| NBA panel update | Shimmer + slide | 500ms | Content shimmers out, new recs slide in |
| Cart badge | Elastic bounce | 300ms | Overshoot scale on count increment |
| Cart drawer open | Slide-in + backdrop | 300ms | Drawer slides from right, page dims |
| Narrator spotlight | Pulsing glow ring | 2s cycle | Continuous pulse around target element |
| Beat 2 launch | Fade-to-dark | 800ms | Page fades to dark, event dispatched |

## 7. Tech Stack

| Layer | Package | Version |
|-------|---------|---------|
| Framework | Flutter Web | stable channel |
| Routing | `go_router` | latest |
| State management | `flutter_riverpod` | latest |
| UI components | `shadcn_ui` | latest (pub.dev) |
| Animations | `flutterfx_widgets` | latest (GitHub: flutterfx/flutterfx_widgets) |
| HTTP client | `dio` | latest |
| Image caching | `cached_network_image` | latest |
| Fonts | `google_fonts` (Inter, DM Serif Display) | latest |

## 8. Backend Touchpoints

Three REST endpoints in the existing Maestro backend (`../src/maestro/`):

| Endpoint | Method | When | Request | Response |
|----------|--------|------|---------|----------|
| `/api/nba/recommendations/{customer_id}` | GET | Category page loads | — | `{recommendations: [{product_id, title, match_pct}]}` |
| `/api/nba/match` | POST | User clicks a preset photo | `{customer_id, image_ref}` | `{ranked_products: [{product_id, match_pct, badge}]}` |
| `/api/events` | POST | "Launch Beat 2" clicked | `{event_type: "cart_abandoned", customer_id, cart_id, ...}` (per Beat 2 build brief §4.1 schema) | `{status: "accepted", event_id}` |

## 9. Project Structure

```
frontend/
├── lib/
│   ├── main.dart                  # App entry, theme, router
│   ├── theme/
│   │   ├── app_theme.dart         # Soft Modern theme definition
│   │   ├── colors.dart            # Palette constants
│   │   └── typography.dart        # Font styles
│   ├── router/
│   │   └── app_router.dart        # GoRouter configuration
│   ├── orchestrator/
│   │   ├── demo_orchestrator.dart  # InheritedWidget + mode management
│   │   ├── scene.dart             # Scene definitions
│   │   └── narrator_strip.dart    # Bottom narrator bar
│   ├── screens/
│   │   ├── home/
│   │   │   └── home_screen.dart
│   │   ├── category/
│   │   │   ├── category_screen.dart
│   │   │   ├── filter_sidebar.dart
│   │   │   ├── product_grid.dart
│   │   │   ├── nba_panel.dart
│   │   │   └── upload_modal.dart
│   │   ├── product/
│   │   │   └── product_screen.dart
│   │   └── cart/
│   │       └── cart_drawer.dart
│   ├── widgets/
│   │   ├── product_card.dart
│   │   ├── promo_bar.dart
│   │   ├── nav_bar.dart
│   │   ├── breadcrumb.dart
│   │   └── badge.dart
│   ├── models/
│   │   ├── product.dart
│   │   ├── customer.dart
│   │   ├── cart.dart
│   │   └── recommendation.dart
│   ├── providers/
│   │   ├── cart_provider.dart
│   │   ├── products_provider.dart
│   │   ├── recommendations_provider.dart
│   │   └── orchestrator_provider.dart
│   ├── services/
│   │   └── api_service.dart       # Dio client for backend calls
│   ├── animations/
│   │   ├── sparkle_effect.dart
│   │   ├── grid_rerank.dart
│   │   └── spotlight_ring.dart
│   └── data/
│       ├── mock_products.dart     # Static product catalog
│       ├── mock_customer.dart     # Cindy's profile
│       └── unsplash_images.dart   # Preset cat photo URLs
├── web/
│   └── index.html
├── pubspec.yaml
├── CLAUDE.md                      # Flutter/Dart-specific instructions
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-05-10-beat1-flutter-storefront-design.md
```

## 10. Quality Pipeline

After each implementation phase, launch impeccable agents for polish:

| Agent | Purpose |
|-------|---------|
| `impeccable:layout` | Fix spacing, alignment, visual rhythm |
| `impeccable:colorize` | Verify palette consistency, contrast ratios |
| `impeccable:animate` | Review animation timing, easing, purpose |
| `impeccable:polish` | Final pass — alignment, spacing, consistency |
| `impeccable:delight` | Add moments of joy, personality, micro-interactions |
| `impeccable:audit` | Accessibility and performance checks |
| `impeccable:harden` | Error states, empty states, loading states |

## 11. Success Criteria

- [ ] App loads in browser, all 5 screens navigable via GoRouter
- [ ] Soft Modern brand identity applied consistently (colors, type, spacing)
- [ ] Product cards display real Unsplash cat/pet imagery
- [ ] "Match My Pet" shows 4 preset photos, clicking one triggers re-rank animation
- [ ] NBA panel updates with match percentages after photo selection
- [ ] Cart drawer slides in with correct product, total, and shipping
- [ ] "Launch Beat 2" button fires `cart_abandoned` event to backend
- [ ] Narrator strip visible in all modes, mode toggle works
- [ ] Auto-pilot mode runs full journey hands-free
- [ ] All FlutterFX animations smooth at 60fps on web
- [ ] Looks conference-stage stunning on a projector/large screen
- [ ] Passes impeccable:audit for accessibility basics
