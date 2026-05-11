import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_colors.dart';
import 'scene.dart';
import 'demo_controller.dart';
import '../providers/orchestrator_provider.dart';

class NarratorStrip extends ConsumerWidget {
  const NarratorStrip({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final orchestrator = ref.watch(orchestratorProvider);
    final notifier = ref.read(orchestratorProvider.notifier);

    return Container(
      height: 52,
      decoration: const BoxDecoration(
        color: Color(0xF01A1A2E),
        boxShadow: [
          BoxShadow(
            color: Color(0x40000000),
            blurRadius: 12,
            offset: Offset(0, -4),
          ),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          // Left: Scene label pill
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.brushedGold.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              orchestrator.currentScene.label,
              style: const TextStyle(
                color: AppColors.brushedGold,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(width: 16),

          // Center: Narrator text
          Expanded(
            child: Text(
              orchestrator.currentScene.narratorText,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 13,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 16),

          // Right: Progress dots
          _ProgressDots(
            total: demoScenes.length,
            current: orchestrator.currentSceneIndex,
          ),
          const SizedBox(width: 12),

          // Right: Mode toggle
          _ModeToggle(
            currentMode: orchestrator.mode,
            onModeChanged: (mode) {
              notifier.setMode(mode);
              // If switching to autopilot, start the full run
              if (mode == DemoMode.autopilot) {
                DemoController.runAutopilot(context, ref);
              }
            },
          ),
          const SizedBox(width: 12),

          // Right: Next button (guided mode only, not on last scene)
          if (orchestrator.mode == DemoMode.guided &&
              !orchestrator.isLastScene)
            _NextButton(
              onPressed: () => DemoController.advanceScene(context, ref),
            ),
        ],
      ),
    );
  }
}

class _ProgressDots extends StatelessWidget {
  final int total;
  final int current;

  const _ProgressDots({required this.total, required this.current});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(total, (i) {
        final isActive = i == current;
        final isPast = i < current;
        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 2),
          width: isActive ? 18 : 6,
          height: 6,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(3),
            color: isActive
                ? AppColors.brushedGold
                : isPast
                    ? AppColors.brushedGold.withValues(alpha: 0.5)
                    : Colors.white24,
          ),
        );
      }),
    );
  }
}

class _ModeToggle extends StatelessWidget {
  final DemoMode currentMode;
  final ValueChanged<DemoMode> onModeChanged;

  const _ModeToggle({
    required this.currentMode,
    required this.onModeChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _ModeButton(
          label: 'Free',
          isActive: currentMode == DemoMode.freeform,
          onTap: () => onModeChanged(DemoMode.freeform),
        ),
        const SizedBox(width: 4),
        _ModeButton(
          label: 'Guided',
          isActive: currentMode == DemoMode.guided,
          onTap: () => onModeChanged(DemoMode.guided),
        ),
        const SizedBox(width: 4),
        _ModeButton(
          label: 'Auto',
          isActive: currentMode == DemoMode.autopilot,
          onTap: () => onModeChanged(DemoMode.autopilot),
        ),
      ],
    );
  }
}

class _ModeButton extends StatelessWidget {
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _ModeButton({
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: isActive ? AppColors.brushedGold : Colors.transparent,
            borderRadius: BorderRadius.circular(6),
            border: isActive
                ? null
                : Border.all(color: Colors.white24, width: 1),
          ),
          child: Text(
            label,
            style: TextStyle(
              color: isActive ? const Color(0xFF1A1A2E) : Colors.white70,
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }
}

class _NextButton extends StatelessWidget {
  final VoidCallback onPressed;

  const _NextButton({required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          decoration: BoxDecoration(
            gradient: AppColors.goldGradient,
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Text(
            'Next \u2192',
            style: TextStyle(
              color: Color(0xFF1A1A2E),
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }
}
