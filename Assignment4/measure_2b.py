import time
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, year, floor
from pyspark.sql.types import IntegerType, DoubleType, StructType, StructField, DateType, StringType
import pandas as pd
import csv
import math
import sys
import os

@udf(returnType=IntegerType())
def jdn(dt):
    """
    Computes the Julian date number for a given date.
    Parameters:
    - dt, datetime : the Gregorian date for which to compute the number

    Return value: an integer denoting the number of days since January 1, 
    4714 BC in the proleptic Julian calendar.
    """
    y = dt.year
    m = dt.month
    d = dt.day
    if m < 3:
        y -= 1
        m += 12
    a = y//100
    b = a//4
    c = 2-a+b
    e = int(365.25*(y+4716))
    f = int(30.6001*(m+1))
    jd = c+d+e+f-1524
    return jd

    
# you probably want to use a function with this signature for computing the
# simple linear regression with least squares using applyInPandas()
# key is the group key, df is a Pandas dataframe
# should return a Pandas dataframe
def lsq(key,df):
    x_bar = df["JDN"].mean()
    y_bar = df["T_AVERAGE"].mean()

    beta_hat = ((df["JDN"] - x_bar) * (df["T_AVERAGE"] - y_bar)).sum() / ((df["JDN"] - x_bar)**2).sum()
    alpha_hat = y_bar - beta_hat * x_bar

    return pd.DataFrame({
        "STATION": [key[0]],
        "NAME": [df["NAME"].iloc[0]],
        "ALPHA_HAT": [alpha_hat],
        "BETA_HAT": [beta_hat]
    })


