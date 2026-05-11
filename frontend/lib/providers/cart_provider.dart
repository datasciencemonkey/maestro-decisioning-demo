import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/product.dart';
import '../models/cart_item.dart';

class CartState {
  final List<CartItem> items;
  final bool isOpen;

  const CartState({this.items = const [], this.isOpen = false});

  double get total => items.fold(0, (sum, item) => sum + item.total);
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);

  CartState copyWith({List<CartItem>? items, bool? isOpen}) {
    return CartState(
      items: items ?? this.items,
      isOpen: isOpen ?? this.isOpen,
    );
  }
}

class CartNotifier extends StateNotifier<CartState> {
  CartNotifier() : super(const CartState());

  void addItem(Product product) {
    final existing = state.items.indexWhere((i) => i.product.id == product.id);
    if (existing >= 0) {
      final updated = List<CartItem>.from(state.items);
      updated[existing] = CartItem(
        product: product,
        quantity: state.items[existing].quantity + 1,
      );
      state = state.copyWith(items: updated, isOpen: true);
    } else {
      state = state.copyWith(
        items: [...state.items, CartItem(product: product)],
        isOpen: true,
      );
    }
  }

  void toggleDrawer() => state = state.copyWith(isOpen: !state.isOpen);
  void close() => state = state.copyWith(isOpen: false);
  void clear() => state = state.copyWith(items: [], isOpen: false);
}

final cartProvider =
    StateNotifierProvider<CartNotifier, CartState>((ref) => CartNotifier());
