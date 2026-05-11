enum ProductBadge { bestseller, tabbyMatch, newArrival }

class Product {
  final String id;
  final String title;
  final String subtitle;
  final double price;
  final double rating;
  final int reviewCount;
  final String imageUrl;
  final String category; // 'cat', 'dog', 'all'
  final ProductBadge? badge;
  final int? matchPercent;
  final String? description;

  const Product({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.price,
    required this.rating,
    required this.reviewCount,
    required this.imageUrl,
    required this.category,
    this.badge,
    this.matchPercent,
    this.description,
  });

  Product copyWith({
    ProductBadge? badge,
    int? matchPercent,
  }) {
    return Product(
      id: id,
      title: title,
      subtitle: subtitle,
      price: price,
      rating: rating,
      reviewCount: reviewCount,
      imageUrl: imageUrl,
      category: category,
      badge: badge ?? this.badge,
      matchPercent: matchPercent ?? this.matchPercent,
      description: description,
    );
  }
}
