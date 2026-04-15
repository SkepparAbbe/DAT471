import os
import argparse
import sys
import time
import multiprocessing as mp
import numpy as np

def get_filenames(path):
    """
    A generator function: Iterates through all .txt files in the path and
    returns the full names of the files

    Parameters:
    - path : string, path to walk through

    Yields:
    The full filenames of all files ending in .txt
    """
    for (root, dirs, files) in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                yield f'{root}/{file}'

def get_file(path):
    """
    Reads the content of the file and returns it as a string.

    Parameters:
    - path : string, path to a file

    Return value:
    The content of the file in a string.
    """
    with open(path,'r') as f:
        return f.read()

def count_words_in_file(filename_queue,wordcount_queue,batch_size):
    """
    Counts the number of occurrences of words in the file
    Performs counting until a None is encountered in the queue
    Counts are stored in wordcount_queue
    Whitespace is ignored

    Parameters:
    - filename_queue, multiprocessing queue :  will contain filenames and None as a sentinel to indicate end of input
    - wordcount_queue, multiprocessing queue : (word,count) dictionaries are put in the queue, and end of input is indicated with a None
    - batch_size, int : size of batches to process

    Returns: None
    """
    i = 0
    counts = dict()
    while (chunk := filename_queue.get()) is not None:
        for word in get_file(chunk).split():
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
        i += 1
        if i == batch_size:
            i = 0
            wordcount_queue.put(counts)
            counts = dict()
    wordcount_queue.put(counts)
    wordcount_queue.put(None)

def get_top10(counts):
    """
    Determines the 10 words with the most occurrences.
    Ties can be solved arbitrarily.

    Parameters:
    - counts, dictionary : a mapping from words (str) to counts (int)
    
    Return value:
    A list of (count,word) pairs (int,str)
    """
    return (sorted(counts.items(), key=lambda item: item[1], reverse=True)[:10])

def merge_counts(global_counts,out_queue,wordcount_queue,num_workers):
    """
    Merges the counts from the queue into the shared dict global_counts. 
    Quits when num_workers Nones have been encountered.

    Parameters:
    - global_counts, manager dict : global dictionary where to store the counts
    - wordcount_queue, manager queue : queue that contains (word,count) pairs and Nones to signal end of input from a worker
    - num_workers, int : number of workers (i.e., how many Nones to expect)

    Return value: None
    """
    nones_seen = 0
    while nones_seen < num_workers:
        dict_from = wordcount_queue.get()
        if dict_from is None:
            nones_seen += 1
            continue
        for (k, v) in dict_from.items():
            if k not in global_counts:
                global_counts[k] = v
            else:
                global_counts[k] += v

    checksum = compute_checksum(global_counts)
    top_10 = get_top10(global_counts)
    out_queue.put((checksum, top_10))
    out_queue.put(None)

def compute_checksum(counts):
    """
    Computes the checksum for the counts as follows:
    The checksum is the sum of products of the length of the word and its count

    Parameters:
    - counts, dictionary : word to count dictionary

    Return value:
    The checksum (int)
    """
    sum = 0
    for word, cnt in counts.items():
        sum += len(word) * cnt

    return sum    


if __name__ == '__main__':
    t1 = time.time()
    parser = argparse.ArgumentParser(description='Counts words of all the text files in the given directory')
    parser.add_argument('-w', '--num-workers', help = 'Number of workers', default=1, type=int)
    parser.add_argument('-b', '--batch-size', help = 'Batch size', default=1, type=int)
    parser.add_argument('path', help = 'Path that contains text files')
    args = parser.parse_args()

    path = args.path

    if not os.path.isdir(path):
        sys.stderr.write(f'{sys.argv[0]}: ERROR: `{path}\' is not a valid directory!\n')
        quit(1)

    num_workers = args.num_workers
    if num_workers < 1:
        sys.stderr.write(f'{sys.argv[0]}: ERROR: Number of workers must be positive (got {num_workers})!\n')
        quit(1)

    batch_size = args.batch_size
    if batch_size < 1:
        sys.stderr.write(f'{sys.argv[0]}: ERROR: Batch size must be positive (got {batch_size})!\n')
        quit(1)

    # construct workers and queues
    # construct a special merger process
    # put filenames into the input queue
    # workers then put dictionaries for the merger
    # the merger shall return the checksum and top 10 through the out queue

    # make queues
    wordcount_queue = mp.Queue()
    filename_queue = mp.Queue()
    out_queue = mp.Queue()

    global_counts = dict()

    workers = [mp.Process(
            target=count_words_in_file, args=(filename_queue, wordcount_queue, batch_size)
        ) for _ in range(num_workers)
    ]

    merger = mp.Process(target=merge_counts, args=(global_counts, out_queue, wordcount_queue, num_workers))
    merger.start()

    t2 = time.time()

    for w in workers:
        w.start()

    filepaths = get_filenames(path)
    for fp in filepaths:
        filename_queue.put(fp)

    for _ in range(num_workers):
        filename_queue.put(None)

    checksum = None
    top_10 = None
    while (result := out_queue.get()) is not None:
        checksum, top_10 = result

    t3 = time.time()

    t_tot = t3 - t1
    t_s = t2 - t1
    t_p = t_tot - t_s

    t_block1 = t2 - t1
    t_block2 = t3 - t2

    print(f"Cores: {num_workers}; Total time: {t_tot:.4f}")
    print(f"Block 1 time: {t_block1:.4f}")
    print(f"Block 2 time: {t_block2:.4f}")
    print(f"Sequential time: {t_s:.4f}")
    print(f"Parallel time: {t_p:.4f}")
    print(f"Parallel fraction: {(t_p / t_tot):.4f}")
    print(f"Checksum: {checksum}")
    print(f"Top 10 words with counts: {top_10}\n")

    # print(f"{num_workers},{batch_size},{t_tot:.4f},{t_s:.4f},{t_p:.4f},{(t_p/t_tot):.4f},{checksum}")