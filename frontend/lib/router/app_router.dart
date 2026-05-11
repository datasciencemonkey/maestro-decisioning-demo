import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/home/home_screen.dart';
import '../screens/category/category_screen.dart';
import '../screens/product/product_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      name: 'home',
      pageBuilder: (context, state) => CustomTransitionPage(
        child: const HomeScreen(),
        transitionsBuilder: _sharedAxisTransition,
      ),
    ),
    GoRoute(
      path: '/photo-books',
      name: 'category',
      pageBuilder: (context, state) => CustomTransitionPage(
        child: const CategoryScreen(),
        transitionsBuilder: _sharedAxisTransition,
      ),
    ),
    GoRoute(
      path: '/product/:id',
      name: 'product',
      pageBuilder: (context, state) {
        final productId = state.pathParameters['id']!;
        return CustomTransitionPage(
          child: ProductScreen(productId: productId),
          transitionsBuilder: _sharedAxisTransition,
        );
      },
    ),
  ],
);

Widget _sharedAxisTransition(
  BuildContext context,
  Animation<double> animation,
  Animation<double> secondaryAnimation,
  Widget child,
) {
  return FadeTransition(
    opacity: CurvedAnimation(parent: animation, curve: Curves.easeInOut),
    child: SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0.05, 0),
        end: Offset.zero,
      ).animate(CurvedAnimation(parent: animation, curve: Curves.easeOutCubic)),
      child: child,
    ),
  );
}
