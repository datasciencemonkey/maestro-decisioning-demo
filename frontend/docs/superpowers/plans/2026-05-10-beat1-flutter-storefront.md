# Beat 1 — Fluttershy Flutter Web Storefront Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a conference-grade Flutter web storefront simulating Cindy's photo book shopping journey — browse, upload pet photo, AI-powered re-ranking, add to cart, and abandon cart to trigger Beat 2.

**Architecture:** GoRouter shell with 4 routes (home, category, product, cart placeholder) + DemoOrchestrator InheritedWidget for 3 demo modes (freeform, guided, auto-pilot). Riverpod for state. ShadCN UI for components, FlutterFX for animations. Static mock data with 3 backend REST endpoints for NBA and events.

**Tech Stack:** Flutter Web, go_router, flutter_riverpod, shadcn_ui (0.54.0), flutterfx_widgets (git), dio, cached_network_image, google_fonts

**Spec:** `docs/superpowers/specs/2026-05-10-beat1-flutter-storefront-design.md`

---

## Swarm Execution Strategy

Tasks 1–4 are sequential (foundation). Tasks 5–10 can be parallelized across swarm agents. Tasks 11–14 are sequential (integration + polish).

```
Phase 1 (Sequential):  Task 1 → Task 2 → Task 3 → Task 4
Phase 2 (Parallel):    Task 5 ↗ Task 6 ↗ Task 7 ↗ Task 8
                       Task 9 ↗ Task 10
Phase 3 (Sequential):  Task 11 → Task 12 → Task 13 → Task 14
```

### Swarm Agent Roles

| Agent | Role | Goal | Tasks |
|-------|------|------|-------|
| **foundation-architect** | Flutter project architect | Scaffold project, theme, router, models | 1–4 |
| **home-builder** | Home screen developer | Build landing page with hero + categories | 5 |
| **catalog-builder** | Category screen developer | Build filter sidebar + product grid + sort | 6 |
| **nba-builder** | NBA/Upload specialist | Build NBA panel + upload modal + re-rank animation | 7 |
| **product-builder** | Product detail developer | Build product page + add-to-cart flow | 8 |
| **cart-builder** | Cart + events developer | Build cart drawer + Beat 2 trigger | 9 |
| **widget-smith** | Shared widget developer | Build reusable nav, promo bar, breadcrumb, product card | 10 |
| **orchestrator-dev** | Demo orchestrator developer | Build DemoOrchestrator + narrator strip + modes | 11 |
| **integrator** | Integration + API developer | Wire backend endpoints + finalize routing | 12 |
| **animation-engineer** | Animation specialist | Add FlutterFX effects + page transitions | 13 |
| **polish-agent** | Quality + polish | Run impeccable skills for conference-grade finish | 14 |

---

## File Structure

```
frontend/
├── lib/
│   ├── main.dart                       # App entry, ShadcnApp, theme, router
│   ├── theme/
│   │   ├── app_colors.dart             # Soft Modern palette constants
│   │   └── app_theme.dart              # ShadcnThemeData + text styles
│   ├── router/
│   │   └── app_router.dart             # GoRouter config with transitions
│   ├── models/
│   │   ├── product.dart                # Product model
│   │   ├── customer.dart               # Customer (Cindy) model
│   │   ├── cart_item.dart              # Cart item model
│   │   └── recommendation.dart         # NBA recommendation model
│   ├── data/
│   │   ├── mock_products.dart          # 12 static products with Unsplash URLs
│   │   ├── mock_customer.dart          # Cindy's profile
│   │   └── unsplash_images.dart        # Preset cat photo URLs + product images
│   ├── providers/
│   │   ├── cart_provider.dart          # Cart state (Riverpod)
│   │   ├── products_provider.dart      # Product catalog + filtering
│   │   ├── recommendations_provider.dart # NBA recommendations state
│   │   └── orchestrator_provider.dart  # Demo mode + scene state
│   ├── services/
│   │   └── api_service.dart            # Dio client for backend
│   ├── widgets/
│   │   ├── promo_bar.dart              # Top promotional banner
│   │   ├── nav_bar.dart                # Main navigation bar
│   │   ├── breadcrumb_bar.dart         # Breadcrumb navigation
│   │   ├── product_card.dart           # Product card with hover + badge
│   │   └── fluttershy_badge.dart       # BESTSELLER / NEW / TABBY MATCH badges
│   ├── screens/
│   │   ├── home/
│   │   │   └── home_screen.dart        # Landing page
│   │   ├── category/
│   │   │   ├── category_screen.dart    # Main category layout (3-col)
│   │   │   ├── filter_sidebar.dart     # Left filter panel
│   │   │   ├── product_grid.dart       # Center product grid
│   │   │   ├── nba_panel.dart          # Right recommendations panel
│   │   │   └── upload_modal.dart       # Pet photo selection overlay
│   │   ├── product/
│   │   │   └── product_screen.dart     # Product detail page
│   │   └── cart/
│   │       └── cart_drawer.dart        # Slide-in cart + Beat 2 trigger
│   └── orchestrator/
│       ├── demo_orchestrator.dart       # InheritedWidget + mode controller
│       ├── scene.dart                   # Scene enum + definitions
│       └── narrator_strip.dart          # Bottom narrator bar
├── test/
│   ├── models/
│   │   └── product_test.dart
│   ├── providers/
│   │   ├── cart_provider_test.dart
│   │   └── products_provider_test.dart
│   └── widgets/
│       └── product_card_test.dart
├── web/
│   └── index.html
├── pubspec.yaml
└── CLAUDE.md
```

---

## Task 1: Scaffold Flutter Project + Dependencies

**Files:**
- Create: `frontend/pubspec.yaml`
- Create: `frontend/lib/main.dart`
- Create: `frontend/web/index.html`
- Create: `frontend/CLAUDE.md`
- Create: `frontend/analysis_options.yaml`

- [ ] **Step 1: Create Flutter web project**

```bash
cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend
flutter create . --project-name fluttershy --platforms web --org com.databricks.demo
```

- [ ] **Step 2: Replace pubspec.yaml with dependencies**

```yaml
name: fluttershy
description: Fluttershy — Beat 1 storefront demo
publish_to: 'none'
version: 1.0.0

environment:
  sdk: ^3.8.0

dependencies:
  flutter:
    sdk: flutter
  shadcn_ui: ^0.54.0
  go_router: ^15.1.2
  flutter_riverpod: ^2.6.1
  riverpod_annotation: ^2.6.1
  dio: ^5.8.0+1
  cached_network_image: ^3.4.1
  google_fonts: ^6.2.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0
  riverpod_generator: ^2.6.4
  build_runner: ^2.4.15

flutter:
  uses-material-design: true
```

- [ ] **Step 3: Install dependencies**

```bash
cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend
flutter pub get
```

Expected: All dependencies resolve successfully.

- [ ] **Step 4: Write minimal main.dart to verify build**

```dart
import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

void main() {
  runApp(const FluttershyApp());
}

class FluttershyApp extends StatelessWidget {
  const FluttershyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ShadApp.material(
      title: 'Fluttershy',
      themeMode: ThemeMode.light,
      home: const Scaffold(
        body: Center(child: Text('Fluttershy')),
      ),
    );
  }
}
```

- [ ] **Step 5: Create CLAUDE.md for frontend directory**

```markdown
# Fluttershy — Beat 1 Flutter Web Storefront

## What This Is
Flutter web app simulating a Shutterfly-like photo book e-commerce experience.
Part of the Maestro Agentic CDP demo — this is Beat 1 (browser interactions).

## Tech Stack
- Flutter Web (stable channel)
- shadcn_ui (0.54.0) — ShadCN-style UI components
- go_router — declarative routing
- flutter_riverpod — state management
- dio — HTTP client for backend API
- google_fonts — Inter + DM Serif Display

## Commands
- Run: `flutter run -d chrome --web-port 8080`
- Test: `flutter test`
- Build: `flutter build web`
- Analyze: `flutter analyze`

## Brand: Soft Modern Palette
- Espresso: #2c1810 (primary text)
- Mocha: #7c6353 (secondary, gradients)
- Brushed Gold: #c4a87a (accent, badges)
- Warm Cream: #ede4d8 (backgrounds)
- Linen: #faf8f6 (page background)

## Backend
The backend lives at `../src/maestro/`. Three endpoints:
- GET /api/nba/recommendations/{customer_id}
- POST /api/nba/match
- POST /api/events (fires cart_abandoned)

## Design Spec
See `docs/superpowers/specs/2026-05-10-beat1-flutter-storefront-design.md`

## Rules
- Keep files under 300 lines
- Use ShadCN components wherever possible (ShadButton, ShadCard, ShadBadge, etc.)
- Follow existing Soft Modern palette — no off-brand colors
- All images from Unsplash — no local assets except logo
- Test widgets with flutter_test
```

- [ ] **Step 6: Verify build runs in Chrome**

```bash
cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend
flutter run -d chrome --web-port 8080 &
# Verify http://localhost:8080 shows "Fluttershy"
```

- [ ] **Step 7: Commit**

```bash
cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro
git add frontend/
git commit -m "feat(frontend): scaffold Flutter web project with dependencies"
```

---

## Task 2: Theme System — Soft Modern Palette

**Files:**
- Create: `lib/theme/app_colors.dart`
- Create: `lib/theme/app_theme.dart`
- Modify: `lib/main.dart`

- [ ] **Step 1: Write app_colors.dart**

```dart
import 'package:flutter/material.dart';

abstract final class AppColors {
  // Soft Modern palette
  static const espresso = Color(0xFF2C1810);
  static const mocha = Color(0xFF7C6353);
  static const brushedGold = Color(0xFFC4A87A);
  static const warmCream = Color(0xFFEDE4D8);
  static const linen = Color(0xFFFAF8F6);
  static const white = Color(0xFFFFFFFF);

  // Semantic
  static const textPrimary = espresso;
  static const textSecondary = mocha;
  static const textMuted = Color(0xFFA89880);
  static const accent = brushedGold;
  static const surface = white;
  static const background = linen;
  static const cardShadow = Color(0x0F2C1810); // 6% opacity

  // Badges
  static const badgeGoldStart = brushedGold;
  static const badgeGoldEnd = Color(0xFFDBC09E);
  static const badgeNew = Color(0xFFEF4444);

  // Gradients
  static const buttonGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [mocha, Color(0xFFA08468)],
  );
  static const promoGradient = LinearGradient(
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
    colors: [mocha, Color(0xFFA08468)],
  );
  static const goldGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [brushedGold, badgeGoldEnd],
  );
  static const heroGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFF5EFE8), warmCream, Color(0xFFE0D4C4)],
  );
}
```