if __name__ == '__main__':
    # do not change the interface
    parser = argparse.ArgumentParser(description = \
                                    'Compute climate data.')
    parser.add_argument('-w','--num-workers',default=1,type=int,
                            help = 'Number of workers')
    parser.add_argument('--csv-out', default='results.csv',
                        help='Path to CSV file to append results to (default: results.csv)')
    parser.add_argument('filename',type=str,help='Input filename')
    args = parser.parse_args()

    # this bit is important: by default, Spark only allocates 1 GiB of memory 
    # which will likely cause an out of memory exception with the full data

    spark = SparkSession.builder \
            .master(f'local[{args.num_workers}]') \
            .config("spark.ui.showConsoleProgress", "false") \
            .config("spark.driver.memory", "128g") \
            .getOrCreate()

    start = time.time()
    # read the CSV file into a pyspark.sql dataframe and compute the things you need
    # STATION,JDN,DATE,LATITUDE,LONGITUDE,ELEVATION,NAME,PRCP,TMAX,TMIN
    schema = StructType([
        StructField("STATION", StringType()),
        StructField("DATE", DateType()),
        StructField("LATITUDE", DoubleType()),
        StructField("LONGITUDE", DoubleType()),
        StructField("ELEVATION", DoubleType()),
        StructField("NAME", StringType()),
        StructField("PRCP", DoubleType()),
        StructField("TMAX", DoubleType()),
        StructField("TMIN", DoubleType()),
    ])
    df = spark.read.csv(args.filename, header=True, schema=schema)
    t2 = time.time()

    # Apply jdn on the DATE column
    averages = df.withColumn('JDN', jdn(df['DATE'])) \
        .withColumn('T_AVERAGE', (col('TMAX') + col('TMIN'))/2)
    averages.cache()

    lsq_fit = averages.groupBy("STATION").applyInPandas(
        lsq,
        schema="STATION string, NAME string, ALPHA_HAT double, BETA_HAT double"
    )

    valid = lsq_fit.filter(col("BETA_HAT").isNotNull() & ~col("BETA_HAT").isNaN())
    valid.cache()
    top_5_coefficients = valid.orderBy('BETA_HAT', ascending=False).limit(5).collect()
    positive_slope_fraction = valid.filter(col('BETA_HAT') > 0).count() / valid.count()
    # positive_slope_fraction = lsq_fit.filter(lsq_fit['BETA_HAT'] > 0).count() / lsq_fit.count()
    beta_min, beta_q1, beta_median, beta_q3, beta_max = valid.approxQuantile("BETA_HAT", [0.0, 0.25, 0.5, 0.75, 1.0], 0)

    # Here you will need to implement computing the decadewise differences 
    # between the average temperatures of 1910s and 2010s

    # There should probably be an if statement to check if any such values were 
    # computed (no suitable stations in the tiny dataset!)

    # Note that values should be printed in celsius
    
    def calculate_differences(key, df):
        df_2010_avg = df[df["DATE"] == 2010]["T_AVERAGE"].mean()
        df_1910_avg = df[df["DATE"] == 1910]["T_AVERAGE"].mean()

        return pd.DataFrame({
            "STATION": [key[0]],
            "NAME": [df["NAME"].iloc[0]],
            "DIFFERENCE": [df_2010_avg - df_1910_avg]
        })

    decade_differences = averages.withColumn("DATE", (floor(year(col('DATE')) / 10) * 10).cast(IntegerType())) \
        .filter((col('DATE') == 2010) | (col('DATE') == 1910)) \
        .withColumn("T_AVERAGE", (col("T_AVERAGE") - 32) * (5.0 / 9)) \
        .groupBy("STATION").applyInPandas(
            calculate_differences,
            schema="STATION string, NAME string, DIFFERENCE double"
        )
    
    valid = decade_differences.filter(col("DIFFERENCE").isNotNull() & ~col("DIFFERENCE").isNaN())
    valid.cache()
    num_valid = valid.count()

    if num_valid > 0:
        top_5_differences = valid.orderBy('DIFFERENCE', ascending=False).limit(5).collect()
        positive_difference_fraction = valid.filter(col('DIFFERENCE') > 0).count() / valid.count()
        tdiff_min, tdiff_q1, tdiff_median, tdiff_q3, tdiff_max = valid.approxQuantile("DIFFERENCE", [0.0, 0.25, 0.5, 0.75, 1.0], 0)

    t3 = time.time()

    # top 5 slopes are printed here
    # replace None with your dataframe, list, or an appropriate expression
    # replace STATIONCODE, STATIONNAME, and BETA with appropriate expressions
    print('Top 5 coefficients:')
    for row in top_5_coefficients:
        print(f'{row['STATION']} at {row['NAME']} BETA={row['BETA_HAT']:0.3e} °F/d')

    # replace None with an appropriate expression
    print('Fraction of positive coefficients:')
    print(positive_slope_fraction)

    # Five-number summary of slopes, replace with appropriate expressions
    print('Five-number summary of BETA values:')
    print(f'beta_min {beta_min:0.3e}')
    print(f'beta_q1 {beta_q1:0.3e}')
    print(f'beta_median {beta_median:0.3e}')
    print(f'beta_q3 {beta_q3:0.3e}')
    print(f'beta_max {beta_max:0.3e}')


    print('Top 5 differences:')
    if num_valid > 0:
        for row in top_5_differences:
            print(f'{row['STATION']} at {row['NAME']} difference {row['DIFFERENCE']:0.1f} °C)')

        print('Fraction of positive differences:')
        print(positive_difference_fraction)

        print('Five-number summary of decade average difference values:')
        print(f'tdiff_min {tdiff_min:0.1f} °C')
        print(f'tdiff_q1 {tdiff_q1:0.1f} °C')
        print(f'tdiff_median {tdiff_median:0.1f} °C')
        print(f'tdiff_q3 {tdiff_q3:0.1f} °C')
        print(f'tdiff_max {tdiff_max:0.1f} °C')
    else:
        print("No stations exist with a valid difference between 2010 and 1910.")

    # Add your time measurements here
    # It may be interesting to also record more fine-grained times (e.g., how 
    # much time was spent computing vs. reading data)
    print(f'num workers: {args.num_workers}')
    end = time.time()
    reading_time = t2 - start #reading data time
    comp_time = t3 - t2 #computation time
    print_time = end - t3 #printing data
    total_time = end - start
    
    print("-------------------------------------------------------")
    print(f'reading data time: {reading_time:0.1f} s')
    print(f'computation only time: {comp_time:0.1f} s')
    print(f'display data time: {print_time:0.1f} s')
    print(f'total time: {total_time:0.1f} s')

    # Write (or append) to CSV
    write_header = not os.path.exists(args.csv_out) or os.path.getsize(args.csv_out) == 0
    with open(args.csv_out, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['num_workers', 'total_time', 'print_time', 'comp_time', 'reading_time'])
        writer.writerow([
            args.num_workers,
            round(total_time, 6),
            round(print_time, 6),
            round(comp_time, 6),
            round(reading_time, 6),
        ])
