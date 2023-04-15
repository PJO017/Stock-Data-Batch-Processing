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

    # Visualize ATR
    atr = data.atr
    output_file("atr.html")
    graph = figure(x_axis_type="datetime", title="{} ATR".format(ticker))
    graph.xaxis.axis_label = 'Date'
    graph.yaxis.axis_label = 'ATR (14 day)'

    x_axis_coordinates = np.array(dates, dtype=np.datetime64)
    y_axis_coordinates = np.array(atr)
    color = "lightblue"
    legend_label = ticker
    graph.line(x_axis_coordinates, y_axis_coordinates,
               color=color, legend_label=legend_label)

    graph.legend.location = "top_left"

    show(graph)


generate_visualizations("TMUS")
