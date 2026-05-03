#!/usr/bin/env python3

import numpy as np
import pandas as pd
import sys

k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
filepath = sys.argv[1]

df = pd.read_csv(filepath)

# Same star naming logic as mapper
def get_star(row):
    if row['Star'] == 'Prime':
        return row['Constellation']
    return row['Star'] + ' ' + row['Constellation']

df['star'] = df.apply(get_star, axis=1)

# Sum RU per star, get top k
result = df.groupby('star')['Mineral value (RU)'].sum().nlargest(k)

for star, ru in result.items():
    print(f"{star}: {ru}")