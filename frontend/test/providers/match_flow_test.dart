import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttershy/providers/products_provider.dart';
import 'package:fluttershy/providers/recommendations_provider.dart';
import 'package:fluttershy/models/product.dart';

void main() {
  group('Match flow', () {
    test('applyMatch updates badges without null errors', () {
      final container = ProviderContainer();

      // Before match: Welcome Home has bestseller badge
      final before = container.read(productsProvider);
      final welcomeHome = before.products.firstWhere(
        (p) => p.id == 'pb_welcome_home_24pp',
      );
      expect(welcomeHome.badge, ProductBadge.bestseller);

      // Apply match scores (same as upload_modal)
      container.read(productsProvider.notifier).applyMatch({
        'pb_welcome_home_24pp': 96,
        'pb_whisker_tales': 91,
        'pb_kitten_cuddles': 88,
        'pb_playful_paws': 93,
        'pb_first_year': 74,
        'pb_classic_soft': 62,
        'pb_paw_prints': 70,
      });

      // After match: filter should be cat, sort should be recommended
      final after = container.read(productsProvider);
      expect(after.filter, PetFilter.cat);
      expect(after.sort, SortOption.recommended);

      // Welcome Home should now have tabbyMatch badge (score 96 >= 90)
      final updatedWelcome = after.products.firstWhere(
        (p) => p.id == 'pb_welcome_home_24pp',
      );
      expect(updatedWelcome.badge, ProductBadge.tabbyMatch);
      expect(updatedWelcome.matchPercent, 96);

      // Whisker Tales should have tabbyMatch (score 91 >= 90)
      final whiskerTales = after.products.firstWhere(
        (p) => p.id == 'pb_whisker_tales',
      );
      expect(whiskerTales.badge, ProductBadge.tabbyMatch);
      expect(whiskerTales.matchPercent, 91);

      // Kitten Cuddles score 88 < 90, should NOT have tabbyMatch
      final kittenCuddles = after.products.firstWhere(
        (p) => p.id == 'pb_kitten_cuddles',
      );
      expect(kittenCuddles.badge, isNull);
      expect(kittenCuddles.matchPercent, 88);

      // Filtered list should be sorted by matchPercent desc
      final filtered = after.filtered;
      expect(filtered.first.id, 'pb_welcome_home_24pp'); // 96%
      expect(filtered[1].matchPercent, greaterThanOrEqualTo(filtered[2].matchPercent ?? 0));

      container.dispose();
    });

    test('recommendations update after match', () {
      final container = ProviderContainer();

      final before = container.read(recommendationsProvider);
      expect(before.length, 3);

      container.read(recommendationsProvider.notifier).updateAfterMatch();

      final after = container.read(recommendationsProvider);
      expect(after.length, 3);
      // After match, scores should be higher
      expect(after.first.matchPercent, greaterThan(before.first.matchPercent));

      container.dispose();
    });
  });
}
