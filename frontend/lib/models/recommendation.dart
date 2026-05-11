class Recommendation {
  final String productId;
  final String title;
  final String imageUrl;
  final int matchPercent;

  const Recommendation({
    required this.productId,
    required this.title,
    required this.imageUrl,
    required this.matchPercent,
  });
}
