docker network create cassandra-network

echo "Network created."

docker run --name node1 --network cassandra-network -e CASSANDRA_CLUSTER_NAME="prod_cluster" -p 7000:7000 -p 9042:9042 -d cassandra:4.1

echo "Node 1 created."
echo "Waiting for node setup..."

sleep 60

echo "Node 1 setup complete."

docker run --name node2 --network cassandra-network -e CASSANDRA_SEEDS=node1 -e CASSANDRA_CLUSTER_NAME="prod_cluster" -d cassandra:4.1

echo "Node 2 created."
echo "Waiting for node setup..."

sleep 60

echo "Node 2 setup complete."

docker run --name node3 --network cassandra-network -e CASSANDRA_SEEDS=node1,node2 -e CASSANDRA_CLUSTER_NAME="prod_cluster" -d cassandra:4.1

echo "Node 3 created."
echo "Cluster initialization complete"

docker exec -it node1 nodetool status