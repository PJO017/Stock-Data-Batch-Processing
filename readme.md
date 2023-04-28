# Stock Market Data Batch Processing

## Description
 This is a cloud computing system for performing batch processing and analysis of historical stock data. The system consists of three main components: the Apache Spark data analysis application, the Cassandra cluster, and the HTTP server used to generate visualizations from data stored in the Cassandra cluster.
 
 Technical Indicators Calculated:  
 - Daily Percentage 
 - Average True Range (ATR)
 - Relative Strength Index (RSI)
 - Volume Price Trend (VPT)
 - Simple Moving Average (SMA)

### Dependencies

 - Java 8/11/17
 - Python 3.7+
 - Python Cassandra Drive (Install with `pip install cassandra-driver`)
 - Pyspark 3.3.2
 - Docker

### Execute Program Locally

- Start Cassandra cluster by running `init_cluster.sh`
- Place IP Address printed from `init_cluster.sh` on line 74 of `Analysis.py`:

  ```python
  cluster = Cluster(['IP-ADDRESS']) # replace with your Cassandra host IP
  ```

- Download dataset from: [Dataset](https://drive.google.com/drive/folders/1KWJ0vnp4ezD54BtjWUgHAHs13wPE1-w_)
- Create directory Named `Data` in Source directory and place dataset file
- Run `Analysis.py` to begin data analysis
- After data analysis is complete:
- Start HTTP server with `python server.py` in `Server` directory
- Open `index.html` in `Client` directory to access frontend
- In Client enter ticker and year of the stock you want to retrieve and click `Send` button
