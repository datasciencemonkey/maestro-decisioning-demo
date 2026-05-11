import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../providers/products_provider.dart';
import 'upload_modal.dart';

class FilterSidebar extends ConsumerWidget {
  const FilterSidebar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(productsProvider);

    return SizedBox(
      width: 220,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Filters', style: AppTheme.headlineSmall),
          const SizedBox(height: 20),

          // Pet type filter
          Text('PET TYPE', style: AppTheme.labelLarge),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _FilterChip(
                label: 'All',
                isActive: state.filter == PetFilter.all,
                onTap: () =>
                    ref.read(productsProvider.notifier).setFilter(PetFilter.all),
              ),
              _FilterChip(
                label: '\u{1F431} Cats',
                isActive: state.filter == PetFilter.cat,
                onTap: () =>
                    ref.read(productsProvider.notifier).setFilter(PetFilter.cat),
              ),
              _FilterChip(
                label: '\u{1F415} Dogs',
                isActive: state.filter == PetFilter.dog,
                onTap: () =>
                    ref.read(productsProvider.notifier).setFilter(PetFilter.dog),
              ),
            ],
          ),
          const SizedBox(height: 28),

          // Book size filter
          Text('BOOK SIZE', style: AppTheme.labelLarge),
          const SizedBox(height: 10),
          const _SizeCheckbox(label: '8\u00d78 Standard', initialValue: true),
          const SizedBox(height: 6),
          const _SizeCheckbox(label: '10\u00d710 Large', initialValue: false),
          const SizedBox(height: 6),
          const _SizeCheckbox(label: '12\u00d712 XL', initialValue: false),

          const Spacer(),

          // Match My Pet trigger card
          _MatchMyPetCard(
            onTap: () => showUploadModal(context),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}

class _FilterChip extends StatefulWidget {
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _FilterChip({
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  State<_FilterChip> createState() => _FilterChipState();
}

class _FilterChipState extends State<_FilterChip> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: widget.isActive ? AppColors.espresso : AppColors.warmCream,
            borderRadius: BorderRadius.circular(AppTheme.radiusButton),
            border: Border.all(
              color: widget.isActive
                  ? AppColors.espresso
                  : (_hovered ? AppColors.mocha : Colors.transparent),
            ),
          ),
          child: Text(
            widget.label,
            style: AppTheme.bodyMedium.copyWith(
              color: widget.isActive
                  ? AppColors.white
                  : AppColors.textSecondary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }
}

class _SizeCheckbox extends StatefulWidget {
  final String label;
  final bool initialValue;

  const _SizeCheckbox({required this.label, required this.initialValue});

  @override
  State<_SizeCheckbox> createState() => _SizeCheckboxState();
}

class _SizeCheckboxState extends State<_SizeCheckbox> {
  late bool _checked;

  @override
  void initState() {
    super.initState();
    _checked = widget.initialValue;
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => setState(() => _checked = !_checked),
      child: Row(
        children: [
          SizedBox(
            width: 18,
            height: 18,
            child: Checkbox(
              value: _checked,
              onChanged: (v) => setState(() => _checked = v ?? false),
              activeColor: AppColors.espresso,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(4),
              ),
              side: const BorderSide(color: AppColors.mocha, width: 1.5),
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              visualDensity: VisualDensity.compact,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            widget.label,
            style: AppTheme.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

class _MatchMyPetCard extends StatefulWidget {
  final VoidCallback onTap;

  const _MatchMyPetCard({required this.onTap});

  @override
  State<_MatchMyPetCard> createState() => _MatchMyPetCardState();
}

class _MatchMyPetCardState extends State<_MatchMyPetCard> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: _hovered
                ? AppColors.brushedGold.withValues(alpha: 0.06)
                : AppColors.surface,
            borderRadius: BorderRadius.circular(AppTheme.radiusCard),
            border: Border.all(
              color: AppColors.brushedGold,
              width: 1.5,
              strokeAlign: BorderSide.strokeAlignInside,
            ),
          ),
          child: Column(
            children: [
              Icon(
                Icons.camera_alt_outlined,
                color: AppColors.brushedGold,
                size: 28,
              ),
              const SizedBox(height: 8),
              Text(
                'Match My Pet',
                style: AppTheme.titleMedium.copyWith(
                  color: AppColors.brushedGold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'AI-powered photo matching',
                style: AppTheme.bodySmall.copyWith(
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
