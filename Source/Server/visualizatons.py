from collections import namedtuple
import numpy as np
import pandas as pd
from cassandra.cluster import Cluster
from bokeh.plotting import ColumnDataSource, figure, gridplot, show
from bokeh.resources import CDN
from bokeh.embed import file_html


# replace localhost with your Cassandra host IP
cluster = Cluster(['34.148.39.178'])
session = cluster.connect()


def queryCluster(ticker):
    # Create prepared statement
    get_stock = session.prepare("""
        SELECT * FROM main.stock WHERE TICKER='{}';
        """.format(ticker))

    return session.execute(get_stock).one()


def createLineGraph(ticker, metric, title, color, year):
    data = queryCluster(ticker)
    df = convertDatatoDF(data)
    filtered_df = df[df['dates'].dt.year == year]

    graph = figure(x_axis_type="datetime",
                   title="{} for {}".format(title, ticker))
    graph.xaxis.axis_label = 'DATE'
    graph.yaxis.axis_label = '{}'.format(title)
    graph.xaxis.major_label_orientation = 0.8

    x_axis_coordinates = np.array(filtered_df['dates'], dtype=np.datetime64)
    y_axis_coordinates = np.array(filtered_df[metric])

    legend_label = title

    graph.line(x_axis_coordinates, y_axis_coordinates,
               color=color, legend_label=legend_label)

    graph.legend.location = "top_left"

    return graph


def createSMAGraph(ticker, year):
    candlestick = createCandleStick(
        ticker, "SMA for {}".format(ticker), year)

    candlestick.xaxis.axis_label = 'DATE'
    candlestick.yaxis.axis_label = '{}'.format("PRICE")

    data = queryCluster(ticker)
    df = convertDatatoDF(data)
    filtered_df = df[df['dates'].dt.year == year]

    x_axis_coordinates = np.array(filtered_df['dates'], dtype=np.datetime64)
    sma_10 = np.array(filtered_df["sma_10"])
    sma_50 = np.array(filtered_df["sma_50"])
    sma_100 = np.array(filtered_df["sma_100"])

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
    df['dates'] = pd.to_datetime(df['dates'])
    return df


def createCandleStick(ticker, title, year):
    data = queryCluster(ticker)
    df = convertDatatoDF(data)
    filtered_df = df[df['dates'].dt.year == year]

    inc = filtered_df.close > filtered_df.open
    dec = filtered_df.open > filtered_df.close

    w = 16*60*60*1000

    graph = figure(x_axis_type="datetime",  width=1000, height=400,
                   title=title, background_fill_color="#efefef", sizing_mode="stretch_width")
    graph.xaxis.major_label_orientation = 0.8

    graph.segment(filtered_df.dates, filtered_df.high,
                  filtered_df.dates, filtered_df.low, color="black")

    graph.vbar(filtered_df.dates[dec], w, filtered_df.open[dec],
               filtered_df.close[dec], color="#eb3c40")
    graph.vbar(filtered_df.dates[inc], w, filtered_df.open[inc], filtered_df.close[inc], fill_color="white",
               line_color="#49a3a3", line_width=0.6)

    return graph


from bokeh.io import output_file, show
from bokeh.layouts import row
from bokeh.models import Div
from bokeh.layouts import column, grid



def generate_visualizations(ticker, year):
    mv_avg_graph = createSMAGraph(ticker, year)

    dp_graph = createLineGraph(ticker, "daily_percentage",
                               "DAILY PERCENTAGE", "red", year)

    atr_graph = createLineGraph(ticker, "atr", "ATR", "orange", year)

    vpt_graph = createLineGraph(ticker, "vpt", "VPT",  "green", year)

    rsi_graph = createLineGraph(ticker, "rsi", "RSI",  "purple", year)

    grid1 = row(mv_avg_graph)
    grid = gridplot([[vpt_graph, rsi_graph], [atr_graph, dp_graph]])

    grid1.width = 1900
    grid1.height = 300
    dp_graph.width = vpt_graph.width = rsi_graph.width = atr_graph.width = 900
    dp_graph.height = vpt_graph.height = rsi_graph.height = atr_graph.height = 300

    html = file_html([grid1, grid], CDN, "{}_visualizations".format(ticker))

    return html
