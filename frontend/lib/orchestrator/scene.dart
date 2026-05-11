enum DemoMode { freeform, guided, autopilot }

enum SceneId {
  homeLanding,
  browsePhotoBooks,
  matchMyPet,
  aiMatching,
  viewProduct,
  addToCart,
  abandonCart,
}

class Scene {
  final SceneId id;
  final String label;
  final String narratorText;
  final String? targetRoute;

  const Scene({
    required this.id,
    required this.label,
    required this.narratorText,
    this.targetRoute,
  });
}

const demoScenes = [
  Scene(
    id: SceneId.homeLanding,
    label: 'Welcome',
    narratorText: "Meet Cindy \u2014 back on Fluttershy for her kitten Whiskers",
    targetRoute: '/',
  ),
  Scene(
    id: SceneId.browsePhotoBooks,
    label: 'Browse',
    narratorText: "She's browsing cat-themed photo book templates",
    targetRoute: '/photo-books',
  ),
  Scene(
    id: SceneId.matchMyPet,
    label: 'Upload',
    narratorText: "She uploads a reference photo of Whiskers",
  ),
  Scene(
    id: SceneId.aiMatching,
    label: 'AI Match',
    narratorText: "NBA panel updates live with cat-matched recommendations",
  ),
  Scene(
    id: SceneId.viewProduct,
    label: 'Product',
    narratorText: "Tabby-pattern templates surface to the top",
    targetRoute: '/product/pb_welcome_home_24pp',
  ),
  Scene(
    id: SceneId.addToCart,
    label: 'Cart',
    narratorText: "She adds the Welcome Home template to cart",
  ),
  Scene(
    id: SceneId.abandonCart,
    label: 'Abandon',
    narratorText: "She abandons cart \u2014 triggering the agent...",
  ),
];
