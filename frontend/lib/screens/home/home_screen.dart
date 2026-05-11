import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../data/mock_products.dart';
import '../../data/unsplash_images.dart';
import '../../widgets/promo_bar.dart';
import '../../widgets/nav_bar.dart';
import '../../widgets/product_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          const PromoBar(),
          const NavBar(),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  _buildHero(context),
                  const SizedBox(height: 40),
                  _buildCategoryTiles(context),
                  const SizedBox(height: 40),
                  _buildFeaturedProducts(context),
                  const SizedBox(height: 60),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHero(BuildContext context) {
    return Container(
      height: 420,
      width: double.infinity,
      decoration: const BoxDecoration(gradient: AppColors.heroGradient),
      child: Stack(
        children: [
          Positioned.fill(
            child: Opacity(
              opacity: 0.3,
              child: CachedNetworkImage(
                imageUrl: UnsplashImages.heroBanner,
                fit: BoxFit.cover,
              ),
            ),
          ),
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'WELCOME HOME COLLECTION',
                  style: AppTheme.labelLarge.copyWith(
                    color: AppColors.brushedGold,
                    letterSpacing: 3,
                  ),
                ),
                const SizedBox(height: 12),
                Text('Pet Photo Books', style: AppTheme.headlineLarge.copyWith(fontSize: 42)),
                const SizedBox(height: 8),
                Text(
                  'Tell their story. Keep their moments.',
                  style: AppTheme.bodyLarge.copyWith(color: AppColors.textSecondary),
                ),
                const SizedBox(height: 24),
                MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: GestureDetector(
                    onTap: () => context.go('/photo-books'),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
                      decoration: BoxDecoration(
                        gradient: AppColors.buttonGradient,
                        borderRadius: BorderRadius.circular(AppTheme.radiusButton),
                      ),
                      child: Text(
                        'Start Creating \u2192',
                        style: AppTheme.titleSmall.copyWith(color: Colors.white),
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

  Widget _buildCategoryTiles(BuildContext context) {
    final categories = [
      ('Photo Books', '\u{1F4DA}', '/photo-books'),
      ('Cards', '\u{1F48C}', '/photo-books'),
      ('Prints', '\u{1F5BC}\uFE0F', '/photo-books'),
      ('Gifts', '\u{1F381}', '/photo-books'),
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 48),
      child: Column(
        children: [
          Text('Shop by Category', style: AppTheme.headlineMedium),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: categories.map((cat) {
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: GestureDetector(
                    onTap: () => context.go(cat.$3),
                    child: Container(
                      width: 160,
                      padding: const EdgeInsets.all(24),
                      decoration: AppTheme.cardDecoration,
                      child: Column(
                        children: [
                          Text(cat.$2, style: const TextStyle(fontSize: 36)),
                          const SizedBox(height: 12),
                          Text(cat.$1, style: AppTheme.titleMedium),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFeaturedProducts(BuildContext context) {
    final featured = mockProducts.take(4).toList();
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 48),
      child: Column(
        children: [
          Text('Featured', style: AppTheme.headlineMedium),
          const SizedBox(height: 24),
          Row(
            children: featured.map((p) {
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: ProductCard(product: p),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