- [ ] **Step 2: Write app_theme.dart**

```dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'app_colors.dart';

abstract final class AppTheme {
  static TextStyle get _heading => GoogleFonts.dmSerifDisplay(
        color: AppColors.textPrimary,
      );

  static TextStyle get _body => GoogleFonts.inter(
        color: AppColors.textPrimary,
      );

  static TextStyle get headlineLarge => _heading.copyWith(fontSize: 32, fontWeight: FontWeight.w400);
  static TextStyle get headlineMedium => _heading.copyWith(fontSize: 24, fontWeight: FontWeight.w400);
  static TextStyle get headlineSmall => _heading.copyWith(fontSize: 18, fontWeight: FontWeight.w400);

  static TextStyle get titleLarge => _body.copyWith(fontSize: 16, fontWeight: FontWeight.w700);
  static TextStyle get titleMedium => _body.copyWith(fontSize: 14, fontWeight: FontWeight.w600);
  static TextStyle get titleSmall => _body.copyWith(fontSize: 12, fontWeight: FontWeight.w600);

  static TextStyle get bodyLarge => _body.copyWith(fontSize: 14, fontWeight: FontWeight.w400);
  static TextStyle get bodyMedium => _body.copyWith(fontSize: 12, fontWeight: FontWeight.w400);
  static TextStyle get bodySmall => _body.copyWith(fontSize: 11, fontWeight: FontWeight.w400);

  static TextStyle get labelLarge => _body.copyWith(
        fontSize: 11,
        fontWeight: FontWeight.w600,
        letterSpacing: 1.5,
        color: AppColors.textMuted,
      );

  static TextStyle get priceLarge => _body.copyWith(fontSize: 18, fontWeight: FontWeight.w700);
  static TextStyle get priceSmall => _body.copyWith(fontSize: 14, fontWeight: FontWeight.w700);

  static const double radiusCard = 14.0;
  static const double radiusButton = 10.0;
  static const double radiusBadge = 8.0;

  static BoxDecoration get cardDecoration => BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(radiusCard),
        boxShadow: const [
          BoxShadow(
            color: AppColors.cardShadow,
            blurRadius: 12,
            offset: Offset(0, 2),
          ),
        ],
      );

  static ThemeData get materialTheme => ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: AppColors.background,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.brushedGold,
          surface: AppColors.surface,
        ),
        textTheme: TextTheme(
          headlineLarge: headlineLarge,
          headlineMedium: headlineMedium,
          headlineSmall: headlineSmall,
          titleLarge: titleLarge,
          titleMedium: titleMedium,
          bodyLarge: bodyLarge,
          bodyMedium: bodyMedium,
          bodySmall: bodySmall,
          labelLarge: labelLarge,
        ),
      );
}
```

- [ ] **Step 3: Update main.dart to use theme**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'theme/app_theme.dart';
import 'theme/app_colors.dart';

void main() {
  runApp(const ProviderScope(child: FluttershyApp()));
}

class FluttershyApp extends StatelessWidget {
  const FluttershyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ShadApp.material(
      title: 'Fluttershy',
      themeMode: ThemeMode.light,
      materialThemeBuilder: (context, theme) => AppTheme.materialTheme,
      home: Scaffold(
        backgroundColor: AppColors.background,
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Fluttershy', style: AppTheme.headlineLarge),
              const SizedBox(height: 8),
              Text('Pet Photo Books', style: AppTheme.bodyLarge.copyWith(color: AppColors.textSecondary)),
            ],
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 4: Verify theme renders in Chrome**

```bash
flutter run -d chrome --web-port 8080
```

Expected: "Fluttershy" in DM Serif Display, "Pet Photo Books" in Inter, linen background.

- [ ] **Step 5: Commit**

```bash
git add frontend/lib/theme/ frontend/lib/main.dart
git commit -m "feat(frontend): add Soft Modern theme system with colors and typography"
```

---

## Task 3: GoRouter Configuration

**Files:**
- Create: `lib/router/app_router.dart`
- Modify: `lib/main.dart`

- [ ] **Step 1: Write app_router.dart**

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/home/home_screen.dart';
import '../screens/category/category_screen.dart';
import '../screens/product/product_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      name: 'home',
      pageBuilder: (context, state) => CustomTransitionPage(
        child: const HomeScreen(),
        transitionsBuilder: _sharedAxisTransition,
      ),
    ),
    GoRoute(
      path: '/photo-books',
      name: 'category',
      pageBuilder: (context, state) => CustomTransitionPage(
        child: const CategoryScreen(),
        transitionsBuilder: _sharedAxisTransition,
      ),
    ),
    GoRoute(
      path: '/product/:id',
      name: 'product',
      pageBuilder: (context, state) {
        final productId = state.pathParameters['id']!;
        return CustomTransitionPage(
          child: ProductScreen(productId: productId),
          transitionsBuilder: _sharedAxisTransition,
        );
      },
    ),
  ],
);

Widget _sharedAxisTransition(
  BuildContext context,
  Animation<double> animation,
  Animation<double> secondaryAnimation,
  Widget child,
) {
  return FadeTransition(
    opacity: CurvedAnimation(parent: animation, curve: Curves.easeInOut),
    child: SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0.05, 0),
        end: Offset.zero,
      ).animate(CurvedAnimation(parent: animation, curve: Curves.easeOutCubic)),
      child: child,
    ),
  );
}
```

- [ ] **Step 2: Create placeholder screens**

Create `lib/screens/home/home_screen.dart`:
```dart
import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';
import '../../theme/app_colors.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Text('Home', style: AppTheme.headlineLarge),
      ),
    );
  }
}
```

Create `lib/screens/category/category_screen.dart`:
```dart
import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';
import '../../theme/app_colors.dart';

class CategoryScreen extends StatelessWidget {
  const CategoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Text('Photo Books', style: AppTheme.headlineLarge),
      ),
    );
  }
}
```

Create `lib/screens/product/product_screen.dart`:
```dart
import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';
import '../../theme/app_colors.dart';

class ProductScreen extends StatelessWidget {
  final String productId;
  const ProductScreen({super.key, required this.productId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Text('Product: $productId', style: AppTheme.headlineLarge),
      ),
    );
  }
}
```

- [ ] **Step 3: Update main.dart to use router**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import 'theme/app_theme.dart';
import 'router/app_router.dart';

void main() {
  runApp(const ProviderScope(child: FluttershyApp()));
}

class FluttershyApp extends StatelessWidget {
  const FluttershyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ShadApp.material(
      title: 'Fluttershy',
      themeMode: ThemeMode.light,
      materialThemeBuilder: (context, theme) => AppTheme.materialTheme,
      home: Builder(
        builder: (context) => MaterialApp.router(
          routerConfig: appRouter,
          title: 'Fluttershy',
          theme: AppTheme.materialTheme,
          debugShowCheckedModeBanner: false,
        ),
      ),
    );
  }
}
```

- [ ] **Step 4: Verify navigation works**

```bash
flutter run -d chrome --web-port 8080
# Navigate to localhost:8080/#/photo-books — should show "Photo Books"
# Navigate to localhost:8080/#/product/test123 — should show "Product: test123"
```

- [ ] **Step 5: Commit**

```bash
git add frontend/lib/router/ frontend/lib/screens/ frontend/lib/main.dart
git commit -m "feat(frontend): add GoRouter with home, category, and product routes"
```

---

## Task 4: Models + Mock Data

**Files:**
- Create: `lib/models/product.dart`
- Create: `lib/models/customer.dart`
- Create: `lib/models/cart_item.dart`
- Create: `lib/models/recommendation.dart`
- Create: `lib/data/mock_products.dart`
- Create: `lib/data/mock_customer.dart`
- Create: `lib/data/unsplash_images.dart`
- Create: `test/models/product_test.dart`

- [ ] **Step 1: Write the product model test**

```dart
// test/models/product_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:fluttershy/models/product.dart';

void main() {
  group('Product', () {
    test('creates with required fields', () {
      final product = Product(
        id: 'pb_welcome_home_24pp',
        title: 'Welcome Home 24pg',
        subtitle: 'Tabby collection · Hardcover',
        price: 42.00,
        rating: 4.9,
        reviewCount: 124,
        imageUrl: 'https://example.com/image.jpg',
        category: 'cat',
      );
      expect(product.id, 'pb_welcome_home_24pp');
      expect(product.price, 42.00);
      expect(product.badge, isNull);
    });

    test('supports badge and matchPercent', () {
      final product = Product(
        id: 'pb_test',
        title: 'Test',
        subtitle: 'Test',
        price: 29.00,
        rating: 4.0,
        reviewCount: 10,
        imageUrl: 'https://example.com/img.jpg',
        category: 'cat',
        badge: ProductBadge.bestseller,
        matchPercent: 98,
      );
      expect(product.badge, ProductBadge.bestseller);
      expect(product.matchPercent, 98);
    });
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/sathish.gangichetty/Documents/cdp/projects/maestro/frontend
flutter test test/models/product_test.dart
```

Expected: FAIL — `package:fluttershy/models/product.dart` not found.

- [ ] **Step 3: Write models**

`lib/models/product.dart`:
```dart
enum ProductBadge { bestseller, tabbyMatch, newArrival }

class Product {
  final String id;
  final String title;
  final String subtitle;
  final double price;
  final double rating;
  final int reviewCount;
  final String imageUrl;
  final String category; // 'cat', 'dog', 'all'
  final ProductBadge? badge;
  final int? matchPercent;
  final String? description;

  const Product({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.price,
    required this.rating,
    required this.reviewCount,
    required this.imageUrl,
    required this.category,
    this.badge,
    this.matchPercent,
    this.description,
  });

  Product copyWith({
    ProductBadge? badge,
    int? matchPercent,
  }) {
    return Product(
      id: id,
      title: title,
      subtitle: subtitle,
      price: price,
      rating: rating,
      reviewCount: reviewCount,
      imageUrl: imageUrl,
      category: category,
      badge: badge ?? this.badge,
      matchPercent: matchPercent ?? this.matchPercent,
      description: description,
    );
  }
}
```

