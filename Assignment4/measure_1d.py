#!/usr/bin/env python3

import time
import argparse
import findspark
import csv
findspark.init()
import os
from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = \
                                    'Compute Twitter follows.')
    parser.add_argument('-w','--num-workers',default=1,type=int,
                            help = 'Number of workers')
    parser.add_argument('--csv-out', default='results.csv',
                        help='Path to CSV file to append results to (default: results.csv)')
    parser.add_argument('filename',type=str,help='Input filename')
    args = parser.parse_args()

    start = time.time()

    conf = SparkConf()
    conf.set("spark.ui.showConsoleProgress", "false")

    sc = SparkContext(master = f'local[{args.num_workers}]', conf=conf)
    sc.setLogLevel("ERROR")

    lines = sc.textFile(args.filename)

    def parse_line(line):
        id_pair = line.split(':')
        follow_ids = [x for x in id_pair[1].strip("\n").split(' ') if x.strip()]
        
        yields = [(id, 1) for id in follow_ids]
        yields.append(("num_user", 1))
        return yields
    
    def seqOp(acc, pair):
        best_pair = (acc[0], acc[1])

        if (pair[0] != "num_user") and (pair[1] > acc[1]):
            best_pair = pair

        if pair[0] == "num_user":
            return (best_pair[0], best_pair[1], acc[2], pair[1], acc[4])
        else:
            return (best_pair[0], best_pair[1], acc[2] + pair[1], acc[3], acc[4] + 1)
                
    def combOp(acc1, acc2):
        best_pair = (acc1[0], acc1[1])

        if acc2[1] > acc1[1]:
            best_pair = (acc2[0], acc2[1])

        return (best_pair[0], best_pair[1], acc1[2] + acc2[2], acc1[3] + acc2[3], acc1[4] + acc2[4])

    statistics = lines.flatMap(parse_line) \
        .reduceByKey(lambda x,y: x+y) \
        .aggregate(("", 0, 0, 0, 0),
            seqOp,
            combOp
        )
        
    best_id, best_followers, total, count, num_users_with_followers = statistics
    avg = total/count
    no_followers = count - num_users_with_followers

    end = time.time()
    
    total_time = end - start

    # the first ??? should be the twitter id
    print(f'max followers: {best_id} has {best_followers} followers')
    print(f'followers on average: {avg}')
    print(f'number of user with no followers: {no_followers}')
    print(f'num workers: {args.num_workers}')
    print(f'total time: {total_time}')

    # Write (or append) to CSV
    write_header = not os.path.exists(args.csv_out) or os.path.getsize(args.csv_out) == 0
    with open(args.csv_out, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['num_workers', 'elapsed_s'])
        writer.writerow([
            args.num_workers,
            round(total_time, 6),
        ])