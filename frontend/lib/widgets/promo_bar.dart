import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class PromoBar extends StatefulWidget {
  const PromoBar({super.key});

  @override
  State<PromoBar> createState() => _PromoBarState();
}

class _PromoBarState extends State<PromoBar>
    with SingleTickerProviderStateMixin {
  late final AnimationController _shimmer;

  @override
  void initState() {
    super.initState();
    _shimmer = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat();
  }

  @override
  void dispose() {
    _shimmer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: const BoxDecoration(gradient: AppColors.promoGradient),
      child: AnimatedBuilder(
        animation: _shimmer,
        builder: (context, child) {
          return ShaderMask(
            shaderCallback: (bounds) {
              final dx = _shimmer.value * 2 - 0.5;
              return LinearGradient(
                begin: Alignment(dx - 0.3, 0),
                end: Alignment(dx + 0.3, 0),
                colors: const [
                  Color(0x00FFFFFF),
                  Color(0x55FFFFFF),
                  Color(0x00FFFFFF),
                ],
              ).createShader(bounds);
            },
            blendMode: BlendMode.srcATop,
            child: child!,
          );
        },
        child: Text(
          '\u{1F43E} Free shipping on pet photo books this week',
          textAlign: TextAlign.center,
          style: AppTheme.bodyMedium.copyWith(
            color: AppColors.white,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.3,
          ),
        ),
      ),
    );
  }
}
