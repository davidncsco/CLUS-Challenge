# Pre-requisite: install docker and kubectl on your machine
# Copy /etc/rancher/k3s/k3s.yaml from master node (10.0.0.60)
# to your ~/.kube/config

# To build frontend app container for Raspberry Pi cluster
# cd to frontend directory and execute this docker command
cd frontend
docker buildx build --platform linux/arm64 -t <frontend container name>:<tag>
# Push image to docker hub
docker push <backend container name>:<tag>
cd ../deployment
# edit devrel500_frontend.yaml and update with the above container name/tag
kubectl apply -f devrel500_frontend.yaml

# To build and deploy backend app container for Raspberry Pi cluster
# execute these commands
cd backend
docker buildx build --platform linux/arm64 -t <backend container name>:<tag>
# Push image to docker hub
docker push <backend container name>:<tag>
cd ../deployment
# edit devrel500_backend.yaml and update with the above container name/tag
kubectl apply -f devrel500_backend.yaml

# Check if all app deployed to server
kubectl get all