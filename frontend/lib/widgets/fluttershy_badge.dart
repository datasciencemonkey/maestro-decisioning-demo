import 'package:flutter/material.dart';
import '../models/product.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class FluttershyBadge extends StatelessWidget {
  final ProductBadge badge;
  final int? matchPercent;

  const FluttershyBadge({
    super.key,
    required this.badge,
    this.matchPercent,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        gradient: _gradient,
        borderRadius: BorderRadius.circular(AppTheme.radiusBadge),
      ),
      child: Text(
        _label,
        style: AppTheme.bodySmall.copyWith(
          color: AppColors.white,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  String get _label {
    switch (badge) {
      case ProductBadge.bestseller:
        return 'BESTSELLER';
      case ProductBadge.tabbyMatch:
        final pct = matchPercent ?? 0;
        return 'TABBY MATCH $pct%';
      case ProductBadge.newArrival:
        return 'NEW';
    }
  }

  LinearGradient get _gradient {
    switch (badge) {
      case ProductBadge.bestseller:
        return AppColors.goldGradient;
      case ProductBadge.tabbyMatch:
        return AppColors.goldGradient;
      case ProductBadge.newArrival:
        return const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppColors.badgeNew, Color(0xFFDC2626)],
        );
    }
  }
}