`lib/models/customer.dart`:
```dart
class Customer {
  final String id;
  final String name;
  final String petName;
  final String petType;
  final String timezone;
  final bool isRepeatBuyer;
  final String preferredChannel;

  const Customer({
    required this.id,
    required this.name,
    required this.petName,
    required this.petType,
    required this.timezone,
    required this.isRepeatBuyer,
    required this.preferredChannel,
  });
}
```

`lib/models/cart_item.dart`:
```dart
import 'product.dart';

class CartItem {
  final Product product;
  final int quantity;

  const CartItem({required this.product, this.quantity = 1});

  double get total => product.price * quantity;
}
```

`lib/models/recommendation.dart`:
```dart
class Recommendation {
  final String productId;
  final String title;
  final String imageUrl;
  final int matchPercent;

  const Recommendation({
    required this.productId,
    required this.title,
    required this.imageUrl,
    required this.matchPercent,
  });
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
flutter test test/models/product_test.dart
```

Expected: All tests PASS.

- [ ] **Step 5: Write mock data**

`lib/data/unsplash_images.dart`:
```dart
/// Unsplash image URLs for the Fluttershy storefront.
/// All images are free to use via Unsplash License.
abstract final class UnsplashImages {
  // Preset "upload" photos — tabby kittens for Match My Pet
  static const presetCats = [
    'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400&h=400&fit=crop',
    'https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=400&h=400&fit=crop',
    'https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=400&h=400&fit=crop',
    'https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13?w=400&h=400&fit=crop',
  ];

  // Product card images — photo book covers
  static const productImages = [
    'https://images.unsplash.com/photo-1615497001839-b0a0eac3274c?w=600&h=400&fit=crop', // tabby kitten
    'https://images.unsplash.com/photo-1596854407944-bf87f6fdd49e?w=600&h=400&fit=crop', // cat portrait
    'https://images.unsplash.com/photo-1561948955-570b270e7c36?w=600&h=400&fit=crop', // cat sitting
    'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=600&h=400&fit=crop', // cool cat
    'https://images.unsplash.com/photo-1543852786-1cf6624b9987?w=600&h=400&fit=crop', // kitten face
    'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600&h=400&fit=crop', // orange cat
    'https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=600&h=400&fit=crop', // playful kitten
    'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=400&fit=crop', // golden dog
    'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=600&h=400&fit=crop', // dogs running
    'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=600&h=400&fit=crop', // bulldog
    'https://images.unsplash.com/photo-1425082661705-1834bfd09dca?w=600&h=400&fit=crop', // bunny
    'https://images.unsplash.com/photo-1606567595334-d39972c85dbe?w=600&h=400&fit=crop', // parrot
  ];

  // Hero banner
  static const heroBanner =
      'https://images.unsplash.com/photo-1615497001839-b0a0eac3274c?w=1400&h=600&fit=crop';
}
```

`lib/data/mock_customer.dart`:
```dart
import '../models/customer.dart';

const cindy = Customer(
  id: 'cust_88241',
  name: 'Cindy',
  petName: 'Whiskers',
  petType: 'tabby',
  timezone: 'America/Chicago',
  isRepeatBuyer: true,
  preferredChannel: 'email',
);
```

`lib/data/mock_products.dart`:
```dart
import '../models/product.dart';
import 'unsplash_images.dart';

final mockProducts = <Product>[
  Product(
    id: 'pb_welcome_home_24pp',
    title: 'Welcome Home 24pg',
    subtitle: 'Tabby collection · Hardcover',
    price: 42.00,
    rating: 4.9,
    reviewCount: 124,
    imageUrl: UnsplashImages.productImages[0],
    category: 'cat',
    badge: ProductBadge.bestseller,
    description: 'A beautiful hardcover photo book to celebrate your new pet\'s arrival. 24 pages of premium matte paper with lay-flat binding.',
  ),
  Product(
    id: 'pb_classic_soft',
    title: 'Classic Softcover',
    subtitle: 'All pets · Softcover',
    price: 29.00,
    rating: 4.2,
    reviewCount: 89,
    imageUrl: UnsplashImages.productImages[1],
    category: 'all',
  ),
  Product(
    id: 'pb_first_year',
    title: 'First Year Journal',
    subtitle: 'All pets · Layflat',
    price: 55.00,
    rating: 4.8,
    reviewCount: 56,
    imageUrl: UnsplashImages.productImages[2],
    category: 'all',
    badge: ProductBadge.newArrival,
  ),
  Product(
    id: 'pb_whisker_tales',
    title: 'Whisker Tales',
    subtitle: 'Cat collection · Hardcover',
    price: 38.00,
    rating: 4.6,
    reviewCount: 203,
    imageUrl: UnsplashImages.productImages[3],
    category: 'cat',
  ),
  Product(
    id: 'pb_paw_prints',
    title: 'Paw Prints Album',
    subtitle: 'All pets · Premium layflat',
    price: 65.00,
    rating: 4.9,
    reviewCount: 78,
    imageUrl: UnsplashImages.productImages[4],
    category: 'all',
  ),
  Product(
    id: 'pb_kitten_cuddles',
    title: 'Kitten Cuddles',
    subtitle: 'Cat collection · Softcover',
    price: 32.00,
    rating: 4.4,
    reviewCount: 167,
    imageUrl: UnsplashImages.productImages[5],
    category: 'cat',
  ),
  Product(
    id: 'pb_playful_paws',
    title: 'Playful Paws',
    subtitle: 'Cat collection · Hardcover',
    price: 45.00,
    rating: 4.7,
    reviewCount: 92,
    imageUrl: UnsplashImages.productImages[6],
    category: 'cat',
  ),
  Product(
    id: 'pb_good_boy',
    title: 'Good Boy Chronicles',
    subtitle: 'Dog collection · Hardcover',
    price: 42.00,
    rating: 4.8,
    reviewCount: 145,
    imageUrl: UnsplashImages.productImages[7],
    category: 'dog',
  ),
  Product(
    id: 'pb_fetch_tales',
    title: 'Fetch & Tales',
    subtitle: 'Dog collection · Softcover',
    price: 29.00,
    rating: 4.3,
    reviewCount: 71,
    imageUrl: UnsplashImages.productImages[8],
    category: 'dog',
  ),
  Product(
    id: 'pb_best_friend',
    title: 'Best Friend Forever',
    subtitle: 'Dog collection · Premium',
    price: 58.00,
    rating: 4.9,
    reviewCount: 199,
    imageUrl: UnsplashImages.productImages[9],
    category: 'dog',
    badge: ProductBadge.bestseller,
  ),
  Product(
    id: 'pb_hoppy_days',
    title: 'Hoppy Days',
    subtitle: 'Small pets · Softcover',
    price: 26.00,
    rating: 4.1,
    reviewCount: 34,
    imageUrl: UnsplashImages.productImages[10],
    category: 'all',
  ),
  Product(
    id: 'pb_feathered_friends',
    title: 'Feathered Friends',
    subtitle: 'Bird collection · Hardcover',
    price: 39.00,
    rating: 4.5,
    reviewCount: 47,
    imageUrl: UnsplashImages.productImages[11],
    category: 'all',
  ),
];
```

- [ ] **Step 6: Run all tests**

```bash
flutter test
```

Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add frontend/lib/models/ frontend/lib/data/ frontend/test/
git commit -m "feat(frontend): add models, mock products, Cindy profile, and Unsplash images"
```

---

## Task 5: Home Screen

**Files:**
- Modify: `lib/screens/home/home_screen.dart`

**Depends on:** Tasks 1–4, Task 10 (shared widgets)

- [ ] **Step 1: Build home screen with hero + category tiles + featured products**

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../data/mock_products.dart';
import '../../data/unsplash_images.dart';
import '../../widgets/promo_bar.dart';
import '../../widgets/nav_bar.dart';
import '../../widgets/product_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          const PromoBar(),
          const NavBar(currentRoute: '/'),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  _buildHero(context),
                  const SizedBox(height: 40),
                  _buildCategoryTiles(context),
                  const SizedBox(height: 40),
                  _buildFeaturedProducts(context),
                  const SizedBox(height: 60),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHero(BuildContext context) {
    return Container(
      height: 420,
      width: double.infinity,
      decoration: const BoxDecoration(gradient: AppColors.heroGradient),
      child: Stack(
        children: [
          Positioned.fill(
            child: Opacity(
              opacity: 0.3,
              child: CachedNetworkImage(
                imageUrl: UnsplashImages.heroBanner,
                fit: BoxFit.cover,
              ),
            ),
          ),
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'WELCOME HOME COLLECTION',
                  style: AppTheme.labelLarge.copyWith(
                    color: AppColors.brushedGold,
                    letterSpacing: 3,
                  ),
                ),
                const SizedBox(height: 12),
                Text('Pet Photo Books', style: AppTheme.headlineLarge.copyWith(fontSize: 42)),
                const SizedBox(height: 8),
                Text(
                  'Tell their story. Keep their moments.',
                  style: AppTheme.bodyLarge.copyWith(color: AppColors.textSecondary),
                ),
                const SizedBox(height: 24),
                MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: GestureDetector(
                    onTap: () => context.go('/photo-books'),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
                      decoration: BoxDecoration(
                        gradient: AppColors.buttonGradient,
                        borderRadius: BorderRadius.circular(AppTheme.radiusButton),
                      ),
                      child: Text(
                        'Start Creating →',
                        style: AppTheme.titleSmall.copyWith(color: Colors.white),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryTiles(BuildContext context) {
    final categories = [
      ('Photo Books', '📚', '/photo-books'),
      ('Cards', '💌', '/photo-books'),
      ('Prints', '🖼️', '/photo-books'),
      ('Gifts', '🎁', '/photo-books'),
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 48),
      child: Column(
        children: [
          Text('Shop by Category', style: AppTheme.headlineMedium),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: categories.map((cat) {
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: GestureDetector(
                    onTap: () => context.go(cat.$3),
                    child: Container(
                      width: 160,
                      padding: const EdgeInsets.all(24),
                      decoration: AppTheme.cardDecoration,
                      child: Column(
                        children: [
                          Text(cat.$2, style: const TextStyle(fontSize: 36)),
                          const SizedBox(height: 12),
                          Text(cat.$1, style: AppTheme.titleMedium),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFeaturedProducts(BuildContext context) {
    final featured = mockProducts.take(4).toList();
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 48),
      child: Column(
        children: [
          Text('Featured', style: AppTheme.headlineMedium),
          const SizedBox(height: 24),
          Row(
            children: featured.map((p) {
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: ProductCard(product: p),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 2: Verify home screen renders**

```bash
flutter run -d chrome --web-port 8080
```

Expected: Home page with hero banner, 4 category tiles, 4 featured product cards.

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/screens/home/
git commit -m "feat(frontend): build home screen with hero, categories, and featured products"
```

