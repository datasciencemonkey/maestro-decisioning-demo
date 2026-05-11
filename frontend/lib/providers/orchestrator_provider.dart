import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../orchestrator/scene.dart';

class OrchestratorState {
  final DemoMode mode;
  final int currentSceneIndex;
  final bool isPlaying;

  const OrchestratorState({
    this.mode = DemoMode.freeform,
    this.currentSceneIndex = 0,
    this.isPlaying = false,
  });

  Scene get currentScene => demoScenes[currentSceneIndex];
  bool get isLastScene => currentSceneIndex >= demoScenes.length - 1;
  double get progress => demoScenes.isEmpty
      ? 0
      : currentSceneIndex / (demoScenes.length - 1);

  OrchestratorState copyWith({
    DemoMode? mode,
    int? currentSceneIndex,
    bool? isPlaying,
  }) {
    return OrchestratorState(
      mode: mode ?? this.mode,
      currentSceneIndex: currentSceneIndex ?? this.currentSceneIndex,
      isPlaying: isPlaying ?? this.isPlaying,
    );
  }
}

class OrchestratorNotifier extends StateNotifier<OrchestratorState> {
  OrchestratorNotifier() : super(const OrchestratorState());

  void setMode(DemoMode mode) => state = state.copyWith(mode: mode);

  void nextScene() {
    if (!state.isLastScene) {
      state = state.copyWith(currentSceneIndex: state.currentSceneIndex + 1);
    }
  }

  void goToScene(int index) {
    if (index >= 0 && index < demoScenes.length) {
      state = state.copyWith(currentSceneIndex: index);
    }
  }

  void reset() => state = const OrchestratorState();

  void setPlaying(bool playing) => state = state.copyWith(isPlaying: playing);
}

final orchestratorProvider =
    StateNotifierProvider<OrchestratorNotifier, OrchestratorState>(
  (ref) => OrchestratorNotifier(),
);
