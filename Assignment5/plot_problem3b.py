import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv('results_problem3b_20260517_100507.csv')
    baseline = df.loc[df['num_workers'] == 1, 'total_time'].values[0]
    df['speedup'] = baseline / df['total_time']

    plt.figure()
    plt.plot(df['num_workers'], df['speedup'], marker='o', label='Empirical')

    plt.title("Speedup vs Number of workers")
    plt.xlabel("Number of workers")
    plt.ylabel("Speedup")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('speedup_problem3b.png', dpi=150)
    plt.show()