import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/product.dart';
import '../data/mock_products.dart';

enum PetFilter { all, cat, dog }

enum SortOption { recommended, priceLow, priceHigh, rating }

class ProductsState {
  final List<Product> products;
  final PetFilter filter;
  final SortOption sort;

  const ProductsState({
    this.products = const [],
    this.filter = PetFilter.all,
    this.sort = SortOption.recommended,
  });

  ProductsState copyWith({
    List<Product>? products,
    PetFilter? filter,
    SortOption? sort,
  }) {
    return ProductsState(
      products: products ?? this.products,
      filter: filter ?? this.filter,
      sort: sort ?? this.sort,
    );
  }

  List<Product> get filtered {
    var result = List<Product>.from(products);

    // Apply pet filter
    if (filter != PetFilter.all) {
      final cat = filter.name; // 'cat' or 'dog'
      result = result
          .where((p) => p.category == cat || p.category == 'all')
          .toList();
    }

    // Apply sort
    switch (sort) {
      case SortOption.recommended:
        // Products with matchPercent first, then by rating
        result.sort((a, b) {
          final aMatch = a.matchPercent ?? 0;
          final bMatch = b.matchPercent ?? 0;
          if (aMatch != bMatch) return bMatch.compareTo(aMatch);
          return b.rating.compareTo(a.rating);
        });
      case SortOption.priceLow:
        result.sort((a, b) => a.price.compareTo(b.price));
      case SortOption.priceHigh:
        result.sort((a, b) => b.price.compareTo(a.price));
      case SortOption.rating:
        result.sort((a, b) => b.rating.compareTo(a.rating));
    }

    return result;
  }
}

class ProductsNotifier extends StateNotifier<ProductsState> {
  ProductsNotifier()
      : super(ProductsState(products: List.of(mockProducts)));

  void setFilter(PetFilter filter) {
    state = state.copyWith(filter: filter);
  }

  void setSort(SortOption sort) {
    state = state.copyWith(sort: sort);
  }

  void applyMatch(Map<String, int> matchScores) {
    final updated = state.products.map((p) {
      final score = matchScores[p.id];
      if (score != null) {
        return p.copyWith(
          matchPercent: score,
          badge: score >= 90 ? ProductBadge.tabbyMatch : p.badge,
        );
      }
      return p;
    }).toList();
    // Switch to Cats filter and Recommended sort so re-ranked results are visible
    state = state.copyWith(
      products: updated,
      filter: PetFilter.cat,
      sort: SortOption.recommended,
    );
  }
}

final productsProvider =
    StateNotifierProvider<ProductsNotifier, ProductsState>(
        (ref) => ProductsNotifier());
