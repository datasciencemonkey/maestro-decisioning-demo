import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttershy/theme/app_theme.dart';
import 'package:fluttershy/theme/app_colors.dart';

void main() {
  testWidgets('App theme applies correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.materialTheme,
          home: const Scaffold(
            body: Center(child: Text('Fluttershy')),
          ),
        ),
      ),
    );
    expect(find.text('Fluttershy'), findsOneWidget);
    final scaffold = tester.widget<Scaffold>(find.byType(Scaffold));
    expect(scaffold.backgroundColor, isNull); // uses theme default
  });

  test('AppColors palette is defined', () {
    expect(AppColors.espresso, const Color(0xFF2C1810));
    expect(AppColors.brushedGold, const Color(0xFFC4A87A));
    expect(AppColors.linen, const Color(0xFFFAF8F6));
  });
}
