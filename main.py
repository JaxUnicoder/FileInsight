# main.py

from pathlib import Path

from organizer import organize_files
from file_stats import print_statistics
from visualizer import show_charts


folder_path = input("Enter folder path: ")
folder = Path(folder_path)

if folder.exists() and folder.is_dir():
    print(f"\nScanning folder: {folder}\n")

    stats, output_root = organize_files(folder)

    print_statistics(stats)
    show_charts(stats)

    print("\nDone! Organized files saved to:")
    print(output_root)

else:
    print("Invalid folder path.")