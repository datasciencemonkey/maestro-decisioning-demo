import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'scene.dart';
import '../router/app_router.dart';
import '../providers/orchestrator_provider.dart';
import '../providers/cart_provider.dart';
import '../providers/products_provider.dart';
import '../providers/recommendations_provider.dart';
import '../data/mock_products.dart';
import '../services/api_service.dart';

/// Executes the real action for each scene in guided/autopilot mode.
class DemoController {
  DemoController._();

  /// Advance to next scene AND perform its action (navigate + trigger).
  static Future<void> advanceScene(WidgetRef ref) async {
    final notifier = ref.read(orchestratorProvider.notifier);
    final state = ref.read(orchestratorProvider);

    if (state.isLastScene) return;

    notifier.nextScene();
    final nextScene = ref.read(orchestratorProvider).currentScene;

    await _performAction(ref, nextScene);
  }

  /// Perform the action for a specific scene.
  static Future<void> _performAction(WidgetRef ref, Scene scene) async {
    // Navigate if scene has a target route — use router directly
    if (scene.targetRoute != null) {
      appRouter.go(scene.targetRoute!);
      await Future<void>.delayed(const Duration(milliseconds: 400));
    }

    switch (scene.id) {
      case SceneId.homeLanding:
        break;

      case SceneId.browsePhotoBooks:
        break;

      case SceneId.matchMyPet:
        appRouter.go('/photo-books');
        await Future<void>.delayed(const Duration(milliseconds: 500));
        _showUploadModalGuided();
        break;

      case SceneId.aiMatching:
        _applyMatchScores(ref);
        break;

      case SceneId.viewProduct:
        break;

      case SceneId.addToCart:
        final product = mockProducts.firstWhere(
          (p) => p.id == 'pb_welcome_home_24pp',
        );
        ref.read(cartProvider.notifier).addItem(product);
        break;

      case SceneId.abandonCart:
        final cart = ref.read(cartProvider);
        await ApiService.fireCartAbandoned(cart);
        break;
    }
  }

  /// Show upload modal via router's navigator — auto-dismiss after delay
  static void _showUploadModalGuided() {
    final navContext = appRouter.routerDelegate.navigatorKey.currentContext;
    if (navContext == null) return;

    showDialog(
      context: navContext,
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
            child: const Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.pets, size: 32, color: Color(0xFFC4A87A)),
                SizedBox(height: 12),
                Text(
                  'Selecting Whiskers photo...',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2C1810),
                  ),
                ),
                SizedBox(height: 16),
                SizedBox(
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

    Future<void>.delayed(const Duration(milliseconds: 1500)).then((_) {
      final ctx = appRouter.routerDelegate.navigatorKey.currentContext;
      if (ctx != null && ctx.mounted) {
        Navigator.of(ctx, rootNavigator: true).pop();
      }
    });
  }

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
  static Future<void> runAutopilot(WidgetRef ref) async {
    final notifier = ref.read(orchestratorProvider.notifier);
    notifier.goToScene(0);
    notifier.setMode(DemoMode.autopilot);
    notifier.setPlaying(true);

    for (var i = 0; i < demoScenes.length; i++) {
      if (!ref.read(orchestratorProvider).isPlaying) break;

      final scene = demoScenes[i];
      notifier.goToScene(i);

      try {
        await _performAction(ref, scene);

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
      } catch (_) {
        // Single scene failure must not abort the whole autopilot
        continue;
      }
    }

    notifier.setPlaying(false);
  }
}
