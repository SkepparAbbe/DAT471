import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import LinearSegmentedColormap

def load_results(path):
    df = pd.read_csv(path, comment='#')
    df.columns = df.columns.str.strip()
    # Average over repeated runs
    df = df.groupby(['workers', 'batch'])['total_time'].mean().reset_index()
    return df

def make_heatmap(df, metric, title, cmap, ax, fmt=".2f"):
    pivot = df.pivot(index='workers', columns='batch', values=metric)
    pivot = pivot.sort_index(ascending=False)  # largest workers at top

    im = ax.imshow(pivot.values, aspect='auto', cmap=cmap)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    ax.set_xlabel('Batch Size', labelpad=8)
    ax.set_ylabel('Workers', labelpad=8)
    ax.set_title(title, fontsize=11, fontweight='bold', pad=10)

    # Annotate cells
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not np.isnan(val):
                ax.text(j, i, f'{val:{fmt}}', ha='center', va='center',
                        fontsize=7, color='white' if val > pivot.values.mean() else 'black')

    plt.colorbar(im, ax=ax, shrink=0.8)
    return pivot

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'results.csv'

    df = load_results(path)

    # Compute speedup relative to 1 worker per batch size
    baseline = df[df['workers'] == df['workers'].min()][['batch', 'total_time']].rename(columns={'total_time': 'base_time'})
    df = df.merge(baseline, on='batch', how='left')
    df['speedup'] = df['base_time'] / df['total_time']
    df['efficiency'] = df['speedup'] / df['workers']

    fig, axes = plt.subplots(3, 1, figsize=(10, 18))

    cold_hot = LinearSegmentedColormap.from_list('cold_hot', ['#1a1a2e', '#e94560', '#f5a623'])
    green_map = LinearSegmentedColormap.from_list('greens', ['#1a1a2e', '#00b894', '#dfe6e9'])
    blue_map  = LinearSegmentedColormap.from_list('blues',  ['#1a1a2e', '#0984e3', '#dfe6e9'])

    make_heatmap(df, 'total_time', 'Total Time (s) - lower is better',
                 cold_hot, axes[0], fmt=".2f")

    make_heatmap(df, 'speedup', 'Speedup - higher is better',
                 green_map, axes[1], fmt=".1f")

    make_heatmap(df, 'efficiency', 'Efficiency (speedup/workers) - closer to 1 is better',
                 blue_map, axes[2], fmt=".2f")

    # Mark best cell in each heatmap
    for ax, metric, best_fn in zip(axes,
                                   ['total_time', 'speedup', 'efficiency'],
                                   [np.nanargmin, np.nanargmax, np.nanargmax]):
        pivot = df.pivot(index='workers', columns='batch', values=metric)
        pivot = pivot.sort_index(ascending=False)
        flat_idx = best_fn(pivot.values)
        row, col = np.unravel_index(flat_idx, pivot.shape)
        ax.add_patch(plt.Rectangle((col - 0.5, row - 0.5), 1, 1,
                                   fill=False, edgecolor='yellow', lw=2.5))
        best_w = pivot.index[row]
        best_b = pivot.columns[col]
        ax.set_xlabel(f'Batch Size\n★ best: workers={best_w}, batch={best_b}', labelpad=8)

    plt.tight_layout()
    out = path.replace('.csv', '_heatmap.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    print(f"Saved to {out}")
    plt.show()

if __name__ == '__main__':
    main()