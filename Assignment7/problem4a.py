import numpy as np
import cupy as cp
import argparse
import pandas as pd
import csv
import sys
import time

def is_gpu_available():
    try:
        cp.cuda.runtime.getDeviceCount()
        return cp.cuda.runtime.getDeviceCount() > 0
    except cp.cuda.runtime.CUDARuntimeError:
        return False

def to_gpu(arr):
    if isinstance(arr, np.ndarray):
        gpu_arr = cp.asarray(arr)
        cp.cuda.Device().synchronize()
        return gpu_arr
    return arr  # already on GPU

def to_cpu(arr):
    if isinstance(arr, cp.ndarray):
        cp.cuda.Device().synchronize()
        return cp.asnumpy(arr)
    return arr  # already on CPU

def linear_scan(X, Q, b = None):
    """
    Perform linear scan for querying nearest neighbor.
    X: n*d dataset
    Q: m*d queries
    b: optional batch size (ignored in this implementation)
    Returns an m-vector of indices I; the value i reports the row in X such 
    that the Euclidean norm of ||X[I[i],:]-Q[i]|| is minimal
    """
    n = X.shape[0]
    m = Q.shape[0]
    I = cp.zeros(m,dtype=cp.int64)
    
    # Precompute X norms once, reused every batch
    X_norm = cp.sum(X**2, axis=1, keepdims=True).T  # (1, n)
    
    for i in range(0, m, b):
        Q_batch = Q[i:i+b, :]                                        # (b, d)
        Q_norm = cp.sum(Q_batch**2, axis=1, keepdims=True)           # (b, 1)
        dist = Q_norm + X_norm - 2 * Q_batch @ X.T                   # (b, n)
        I[i:i+b] = cp.argmin(dist, axis=1)

    r = m % b
    if r != 0:
        Q_batch = Q[-r:, :]                                          # (r, d)
        Q_norm = cp.sum(Q_batch**2, axis=1, keepdims=True)           # (r, 1)
        dist = Q_norm + X_norm - 2 * Q_batch @ X.T                   # (r, n)
        I[-r:] = cp.argmin(dist, axis=1)

    return I
        

def load_glove(fn):
    """
    Loads the glove dataset from the file
    Returns (X,L) where X is the dataset vectors and L is the words associated
    with the respective rows.
    """
    df = pd.read_table(fn, sep = ' ', index_col = 0, header = None,
                           quoting = csv.QUOTE_NONE, keep_default_na = False)
    X = np.ascontiguousarray(df, dtype = np.float32)
    L = df.index.tolist()
    return (X, L)

def load_pubs(fn):
    """
    Loads the pubs dataset from the file
    Returns (X,L) where X is the dataset vectors (easting,northing) and 
    L is the list of names of pubs, associated with each row
    """
    df = pd.read_csv(fn)
    L = df['name'].tolist()
    X = np.ascontiguousarray(df[['easting','northing']], dtype = np.float32)
    return (X, L)

def load_queries(fn):
    """
    Loads the m*d array of query vectors from the file
    """
    return np.loadtxt(fn, delimiter = ' ', dtype = np.float32)

def load_query_labels(fn):
    """
    Loads the m-long list of correct query labels from a file
    """
    with open(fn,'r') as f:
        return f.read().splitlines()

if __name__ == '__main__':
    parser = argparse.ArgumentParser( \
          description = 'Perform nearest neighbor queries under the '
          'Euclidean metric using linear scan, measure the time '
          'and optionally verify the correctness of the results')
    parser.add_argument(
        '-d', '--dataset', type=str, required=True,
        help = 'Dataset file (must be pubs or glove)')
    parser.add_argument(
        '-q', '--queries', type=str, required=True,
        help = 'Queries file (must be compatible with the dataset)')
    parser.add_argument(
        '-l', '--labels', type=str, required=False,
        help = 'Optional correct query labels; if provided, the correctness '
        'of returned results is checked')
    parser.add_argument(
        '-b', '--batch-size', type=int, required=False,
        help = 'Size of batches')
    args = parser.parse_args()

    on_gpu = is_gpu_available()
    print(f"GPU available: {on_gpu}")

    t1 = time.time()
    if 'pubs' in args.dataset:
        (X,L) = load_pubs(args.dataset)
    elif 'glove' in args.dataset:
        (X,L) = load_glove(args.dataset)
    else:
        sys.stderr.write(f'{sys.argv[0]}: error: Only glove/pubs supported\n')
        exit(1)
    t2 = time.time()

    (n,d) = X.shape
    assert len(L) == n

    t3 = time.time()
    Q = load_queries(args.queries)
    t4 = time.time()

    assert X.flags['C_CONTIGUOUS']
    assert Q.flags['C_CONTIGUOUS']
    assert X.dtype == np.float32
    assert Q.dtype == np.float32
    
    m = Q.shape[0]
    assert Q.shape[1] == d

    t5 = time.time()
    QL = None
    if args.labels is not None:
        QL = load_query_labels(args.labels)
        assert len(QL) == m
    t6 = time.time()

    X = to_gpu(X)
    Q = to_gpu(Q)

    t7 = time.time()
    
    I = linear_scan(X,Q,args.batch_size)
    cp.cuda.Stream.null.synchronize() 

    t8 = time.time()

    I = to_cpu(I)

    t9 = time.time()

    assert I.shape == (m,)

    num_erroneous = 0
    if QL is not None:
        for (i,j) in enumerate(I):
            if QL[i] != L[j]:
                # sys.stderr.write(f'{i}th query was erroneous: got "{L[j]}", '
                #                      f'but expected "{QL[i]}"\n')
                num_erroneous += 1

    print(f'Loading dataset ({n} vectors of length {d}) took', t2-t1)
    print(f'Transferring data to GPU took', t7-t6)
    print(f'Transferring data to CPU took', t9-t8)
    print(f'Performing {m} NN queries took', t8-t7)
    print(f"Batch size used (b={args.batch_size})")
    print(f'Number of erroneous queries: {num_erroneous}')