---

## Task 6: Category Screen — Filter Sidebar + Product Grid

**Files:**
- Modify: `lib/screens/category/category_screen.dart`
- Create: `lib/screens/category/filter_sidebar.dart`
- Create: `lib/screens/category/product_grid.dart`
- Create: `lib/providers/products_provider.dart`

**Depends on:** Tasks 1–4, Task 10 (shared widgets)

- [ ] **Step 1: Write products_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/product.dart';
import '../data/mock_products.dart';

enum PetFilter { all, cat, dog }
enum SortOption { recommended, priceLow, priceHigh, rating }

class ProductsState {
  final List<Product> products;
  final PetFilter petFilter;
  final SortOption sortOption;
  final bool matchActive;

  const ProductsState({
    required this.products,
    this.petFilter = PetFilter.all,
    this.sortOption = SortOption.recommended,
    this.matchActive = false,
  });

  List<Product> get filtered {
    var result = products.where((p) {
      if (petFilter == PetFilter.all) return true;
      if (petFilter == PetFilter.cat) return p.category == 'cat';
      if (petFilter == PetFilter.dog) return p.category == 'dog';
      return true;
    }).toList();

    switch (sortOption) {
      case SortOption.recommended:
        if (matchActive) {
          result.sort((a, b) => (b.matchPercent ?? 0).compareTo(a.matchPercent ?? 0));
        }
        break;
      case SortOption.priceLow:
        result.sort((a, b) => a.price.compareTo(b.price));
        break;
      case SortOption.priceHigh:
        result.sort((a, b) => b.price.compareTo(a.price));
        break;
      case SortOption.rating:
        result.sort((a, b) => b.rating.compareTo(a.rating));
        break;
    }
    return result;
  }

  ProductsState copyWith({
    List<Product>? products,
    PetFilter? petFilter,
    SortOption? sortOption,
    bool? matchActive,
  }) {
    return ProductsState(
      products: products ?? this.products,
      petFilter: petFilter ?? this.petFilter,
      sortOption: sortOption ?? this.sortOption,
      matchActive: matchActive ?? this.matchActive,
    );
  }
}

class ProductsNotifier extends StateNotifier<ProductsState> {
  ProductsNotifier() : super(ProductsState(products: mockProducts));

  void setFilter(PetFilter filter) {
    state = state.copyWith(petFilter: filter);
  }

  void setSort(SortOption option) {
    state = state.copyWith(sortOption: option);
  }

  void applyMatch(Map<String, int> matchScores) {
    final updated = state.products.map((p) {
      final score = matchScores[p.id];
      if (score != null) {
        return p.copyWith(
          matchPercent: score,
          badge: score >= 85 ? ProductBadge.tabbyMatch : p.badge,
        );
      }
      return p;
    }).toList();
    state = state.copyWith(products: updated, matchActive: true, petFilter: PetFilter.cat);
  }
}

final productsProvider = StateNotifierProvider<ProductsNotifier, ProductsState>((ref) {
  return ProductsNotifier();
});
```

- [ ] **Step 2: Write filter_sidebar.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shadcn_ui/shadcn_ui.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../providers/products_provider.dart';
import 'upload_modal.dart';

class FilterSidebar extends ConsumerWidget {
  const FilterSidebar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(productsProvider);

    return Container(
      width: 220,
      padding: const EdgeInsets.all(20),
      decoration: AppTheme.cardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Filters', style: AppTheme.titleLarge),
          const SizedBox(height: 20),

          // Pet type
          Text('PET TYPE', style: AppTheme.labelLarge),
          const SizedBox(height: 8),
          Wrap(
            spacing: 6,
            children: PetFilter.values.map((f) {
              final label = switch (f) {
                PetFilter.all => 'All',
                PetFilter.cat => '🐱 Cats',
                PetFilter.dog => '🐕 Dogs',
              };
              final isActive = state.petFilter == f;
              return MouseRegion(
                cursor: SystemMouseCursors.click,
                child: GestureDetector(
                  onTap: () => ref.read(productsProvider.notifier).setFilter(f),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: isActive ? AppColors.espresso : AppColors.warmCream,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      label,
                      style: AppTheme.bodySmall.copyWith(
                        color: isActive ? Colors.white : AppColors.textSecondary,
                        fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),

          // Book size
          Text('BOOK SIZE', style: AppTheme.labelLarge),
          const SizedBox(height: 8),
          ...[('8×8 Standard', true), ('10×10 Large', false), ('12×12 XL', false)].map(
            (item) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  ShadCheckbox(value: item.$2, onChanged: (_) {}),
                  const SizedBox(width: 8),
                  Text(item.$1, style: AppTheme.bodySmall),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Match My Pet trigger
          MouseRegion(
            cursor: SystemMouseCursors.click,
            child: GestureDetector(
              onTap: () => showUploadModal(context),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      AppColors.brushedGold.withValues(alpha: 0.15),
                      AppColors.brushedGold.withValues(alpha: 0.05),
                    ],
                  ),
                  border: Border.all(color: AppColors.brushedGold, width: 1.5, style: BorderStyle.solid),
                  borderRadius: BorderRadius.circular(AppTheme.radiusButton),
                ),
                child: Column(
                  children: [
                    const Text('📸', style: TextStyle(fontSize: 24)),
                    const SizedBox(height: 6),
                    Text('Match My Pet', style: AppTheme.titleSmall.copyWith(color: AppColors.brushedGold)),
                    const SizedBox(height: 2),
                    Text('AI-powered photo matching', style: AppTheme.bodySmall.copyWith(color: AppColors.textMuted, fontSize: 10)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 3: Write product_grid.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../providers/products_provider.dart';
import '../../widgets/product_card.dart';

class ProductGrid extends ConsumerWidget {
  const ProductGrid({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(productsProvider);
    final products = state.filtered;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Sort bar
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Showing ${products.length} pet photo books',
              style: AppTheme.bodyMedium.copyWith(color: AppColors.textSecondary),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: AppTheme.cardDecoration,
              child: MouseRegion(
                cursor: SystemMouseCursors.click,
                child: GestureDetector(
                  onTap: () {
                    // Cycle through sort options
                    final current = state.sortOption;
                    final next = SortOption.values[(current.index + 1) % SortOption.values.length];
                    ref.read(productsProvider.notifier).setSort(next);
                  },
                  child: Text(
                    'Sort: ${_sortLabel(state.sortOption)} ▾',
                    style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w500),
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Grid
        LayoutBuilder(
          builder: (context, constraints) {
            final crossAxisCount = constraints.maxWidth > 900 ? 3 : 2;
            return GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 0.72,
              ),
              itemCount: products.length,
              itemBuilder: (context, index) {
                return ProductCard(
                  product: products[index],
                  key: ValueKey(products[index].id),
                );
              },
            );
          },
        ),
      ],
    );
  }

  String _sortLabel(SortOption option) {
    return switch (option) {
      SortOption.recommended => 'Recommended',
      SortOption.priceLow => 'Price: Low',
      SortOption.priceHigh => 'Price: High',
      SortOption.rating => 'Top Rated',
    };
  }
}
```

- [ ] **Step 4: Update category_screen.dart with 3-column layout**

```dart
import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../widgets/promo_bar.dart';
import '../../widgets/nav_bar.dart';
import '../../widgets/breadcrumb_bar.dart';
import 'filter_sidebar.dart';
import 'product_grid.dart';
import 'nba_panel.dart';

class CategoryScreen extends StatelessWidget {
  const CategoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          const PromoBar(),
          const NavBar(currentRoute: '/photo-books'),
          const BreadcrumbBar(items: ['Home', 'Photo Books', 'Pet Photo Books']),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const FilterSidebar(),
                  const SizedBox(width: 24),
                  const Expanded(child: ProductGrid()),
                  const SizedBox(width: 24),
                  const NbaPanel(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 5: Verify category page renders**

```bash
flutter run -d chrome --web-port 8080
# Navigate to /#/photo-books
```

Expected: 3-column layout — filters left, product grid center, NBA panel right.

- [ ] **Step 6: Commit**

```bash
git add frontend/lib/screens/category/ frontend/lib/providers/products_provider.dart
git commit -m "feat(frontend): build category screen with filter sidebar and product grid"
```

---

## Task 7: NBA Panel + Upload Modal

**Files:**
- Create: `lib/screens/category/nba_panel.dart`
- Create: `lib/screens/category/upload_modal.dart`
- Create: `lib/providers/recommendations_provider.dart`

**Depends on:** Tasks 1–4

- [ ] **Step 1: Write recommendations_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/recommendation.dart';
import '../data/unsplash_images.dart';

class RecommendationsNotifier extends StateNotifier<List<Recommendation>> {
  RecommendationsNotifier()
      : super([
          Recommendation(productId: 'pb_welcome_home_24pp', title: 'Welcome Home 24pg', imageUrl: UnsplashImages.productImages[0], matchPercent: 92),
          Recommendation(productId: 'pb_whisker_tales', title: 'Whisker Tales', imageUrl: UnsplashImages.productImages[3], matchPercent: 85),
          Recommendation(productId: 'pb_paw_prints', title: 'Paw Prints Album', imageUrl: UnsplashImages.productImages[4], matchPercent: 78),
        ]);

  void updateAfterMatch() {
    state = [
      Recommendation(productId: 'pb_welcome_home_24pp', title: 'Welcome Home 24pg', imageUrl: UnsplashImages.productImages[0], matchPercent: 98),
      Recommendation(productId: 'pb_kitten_cuddles', title: 'Kitten Cuddles', imageUrl: UnsplashImages.productImages[5], matchPercent: 94),
      Recommendation(productId: 'pb_whisker_tales', title: 'Whisker Tales', imageUrl: UnsplashImages.productImages[3], matchPercent: 91),
    ];
  }
}

final recommendationsProvider = StateNotifierProvider<RecommendationsNotifier, List<Recommendation>>((ref) {
  return RecommendationsNotifier();
});
```

