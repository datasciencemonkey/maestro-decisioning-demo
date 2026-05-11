import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/recommendation.dart';
import '../data/unsplash_images.dart';

final _initialRecommendations = <Recommendation>[
  Recommendation(
    productId: 'pb_welcome_home_24pp',
    title: 'Welcome Home 24pg',
    imageUrl: UnsplashImages.productImages[0],
    matchPercent: 72,
  ),
  Recommendation(
    productId: 'pb_whisker_tales',
    title: 'Whisker Tales',
    imageUrl: UnsplashImages.productImages[3],
    matchPercent: 65,
  ),
  Recommendation(
    productId: 'pb_kitten_cuddles',
    title: 'Kitten Cuddles',
    imageUrl: UnsplashImages.productImages[5],
    matchPercent: 58,
  ),
];

final _matchedRecommendations = <Recommendation>[
  Recommendation(
    productId: 'pb_welcome_home_24pp',
    title: 'Welcome Home 24pg',
    imageUrl: UnsplashImages.productImages[0],
    matchPercent: 96,
  ),
  Recommendation(
    productId: 'pb_playful_paws',
    title: 'Playful Paws',
    imageUrl: UnsplashImages.productImages[6],
    matchPercent: 93,
  ),
  Recommendation(
    productId: 'pb_whisker_tales',
    title: 'Whisker Tales',
    imageUrl: UnsplashImages.productImages[3],
    matchPercent: 91,
  ),
];

class RecommendationsNotifier extends StateNotifier<List<Recommendation>> {
  RecommendationsNotifier() : super(_initialRecommendations);

  void updateAfterMatch() {
    state = _matchedRecommendations;
  }

  void reset() {
    state = _initialRecommendations;
  }
}

final recommendationsProvider =
    StateNotifierProvider<RecommendationsNotifier, List<Recommendation>>(
        (ref) => RecommendationsNotifier());
