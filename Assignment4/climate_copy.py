import time
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import IntegerType, DoubleType
import pandas as pd
import math
import sys

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
    parser.add_argument('filename',type=str,help='Input filename')
    args = parser.parse_args()

    # this bit is important: by default, Spark only allocates 1 GiB of memory 
    # which will likely cause an out of memory exception with the full data

    spark = SparkSession.builder \
            .master(f'local[{args.num_workers}]') \
            .config("spark.ui.showConsoleProgress", "false") \
            .config("spark.driver.memory", "16g") \
            .getOrCreate()
    


    # read the CSV file into a pyspark.sql dataframe and compute the things you need
    # STATION,JDN,DATE,LATITUDE,LONGITUDE,ELEVATION,NAME,PRCP,TMAX,TMIN
    df = spark.read.csv(args.filename, header=True, inferSchema=True)

    print('Original dataset:\n\n')
    df.show(2)

    # Apply jdn on the DATE column
    df2 = df.withColumn('JDN', jdn(df['DATE']))
    print('With julian day numbers:')
    df2.show(2)
    df3 = df2.withColumn('T_AVERAGE', (df2['TMAX'] + df2['TMIN'])/2)
    df3.cache()
    print('With T_AVERAGE column:')
    df3.show(2)

    lsq_fit = df3.groupBy("STATION").applyInPandas(
        lsq,
        schema="STATION string, NAME string, ALPHA_HAT double, BETA_HAT double"
    )
    lsq_fit.cache()

    print('alpha and beta values for each station (NON_JOINED):')
    
    # top 5 slopes are printed here
    # replace None with your dataframe, list, or an appropriate expression
    # replace STATIONCODE, STATIONNAME, and BETA with appropriate expressions
    print('Top 5 coefficients:')
    for row in lsq_fit.orderBy('BETA_HAT', ascending=False).limit(5).collect():
        print(f'{row['STATION']} at {row['NAME']} BETA={row['BETA_HAT']:0.3e} °F/d')

    # replace None with an appropriate expression
    print('Fraction of positive coefficients:')
    print(lsq_fit.filter(lsq_fit['BETA_HAT'] > 0).count() / lsq_fit.count())

    # Five-number summary of slopes, replace with appropriate expressions
    print('Five-number summary of BETA values:')
    beta_min, beta_q1, beta_median, beta_q3, beta_max = lsq_fit.approxQuantile("BETA_HAT", [0.0, 0.25, 0.5, 0.75, 1.0], 0)
    print(f'beta_min {beta_min:0.3e}')
    print(f'beta_q1 {beta_q1:0.3e}')
    print(f'beta_median {beta_median:0.3e}')
    print(f'beta_q3 {beta_q3:0.3e}')
    print(f'beta_max {beta_max:0.3e}')

    # Here you will need to implement computing the decadewise differences 
    # between the average temperatures of 1910s and 2010s

    # There should probably be an if statement to check if any such values were 
    # computed (no suitable stations in the tiny dataset!)

    # Note that values should be printed in celsius

    @udf(returnType=IntegerType())
    def decadize_year(dt):
        return 10 * math.floor(dt.year / 10)

    df4 = df3.withColumn("DATE", decadize_year(df3['DATE'])) \
        .filter((col('DATE') == 2010) | (col('DATE') == 1910))
    df4.show(5)

    @udf(returnType=DoubleType())
    def convertToCelsius(temp):
        return (temp - 32)*(5/9)

    df5 = df4.withColumn("T_AVERAGE", convertToCelsius(df4["T_AVERAGE"]))

    def calculate_differences(key, df):
        df_2010_avg = df[df["DATE"] == 2010]["T_AVERAGE"].mean()
        df_1910_avg = df[df["DATE"] == 1910]["T_AVERAGE"].mean()

        return pd.DataFrame({
            "STATION": [key[0]],
            "NAME": [df["NAME"].iloc[0]],
            "DIFFERENCE": [df_2010_avg - df_1910_avg]
        })

    decade_differences = df5.groupBy("STATION").applyInPandas(
        calculate_differences,
        schema="STATION string, NAME string, DIFFERENCE double"
    )
    decade_differences.cache()
    decade_differences.show(5)

    # Replace None with an appropriate expression
    # Replace STATION, STATIONNAME, and TAVGDIFF with appropriate expressions

    print('Top 5 differences:')
    for row in decade_differences.orderBy('DIFFERENCE', ascending=False).limit(5).collect():
        print(f'{row['STATION']} at {row['NAME']} difference {row['DIFFERENCE']:0.1f} °C)')

    # replace None with an appropriate expression
    print('Fraction of positive differences:')
    print(decade_differences.filter(decade_differences['DIFFERENCE'] > 0).count() / decade_differences.count())

    # Five-number summary of temperature differences, replace with appropriate expressions
    print('Five-number summary of decade average difference values:')
    tdiff_min, tdiff_q1, tdiff_median, tdiff_q3, tdiff_max = decade_differences.approxQuantile("DIFFERENCE", [0.0, 0.25, 0.5, 0.75, 1.0], 0)
    print(f'tdiff_min {tdiff_min:0.1f} °C')
    print(f'tdiff_q1 {tdiff_q1:0.1f} °C')
    print(f'tdiff_median {tdiff_median:0.1f} °C')
    print(f'tdiff_q3 {tdiff_q3:0.1f} °C')
    print(f'tdiff_max {tdiff_max:0.1f} °C')

    # Add your time measurements here
    # It may be interesting to also record more fine-grained times (e.g., how 
    # much time was spent computing vs. reading data)
    print(f'num workers: {args.num_workers}')
    print(f'total time: {None:0.1f} s')
