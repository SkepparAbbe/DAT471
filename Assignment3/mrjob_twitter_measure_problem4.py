#!/usr/bin/env python3

from mrjob_twitter_followers_new import MRJobTwitterFollowers
import time
import argparse
import csv
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='mrjob_twitter_measure',
        description='Measure the running time of the twitter job',
    )
    parser.add_argument('-w', '--num-workers', type=int, default=1)
    parser.add_argument('filename')
    parser.add_argument('--csv-out', default='results.csv',
                        help='Path to CSV file to append results to (default: results.csv)')
    args = parser.parse_args()

    mr_job = MRJobTwitterFollowers(args=[
        '-r', 'local',
        '--num-cores', str(args.num_workers),
        args.filename
    ])

    start = time.time()
    with mr_job.make_runner() as runner:
        runner.run()
        results = {}
        for key, value in mr_job.parse_output(runner.cat_output()):
            results[key] = value
            print(key, value)
    end = time.time()
    elapsed = end - start

    print(f'Number of workers: {args.num_workers}')
    print(f'Time elapsed: {elapsed} s')

    # Write (or append) to CSV
    write_header = not os.path.exists(args.csv_out) or os.path.getsize(args.csv_out) == 0
    with open(args.csv_out, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['num_workers', 'elapsed_s'])
        writer.writerow([
            args.num_workers,
            round(elapsed, 4),
        ])