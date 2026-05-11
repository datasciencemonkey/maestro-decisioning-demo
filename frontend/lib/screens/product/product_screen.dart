import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/mock_products.dart';
import '../../models/product.dart';
import '../../providers/cart_provider.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../widgets/breadcrumb_bar.dart';
import '../../widgets/fluttershy_badge.dart';
import '../../widgets/nav_bar.dart';
import '../../widgets/promo_bar.dart';

class ProductScreen extends StatelessWidget {
  final String productId;
  const ProductScreen({super.key, required this.productId});

  @override
  Widget build(BuildContext context) {
    final product = mockProducts.firstWhere(
      (p) => p.id == productId,
      orElse: () => mockProducts.first,
    );

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          const PromoBar(),
          const NavBar(),
          BreadcrumbBar(
            items: [
              BreadcrumbItem(
                label: 'Home',
                onTap: () => context.go('/'),
              ),
              BreadcrumbItem(
                label: 'Photo Books',
                onTap: () => context.go('/photo-books'),
              ),
              BreadcrumbItem(label: product.title),
            ],
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 24),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Left column — product image
                  Expanded(
                    flex: 5,
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(
                        AppTheme.radiusCard,
                      ),
                      child: CachedNetworkImage(
                        imageUrl: product.imageUrl,
                        height: 480,
                        width: double.infinity,
                        fit: BoxFit.cover,
                        placeholder: (_, __) => Container(
                          height: 480,
                          decoration: BoxDecoration(
                            color: AppColors.warmCream,
                            borderRadius: BorderRadius.circular(
                              AppTheme.radiusCard,
                            ),
                          ),
                          child: const Center(
                            child: CircularProgressIndicator(
                              color: AppColors.accent,
                              strokeWidth: 2,
                            ),
                          ),
                        ),
                        errorWidget: (_, __, ___) => Container(
                          height: 480,
                          decoration: BoxDecoration(
                            color: AppColors.warmCream,
                            borderRadius: BorderRadius.circular(
                              AppTheme.radiusCard,
                            ),
                          ),
                          child: const Center(
                            child: Icon(
                              Icons.image_not_supported_outlined,
                              size: 48,
                              color: AppColors.textMuted,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 48),

                  // Right column — product info
                  Expanded(
                    flex: 4,
                    child: _ProductInfo(product: product),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ProductInfo extends ConsumerStatefulWidget {
  final Product product;
  const _ProductInfo({required this.product});

  @override
  ConsumerState<_ProductInfo> createState() => _ProductInfoState();
}

class _ProductInfoState extends ConsumerState<_ProductInfo> {
  static const _sizes = ['8\u00D78', '10\u00D710', '12\u00D712'];
  int _selectedSize = 0;

  @override
  Widget build(BuildContext context) {
    final product = widget.product;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Badge
        if (product.badge != null) ...[
          FluttershyBadge(
            badge: product.badge!,
            matchPercent: product.matchPercent,
          ),
          const SizedBox(height: 12),
        ],

        // Title
        Text(product.title, style: AppTheme.headlineLarge),
        const SizedBox(height: 6),

        // Subtitle
        Text(
          product.subtitle,
          style: AppTheme.bodyLarge.copyWith(color: AppColors.textSecondary),
        ),
        const SizedBox(height: 14),

        // Star rating row
        Row(
          children: [
            for (int i = 0; i < 5; i++)
              Icon(
                i < product.rating.round()
                    ? Icons.star_rounded
                    : Icons.star_border_rounded,
                color: AppColors.brushedGold,
                size: 20,
              ),
            const SizedBox(width: 8),
            Text(
              '${product.rating}',
              style: AppTheme.titleMedium,
            ),
            const SizedBox(width: 6),
            Text(
              '(${product.reviewCount} reviews)',
              style: AppTheme.bodyMedium.copyWith(
                color: AppColors.textMuted,
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // Price
        Text(
          '\$${product.price.toStringAsFixed(2)}',
          style: AppTheme.priceLarge,
        ),
        const SizedBox(height: 24),

        // Size selector
        Text(
          'SIZE',
          style: AppTheme.labelLarge,
        ),
        const SizedBox(height: 10),
        Row(
          children: List.generate(_sizes.length, (i) {
            final selected = i == _selectedSize;
            return Padding(
              padding: EdgeInsets.only(right: i < _sizes.length - 1 ? 10 : 0),
              child: GestureDetector(
                onTap: () => setState(() => _selectedSize = i),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: selected ? AppColors.espresso : AppColors.white,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(
                      color: selected
                          ? AppColors.espresso
                          : AppColors.warmCream,
                      width: 1.5,
                    ),
                  ),
                  child: Text(
                    _sizes[i],
                    style: AppTheme.titleMedium.copyWith(
                      color: selected
                          ? AppColors.white
                          : AppColors.textPrimary,
                    ),
                  ),
                ),
              ),
            );
          }),
        ),
        const SizedBox(height: 28),

        // Add to Cart button
        SizedBox(
          width: double.infinity,
          height: 48,
          child: DecoratedBox(
            decoration: BoxDecoration(
              gradient: AppColors.buttonGradient,
              borderRadius: BorderRadius.circular(AppTheme.radiusButton),
            ),
            child: ElevatedButton(
              onPressed: () {
                ref.read(cartProvider.notifier).addItem(product);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppTheme.radiusButton),
                ),
              ),
              child: Text(
                'Add to Cart \u2014 \$${product.price.toStringAsFixed(2)}',
                style: AppTheme.titleMedium.copyWith(
                  color: AppColors.white,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ),

        // Description
        if (product.description != null) ...[
          const SizedBox(height: 32),
          Text('ABOUT THIS BOOK', style: AppTheme.labelLarge),
          const SizedBox(height: 10),
          Text(
            product.description!,
            style: AppTheme.bodyLarge.copyWith(
              color: AppColors.textSecondary,
              height: 1.6,
            ),
          ),
        ],
      ],
    );
  }
}
