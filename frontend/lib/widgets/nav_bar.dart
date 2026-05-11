import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../providers/cart_provider.dart';

class NavBar extends ConsumerWidget {
  const NavBar({super.key});

  static const _navLinks = [
    _NavLink('Photo Books', '/photo-books'),
    _NavLink('Cards', '/photo-books'),
    _NavLink('Prints', '/photo-books'),
    _NavLink('Gifts', '/photo-books'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cartState = ref.watch(cartProvider);

    return Container(
      color: AppColors.white,
      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
      child: Row(
        children: [
          // Logo + brand name
          GestureDetector(
            onTap: () => context.go('/'),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.flutter_dash, color: AppColors.accent, size: 28),
                const SizedBox(width: 8),
                Text(
                  'Fluttershy',
                  style: AppTheme.headlineSmall.copyWith(
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(width: 40),

          // Nav links
          for (final link in _navLinks) ...[
            _NavLinkButton(link: link),
            const SizedBox(width: 24),
          ],

          const Spacer(),

          // Search bar
          SizedBox(
            width: 220,
            height: 36,
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search photo books...',
                hintStyle: AppTheme.bodyMedium.copyWith(
                  color: AppColors.textMuted,
                ),
                prefixIcon: Icon(
                  Icons.search,
                  size: 18,
                  color: AppColors.textMuted,
                ),
                filled: true,
                fillColor: AppColors.background,
                contentPadding: const EdgeInsets.symmetric(vertical: 0),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(AppTheme.radiusButton),
                  borderSide: BorderSide.none,
                ),
              ),
              style: AppTheme.bodyMedium,
            ),
          ),

          const SizedBox(width: 20),

          // Cart icon with badge
          GestureDetector(
            onTap: () =>
                ref.read(cartProvider.notifier).toggleDrawer(),
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                Icon(
                  Icons.shopping_bag_outlined,
                  color: AppColors.textPrimary,
                  size: 24,
                ),
                if (cartState.itemCount > 0)
                  Positioned(
                    right: -8,
                    top: -6,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: const BoxDecoration(
                        gradient: AppColors.buttonGradient,
                        shape: BoxShape.circle,
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 18,
                        minHeight: 18,
                      ),
                      child: Text(
                        '${cartState.itemCount}',
                        textAlign: TextAlign.center,
                        style: AppTheme.bodySmall.copyWith(
                          color: AppColors.white,
                          fontWeight: FontWeight.w700,
                          fontSize: 10,
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
}

class _NavLink {
  final String label;
  final String route;
  const _NavLink(this.label, this.route);
}

class _NavLinkButton extends StatefulWidget {
  final _NavLink link;
  const _NavLinkButton({required this.link});

  @override
  State<_NavLinkButton> createState() => _NavLinkButtonState();
}

class _NavLinkButtonState extends State<_NavLinkButton> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: () => context.go(widget.link.route),
        child: Text(
          widget.link.label,
          style: AppTheme.titleMedium.copyWith(
            color: _hovered ? AppColors.accent : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }
}
