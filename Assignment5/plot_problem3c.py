import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    values = np.load("values.npy")
    plt.bar(range(1000), values, width=1.0, edgecolor='steelblue', linewidth=0.5)
    plt.xlabel("Seeds")
    plt.ylabel("Cardinality Estimate")
    plt.tight_layout(pad=2.0)
    plt.savefig('problem3c_histogram.png')
    plt.show()