import matplotlib.pyplot as plt
import argparse
import re

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Produces a speedup plot for problem 2d')
    parser.add_argument('-p', '--path', help = 'Path containing timed results')
    args = parser.parse_args()

    path = args.path
    pattern = r"Cores: (\d+).*; Total time: ([\d.]+)"

    speedup_dict = dict()
    # baseline_time = 110.6445 # problem 2d
    baseline_time = 121.7046 # problem 2e
    with open(path,'r') as f:
        while True:
            line = f.readline()
            if (len(line) < 1): break

            match = re.search(pattern, line.strip())
            if match is None:
                continue

            cores = int(match.group(1))
            total_time = float(match.group(2))

            if cores == 1:
                speedup_dict[1] = 1
            else:
                speedup_dict[cores] = baseline_time / total_time

    print(speedup_dict)
    plt.title("Speedup vs Number of Cores")
    plt.xlabel("Number of Cores")
    plt.ylabel("Speedup - t(n)")

    sorted_keys = sorted(speedup_dict.keys())
    sorted_vals = [speedup_dict[k] for k in sorted_keys]

    plt.plot(sorted_keys, sorted_vals, marker='o', label="Speedup")
    # plt.hlines(3.37, min(sorted_keys), max(sorted_keys), colors='red', linestyles='dashed', label="Theoretical max") # Theoretical max for 2d
    plt.hlines(8.21, min(sorted_keys), max(sorted_keys), colors='red', linestyles='dashed', label="Theoretical max") # Theoretical max for 2e
    plt.legend()

    current_ticks = list(plt.yticks()[0])
    # current_ticks.append(3.37) # Theoretical max for 2d
    current_ticks.append(8.21) # Theoretical max for 2e
    current_ticks.append(4)
    current_ticks.remove(8.0)
    plt.yticks(sorted(current_ticks))
    plt.ylim(0.6, 9) 

    plt.savefig("problem2e.png")