import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    values = np.load("values.npy")
    plt.bar(range(128), values, width=1.0, edgecolor='steelblue', linewidth=0.5)
    plt.xlabel("Hash bucket (7 LSBs)")
    plt.ylabel("Frequency")
    plt.savefig('problem3c_histogram.png')
    plt.show()