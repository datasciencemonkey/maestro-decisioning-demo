import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';
import '../../widgets/promo_bar.dart';
import '../../widgets/nav_bar.dart';
import '../../widgets/breadcrumb_bar.dart';
import 'filter_sidebar.dart';
import 'product_grid.dart';
import 'nba_panel.dart';

class CategoryScreen extends StatelessWidget {
  const CategoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        children: [
          const PromoBar(),
          const NavBar(),
          BreadcrumbBar(
            items: const [
              BreadcrumbItem(label: 'Home'),
              BreadcrumbItem(label: 'Photo Books'),
              BreadcrumbItem(label: 'Pet Photo Books'),
            ],
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  FilterSidebar(),
                  SizedBox(width: 24),
                  Expanded(child: ProductGrid()),
                  SizedBox(width: 24),
                  NbaPanel(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
