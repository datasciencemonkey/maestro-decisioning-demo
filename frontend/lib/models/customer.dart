class Customer {
  final String id;
  final String name;
  final String petName;
  final String petType;
  final String timezone;
  final bool isRepeatBuyer;
  final String preferredChannel;

  const Customer({
    required this.id,
    required this.name,
    required this.petName,
    required this.petType,
    required this.timezone,
    required this.isRepeatBuyer,
    required this.preferredChannel,
  });
}
