import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

abstract final class AppTheme {
  static TextStyle get _heading => GoogleFonts.dmSerifDisplay(
        color: AppColors.textPrimary,
      );

  static TextStyle get _body => GoogleFonts.inter(
        color: AppColors.textPrimary,
      );

  static TextStyle get headlineLarge =>
      _heading.copyWith(fontSize: 32, fontWeight: FontWeight.w400);
  static TextStyle get headlineMedium =>
      _heading.copyWith(fontSize: 24, fontWeight: FontWeight.w400);
  static TextStyle get headlineSmall =>
      _heading.copyWith(fontSize: 18, fontWeight: FontWeight.w400);

  static TextStyle get titleLarge =>
      _body.copyWith(fontSize: 16, fontWeight: FontWeight.w700);
  static TextStyle get titleMedium =>
      _body.copyWith(fontSize: 14, fontWeight: FontWeight.w600);
  static TextStyle get titleSmall =>
      _body.copyWith(fontSize: 12, fontWeight: FontWeight.w600);

  static TextStyle get bodyLarge =>
      _body.copyWith(fontSize: 14, fontWeight: FontWeight.w400);
  static TextStyle get bodyMedium =>
      _body.copyWith(fontSize: 12, fontWeight: FontWeight.w400);
  static TextStyle get bodySmall =>
      _body.copyWith(fontSize: 11, fontWeight: FontWeight.w400);

  static TextStyle get labelLarge => _body.copyWith(
        fontSize: 11,
        fontWeight: FontWeight.w600,
        letterSpacing: 1.5,
        color: AppColors.textMuted,
      );

  static TextStyle get priceLarge =>
      _body.copyWith(fontSize: 18, fontWeight: FontWeight.w700);
  static TextStyle get priceSmall =>
      _body.copyWith(fontSize: 14, fontWeight: FontWeight.w700);

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
