import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'scene.dart';
import '../providers/orchestrator_provider.dart';
import '../providers/cart_provider.dart';
import '../providers/products_provider.dart';
import '../providers/recommendations_provider.dart';
import '../data/mock_products.dart';
import '../services/api_service.dart';

/// Executes the real action for each scene in guided/autopilot mode.
/// Call [advanceScene] from the narrator strip's Next button.
class DemoController {
  DemoController._();

  /// Advance to next scene AND perform its action (navigate + trigger).
  static Future<void> advanceScene(BuildContext context, WidgetRef ref) async {
    final notifier = ref.read(orchestratorProvider.notifier);
    final state = ref.read(orchestratorProvider);

    if (state.isLastScene) return;

    // Move to next scene
    notifier.nextScene();
    final nextScene = ref.read(orchestratorProvider).currentScene;

    // Perform the scene's action
    await _performAction(context, ref, nextScene);
  }

  /// Perform the action for a specific scene.
  static Future<void> _performAction(
    BuildContext context,
    WidgetRef ref,
    Scene scene,
  ) async {
    // Navigate if scene has a target route
    if (scene.targetRoute != null && context.mounted) {
      context.go(scene.targetRoute!);
      // Small delay for route transition to settle
      await Future<void>.delayed(const Duration(milliseconds: 400));
    }

    // Perform scene-specific action
    switch (scene.id) {
      case SceneId.homeLanding:
        // Just navigate (handled above)
        break;

      case SceneId.browsePhotoBooks:
        // Just navigate to /photo-books (handled above)
        break;

      case SceneId.matchMyPet:
        // Ensure we're on /photo-books, then show upload modal
        if (context.mounted) {
          context.go('/photo-books');
          await Future<void>.delayed(const Duration(milliseconds: 500));
          if (context.mounted) {
            _showUploadModalGuided(context);
          }
        }
        break;

      case SceneId.aiMatching:
        // Trigger the match programmatically (simulate photo selection)
        _applyMatchScores(ref);
        break;

      case SceneId.viewProduct:
        // Navigate to the Welcome Home product (handled above via targetRoute)
        break;

      case SceneId.addToCart:
        // Add Welcome Home product to cart
        final product = mockProducts.firstWhere(
          (p) => p.id == 'pb_welcome_home_24pp',
        );
        ref.read(cartProvider.notifier).addItem(product);
        break;

      case SceneId.abandonCart:
        // Fire the cart_abandoned event
        final cart = ref.read(cartProvider);
        await ApiService.fireCartAbandoned(cart);
        break;
    }
  }

  /// Show upload modal in guided mode — auto-dismiss after delay
  static void _showUploadModalGuided(BuildContext context) {
    showDialog(
      context: context,
      barrierColor: Colors.black54,
      builder: (_) => Center(
        child: Material(
          color: Colors.transparent,
          child: Container(
            width: 300,
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: const [
                BoxShadow(color: Colors.black26, blurRadius: 24),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.pets, size: 32, color: Color(0xFFC4A87A)),
                const SizedBox(height: 12),
                const Text(
                  'Selecting Whiskers photo...',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2C1810),
                  ),
                ),
                const SizedBox(height: 16),
                const SizedBox(
                  width: 36,
                  height: 36,
                  child: CircularProgressIndicator(
                    strokeWidth: 3,
                    color: Color(0xFFC4A87A),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    // Auto-dismiss after analysis time
    Future<void>.delayed(const Duration(milliseconds: 1500)).then((_) {
      if (context.mounted) {
        Navigator.of(context, rootNavigator: true).pop();
      }
    });
  }

  /// Apply match scores programmatically (same as upload_modal)
  static void _applyMatchScores(WidgetRef ref) {
    ref.read(productsProvider.notifier).applyMatch({
      'pb_welcome_home_24pp': 96,
      'pb_whisker_tales': 91,
      'pb_kitten_cuddles': 88,
      'pb_playful_paws': 93,
      'pb_first_year': 74,
      'pb_classic_soft': 62,
      'pb_paw_prints': 70,
    });
    ref.read(recommendationsProvider.notifier).updateAfterMatch();
  }

  /// Run the full demo in autopilot mode with realistic delays.
  static Future<void> runAutopilot(BuildContext context, WidgetRef ref) async {
    final notifier = ref.read(orchestratorProvider.notifier);
    notifier.reset();
    notifier.setMode(DemoMode.autopilot);
    notifier.setPlaying(true);

    for (var i = 0; i < demoScenes.length; i++) {
      if (!ref.read(orchestratorProvider).isPlaying) break;

      final scene = demoScenes[i];
      notifier.goToScene(i);

      if (!context.mounted) break;
      await _performAction(context, ref, scene);

      // Realistic inter-scene delay
      final delay = switch (scene.id) {
        SceneId.homeLanding => 2000,
        SceneId.browsePhotoBooks => 2500,
        SceneId.matchMyPet => 2000,
        SceneId.aiMatching => 1500,
        SceneId.viewProduct => 2500,
        SceneId.addToCart => 2000,
        SceneId.abandonCart => 1000,
      };
      await Future<void>.delayed(Duration(milliseconds: delay));
    }

    notifier.setPlaying(false);
  }
}
