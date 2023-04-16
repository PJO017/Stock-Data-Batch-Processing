from collections import namedtuple
import numpy as np
import pandas as pd
from cassandra.cluster import Cluster
from bokeh.plotting import ColumnDataSource, figure, gridplot, show
from bokeh.resources import CDN
from bokeh.embed import file_html


# replace localhost with your Cassandra host IP
cluster = Cluster(['34.75.190.139'])
session = cluster.connect()


def queryCluster(ticker):
    # Create prepared statement
    get_stock = session.prepare("""
        SELECT * FROM main.stock WHERE TICKER='{}';
        """.format(ticker))

    return session.execute(get_stock).one()


def createLineGraph(ticker, metric, title, color):
    data = queryCluster(ticker)
    dates = [date.date() for date in data.dates]

    graph = figure(x_axis_type="datetime",
                   title="{} for {}".format(title, ticker))
    graph.xaxis.axis_label = 'DATE'
    graph.yaxis.axis_label = '{}'.format(title)
    graph.xaxis.major_label_orientation = 0.8

    x_axis_coordinates = np.array(dates, dtype=np.datetime64)
    y_axis_coordinates = np.array(getattr(data, metric))

    legend_label = title

    graph.line(x_axis_coordinates, y_axis_coordinates,
               color=color, legend_label=legend_label)

    graph.legend.location = "top_left"

    return graph


def createSMAGraph(ticker):
    candlestick = createCandleStick(ticker, "SMA for {}".format(ticker))

    candlestick.xaxis.axis_label = 'DATE'
    candlestick.yaxis.axis_label = '{}'.format("PRICE")

    data = queryCluster(ticker)
    dates = [date.date() for date in data.dates]

    x_axis_coordinates = np.array(dates, dtype=np.datetime64)
    sma_10 = np.array(getattr(data, "sma_10"))
    sma_50 = np.array(getattr(data, "sma_50"))
    sma_100 = np.array(getattr(data, "sma_100"))

    candlestick.line(x_axis_coordinates, sma_10,
                     color="blue", legend_label="SMA 10")
    candlestick.line(x_axis_coordinates, sma_50,
                     color="red", legend_label="SMA 50")
    candlestick.line(x_axis_coordinates, sma_100,
                     color="green", legend_label="SMA 100")

    candlestick.legend.location = "top_left"

    return candlestick


def convertDatatoDF(data):
    data_dict = data._asdict()
    data_dict['dates'] = [date.date()
                          for date in data_dict['dates']]

    datadict = {k: v for k, v in data_dict.items()}
    df = pd.DataFrame(datadict)
    return df


def createCandleStick(ticker, title):
    data = queryCluster(ticker)
    df = convertDatatoDF(data)

    inc = df.close > df.open
    dec = df.open > df.close

    w = 16*60*60*1000

    graph = figure(x_axis_type="datetime",  width=1000, height=400,
                   title=title, background_fill_color="#efefef")
    graph.xaxis.major_label_orientation = 0.8

    graph.segment(df.dates, df.high, df.dates, df.low, color="black")

    graph.vbar(df.dates[dec], w, df.open[dec], df.close[dec], color="#eb3c40")
    graph.vbar(df.dates[inc], w, df.open[inc], df.close[inc], fill_color="white",
               line_color="#49a3a3", line_width=0.6)

    return graph


def generate_visualizations(ticker):
    # Visualize metrics
    mv_avg_graph = createSMAGraph(ticker)

    dp_graph = createLineGraph(ticker, "daily_percentage",
                               "DAILY PERCENTAGE", "red")

    atr_graph = createLineGraph(ticker, "atr", "ATR", "orange")

    vpt_graph = createLineGraph(ticker, "vpt", "VPT",  "green")

    rsi_graph = createLineGraph(ticker, "rsi", "RSI",  "purple")

    grid = gridplot([[mv_avg_graph, dp_graph], [
        vpt_graph, rsi_graph], [atr_graph]])

    html = file_html(grid, CDN, "{}_visualizations".format(ticker))
    print(html)

    return (html)
