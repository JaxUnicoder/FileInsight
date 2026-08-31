from pathlib import Path

folder_path = input("Enter folder path: ")
folder = Path(folder_path)

if folder.exists() and folder.is_dir():
    print(f"\nScanning folder: {folder}\n")

    for item in folder.rglob("*"):
        if item.is_file():
            print(item)
else:
    print("Invalid folder path.")