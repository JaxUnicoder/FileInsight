from pathlib import Path
from shutil import copy2
import matplotlib.pyplot as plt


rules = {
    "IMGS": [".jpg", ".jpeg", ".png", ".webp"],
    "MUSICS": [".mp3", ".wav", ".flac"],
    "VIDEOS": [".mp4", ".mkv", ".mov"],
    "FILES": [".pdf", ".docx", ".txt"]
}


def get_unique_path(target_dir, file_name):
    target_path = target_dir / file_name

    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix

    index = 1

    while True:
        new_name = f"{stem}_{index}{suffix}"
        new_path = target_dir / new_name

        if not new_path.exists():
            return new_path

        index += 1


folder_path = input("Enter folder path: ")
folder = Path(folder_path)

if folder.exists() and folder.is_dir():
    print(f"\nScanning folder: {folder}\n")

    output_root = folder.parent / f"{folder.name}_organized"

    stats = {
        "IMGS": {"count": 0, "size": 0},
        "MUSICS": {"count": 0, "size": 0},
        "VIDEOS": {"count": 0, "size": 0},
        "FILES": {"count": 0, "size": 0},
        "OTHERS": {"count": 0, "size": 0}
    }

    for item in folder.rglob("*"):
        if item.is_file():

            suffix = item.suffix.lower()
            category = "OTHERS"

            for category_name, extensions in rules.items():
                if suffix in extensions:
                    category = category_name
                    break

            stats[category]["count"] += 1
            stats[category]["size"] += item.stat().st_size

            target_dir = output_root / category

            target_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            target_path = get_unique_path(
                target_dir,
                item.name
            )

            copy2(item, target_path)

            print(
                f"{item.name} -> "
                f"{category} -> "
                f"{target_path.name}"
            )

    print("\nStatistics:")

    print("\n" + "=" * 40)
    print("FileInsight Statistics")
    print("=" * 40)

    print(f"{'Category':<10} {'Files':>8} {'Size(MB)':>12}")
    print("-" * 40)

    for category, data in stats.items():
        size_mb = data["size"] / (1024 * 1024)

        print(
            f"{category:<10} "
            f"{data['count']:>8} "
            f"{size_mb:>12.2f}"
        )

    print("=" * 40)

    categories = []
    sizes_mb = []

    for category, data in stats.items():
        categories.append(category)
        sizes_mb.append(data["size"] / (1024 * 1024))

    plt.bar(categories, sizes_mb)

    plt.title("File Size by Category")
    plt.xlabel("Category")
    plt.ylabel("Size (MB)")

    plt.show()

else:
    print("Invalid folder path.")