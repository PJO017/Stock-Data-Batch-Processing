import numpy as np
from cassandra.cluster import Cluster
from bokeh.plotting import figure, gridplot
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


def createGraph(ticker, yaxis, title, dates, color):
    graph = figure(x_axis_type="datetime", title="{} {}".format(ticker, title))
    graph.xaxis.axis_label = 'Date'
    graph.yaxis.axis_label = '{}'.format(title)

    x_axis_coordinates = np.array(dates, dtype=np.datetime64)
    y_axis_coordinates = np.array(yaxis)
    legend_label = ticker
    graph.line(x_axis_coordinates, y_axis_coordinates,
               color=color, legend_label=legend_label)

    graph.legend.location = "top_left"

    return graph


def generate_visualizations(ticker):
    data = queryCluster(ticker)
    dates = [date.date() for date in data.dates]

    # Visualize metrics
    moving_avg = data.moving_avg
    mv_avg_graph = createGraph(
        ticker, moving_avg, "MOVING AVERAGE", dates, "blue")

    daily_percentage = data.daily_percentage
    dp_graph = createGraph(ticker, daily_percentage,
                           "DAILY PERCENTAGE", dates, "red")

    atr = data.atr
    atr_graph = createGraph(ticker, atr, "ATR", dates, "orange")

    vpt = data.vpt
    vpt_graph = createGraph(ticker, vpt, "VPT", dates, "green")

    rsi = data.rsi
    rsi_graph = createGraph(ticker, rsi, "RSI", dates, "purple")

    grid = gridplot([[mv_avg_graph, dp_graph], [
                    vpt_graph, rsi_graph], [atr_graph]])

    html = file_html(grid, CDN, "{}_visualizations".format(ticker))
    print(html)

    return (html)


generate_visualizations("TMUS")
