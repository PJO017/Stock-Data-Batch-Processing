import numpy as np
from cassandra.cluster import Cluster
from bokeh.plotting import figure, output_file, show

# replace localhost with your Cassandra host IP
cluster = Cluster(['104.196.157.153'])
session = cluster.connect()


def queryCluster(ticker):
    # Create prepared statement
    get_stock = session.prepare("""
        SELECT * FROM main.stock WHERE TICKER='{}';
        """.format(ticker))

    return session.execute(get_stock).one()


def generate_visualizations(ticker):
    data = queryCluster(ticker)

    # Visualize metrics
    moving_avg = data.moving_avg
    graphHelper(ticker, moving_avg, "MOVING AVERAGE", data)

    daily_percentage = data.daily_percentage
    graphHelper(ticker, daily_percentage, "DAILY PERCENTAGE", data)

    atr = data.atr
    graphHelper(ticker, atr, "ATR", data)

    vpt = data.vpt
    graphHelper(ticker, vpt, "VPT", data)

    rsi = data.rsi
    graphHelper(ticker, rsi, "RSI", data)


def graphHelper(ticker, yaxis, title, data):
    dates = [date.date() for date in data.dates]

    output_file("output.html")
    graph = figure(x_axis_type="datetime", title="{} {}".format(ticker, title))
    graph.xaxis.axis_label = 'Date'
    graph.yaxis.axis_label = '{} (14 day)'.format(title)

    x_axis_coordinates = np.array(dates, dtype=np.datetime64)
    y_axis_coordinates = np.array(yaxis)
    color = "lightblue"
    legend_label = ticker
    graph.line(x_axis_coordinates, y_axis_coordinates,
               color=color, legend_label=legend_label)

    graph.legend.location = "top_left"

    show(graph)

generate_visualizations("TMUS")
