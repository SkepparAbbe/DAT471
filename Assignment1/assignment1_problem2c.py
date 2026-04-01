#!/usr/bin/env python3

import sys
import duckdb

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(f'Usage: {sys.argv[0]} <input_csv>\n')
        sys.exit(1)
    
    input_csv = sys.argv[1]

    with duckdb.connect(database=":memory:") as con:
        con.execute('CREATE VIEW hour AS SELECT * FROM ' + f'read_csv_auto(\'{input_csv}\', header=True);')

        SQL_QUERY = "SELECT COUNT(*) AS num_rows FROM hour"
        print("The number of rows of data in the file is: ")
        print(con.execute(SQL_QUERY).df().iloc[0]['num_rows'])

        SQL_QUERY = "SELECT hr, AVG(cnt) AS avg_cnt FROM hour GROUP BY hr ORDER BY hr"
        print("\nThe average hourly count of bike rentals: ")
        result = con.execute(SQL_QUERY).df()
        result.apply(lambda row: print(f"Hour ({int(row.loc['hr'])}); Avg: {row.loc['avg_cnt']:.3f}"), axis=1)

        SQL_QUERY = "SELECT hr, AVG(cnt) AS avg_cnt FROM hour GROUP BY hr ORDER BY avg_cnt DESC LIMIT 5"
        print("\nThe top-5 busiest hours based on average hourly count of bike rentals: ")
        result = con.execute(SQL_QUERY).df()
        result.apply(lambda row: print(f"Hour ({int(row.loc['hr'])}); Avg: {row.loc['avg_cnt']:.3f}"), axis=1)

        SQL_QUERY = "SELECT dteday, AVG(cnt) AS avg_cnt FROM hour WHERE (yr = 1 AND mnth = 1) GROUP BY dteday ORDER BY dteday"
        print("\nAverage daily count of bike rentals in the month of January 2012: ")
        result = con.execute(SQL_QUERY).df()
        result.apply(lambda row: print(f"Day ({str(row.loc['dteday']).split(' ')[0]}); Avg: {row.loc['avg_cnt']:.3f}"), axis=1)