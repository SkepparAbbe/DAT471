import sys
filepath = sys.argv[1]

with open(filepath, 'r') as f:
    for line in f:
        id_pair = line.split(':')
        follow_ids = [x for x in id_pair[1].strip("\n").split(' ') if x.strip()]
        count = len(follow_ids)

        if (count > 2):
            print(line)
            print(follow_ids)
            print(f"({id_pair[0]}, {count})")
            print("\n")