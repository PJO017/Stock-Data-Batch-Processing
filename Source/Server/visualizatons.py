import numpy as np
from cassandra.cluster import Cluster
from bokeh.plotting import figure, output_file, show

# replace localhost with your Cassandra host IP
cluster = Cluster(['localhost'])
session = cluster.connect()


def queryCluster(ticker):
    # Create prepared statement
    get_stock = session.prepare("""
        SELECT * FROM main.stock WHERE TICKER='{}';
        """.format(ticker))

    return session.execute(get_stock).one()


def generate_visualizations(ticker):
    data = queryCluster(ticker)
    dates = [date.date() for date in data.dates]

    # Visualize metrics
    moving_avg = data.moving_avg
    graphHelper(ticker, moving_avg, "MOVING AVERAGE", dates)

    daily_percentage = data.daily_percentage
    graphHelper(ticker, daily_percentage, "DAILY PERCENTAGE", dates)

    atr = data.atr
    graphHelper(ticker, atr, "ATR", dates)

    vpt = data.vpt
    graphHelper(ticker, vpt, "VPT", dates)

    rsi = data.rsi
    graphHelper(ticker, rsi, "RSI", dates)


def graphHelper(ticker, yaxis, title, dates):

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
