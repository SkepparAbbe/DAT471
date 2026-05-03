 #!/usr/bin/env python3
from mrjob.job import MRJob
from mrjob.job import MRStep

class MRJobTwitterFollowers(MRJob):
    def mapper(self, _, line):
        id_pair = line.split(':')
        follow_ids = [x for x in id_pair[1].strip("\n").split(' ') if x.strip()]

        for id in follow_ids:
            yield (id, 1)

        yield("num_users", 1)

    # Combiner to reduce IO
    def combiner(self, id, counts):
        yield (id, sum(counts))

    # Same step as combiner to remove duplicates of ID pairs
    def reducer_sum(self, id, counts):
        yield (None, (id, sum(counts)))

    def reducer(self, _, pairs):
        best_id, best_count = None, -1
        num_users_with_followers, total_num_follwers, no_followers = 0, 0, 0
        num_users = 0

        for id, c in pairs:
            if id == "num_users":
                num_users += c
                continue

            if c > best_count:
                best_count = c
                best_id = id

            total_num_follwers += c
            num_users_with_followers += 1
            
        no_followers = num_users - num_users_with_followers

        yield ('most followers id', best_id)
        yield ('most followers', best_count)
        yield ('average followers', total_num_follwers / num_users)
        yield ('count no followers', no_followers)
        
    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer_sum),
            MRStep(reducer=self.reducer)
        ]

if __name__ == '__main__':
    MRJobTwitterFollowers.run()