import 'package:flutter/material.dart';
import '../models/product.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class FluttershyBadge extends StatefulWidget {
  final ProductBadge badge;
  final int? matchPercent;

  const FluttershyBadge({
    super.key,
    required this.badge,
    this.matchPercent,
  });

  @override
  State<FluttershyBadge> createState() => _FluttershyBadgeState();
}

class _FluttershyBadgeState extends State<FluttershyBadge>
    with SingleTickerProviderStateMixin {
  AnimationController? _shimmer;

  bool get _isTabbyMatch => widget.badge == ProductBadge.tabbyMatch;

  @override
  void initState() {
    super.initState();
    _syncShimmer();
  }

  @override
  void didUpdateWidget(FluttershyBadge oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.badge != widget.badge) {
      _syncShimmer();
    }
  }

  void _syncShimmer() {
    if (_isTabbyMatch && _shimmer == null) {
      _shimmer = AnimationController(
        vsync: this,
        duration: const Duration(seconds: 2),
      )..repeat();
    } else if (!_isTabbyMatch && _shimmer != null) {
      _shimmer!.dispose();
      _shimmer = null;
    }
  }

  @override
  void dispose() {
    _shimmer?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final child = Container(
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

    if (!_isTabbyMatch) return child;

    return AnimatedBuilder(
      animation: _shimmer!,
      builder: (context, inner) {
        final dx = _shimmer!.value * 2 - 0.5;
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment(dx - 0.3, 0),
              end: Alignment(dx + 0.3, 0),
              colors: const [
                Color(0x00FFFFFF),
                Color(0x44FFFFFF),
                Color(0x00FFFFFF),
              ],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: inner,
        );
      },
      child: child,
    );
  }

  String get _label {
    switch (widget.badge) {
      case ProductBadge.bestseller:
        return 'BESTSELLER';
      case ProductBadge.tabbyMatch:
        final pct = widget.matchPercent ?? 0;
        return 'TABBY MATCH $pct%';
      case ProductBadge.newArrival:
        return 'NEW';
    }
  }

  LinearGradient get _gradient {
    switch (widget.badge) {
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
