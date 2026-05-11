import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../data/unsplash_images.dart';
import '../../providers/products_provider.dart';
import '../../providers/recommendations_provider.dart';

void showUploadModal(BuildContext context) {
  showDialog(
    context: context,
    barrierColor: AppColors.espresso.withValues(alpha: 0.5),
    builder: (_) => const _UploadModalDialog(),
  );
}

class _UploadModalDialog extends ConsumerStatefulWidget {
  const _UploadModalDialog();

  @override
  ConsumerState<_UploadModalDialog> createState() => _UploadModalDialogState();
}

class _UploadModalDialogState extends ConsumerState<_UploadModalDialog> {
  bool _analyzing = false;

  Future<void> _onPhotoSelected() async {
    setState(() => _analyzing = true);

    try {
      await Future<void>.delayed(const Duration(milliseconds: 1200));

      if (!mounted) return;

      // Apply match scores to products
      ref.read(productsProvider.notifier).applyMatch({
        'pb_welcome_home_24pp': 96,
        'pb_whisker_tales': 91,
        'pb_kitten_cuddles': 88,
        'pb_playful_paws': 93,
        'pb_first_year': 74,
        'pb_classic_soft': 62,
        'pb_paw_prints': 70,
      });

      // Update recommendations with higher-scoring matches
      ref.read(recommendationsProvider.notifier).updateAfterMatch();

      // Small delay to let UI settle before dismissing
      await Future<void>.delayed(const Duration(milliseconds: 200));

      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (_) {
      // Swallow errors so the demo never crashes on stage
      if (mounted) {
        Navigator.of(context).pop();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Material(
        color: Colors.transparent,
        child: Container(
          width: 380,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(AppTheme.radiusCard),
            boxShadow: const [
              BoxShadow(
                color: AppColors.cardShadow,
                blurRadius: 24,
                offset: Offset(0, 8),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildHeader(),
              const SizedBox(height: 20),
              if (_analyzing) _buildAnalyzing() else _buildPhotoGrid(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Icon(Icons.pets, size: 20, color: AppColors.brushedGold),
            const SizedBox(width: 8),
            Text('Match My Pet', style: AppTheme.headlineSmall),
          ],
        ),
        GestureDetector(
          onTap: () => Navigator.of(context).pop(),
          child: Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: AppColors.warmCream,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              Icons.close,
              size: 18,
              color: AppColors.textSecondary,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPhotoGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Select a photo of your pet',
          style: AppTheme.bodyMedium.copyWith(color: AppColors.textSecondary),
        ),
        const SizedBox(height: 14),
        GridView.count(
          crossAxisCount: 2,
          mainAxisSpacing: 10,
          crossAxisSpacing: 10,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          children: UnsplashImages.presetCats.map((url) {
            return GestureDetector(
              onTap: _onPhotoSelected,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(AppTheme.radiusBadge),
                child: CachedNetworkImage(
                  imageUrl: url,
                  fit: BoxFit.cover,
                  placeholder: (_, __) => Container(
                    color: AppColors.warmCream,
                    child: const Center(
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: AppColors.brushedGold,
                        ),
                      ),
                    ),
                  ),
                  errorWidget: (_, __, ___) => Container(
                    color: AppColors.warmCream,
                    child: const Icon(Icons.image, color: AppColors.textMuted),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildAnalyzing() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 40),
      child: Column(
        children: [
          const SizedBox(
            width: 48,
            height: 48,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              color: AppColors.brushedGold,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Analyzing your pet...',
            style: AppTheme.titleMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Matching with photo book styles',
            style: AppTheme.bodySmall.copyWith(
              color: AppColors.textMuted,
            ),
          ),
        ],
      ),
    );
  }
}
