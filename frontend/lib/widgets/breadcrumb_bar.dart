import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class BreadcrumbItem {
  final String label;
  final VoidCallback? onTap;

  const BreadcrumbItem({required this.label, this.onTap});
}

class BreadcrumbBar extends StatelessWidget {
  final List<BreadcrumbItem> items;

  const BreadcrumbBar({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: const Duration(milliseconds: 300),
      builder: (context, opacity, child) {
        return Opacity(opacity: opacity, child: child);
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
        child: Row(
          children: [
            for (int i = 0; i < items.length; i++) ...[
              if (i > 0)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Text(
                    '\u203A',
                    style: AppTheme.bodyMedium.copyWith(
                      color: AppColors.accent,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              _BreadcrumbLabel(
                item: items[i],
                isLast: i == items.length - 1,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _BreadcrumbLabel extends StatefulWidget {
  final BreadcrumbItem item;
  final bool isLast;

  const _BreadcrumbLabel({required this.item, required this.isLast});

  @override
  State<_BreadcrumbLabel> createState() => _BreadcrumbLabelState();
}

class _BreadcrumbLabelState extends State<_BreadcrumbLabel> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    final isClickable = widget.item.onTap != null && !widget.isLast;

    return MouseRegion(
      onEnter: isClickable ? (_) => setState(() => _hovered = true) : null,
      onExit: isClickable ? (_) => setState(() => _hovered = false) : null,
      child: GestureDetector(
        onTap: isClickable ? widget.item.onTap : null,
        child: Text(
          widget.item.label,
          style: AppTheme.bodyMedium.copyWith(
            color: widget.isLast
                ? AppColors.textPrimary
                : (_hovered ? AppColors.accent : AppColors.textMuted),
            fontWeight: widget.isLast ? FontWeight.w700 : FontWeight.w400,
          ),
        ),
      ),
    );
  }
}
