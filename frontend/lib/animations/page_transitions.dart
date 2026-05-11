import 'package:flutter/material.dart';

class FadeSlideTransition extends StatelessWidget {
  const FadeSlideTransition({
    super.key,
    required this.animation,
    required this.child,
  });

  final Animation<double> animation;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final curvedFade = CurvedAnimation(
      parent: animation,
      curve: Curves.easeInOut,
    );
    final curvedSlide = CurvedAnimation(
      parent: animation,
      curve: Curves.easeOutCubic,
    );
    final slideOffset = Tween<Offset>(
      begin: const Offset(0.03, 0),
      end: Offset.zero,
    ).animate(curvedSlide);

    return FadeTransition(
      opacity: curvedFade,
      child: SlideTransition(
        position: slideOffset,
        child: child,
      ),
    );
  }
}

class StaggeredFadeIn extends StatelessWidget {
  const StaggeredFadeIn({
    super.key,
    required this.index,
    required this.child,
    this.totalDuration = const Duration(milliseconds: 800),
  });

  final int index;
  final Widget child;
  final Duration totalDuration;

  @override
  Widget build(BuildContext context) {
    final duration = totalDuration + Duration(milliseconds: index * 100);

    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: 1),
      duration: duration,
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
