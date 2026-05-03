 #!/usr/bin/env python3

from mrjob.job import MRJob

class MRJobTwitterFollows(MRJob):
    def mapper(self, _, line):
        id_pair = line.split(':')
        follow_ids = [x for x in id_pair[1].strip("\n").split(' ') if x.strip()]
        count = len(follow_ids)
            
        yield (None, (id_pair[0], count))

    def combiner(self, _, pairs):
        # Consume because we need the length and reusable list
        max_id, max_follows, length, follows_sum, no_following = "", 0, 0, 0, 0

        # For loop to not allocate the generator output of mappers.
        for id_x, val_x in pairs:
            if val_x == 0:
                no_following += 1
            if val_x > max_follows:
                max_follows = val_x
                max_id = id_x
            length += 1
            follows_sum += val_x

        yield (None, [max_id, max_follows, follows_sum, length, no_following])
        
    def reducer(self, _, local_reducer_values):
        # Consume because list size is small enough
        local_reducer_values = list(local_reducer_values)
        best = max(local_reducer_values, key=lambda x: x[1])

        yield ('most followed id', best[0])
        yield ('most followed', best[1])
        yield ('average followed', (sum(x[2] for x in local_reducer_values)) / (sum(x[3] for x in local_reducer_values)))
        yield ('count follows no-one', sum(x[-1] for x in local_reducer_values))

if __name__ == '__main__':
    MRJobTwitterFollows.run()

