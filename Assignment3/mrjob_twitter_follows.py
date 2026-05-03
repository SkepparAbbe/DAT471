 #!/usr/bin/env python3

from mrjob.job import MRJob

class MRJobTwitterFollows(MRJob):
    # The final (key,value) pairs returned by the class should be
    # 
    # yield ('most followed id', ???)
    # yield ('most followed', ???)
    # yield ('average followed', ???)
    # yield ('count follows no-one', ???)
    #
    # You will, of course, need to replace ??? with a suitable expression

    def mapper(self, _, line):
        id_pair = line.split(':')
        follow_ids = [x for x in id_pair[1].strip("\n").split(' ') if x.strip()]
        count = len(follow_ids)
            
        yield (None, (id_pair[0], count))

    def combiner(self, _, pairs):
        # Consume because we need the length and reusable list
        pairs = list(pairs)
        best = max(pairs, key=lambda x: x[1])

        yield (None, [best[0], best[1], sum(x[1] for x in pairs), len(pairs), sum((1 if p[1] == 0 else 0 for p in pairs))])
        
    def reducer(self, _, local_reducer_values):
        # Consume because we need the length and reusable list
        local_reducer_values = list(local_reducer_values)
        best = max(local_reducer_values, key=lambda x: x[1])

        yield ('most followed id', best[0])
        yield ('most followed', best[1])
        yield ('average followed', (sum(x[2] for x in local_reducer_values)) / (sum(x[3] for x in local_reducer_values)))
        yield ('count follows no-one', sum(x[-1] for x in local_reducer_values))

if __name__ == '__main__':
    MRJobTwitterFollows.run()

