#!/usr/bin/env python3

from mrjob.job import MRJob
import csv

class MRMineral(MRJob):
    def mapper(self, _, line):
        row = next(csv.reader([line]))
        if row[0] == 'Constellation':
            return
        
        star = None
    
        if row[1] == "Prime":
            star = row[0]
        else:
            star = row[1] + " " + row[0]

        ru = int(row[5])
        yield (star, ru)

    def combiner(self, star, rus):
        yield (star, sum(rus))
        
    def reducer(self, star, rus):
        yield (star, sum(rus))

if __name__ == '__main__':
    MRMineral().run()