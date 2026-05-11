import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_theme.dart';
import '../../providers/products_provider.dart';
import '../../widgets/product_card.dart';

class ProductGrid extends ConsumerWidget {
  const ProductGrid({super.key});

  static const _sortLabels = {
    SortOption.recommended: 'Recommended',
    SortOption.priceLow: 'Price: Low to High',
    SortOption.priceHigh: 'Price: High to Low',
    SortOption.rating: 'Top Rated',
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(productsProvider);
    final filtered = state.filtered;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Sort bar
        Row(
          children: [
            Text(
              'Showing ${filtered.length} pet photo books',
              style: AppTheme.bodyMedium.copyWith(
                color: AppColors.textMuted,
              ),
            ),
            const Spacer(),
            _SortDropdown(
              current: state.sort,
              onChanged: (sort) =>
                  ref.read(productsProvider.notifier).setSort(sort),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Product grid
        Expanded(
          child: LayoutBuilder(
            builder: (context, constraints) {
              final crossAxisCount = constraints.maxWidth > 900 ? 3 : 2;
              return GridView.builder(
                padding: EdgeInsets.zero,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: crossAxisCount,
                  childAspectRatio: 0.62,
                  crossAxisSpacing: 20,
                  mainAxisSpacing: 20,
                ),
                itemCount: filtered.length,
                itemBuilder: (context, index) =>
                    ProductCard(product: filtered[index]),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _SortDropdown extends StatefulWidget {
  final SortOption current;
  final ValueChanged<SortOption> onChanged;

  const _SortDropdown({required this.current, required this.onChanged});

  @override
  State<_SortDropdown> createState() => _SortDropdownState();
}

class _SortDropdownState extends State<_SortDropdown> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        decoration: BoxDecoration(
          color: _hovered ? AppColors.warmCream : AppColors.surface,
          borderRadius: BorderRadius.circular(AppTheme.radiusButton),
          border: Border.all(
            color: AppColors.warmCream,
          ),
        ),
        child: DropdownButtonHideUnderline(
          child: DropdownButton<SortOption>(
            value: widget.current,
            isDense: true,
            icon: const Icon(
              Icons.unfold_more,
              size: 16,
              color: AppColors.textMuted,
            ),
            style: AppTheme.bodyMedium.copyWith(
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w600,
            ),
            dropdownColor: AppColors.surface,
            borderRadius: BorderRadius.circular(AppTheme.radiusCard),
            items: SortOption.values.map((option) {
              return DropdownMenuItem(
                value: option,
                child: Text(
                  ProductGrid._sortLabels[option]!,
                  style: AppTheme.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                    fontWeight: option == widget.current
                        ? FontWeight.w600
                        : FontWeight.w400,
                  ),
                ),
              );
            }).toList(),
            onChanged: (v) {
              if (v != null) widget.onChanged(v);
            },
          ),
        ),
      ),
    );
  }
}
