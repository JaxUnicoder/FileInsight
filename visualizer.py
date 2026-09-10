# visualizer.py

import matplotlib.pyplot as plt


def show_charts(stats):
    categories = []
    sizes_mb = []

    for category, data in stats.items():
        categories.append(category)
        sizes_mb.append(data["size"] / (1024 ** 2))

    plt.figure()
    plt.bar(categories, sizes_mb)
    plt.title("File Size by Category")
    plt.xlabel("Category")
    plt.ylabel("Size (MB)")
    plt.show()

    pie_labels = []
    pie_sizes = []

    for category, data in stats.items():
        if data["size"] > 0:
            pie_labels.append(category)
            pie_sizes.append(data["size"])

    plt.figure()
    plt.pie(
        pie_sizes,
        labels=pie_labels,
        autopct="%1.1f%%"
    )
    plt.title("Storage Distribution by Category")
    plt.show()