import matplotlib.pyplot as plt
import numpy as np

def plot_asymptotic_complexity(algorithm_names, complexities):
    x = np.arange(len(algorithm_names))
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(x, complexities, width, label='Asymptotic Complexity')

    ax.set_xlabel('Cache Algorithms')
    ax.set_ylabel('Complexity')
    ax.set_title('Asymptotic Time Complexity of Cache Algorithms')
    ax.set_xticks(x)
    ax.set_xticklabels(algorithm_names)
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(bars)

    plt.tight_layout()
    plt.savefig('static/complexity_graph.png')

# Example usage
if __name__ == '__main__':
    algorithm_names = ['LRU', 'LFU', 'ARC', 'WTinyLFU', 'Random']
    complexities = [1, 2, 3, 2, 1]  # Replace with actual complexities O(1), O(log n), O(1), O(1), O(1)

    plot_asymptotic_complexity(algorithm_names, complexities)
