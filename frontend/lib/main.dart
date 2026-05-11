import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/app_theme.dart';
import 'router/app_router.dart';
import 'orchestrator/demo_controller.dart';
import 'orchestrator/narrator_strip.dart';
import 'screens/cart/cart_drawer.dart';

void main() {
  runApp(const ProviderScope(child: FluttershyApp()));
}

class FluttershyApp extends StatelessWidget {
  const FluttershyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: appRouter,
      title: 'Fluttershy',
      theme: AppTheme.materialTheme,
      debugShowCheckedModeBanner: false,
      builder: (context, child) {
        return Navigator(
          key: rootNavigatorKey,
          onGenerateRoute: (_) => MaterialPageRoute(
            builder: (_) => Stack(
              children: [
                Positioned.fill(
                  bottom: 52,
                  child: child ?? const SizedBox.shrink(),
                ),
                const Positioned.fill(child: CartDrawer()),
                const Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  child: NarratorStrip(),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
