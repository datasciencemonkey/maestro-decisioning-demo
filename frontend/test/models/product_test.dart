import 'package:flutter_test/flutter_test.dart';
import 'package:fluttershy/models/product.dart';

void main() {
  group('Product', () {
    test('creates with required fields', () {
      final product = Product(
        id: 'pb_welcome_home_24pp',
        title: 'Welcome Home 24pg',
        subtitle: 'Tabby collection · Hardcover',
        price: 42.00,
        rating: 4.9,
        reviewCount: 124,
        imageUrl: 'https://example.com/image.jpg',
        category: 'cat',
      );
      expect(product.id, 'pb_welcome_home_24pp');
      expect(product.price, 42.00);
      expect(product.badge, isNull);
    });

    test('supports badge and matchPercent', () {
      final product = Product(
        id: 'pb_test',
        title: 'Test',
        subtitle: 'Test',
        price: 29.00,
        rating: 4.0,
        reviewCount: 10,
        imageUrl: 'https://example.com/img.jpg',
        category: 'cat',
        badge: ProductBadge.bestseller,
        matchPercent: 98,
      );
      expect(product.badge, ProductBadge.bestseller);
      expect(product.matchPercent, 98);
    });

    test('copyWith updates badge and matchPercent', () {
      final product = Product(
        id: 'pb_test',
        title: 'Test',
        subtitle: 'Test',
        price: 29.00,
        rating: 4.0,
        reviewCount: 10,
        imageUrl: 'https://example.com/img.jpg',
        category: 'cat',
      );
      final updated = product.copyWith(
        badge: ProductBadge.tabbyMatch,
        matchPercent: 95,
      );
      expect(updated.badge, ProductBadge.tabbyMatch);
      expect(updated.matchPercent, 95);
      expect(updated.id, product.id);
      expect(updated.price, product.price);
    });
  });
}
