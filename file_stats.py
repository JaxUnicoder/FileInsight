# statistics.py

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"

    if size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"

    return f"{size_bytes / (1024 ** 3):.2f} GB"


def print_statistics(stats):
    print("\nStatistics:")

    print("\n" + "=" * 40)
    print("FileInsight Statistics")
    print("=" * 40)

    print(f"{'Category':<10} {'Files':>8} {'Size':>12}")
    print("-" * 40)

    for category, data in stats.items():
        readable_size = format_size(data["size"])

        print(
            f"{category:<10} "
            f"{data['count']:>8} "
            f"{readable_size:>12}"
        )

    print("=" * 40)