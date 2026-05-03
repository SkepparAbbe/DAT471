import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv('results_problem4_20260503_163023.csv')
    baseline = df.loc[df['num_workers'] == 1, 'elapsed_s'].values[0]
    df['speedup'] = baseline / df['elapsed_s']

    plt.figure()
    plt.plot(df['num_workers'], df['speedup'], marker='o', label='Empirical')

    plt.title("Speedup vs Number of Cores")
    plt.xlabel("Number of Cores")
    plt.ylabel("Speedup")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('speedup_problem4c_new.png', dpi=150)
    plt.show()