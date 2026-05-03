#!/usr/bin/env python3

from mrjob.job import MRJob
from mrjob.job import MRStep
from collections import Counter
import csv

class MRMineral(MRJob):

    
    def configure_args(self):
        super(MRMineral, self).configure_args()
        self.add_passthru_arg(
            '-k', default=5, action='store', help='Display k stars with largest RU'
        )

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
        yield (None, (star, sum(rus)))

    def top10_reducer(self, _, star_ru_pairs):
        c = Counter()
        for star, ru in star_ru_pairs:
            c[star] += ru
        for star, ru in c.most_common(int(self.options.k)):
            yield (star, ru)

    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(reducer=self.top10_reducer)
        ]

if __name__ == '__main__':
    MRMineral().run()