echo "Stopping nodes..."
docker stop node1 node2 node3

echo "Removing containers..."
docker rm node1 node2 node3

echo "Removing cluster network..."
docker network rm cassandra-network


