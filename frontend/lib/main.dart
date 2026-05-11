import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/app_theme.dart';
import 'router/app_router.dart';

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
    );
  }
}
