# %%
from pyspark.sql import SparkSession

# %%
spark=SparkSession.builder.appName('Stock-Data-Analysis').getOrCreate()

# %%
spark

# %%
# Read the dataset 
df = spark.read.option('header', 'true').csv("./Data/FS_sp500_Value.csv").drop("_c0")

# %%
# Analysis functions 

from pyspark.sql import functions as F 
from pyspark.sql.window import Window

def calcSimpleMovingAvg(df, col, span):
  window = Window.partitionBy("Ticker").orderBy("Date").rowsBetween(-span, 0)
  df = df.withColumn("moving_avg", F.avg(col).over(window))

  return df.rdd.map(lambda x: x.moving_avg).collect()

def calcDailyPercentChange(df):
  window = Window.partitionBy("Ticker").orderBy("Date")
  df = df.withColumn("prev_close", F.lag(df.Close).over(window))
  df = df.withColumn("change", F.when(F.isnull( (df.Close - df.prev_close)/df.prev_close ), 0).otherwise(F.round(F.abs((df.Close - df.prev_close)/df.prev_close) *100, 3)) )

  return df.rdd.map(lambda x: x.change).collect()

def calcATR(df):
  window = Window.partitionBy("Ticker").orderBy("Date")
  df = df.withColumn("prev_close", F.lag(df.Close).over(window))
  df = df.withColumn("h-l", df.High-df.Low)
  df = df.withColumn("h-p", F.when(F.isnull( F.abs(df.High-df.prev_close)), 0).otherwise( F.abs(df.High-df.prev_close)))
  df = df.withColumn("l-p", F.when(F.isnull( F.abs(df.Low-df.prev_close)), 0).otherwise( F.abs(df.Low-df.prev_close)))
  df = df.withColumn("true_range", F.greatest("h-l", "h-p", "l-p"))

  return calcSimpleMovingAvg(df, "true_range", 14)

def calcRSI(df):
  window = Window.partitionBy("Ticker").orderBy("Date")
  df = df.withColumn("prev_close", F.lag(df.Close).over(window)) 
  df = df.withColumn("change", F.when(F.isnull(df.Close - df.prev_close), 0).otherwise(df.Close - df.prev_close))

  window = Window.partitionBy("Ticker").orderBy("Date").rowsBetween(-14, 0)
  df = df.withColumn("change_up", F.when(df.change < 0, 0).otherwise(df.change))
  df = df.withColumn("change_down", F.when(df.change > 0, 0).otherwise(df.change))
  df = df.withColumn("avg_up", F.avg(df.change_up).over(window)).drop(df.change_up)
  df = df.withColumn("avg_down", F.avg(df.change_down).over(window)).drop(df.change_down)
  df = df.withColumn("rsi", F.round((100 * df.avg_up / (df.avg_up + F.abs(df.avg_down))), 4))
  df = df.fillna(0)
  return df.rdd.map(lambda x: x.rsi).collect()

def calcVPT(df):
  window = Window.partitionBy("Ticker").orderBy("Date")
  df = df.withColumn("prev_close", F.lag(df.Close).over(window))
  df = df.withColumn("temp_vpt", F.when(F.isnull((df.Volume * (df.Close - df.prev_close))/df.prev_close), 0).otherwise((df.Volume * (df.Close - df.prev_close))/df.prev_close))
  df = df.withColumn("prev_vpt", F.lag(df.temp_vpt).over(window))
  df = df.withColumn("vpt", F.when(F.isnull( df.prev_vpt), df.temp_vpt).otherwise(df.temp_vpt + df.prev_vpt)).drop(df.temp_vpt).drop(df.prev_vpt)
  return df.rdd.map(lambda x: x.vpt).collect()

def getList(df, col_name, double=True): 
  rows = df.select(F.col(col_name)).collect()
  if double: 
    return [float(row[0]) for row in rows]
  return [row[0] for row in rows]

# %%
from cassandra.cluster import Cluster

cluster = Cluster(['IP-ADDRESS']) # replace localhost with your Cassandra host IP
session = cluster.connect()

# Create keyspace 
session.execute("CREATE KEYSPACE main WITH replication = {'class':'SimpleStrategy', 'replication_factor': 3};")

# Create stock table
session.execute("CREATE TABLE main.stock(TICKER text, SMA_10 LIST<double>, SMA_50 LIST<double>, SMA_100 LIST<double>, DAILY_PERCENTAGE LIST<double>, ATR LIST<double>, VPT LIST<double>, RSI LIST<double>, DATES LIST<date>, OPEN LIST<double>, CLOSE LIST<double>, LOW LIST<double>, HIGH LIST<double>, PRIMARY KEY(TICKER));")

# Create prepared statement
insert_stock = session.prepare("""
    INSERT INTO main.stock (TICKER, SMA_10, SMA_50, SMA_100, DAILY_PERCENTAGE, ATR, VPT, RSI, DATES, OPEN, CLOSE, LOW, HIGH) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

# %%
def executeCalc(df): 
  data = [df.collect()[0][0], calcSimpleMovingAvg(df, 'Close', 10),calcSimpleMovingAvg(df, 'Close', 50),calcSimpleMovingAvg(df, 'Close', 100),calcDailyPercentChange(df), calcATR(df), calcVPT(df), calcRSI(df), getList(df, "Date", False), getList(df, "Open"), getList(df, "Close"),getList(df, "Low"), getList(df, "High")]
  session.execute(insert_stock, (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],data[8],data[9],data[10],data[11],data[12]))
  print(data[0] + " data entered into Cassandra \n")

# %%
from pyspark.sql.functions import col

tickers = df.select(col("Ticker")).distinct().rdd.flatMap(lambda x: x).collect()
stock_dfs = [df.where(df["Ticker"] == ticker) for ticker in tickers]

for df in stock_dfs:
  executeCalc(df)



