from pathlib import Path
from shutil import copy2

rules = {
    "IMGS": [".jpg", ".jpeg", ".png", ".webp"],
    "MUSICS": [".mp3", ".wav", ".flac"],
    "VIDEOS": [".mp4", ".mkv", ".mov"],
    "FILES": [".pdf", ".docx", ".txt"]
}

folder_path = input("Enter folder path: ")
folder = Path(folder_path)

if folder.exists() and folder.is_dir():
    print(f"\nScanning folder: {folder}\n")

    output_root = folder.parent / f"{folder.name}_organized"

    for item in folder.rglob("*"):
        if item.is_file():

            suffix = item.suffix.lower()
            category = "OTHERS"

            for category_name, extensions in rules.items():
                if suffix in extensions:
                    category = category_name
                    break

            target_dir = output_root / category

            target_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            target_path = target_dir / item.name

            copy2(item, target_path)

            print(f"{item.name} -> {category}")

    print(f"\nDone! Organized files saved to:")
    print(output_root)

else:
    print("Invalid folder path.")