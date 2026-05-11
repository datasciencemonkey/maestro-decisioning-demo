import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class PromoBar extends StatelessWidget {
  const PromoBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: const BoxDecoration(gradient: AppColors.promoGradient),
      child: Text(
        '\u{1F43E} Free shipping on pet photo books this week',
        textAlign: TextAlign.center,
        style: AppTheme.bodyMedium.copyWith(
          color: AppColors.white,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}
