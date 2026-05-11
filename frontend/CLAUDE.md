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
