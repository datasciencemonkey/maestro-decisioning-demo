import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/cart_item.dart';
import '../../providers/cart_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';

class CartDrawer extends ConsumerWidget {
  const CartDrawer({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cart = ref.watch(cartProvider);
    if (!cart.isOpen) return const SizedBox.shrink();

    return Stack(
      children: [
        // Backdrop
        GestureDetector(
          onTap: () => ref.read(cartProvider.notifier).close(),
          child: Container(color: Colors.black54),
        ),
        // Drawer
        Positioned(
          top: 0,
          bottom: 0,
          right: 0,
          width: 380,
          child: Semantics(
            label: 'Shopping cart',
            child: Material(
            elevation: 16,
            shadowColor: AppColors.cardShadow,
            child: Container(
              color: AppColors.white,
              child: Column(
                children: [
                  _Header(ref: ref),
                  Expanded(
                    child: cart.items.isEmpty
                        ? _EmptyState()
                        : ListView.separated(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 20, vertical: 12),
                            itemCount: cart.items.length,
                            separatorBuilder: (_, __) =>
                                const Divider(height: 24),
                            itemBuilder: (_, i) =>
                                _CartItemRow(item: cart.items[i]),
                          ),
                  ),
                  if (cart.items.isNotEmpty) ...[
                    _Summary(cart: cart),
                    _CheckoutButton(),
                  ],
                  _DemoControl(ref: ref),
                ],
              ),
            ),
          ),
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------
class _Header extends StatelessWidget {
  final WidgetRef ref;
  const _Header({required this.ref});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.warmCream)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('Your Cart', style: AppTheme.headlineSmall),
          IconButton(
            icon: const Icon(Icons.close, size: 20, color: AppColors.mocha),
            onPressed: () => ref.read(cartProvider.notifier).close(),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------
class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.shopping_cart_outlined,
                size: 48, color: AppColors.textMuted),
            const SizedBox(height: 12),
            Text('Your cart is empty',
                style:
                    AppTheme.bodyLarge.copyWith(color: AppColors.textMuted)),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Single cart item row
// ---------------------------------------------------------------------------
class _CartItemRow extends StatelessWidget {
  final CartItem item;
  const _CartItemRow({required this.item});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Thumbnail
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: CachedNetworkImage(
            imageUrl: item.product.imageUrl,
            width: 64,
            height: 64,
            fit: BoxFit.cover,
            placeholder: (_, __) => Container(
              width: 64,
              height: 64,
              color: AppColors.warmCream,
            ),
            errorWidget: (_, __, ___) => Container(
              width: 64,
              height: 64,
              color: AppColors.warmCream,
              child: const Icon(Icons.image_not_supported,
                  size: 24, color: AppColors.textMuted),
            ),
          ),
        ),
        const SizedBox(width: 12),
        // Details
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(item.product.title,
                  style: AppTheme.titleMedium, maxLines: 1,
                  overflow: TextOverflow.ellipsis),
              const SizedBox(height: 2),
              Text(item.product.subtitle,
                  style: AppTheme.bodySmall
                      .copyWith(color: AppColors.textSecondary)),
              const SizedBox(height: 6),
              Text('Qty: ${item.quantity}',
                  style: AppTheme.bodySmall
                      .copyWith(color: AppColors.textMuted)),
            ],
          ),
        ),
        // Price
        Text('\$${item.total.toStringAsFixed(2)}',
            style: AppTheme.priceSmall),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Summary section
// ---------------------------------------------------------------------------
class _Summary extends StatelessWidget {
  final CartState cart;
  const _Summary({required this.cart});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.warmCream)),
      ),
      child: Column(
        children: [
          _summaryRow('Subtotal', '\$${cart.total.toStringAsFixed(2)}'),
          const SizedBox(height: 6),
          _summaryRow(
            'Shipping',
            'FREE \u{1F43E}',
            valueColor: const Color(0xFF16A34A),
          ),
          const SizedBox(height: 6),
          _summaryRow('Est. Delivery', 'May 14\u201316',
              valueStyle: AppTheme.bodyMedium
                  .copyWith(color: AppColors.textSecondary)),
          const SizedBox(height: 10),
          const Divider(height: 1, color: AppColors.warmCream),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Total', style: AppTheme.titleLarge),
              Text('\$${cart.total.toStringAsFixed(2)}',
                  style: AppTheme.priceLarge),
            ],
          ),
        ],
      ),
    );
  }

  Widget _summaryRow(String label, String value,
      {Color? valueColor, TextStyle? valueStyle}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style:
                AppTheme.bodyMedium.copyWith(color: AppColors.textSecondary)),
        Text(value,
            style: valueStyle ??
                AppTheme.bodyMedium.copyWith(
                    color: valueColor ?? AppColors.textPrimary,
                    fontWeight: FontWeight.w600)),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Checkout button
// ---------------------------------------------------------------------------
class _CheckoutButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
      child: SizedBox(
        width: double.infinity,
        height: 48,
        child: DecoratedBox(
          decoration: BoxDecoration(
            gradient: AppColors.buttonGradient,
            borderRadius: BorderRadius.circular(AppTheme.radiusButton),
          ),
          child: ElevatedButton(
            onPressed: () {
              // Checkout flow — placeholder for Beat 3
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppTheme.radiusButton),
              ),
            ),
            child: Text(
              'Proceed to Checkout \u2192',
              style: AppTheme.titleMedium.copyWith(color: AppColors.white),
            ),
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Demo control section
// ---------------------------------------------------------------------------
class _DemoControl extends StatefulWidget {
  final WidgetRef ref;
  const _DemoControl({required this.ref});

  @override
  State<_DemoControl> createState() => _DemoControlState();
}

class _DemoControlState extends State<_DemoControl> {
  bool _firing = false;

  Future<void> _onTap() async {
    if (_firing) return;
    setState(() => _firing = true);
    try {
      await ApiService.fireCartAbandoned(widget.ref.read(cartProvider));
    } finally {
      if (mounted) setState(() => _firing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF1A1A2E), Color(0xFF2D2D4E)],
        ),
        border: Border(
          top: BorderSide(
              color: AppColors.brushedGold.withValues(alpha: 0.4), width: 1),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Label
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
            decoration: BoxDecoration(
              border:
                  Border.all(color: AppColors.brushedGold.withValues(alpha: 0.5)),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              'DEMO CONTROL',
              style: AppTheme.labelLarge.copyWith(
                color: AppColors.brushedGold,
                fontSize: 10,
                letterSpacing: 2.0,
              ),
            ),
          ),
          const SizedBox(height: 12),
          // Beat 2 trigger button
          Semantics(
            label: 'Launch Beat 2 demo',
            child: SizedBox(
              width: double.infinity,
              height: 44,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: AppColors.goldGradient,
                  borderRadius: BorderRadius.circular(AppTheme.radiusButton),
                ),
                child: ElevatedButton(
                  onPressed: _firing ? null : _onTap,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    disabledBackgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(AppTheme.radiusButton),
                    ),
                  ),
                  child: _firing
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: AppColors.espresso),
                        )
                      : Text(
                          '\u{1F680} Abandon Cart \u2192 Launch Beat 2',
                          style: AppTheme.titleMedium
                              .copyWith(color: AppColors.espresso),
                        ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Fires cart_abandoned event to start cross-campaign agent',
            style: AppTheme.bodySmall.copyWith(
              color: AppColors.brushedGold.withValues(alpha: 0.6),
              fontSize: 10,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
