from cassandra.cluster import Cluster

# replace localhost with your Cassandra host IP
cluster = Cluster(['localhost'])
session = cluster.connect()


def visualize(ticker):

    # Create prepared statement
    get_stock = session.prepare("""
        SELECT * FROM main.stock WHERE TICKER='{}';
        """.format(ticker))

    ticker_data = session.execute(get_stock).one()
    return ticker_data
