import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../providers/cart_provider.dart';
import '../data/mock_customer.dart';

class ApiService {
  static final _dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 10),
  ));

  static Future<void> fireCartAbandoned(CartState cart) async {
    try {
      await _dio.post('/api/events', data: {
        'event_type': 'cart_abandoned',
        'customer_id': cindy.id,
        'cart_id': 'cart_${DateTime.now().millisecondsSinceEpoch}',
        'abandoned_at': DateTime.now().toUtc().toIso8601String(),
        'cart_total': cart.total,
        'items': cart.items
            .map((item) => {
                  'product_id': item.product.id,
                  'title': item.product.title,
                  'price': item.product.price,
                  'quantity': item.quantity,
                })
            .toList(),
        'tier1_clearance': true,
      });
    } catch (e) {
      // Backend may not be running — print but don't crash
      debugPrint('fireCartAbandoned error: $e');
    }
  }

  static Future<Map<String, dynamic>?> fetchRecommendations(
      String customerId) async {
    try {
      final response = await _dio.get('/api/nba/recommendations/$customerId');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('fetchRecommendations error: $e');
      return null;
    }
  }

  static Future<Map<String, dynamic>?> matchPhoto(
      String customerId, String imageRef) async {
    try {
      final response = await _dio.post('/api/nba/match', data: {
        'customer_id': customerId,
        'image_ref': imageRef,
      });
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('matchPhoto error: $e');
      return null;
    }
  }
}