- [ ] **Step 2: Write nba_panel.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../data/mock_customer.dart';
import '../../providers/recommendations_provider.dart';

class NbaPanel extends ConsumerWidget {
  const NbaPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recommendations = ref.watch(recommendationsProvider);

    return Container(
      width: 240,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppTheme.radiusCard),
        border: Border.all(color: AppColors.brushedGold.withValues(alpha: 0.2), width: 1.5),
        boxShadow: const [BoxShadow(color: AppColors.cardShadow, blurRadius: 12, offset: Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header
          Row(
            children: [
              Container(
                width: 8, height: 8,
                decoration: const BoxDecoration(color: Color(0xFF22C55E), shape: BoxShape.circle),
              ),
              const SizedBox(width: 8),
              Text('AI RECOMMENDATIONS', style: AppTheme.labelLarge.copyWith(fontSize: 10)),
            ],
          ),
          const SizedBox(height: 14),

          // Customer card
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.warmCream,
              borderRadius: BorderRadius.circular(AppTheme.radiusBadge),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('👋 Welcome, ${cindy.name}', style: AppTheme.titleSmall),
                const SizedBox(height: 4),
                Text('Repeat buyer · Cat parent 🐱', style: AppTheme.bodySmall.copyWith(color: AppColors.textSecondary)),
                Text('Pet: ${cindy.petName} (${cindy.petType} kitten)', style: AppTheme.bodySmall.copyWith(color: AppColors.brushedGold)),
              ],
            ),
          ),
          const SizedBox(height: 14),

          Text('PICKED FOR YOU', style: AppTheme.labelLarge.copyWith(fontSize: 9)),
          const SizedBox(height: 8),

          // Recommendation items
          ...recommendations.map((rec) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.circular(AppTheme.radiusBadge),
              ),
              child: Row(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: CachedNetworkImage(
                      imageUrl: rec.imageUrl,
                      width: 36, height: 36, fit: BoxFit.cover,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(rec.title, style: AppTheme.bodySmall.copyWith(fontWeight: FontWeight.w600)),
                        Text('${rec.matchPercent}% match', style: AppTheme.bodySmall.copyWith(color: AppColors.brushedGold, fontSize: 10)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          )),

          const Divider(color: AppColors.warmCream),
          const SizedBox(height: 4),
          Center(
            child: Text(
              'Powered by Mosaic AI · Real-time',
              style: AppTheme.bodySmall.copyWith(color: AppColors.textMuted, fontSize: 9),
            ),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 3: Write upload_modal.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../data/unsplash_images.dart';
import '../../providers/products_provider.dart';
import '../../providers/recommendations_provider.dart';

void showUploadModal(BuildContext context) {
  showDialog(
    context: context,
    barrierColor: Colors.black54,
    builder: (context) => const _UploadModal(),
  );
}

class _UploadModal extends ConsumerStatefulWidget {
  const _UploadModal();

  @override
  ConsumerState<_UploadModal> createState() => _UploadModalState();
}

class _UploadModalState extends ConsumerState<_UploadModal> with SingleTickerProviderStateMixin {
  int? _selectedIndex;
  bool _analyzing = false;

  Future<void> _onPhotoSelected(int index) async {
    setState(() {
      _selectedIndex = index;
      _analyzing = true;
    });

    // Simulate AI analysis delay
    await Future.delayed(const Duration(milliseconds: 1200));

    // Apply match scores
    final matchScores = {
      'pb_welcome_home_24pp': 98,
      'pb_whisker_tales': 94,
      'pb_kitten_cuddles': 91,
      'pb_playful_paws': 87,
      'pb_paw_prints': 82,
      'pb_first_year': 76,
    };

    ref.read(productsProvider.notifier).applyMatch(matchScores);
    ref.read(recommendationsProvider.notifier).updateAfterMatch();

    if (mounted) {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        width: 420,
        padding: const EdgeInsets.all(28),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 40)],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Match My Pet', style: AppTheme.headlineSmall),
                MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: GestureDetector(
                    onTap: () => Navigator.of(context).pop(),
                    child: const Icon(Icons.close, color: AppColors.textMuted),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Select a photo to find matching photo books',
              style: AppTheme.bodyMedium.copyWith(color: AppColors.textSecondary),
            ),
            const SizedBox(height: 20),

            if (_analyzing) ...[
              const SizedBox(height: 40),
              SizedBox(
                width: 48, height: 48,
                child: CircularProgressIndicator(
                  strokeWidth: 3,
                  valueColor: const AlwaysStoppedAnimation(AppColors.brushedGold),
                ),
              ),
              const SizedBox(height: 16),
              Text('Analyzing with AI...', style: AppTheme.titleSmall.copyWith(color: AppColors.brushedGold)),
              const SizedBox(height: 8),
              Text('Finding matching photo books', style: AppTheme.bodySmall.copyWith(color: AppColors.textMuted)),
              const SizedBox(height: 40),
            ] else ...[
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                ),
                itemCount: UnsplashImages.presetCats.length,
                itemBuilder: (context, index) {
                  final isSelected = _selectedIndex == index;
                  return MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: () => _onPhotoSelected(index),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSelected ? AppColors.brushedGold : Colors.transparent,
                            width: 3,
                          ),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(9),
                          child: CachedNetworkImage(
                            imageUrl: UnsplashImages.presetCats[index],
                            fit: BoxFit.cover,
                            placeholder: (_, __) => Container(color: AppColors.warmCream),
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

- [ ] **Step 4: Verify upload flow works**

```bash
flutter run -d chrome --web-port 8080
# Navigate to /#/photo-books → click "Match My Pet" → select a cat photo
# Grid should re-sort, TABBY MATCH badges appear, NBA panel updates
```

- [ ] **Step 5: Commit**

```bash
git add frontend/lib/screens/category/nba_panel.dart frontend/lib/screens/category/upload_modal.dart frontend/lib/providers/recommendations_provider.dart
git commit -m "feat(frontend): add NBA panel, upload modal, and AI matching flow"
```

---

## Task 8: Product Detail Screen

**Files:**
- Modify: `lib/screens/product/product_screen.dart`

**Depends on:** Tasks 1–4, Task 10 (shared widgets)

- [ ] **Step 1: Build product detail screen**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../data/mock_products.dart';
import '../../models/product.dart';
import '../../providers/cart_provider.dart';
import '../../widgets/promo_bar.dart';
import '../../widgets/nav_bar.dart';
import '../../widgets/breadcrumb_bar.dart';
import '../../widgets/fluttershy_badge.dart';

class ProductScreen extends StatelessWidget {
  final String productId;
  const ProductScreen({super.key, required this.productId});

  @override
  Widget build(BuildContext context) {
    final product = mockProducts.firstWhere(
      (p) => p.id == productId,
      orElse: () => mockProducts.first,
    );

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          const PromoBar(),
          const NavBar(currentRoute: '/product'),
          BreadcrumbBar(items: ['Home', 'Photo Books', product.title]),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(48),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Product image
                  Expanded(
                    flex: 5,
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(AppTheme.radiusCard),
                      child: CachedNetworkImage(
                        imageUrl: product.imageUrl,
                        height: 480,
                        fit: BoxFit.cover,
                        placeholder: (_, __) => Container(
                          height: 480,
                          decoration: const BoxDecoration(gradient: AppColors.heroGradient),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 48),

                  // Product info
                  Expanded(
                    flex: 4,
                    child: _ProductInfo(product: product),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ProductInfo extends ConsumerWidget {
  final Product product;
  const _ProductInfo({required this.product});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (product.badge != null) ...[
          FluttershyBadge(badge: product.badge!),
          const SizedBox(height: 12),
        ],
        Text(product.title, style: AppTheme.headlineLarge),
        const SizedBox(height: 8),
        Text(product.subtitle, style: AppTheme.bodyLarge.copyWith(color: AppColors.textSecondary)),
        const SizedBox(height: 12),

        // Rating
        Row(
          children: [
            ...List.generate(5, (i) {
              return Icon(
                i < product.rating.round() ? Icons.star_rounded : Icons.star_outline_rounded,
                color: AppColors.brushedGold,
                size: 20,
              );
            }),
            const SizedBox(width: 8),
            Text('(${product.reviewCount} reviews)', style: AppTheme.bodySmall.copyWith(color: AppColors.textMuted)),
          ],
        ),
        const SizedBox(height: 24),

        Text('\$${product.price.toStringAsFixed(2)}', style: AppTheme.priceLarge),
        const SizedBox(height: 24),

        // Size selector
        Text('SIZE', style: AppTheme.labelLarge),
        const SizedBox(height: 8),
        Row(
          children: ['8×8', '10×10', '12×12'].map((size) {
            final isSelected = size == '8×8';
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.espresso : AppColors.surface,
                  borderRadius: BorderRadius.circular(AppTheme.radiusBadge),
                  border: Border.all(color: isSelected ? AppColors.espresso : AppColors.warmCream),
                ),
                child: Text(
                  size,
                  style: AppTheme.bodyMedium.copyWith(
                    color: isSelected ? Colors.white : AppColors.textPrimary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 32),

        // Add to cart
        MouseRegion(
          cursor: SystemMouseCursors.click,
          child: GestureDetector(
            onTap: () => ref.read(cartProvider.notifier).addItem(product),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 16),
              decoration: BoxDecoration(
                gradient: AppColors.buttonGradient,
                borderRadius: BorderRadius.circular(AppTheme.radiusButton),
              ),
              child: Center(
                child: Text(
                  'Add to Cart — \$${product.price.toStringAsFixed(2)}',
                  style: AppTheme.titleMedium.copyWith(color: Colors.white),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Description
        if (product.description != null) ...[
          const SizedBox(height: 24),
          Text('ABOUT THIS BOOK', style: AppTheme.labelLarge),
          const SizedBox(height: 8),
          Text(product.description!, style: AppTheme.bodyLarge.copyWith(color: AppColors.textSecondary, height: 1.6)),
        ],
      ],
    );
  }
}
```

- [ ] **Step 2: Verify product page renders**

```bash
flutter run -d chrome --web-port 8080
# Navigate to /#/product/pb_welcome_home_24pp
```

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/screens/product/
git commit -m "feat(frontend): build product detail screen with image, info, and add-to-cart"
```

---

## Task 9: Cart Drawer + Beat 2 Trigger

**Files:**
- Create: `lib/screens/cart/cart_drawer.dart`
- Create: `lib/providers/cart_provider.dart`
- Create: `test/providers/cart_provider_test.dart`

**Depends on:** Tasks 1–4

- [ ] **Step 1: Write cart_provider test**

```dart
// test/providers/cart_provider_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttershy/providers/cart_provider.dart';
import 'package:fluttershy/models/product.dart';

void main() {
  final testProduct = Product(
    id: 'test_1', title: 'Test', subtitle: 'Test',
    price: 42.00, rating: 4.0, reviewCount: 10,
    imageUrl: 'https://example.com/img.jpg', category: 'cat',
  );

  group('CartNotifier', () {
    test('starts empty', () {
      final container = ProviderContainer();
      final cart = container.read(cartProvider);
      expect(cart.items, isEmpty);
      expect(cart.total, 0.0);
      container.dispose();
    });

    test('addItem adds product to cart', () {
      final container = ProviderContainer();
      container.read(cartProvider.notifier).addItem(testProduct);
      final cart = container.read(cartProvider);
      expect(cart.items.length, 1);
      expect(cart.items.first.product.id, 'test_1');
      expect(cart.total, 42.00);
      container.dispose();
    });

    test('clear empties cart', () {
      final container = ProviderContainer();
      container.read(cartProvider.notifier).addItem(testProduct);
      container.read(cartProvider.notifier).clear();
      expect(container.read(cartProvider).items, isEmpty);
      container.dispose();
    });
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
flutter test test/providers/cart_provider_test.dart
```

Expected: FAIL — `cart_provider.dart` not found.

- [ ] **Step 3: Write cart_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/product.dart';
import '../models/cart_item.dart';

class CartState {
  final List<CartItem> items;
  final bool isOpen;

  const CartState({this.items = const [], this.isOpen = false});

  double get total => items.fold(0, (sum, item) => sum + item.total);
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);

  CartState copyWith({List<CartItem>? items, bool? isOpen}) {
    return CartState(items: items ?? this.items, isOpen: isOpen ?? this.isOpen);
  }
}

class CartNotifier extends StateNotifier<CartState> {
  CartNotifier() : super(const CartState());

  void addItem(Product product) {
    final existing = state.items.indexWhere((i) => i.product.id == product.id);
    if (existing >= 0) {
      final updated = List<CartItem>.from(state.items);
      updated[existing] = CartItem(product: product, quantity: state.items[existing].quantity + 1);
      state = state.copyWith(items: updated, isOpen: true);
    } else {
      state = state.copyWith(items: [...state.items, CartItem(product: product)], isOpen: true);
    }
  }

  void toggleDrawer() {
    state = state.copyWith(isOpen: !state.isOpen);
  }

  void close() {
    state = state.copyWith(isOpen: false);
  }

  void clear() {
    state = state.copyWith(items: [], isOpen: false);
  }
}

final cartProvider = StateNotifierProvider<CartNotifier, CartState>((ref) {
  return CartNotifier();
});
```

- [ ] **Step 4: Run test to verify it passes**

```bash
flutter test test/providers/cart_provider_test.dart
```

Expected: All tests PASS.

- [ ] **Step 5: Write cart_drawer.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../providers/cart_provider.dart';
import '../../services/api_service.dart';

class CartDrawer extends ConsumerWidget {
  const CartDrawer({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cart = ref.watch(cartProvider);

    if (!cart.isOpen) return const SizedBox.shrink();

    return Stack(
      children: [
        // Backdrop
        GestureDetector(
          onTap: () => ref.read(cartProvider.notifier).close(),
          child: Container(color: Colors.black54),
        ),
        // Drawer
        Positioned(
          right: 0, top: 0, bottom: 0,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOutCubic,
            width: 380,
            decoration: const BoxDecoration(
              color: AppColors.surface,
              boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 24, offset: Offset(-4, 0))],
            ),
            child: Column(
              children: [
                // Header
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Your Cart', style: AppTheme.titleLarge.copyWith(fontSize: 18)),
                      MouseRegion(
                        cursor: SystemMouseCursors.click,
                        child: GestureDetector(
                          onTap: () => ref.read(cartProvider.notifier).close(),
                          child: const Icon(Icons.close, color: AppColors.textMuted, size: 22),
                        ),
                      ),
                    ],
                  ),
                ),

                // Items
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    itemCount: cart.items.length,
                    itemBuilder: (context, index) {
                      final item = cart.items[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.background,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: CachedNetworkImage(
                                imageUrl: item.product.imageUrl,
                                width: 64, height: 64, fit: BoxFit.cover,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(item.product.title, style: AppTheme.titleSmall),
                                  Text(item.product.subtitle, style: AppTheme.bodySmall.copyWith(color: AppColors.textSecondary)),
                                  const SizedBox(height: 6),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text('Qty: ${item.quantity}', style: AppTheme.bodySmall.copyWith(color: AppColors.textMuted)),
                                      Text('\$${item.total.toStringAsFixed(2)}', style: AppTheme.priceSmall),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),

                // Summary + buttons
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 8, offset: const Offset(0, -2))],
                  ),
                  child: Column(
                    children: [
                      _summaryRow('Subtotal', '\$${cart.total.toStringAsFixed(2)}'),
                      _summaryRow('Shipping', 'FREE 🐾', valueColor: const Color(0xFF22C55E)),
                      _summaryRow('Est. delivery', 'May 14–16'),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Total', style: AppTheme.priceSmall),
                          Text('\$${cart.total.toStringAsFixed(2)}', style: AppTheme.priceLarge),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Checkout button
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        decoration: BoxDecoration(
                          gradient: AppColors.buttonGradient,
                          borderRadius: BorderRadius.circular(AppTheme.radiusButton),
                        ),
                        child: Center(
                          child: Text('Proceed to Checkout →', style: AppTheme.titleSmall.copyWith(color: Colors.white)),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Beat 2 trigger
                      _Beat2TriggerButton(),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _summaryRow(String label, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: AppTheme.bodySmall.copyWith(color: AppColors.textSecondary)),
          Text(value, style: AppTheme.bodySmall.copyWith(
            color: valueColor ?? AppColors.textPrimary,
            fontWeight: FontWeight.w600,
          )),
        ],
      ),
    );
  }
}

class _Beat2TriggerButton extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () async {
          // Fire cart_abandoned event
          await ApiService.fireCartAbandoned(ref.read(cartProvider));
        },
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [Color(0xFF1A1A2E), Color(0xFF2D2D4E)]),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.brushedGold.withValues(alpha: 0.3)),
          ),
          child: Column(
            children: [
              Text('DEMO CONTROL', style: AppTheme.labelLarge.copyWith(color: AppColors.brushedGold, fontSize: 9)),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: BoxDecoration(
                  gradient: AppColors.goldGradient,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '🚀 Abandon Cart → Launch Beat 2',
                  style: AppTheme.titleSmall.copyWith(color: const Color(0xFF1A1A2E)),
                ),
              ),
              const SizedBox(height: 6),
              Text('Fires cart_abandoned event to agent', style: AppTheme.bodySmall.copyWith(color: const Color(0xFF666666), fontSize: 9)),
            ],
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 6: Run tests**

```bash
flutter test
```

- [ ] **Step 7: Commit**

```bash
git add frontend/lib/screens/cart/ frontend/lib/providers/cart_provider.dart frontend/test/providers/
git commit -m "feat(frontend): add cart drawer with Beat 2 trigger button"
```

---

## Task 10: Shared Widgets

**Files:**
- Create: `lib/widgets/promo_bar.dart`
- Create: `lib/widgets/nav_bar.dart`
- Create: `lib/widgets/breadcrumb_bar.dart`
- Create: `lib/widgets/product_card.dart`
- Create: `lib/widgets/fluttershy_badge.dart`

**Depends on:** Tasks 1–4

- [ ] **Step 1: Write promo_bar.dart**

```dart
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class PromoBar extends StatelessWidget {
  const PromoBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: const BoxDecoration(gradient: AppColors.promoGradient),
      child: Center(
        child: Text(
          '🐾  Free shipping on pet photo books this week',
          style: AppTheme.bodySmall.copyWith(color: Colors.white, letterSpacing: 1.5),
        ),
      ),
    );
  }
}
```

- [ ] **Step 2: Write nav_bar.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../providers/cart_provider.dart';

class NavBar extends ConsumerWidget {
  final String currentRoute;
  const NavBar({super.key, required this.currentRoute});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cartCount = ref.watch(cartProvider).itemCount;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
      color: AppColors.surface,
      child: Row(
        children: [
          // Logo
          MouseRegion(
            cursor: SystemMouseCursors.click,
            child: GestureDetector(
              onTap: () => context.go('/'),
              child: Row(
                children: [
                  Container(
                    width: 34, height: 34,
                    decoration: BoxDecoration(
                      gradient: AppColors.buttonGradient,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Center(child: Text('🦋', style: TextStyle(fontSize: 18))),
                  ),
                  const SizedBox(width: 10),
                  Text('Fluttershy', style: AppTheme.titleLarge.copyWith(fontSize: 20)),
                ],
              ),
            ),
          ),
          const Spacer(),

          // Nav links
          ...[
            ('Photo Books', '/photo-books'),
            ('Cards', '/photo-books'),
            ('Prints', '/photo-books'),
            ('Gifts', '/photo-books'),
          ].map((item) {
            final isActive = currentRoute == item.$2 && item.$1 == 'Photo Books';
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: MouseRegion(
                cursor: SystemMouseCursors.click,
                child: GestureDetector(
                  onTap: () => context.go(item.$2),
                  child: Text(
                    item.$1,
                    style: AppTheme.bodyMedium.copyWith(
                      color: isActive ? AppColors.textPrimary : AppColors.textMuted,
                      fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                    ),
                  ),
                ),
              ),
            );
          }),
          const SizedBox(width: 16),

          // Search
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.search, size: 16, color: AppColors.textMuted),
                const SizedBox(width: 6),
                Text('Search...', style: AppTheme.bodySmall.copyWith(color: AppColors.textMuted)),
              ],
            ),
          ),
          const SizedBox(width: 16),

          // Cart icon
          MouseRegion(
            cursor: SystemMouseCursors.click,
            child: GestureDetector(
              onTap: () => ref.read(cartProvider.notifier).toggleDrawer(),
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  Container(
                    width: 34, height: 34,
                    decoration: BoxDecoration(
                      color: AppColors.espresso,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Center(child: Icon(Icons.shopping_bag_outlined, color: Colors.white, size: 18)),
                  ),
                  if (cartCount > 0)
                    Positioned(
                      right: -6, top: -6,
                      child: Container(
                        width: 18, height: 18,
                        decoration: BoxDecoration(
                          gradient: AppColors.goldGradient,
                          shape: BoxShape.circle,
                        ),
                        child: Center(
                          child: Text(
                            '$cartCount',
                            style: AppTheme.bodySmall.copyWith(color: AppColors.espresso, fontSize: 9, fontWeight: FontWeight.w700),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 3: Write breadcrumb_bar.dart**

```dart
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class BreadcrumbBar extends StatelessWidget {
  final List<String> items;
  const BreadcrumbBar({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 10),
      color: AppColors.background,
      child: Row(
        children: [
          for (int i = 0; i < items.length; i++) ...[
            if (i > 0) Padding(
              padding: const EdgeInsets.symmetric(horizontal: 6),
              child: Text('›', style: AppTheme.bodySmall.copyWith(color: AppColors.brushedGold)),
            ),
            Text(
              items[i],
              style: AppTheme.bodySmall.copyWith(
                color: i == items.length - 1 ? AppColors.textPrimary : AppColors.textMuted,
                fontWeight: i == items.length - 1 ? FontWeight.w500 : FontWeight.w400,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
```

- [ ] **Step 4: Write product_card.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../models/product.dart';
import '../providers/cart_provider.dart';
import 'fluttershy_badge.dart';

class ProductCard extends ConsumerStatefulWidget {
  final Product product;
  const ProductCard({super.key, required this.product});

  @override
  ConsumerState<ProductCard> createState() => _ProductCardState();
}

class _ProductCardState extends ConsumerState<ProductCard> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    final product = widget.product;

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: () => context.go('/product/${product.id}'),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          transform: Matrix4.identity()..translate(0.0, _hovered ? -4.0 : 0.0),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(AppTheme.radiusCard),
            boxShadow: [
              BoxShadow(
                color: AppColors.cardShadow,
                blurRadius: _hovered ? 20 : 12,
                offset: Offset(0, _hovered ? 6 : 2),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Image
              ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
                child: Stack(
                  children: [
                    CachedNetworkImage(
                      imageUrl: product.imageUrl,
                      width: double.infinity,
                      height: 180,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(
                        height: 180,
                        decoration: const BoxDecoration(gradient: AppColors.heroGradient),
                      ),
                    ),
                    if (product.badge != null)
                      Positioned(
                        top: 8, left: 8,
                        child: FluttershyBadge(badge: product.badge!, matchPercent: product.matchPercent),
                      ),
                  ],
                ),
              ),

              // Info
              Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(product.title, style: AppTheme.titleSmall, maxLines: 1, overflow: TextOverflow.ellipsis),
                    const SizedBox(height: 2),
                    Text(product.subtitle, style: AppTheme.bodySmall.copyWith(color: AppColors.textSecondary)),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            ...List.generate(5, (i) => Icon(
                              i < product.rating.round() ? Icons.star_rounded : Icons.star_outline_rounded,
                              color: AppColors.brushedGold, size: 14,
                            )),
                            const SizedBox(width: 4),
                            Text('(${product.reviewCount})', style: AppTheme.bodySmall.copyWith(color: AppColors.textMuted, fontSize: 10)),
                          ],
                        ),
                        Text('\$${product.price.toStringAsFixed(0)}', style: AppTheme.priceSmall),
                      ],
                    ),
                    const SizedBox(height: 10),
                    GestureDetector(
                      onTap: () {
                        ref.read(cartProvider.notifier).addItem(product);
                      },
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        decoration: BoxDecoration(
                          gradient: AppColors.buttonGradient,
                          borderRadius: BorderRadius.circular(AppTheme.radiusBadge),
                        ),
                        child: Center(
                          child: Text('Add to Cart', style: AppTheme.bodySmall.copyWith(color: Colors.white, fontWeight: FontWeight.w600)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 5: Write fluttershy_badge.dart**

```dart
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../models/product.dart';

class FluttershyBadge extends StatelessWidget {
  final ProductBadge badge;
  final int? matchPercent;
  const FluttershyBadge({super.key, required this.badge, this.matchPercent});

  @override
  Widget build(BuildContext context) {
    final (label, gradient, textColor) = switch (badge) {
      ProductBadge.bestseller => ('✨ BESTSELLER', AppColors.goldGradient, AppColors.espresso),
      ProductBadge.tabbyMatch => ('✨ TABBY MATCH${matchPercent != null ? ' $matchPercent%' : ''}', AppColors.goldGradient, AppColors.espresso),
      ProductBadge.newArrival => (
        'NEW',
        const LinearGradient(colors: [Color(0xFFEF4444), Color(0xFFF87171)]),
        Colors.white,
      ),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(AppTheme.radiusBadge),
      ),
      child: Text(
        label,
        style: AppTheme.bodySmall.copyWith(color: textColor, fontWeight: FontWeight.w700, fontSize: 9),
      ),
    );
  }
}
```

- [ ] **Step 6: Verify shared widgets render in app**

```bash
flutter run -d chrome --web-port 8080
```

Expected: Promo bar, nav bar with logo + links + cart icon, breadcrumbs, product cards with hover effects and badges.

- [ ] **Step 7: Commit**

```bash
git add frontend/lib/widgets/
git commit -m "feat(frontend): add shared widgets — promo bar, nav, breadcrumb, product card, badge"
```

---

## Task 11: DemoOrchestrator + Narrator Strip

**Files:**
- Create: `lib/orchestrator/demo_orchestrator.dart`
- Create: `lib/orchestrator/scene.dart`
- Create: `lib/orchestrator/narrator_strip.dart`
- Create: `lib/providers/orchestrator_provider.dart`
- Modify: `lib/main.dart`

**Depends on:** All screen tasks (5–10)

- [ ] **Step 1: Write scene.dart**

```dart
enum DemoMode { freeform, guided, autopilot }

enum SceneId {
  homeLanding,
  browsePhotoBooks,
  matchMyPet,
  aiMatching,
  viewProduct,
  addToCart,
  abandonCart,
}

class Scene {
  final SceneId id;
  final String label;
  final String narratorText;
  final String? targetRoute;

  const Scene({
    required this.id,
    required this.label,
    required this.narratorText,
    this.targetRoute,
  });
}

const demoScenes = [
  Scene(id: SceneId.homeLanding, label: 'Welcome', narratorText: "Meet Cindy — back on Fluttershy for her kitten Whiskers", targetRoute: '/'),
  Scene(id: SceneId.browsePhotoBooks, label: 'Browse', narratorText: "She's browsing cat-themed photo book templates", targetRoute: '/photo-books'),
  Scene(id: SceneId.matchMyPet, label: 'Upload', narratorText: "She uploads a reference photo of Whiskers"),
  Scene(id: SceneId.aiMatching, label: 'AI Match', narratorText: "NBA panel updates live with cat-matched recommendations"),
  Scene(id: SceneId.viewProduct, label: 'Product', narratorText: "Tabby-pattern templates surface to the top", targetRoute: '/product/pb_welcome_home_24pp'),
  Scene(id: SceneId.addToCart, label: 'Cart', narratorText: "She adds the Welcome Home template to cart"),
  Scene(id: SceneId.abandonCart, label: 'Abandon', narratorText: "She abandons cart — triggering the agent..."),
];
```

- [ ] **Step 2: Write orchestrator_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../orchestrator/scene.dart';

class OrchestratorState {
  final DemoMode mode;
  final int currentSceneIndex;
  final bool isPlaying;

  const OrchestratorState({
    this.mode = DemoMode.freeform,
    this.currentSceneIndex = 0,
    this.isPlaying = false,
  });

  Scene get currentScene => demoScenes[currentSceneIndex];
  bool get isLastScene => currentSceneIndex >= demoScenes.length - 1;
  double get progress => (currentSceneIndex + 1) / demoScenes.length;

  OrchestratorState copyWith({DemoMode? mode, int? currentSceneIndex, bool? isPlaying}) {
    return OrchestratorState(
      mode: mode ?? this.mode,
      currentSceneIndex: currentSceneIndex ?? this.currentSceneIndex,
      isPlaying: isPlaying ?? this.isPlaying,
    );
  }
}

class OrchestratorNotifier extends StateNotifier<OrchestratorState> {
  OrchestratorNotifier() : super(const OrchestratorState());

  void setMode(DemoMode mode) => state = state.copyWith(mode: mode);

  void nextScene() {
    if (!state.isLastScene) {
      state = state.copyWith(currentSceneIndex: state.currentSceneIndex + 1);
    }
  }

  void goToScene(int index) {
    if (index >= 0 && index < demoScenes.length) {
      state = state.copyWith(currentSceneIndex: index);
    }
  }

  void reset() => state = const OrchestratorState();

  void setPlaying(bool playing) => state = state.copyWith(isPlaying: playing);
}

final orchestratorProvider = StateNotifierProvider<OrchestratorNotifier, OrchestratorState>((ref) {
  return OrchestratorNotifier();
});
```

- [ ] **Step 3: Write narrator_strip.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../providers/orchestrator_provider.dart';
import 'scene.dart';

class NarratorStrip extends ConsumerWidget {
  const NarratorStrip({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(orchestratorProvider);

    return Container(
      height: 52,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      decoration: BoxDecoration(
        color: const Color(0xF01A1A2E),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.2), blurRadius: 12, offset: const Offset(0, -2))],
      ),
      child: Row(
        children: [
          // Scene label
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.brushedGold.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              state.currentScene.label,
              style: AppTheme.bodySmall.copyWith(color: AppColors.brushedGold, fontWeight: FontWeight.w600, fontSize: 10),
            ),
          ),
          const SizedBox(width: 16),

          // Narrator text
          Expanded(
            child: Text(
              state.currentScene.narratorText,
              style: AppTheme.bodyMedium.copyWith(color: Colors.white70),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 16),

          // Progress dots
          Row(
            children: List.generate(demoScenes.length, (i) {
              final isActive = i == state.currentSceneIndex;
              final isPast = i < state.currentSceneIndex;
              return Container(
                width: isActive ? 18 : 6,
                height: 6,
                margin: const EdgeInsets.symmetric(horizontal: 2),
                decoration: BoxDecoration(
                  color: isActive ? AppColors.brushedGold : isPast ? AppColors.brushedGold.withValues(alpha: 0.5) : Colors.white24,
                  borderRadius: BorderRadius.circular(3),
                ),
              );
            }),
          ),
          const SizedBox(width: 16),

          // Mode toggle
          ...DemoMode.values.map((mode) {
            final isActive = state.mode == mode;
            final label = switch (mode) {
              DemoMode.freeform => 'Free',
              DemoMode.guided => 'Guided',
              DemoMode.autopilot => 'Auto',
            };
            return Padding(
              padding: const EdgeInsets.only(left: 4),
              child: MouseRegion(
                cursor: SystemMouseCursors.click,
                child: GestureDetector(
                  onTap: () => ref.read(orchestratorProvider.notifier).setMode(mode),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: isActive ? AppColors.brushedGold : Colors.transparent,
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: isActive ? AppColors.brushedGold : Colors.white24),
                    ),
                    child: Text(
                      label,
                      style: AppTheme.bodySmall.copyWith(
                        color: isActive ? const Color(0xFF1A1A2E) : Colors.white54,
                        fontWeight: isActive ? FontWeight.w700 : FontWeight.w400,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ),
              ),
            );
          }),

          const SizedBox(width: 8),

          // Next button (guided mode)
          if (state.mode == DemoMode.guided && !state.isLastScene)
            MouseRegion(
              cursor: SystemMouseCursors.click,
              child: GestureDetector(
                onTap: () => ref.read(orchestratorProvider.notifier).nextScene(),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    gradient: AppColors.goldGradient,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text('Next →', style: AppTheme.bodySmall.copyWith(color: AppColors.espresso, fontWeight: FontWeight.w700, fontSize: 10)),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 4: Wire orchestrator + narrator into main.dart using Stack**

Update `main.dart` to wrap the router outlet in a Stack with the NarratorStrip and CartDrawer overlaid:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/app_theme.dart';
import 'theme/app_colors.dart';
import 'router/app_router.dart';
import 'orchestrator/narrator_strip.dart';
import 'screens/cart/cart_drawer.dart';

void main() {
  runApp(const ProviderScope(child: FluttershyApp()));
}

class FluttershyApp extends StatelessWidget {
  const FluttershyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: appRouter,
      title: 'Fluttershy',
      theme: AppTheme.materialTheme,
      debugShowCheckedModeBanner: false,
      builder: (context, child) {
        return Stack(
          children: [
            // Main content
            Positioned.fill(
              bottom: 52, // narrator strip height
              child: child ?? const SizedBox.shrink(),
            ),
            // Cart drawer overlay
            const Positioned.fill(child: CartDrawer()),
            // Narrator strip
            const Positioned(left: 0, right: 0, bottom: 0, child: NarratorStrip()),
          ],
        );
      },
    );
  }
}
```

- [ ] **Step 5: Verify narrator strip and cart drawer work**

```bash
flutter run -d chrome --web-port 8080
```

Expected: Narrator strip at bottom with scene text, progress dots, mode toggle. Cart drawer opens when cart icon clicked.

- [ ] **Step 6: Commit**

```bash
git add frontend/lib/orchestrator/ frontend/lib/providers/orchestrator_provider.dart frontend/lib/main.dart
git commit -m "feat(frontend): add DemoOrchestrator, narrator strip, and cart drawer integration"
```

---

## Task 12: API Service

**Files:**
- Create: `lib/services/api_service.dart`

**Depends on:** Task 9 (cart provider for event payload)

- [ ] **Step 1: Write api_service.dart**

```dart
import 'package:dio/dio.dart';
import '../providers/cart_provider.dart';
import '../data/mock_customer.dart';

class ApiService {
  static final _dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 5),
  ));

  /// Fire cart_abandoned event to the Beat 2 agent
  static Future<void> fireCartAbandoned(CartState cart) async {
    final payload = {
      'event_type': 'cart_abandoned',
      'customer_id': cindy.id,
      'cart_id': 'cart_${DateTime.now().millisecondsSinceEpoch.toRadixString(16)}',
      'abandoned_at': DateTime.now().toIso8601String(),
      'cart_total': cart.total,
      'items': cart.items.map((item) => {
        'product_id': item.product.id,
        'qty': item.quantity,
        'price': item.product.price,
      }).toList(),
      'tier1_clearance': true,
    };

    try {
      await _dio.post('/api/events', data: payload);
    } catch (e) {
      // In demo mode, log but don't crash
      print('Event dispatch: $e (backend may not be running)');
    }
  }

  /// Fetch NBA recommendations
  static Future<Map<String, dynamic>?> fetchRecommendations(String customerId) async {
    try {
      final response = await _dio.get('/api/nba/recommendations/$customerId');
      return response.data;
    } catch (e) {
      return null; // Fall back to local mock data
    }
  }

  /// Post photo match for re-ranking
  static Future<Map<String, dynamic>?> matchPhoto(String customerId, String imageRef) async {
    try {
      final response = await _dio.post('/api/nba/match', data: {
        'customer_id': customerId,
        'image_ref': imageRef,
      });
      return response.data;
    } catch (e) {
      return null; // Fall back to local mock scores
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/lib/services/
git commit -m "feat(frontend): add API service for NBA and cart_abandoned events"
```

---

## Task 13: Animations (FlutterFX + Custom)

**Files:**
- Create: `lib/animations/page_transitions.dart`
- Create: `lib/animations/card_animations.dart`
- Modify: various screen files to add animation hooks

**Depends on:** All screen tasks

- [ ] **Step 1: Write page_transitions.dart**

```dart
import 'package:flutter/material.dart';

class FadeSlideTransition extends StatelessWidget {
  final Animation<double> animation;
  final Widget child;

  const FadeSlideTransition({super.key, required this.animation, required this.child});

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: CurvedAnimation(parent: animation, curve: Curves.easeInOut),
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0.03, 0),
          end: Offset.zero,
        ).animate(CurvedAnimation(parent: animation, curve: Curves.easeOutCubic)),
        child: child,
      ),
    );
  }
}

class StaggeredFadeIn extends StatelessWidget {
  final int index;
  final Widget child;
  final Duration totalDuration;

  const StaggeredFadeIn({
    super.key,
    required this.index,
    required this.child,
    this.totalDuration = const Duration(milliseconds: 800),
  });

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: Duration(milliseconds: totalDuration.inMilliseconds + (index * 100)),
      curve: Curves.easeOutCubic,
      builder: (context, value, child) {
        return Opacity(
          opacity: value.clamp(0.0, 1.0),
          child: Transform.translate(
            offset: Offset(0, 12 * (1 - value)),
            child: child,
          ),
        );
      },
      child: child,
    );
  }
}
```

- [ ] **Step 2: Write card_animations.dart**

```dart
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class GoldShimmer extends StatefulWidget {
  final Widget child;
  final bool active;

  const GoldShimmer({super.key, required this.child, this.active = false});

  @override
  State<GoldShimmer> createState() => _GoldShimmerState();
}

class _GoldShimmerState extends State<GoldShimmer> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );
    if (widget.active) _controller.repeat();
  }

  @override
  void didUpdateWidget(GoldShimmer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.active && !oldWidget.active) {
      _controller.repeat();
    } else if (!widget.active && oldWidget.active) {
      _controller.stop();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.active) return widget.child;

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment(-1.0 + 2.0 * _controller.value, 0),
              end: Alignment(-0.5 + 2.0 * _controller.value, 0),
              colors: [
                AppColors.brushedGold,
                Colors.white,
                AppColors.brushedGold,
              ],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcIn,
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

class ScaleInWidget extends StatelessWidget {
  final Widget child;
  final Duration delay;

  const ScaleInWidget({super.key, required this.child, this.delay = Duration.zero});

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: const Duration(milliseconds: 400),
      curve: Curves.elasticOut,
      builder: (context, value, child) {
        return Transform.scale(scale: value, child: child);
      },
      child: child,
    );
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/animations/
git commit -m "feat(frontend): add page transitions, staggered fade-in, and gold shimmer animations"
```

---

## Task 14: Polish Pass — Impeccable Agents

**Depends on:** All previous tasks

This task is executed by launching impeccable agents in sequence:

- [ ] **Step 1: Run `impeccable:layout`** — Fix spacing, alignment, visual rhythm across all screens
- [ ] **Step 2: Run `impeccable:colorize`** — Verify Soft Modern palette consistency, contrast ratios
- [ ] **Step 3: Run `impeccable:animate`** — Review animation timing, easing, purpose
- [ ] **Step 4: Run `impeccable:polish`** — Final alignment, spacing, consistency pass
- [ ] **Step 5: Run `impeccable:delight`** — Add micro-interactions, personality touches
- [ ] **Step 6: Run `impeccable:harden`** — Loading states, error states, empty states
- [ ] **Step 7: Run `impeccable:audit`** — Accessibility and performance checks

- [ ] **Step 8: Final verification**

```bash
flutter analyze
flutter test
flutter run -d chrome --web-port 8080
# Walk through full Cindy journey in all 3 demo modes
```

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "polish(frontend): conference-grade finish via impeccable agents"
```

---

## Execution Notes

- **Phase 1 (Tasks 1–4):** Must be sequential — each depends on the previous
- **Phase 2 (Tasks 5–10):** Can be parallelized across 6 swarm agents — each builds an independent screen/widget set
- **Phase 3 (Tasks 11–14):** Sequential — orchestrator needs screens, animations need widgets, polish needs everything
- **Total estimated commits:** 14
- **Key risk:** ShadCN UI API differences from web ShadCN — may need adapter patterns. Check `shadcn_ui` docs when writing widget code.
