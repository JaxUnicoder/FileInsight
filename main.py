from pathlib import Path

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

    for item in folder.rglob("*"):
        if item.is_file():

            suffix = item.suffix.lower()
            category = "OTHERS"

            for category_name, extensions in rules.items():
                if suffix in extensions:
                    category = category_name
                    break

            print(f"{item.name} -> {category}")

else:
    print("Invalid folder path.")