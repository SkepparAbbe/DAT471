import numpy as np

def linear_scan_with_remainder(X, Q, b):
    m = Q.shape[0]
    I = np.zeros(m, dtype=np.int64)
    iterations = []

    for i in range(0, m, b):
        Q_batch = Q[i:i+b, :]
        D_batch = Q_batch[:, np.newaxis, :] - X[np.newaxis, :, :]
        dist = np.linalg.norm(D_batch, axis=2)
        I[i:i+b] = np.argsort(dist, axis=1)[:, 0]
        iterations.append(f"Loop wrote I[{i}:{min(i+b, m)}]")

    r = m % b
    if r != 0:
        Q_batch = Q[-r:, :]
        D_batch = Q_batch[:, np.newaxis, :] - X[np.newaxis, :, :]
        dist = np.linalg.norm(D_batch, axis=2)
        I[-r:] = np.argsort(dist, axis=1)[:, 0]
        iterations.append(f"Remainder block wrote I[{m-r}:{m}]  <-- DUPLICATE")

    for line in iterations:
        print(line)
    return I

def linear_scan_without_remainder(X, Q, b):
    m = Q.shape[0]
    I = np.zeros(m, dtype=np.int64)

    for i in range(0, m, b):
        Q_batch = Q[i:i+b, :]
        D_batch = Q_batch[:, np.newaxis, :] - X[np.newaxis, :, :]
        dist = np.linalg.norm(D_batch, axis=2)
        I[i:i+b] = np.argsort(dist, axis=1)[:, 0]

    return I

np.random.seed(42)
X = np.random.rand(400, 50).astype(np.float32)
Q = np.random.rand(100, 50).astype(np.float32)

print("=== With remainder block ===")
I_with = linear_scan_with_remainder(X, Q, b=32)

print("\n=== Without remainder block ===")
I_without = linear_scan_without_remainder(X, Q, b=32)

print(f"\nResults identical: {np.array_equal(I_with, I_without)}")