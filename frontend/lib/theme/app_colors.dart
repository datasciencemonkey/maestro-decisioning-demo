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
  static const cardShadow = Color(0x0F2C1810);

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
