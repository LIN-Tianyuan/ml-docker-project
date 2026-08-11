# STEP
## Set up the environment
### 1. Check/Install Homebrew
```bash
which brew
```
If a path is displayed (such as `/usr/local/bin/brew` or `/opt/homebrew/bin/brew`), it means it's already installed.

If not, run this installer:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
### 2. Install Docker Desktop
```bash
brew install --cask docker
```
```bash
docker --version
docker run hello-world
# Hello from Docker!
```
### 3. Install kubectl
```bash
brew install kubectl
```
```bash
kubectl version --client
```
### 4. Install minikube
```bash
brew install minikube
```
Verify and start (the image will be downloaded automatically on first startup; this may take a few minutes):
```bash
minikube start
# Done! kubectl is now configured to use "minikube" cluster
```
```bash
kubectl get nodes
# Should see a node with a status of “Ready.”
```
## Docker + Kubernetes
Train the model → Package it as an API → Build a Docker image
### 1. Create a project directory
```bash
mkdir -p ~/ml-docker-project
cd ~/ml-docker-project
```

### 2. Create a Python virtual environment and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install scikit-learn fastapi uvicorn joblib
```

### 3. Train a simple model
```bash
# train.py
# python train.py

# A new file named "model.joblib" has appeared in the current directory.

```

### 4. Create a FastAPI Service
```bash
# app.py
```

### 5. Local Testing
```bash
uvicorn app:app --reload --port 8000

# Uvicorn running on http://127.0.0.1:8000

# Open another terminal window 
# (while keeping the service running in the first terminal) 
# and test the health check interface:

curl http://127.0.0.1:8000/health
# {"status":"ok"}

curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
  
# {"prediction":"setosa"}
```

### 6. Create a requirements.txt file
First, finalize the list of dependencies so they can be installed during the Docker build:
```bash
pip freeze > requirements.txt
```

### 7. Create a Dockerfile
```bash
# dockerfile
```
 - `COPY requirements.txt.` 
   - This is placed separately at the beginning to take advantage of Docker’s layer caching mechanism—as long as the dependencies haven’t changed, packages don’t need to be reinstalled during a rebuild, which significantly speeds up the build process
 - `host 0.0.0.0` is very important
   - Using `127.0.0.1` works fine when running locally, but you must bind `0.0.0.0` inside the container; otherwise, external users won’t be able to access the service inside the container (this is the most common pitfall for beginners).

### 8. Build an image
```bash
docker build -t iris-classifier:v1 .

docker images
# iris-classifier
```

### 9. Run the container and verify that it works properly
```bash
docker run -d -p 8000:8000 --name iris-api iris-classifier:v1
# Parameter Description:
# -d: Run in the background
# -p 8000:8000: Map port 8000 inside the container to port 8000 on computer
# --name iris-api: Assign a name to the container for easier management

docker ps
# iris-api : Up
```

### 10. Test Services in a Container
```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 6.3, "sepal_width": 3.3, "petal_length": 6.0, "petal_width": 2.5}'
# virginica
```

### 11. First, clear the local containers (to avoid port conflicts).
```bash
docker stop iris-api
docker rm iris-api
```

### 12. Load the image into minikube
Since Minikube is a standalone Docker environment, 
it cannot see the images we’ve built locally; 
need to manually load them into it:
```bash
minikube image load iris-classifier:v1
```
```bash
minikube image ls | grep iris-classifier
# If can see the mirror name, it means the mirror has loaded successfully.
```

### 13. Create a Deployment configuration file
```bash
# deployment.yaml
```
`replicas: 2`: 
 - Starts 2 Pod replicas so that the service can continue even if one fails; this is the foundation of K8s “high availability.” 

`imagePullPolicy: Never`: 
 - Since we’re loading the image locally rather than pulling it from a remote repository like Docker Hub, we must explicitly declare this; otherwise, K8s will report an error stating that the image cannot be found.

`resources.requests/limits`: 
 - GPU/resource pool optimization — each container declares how many resources it needs, and K8s uses this information for scheduling
### 14. Create a Service Configuration File
```bash
service.yaml
```
 - Deployment manages Pods (where containers actually run), but a Pod’s IP address is dynamic and unstable. 

 - A Service provides a stable access point for this group of Pods and automatically performs load balancing, distributing requests across the two replicas.

### 15. Deploy to the cluster
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```
Check Status:
```bash
kubectl get pods

NAME                                          READY   STATUS    RESTARTS   AGE
iris-classifier-deployment-5576fbf75f-nxfls   1/1     Running   0          20s
iris-classifier-deployment-5576fbf75f-xkltd   1/1     Running   0          20s

kubectl get deployments

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
iris-classifier-deployment   2/2     2            2           31s

kubectl get services

(venv) (base) ningmenmaodeMBP:ml-docker-project citron$ kubectl get services
NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
iris-classifier-service   NodePort    10.99.246.34   <none>        8000:30080/TCP   29s
```

 - The complete workflow: train the model → wrap it as an API → containerize it using Docker → deploy it to Kubernetes → expose it as a service for access. 
 - The core framework of MLOps.
### 16. Creating a “New Version”

 - Straightforward change to the API by adding a version number field to simulate the release of a new version:
```python
# app.py
@app.post("/predict")
def predict(features: IrisFeatures):
    data = np.array([[
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width
    ]])
    prediction = model.predict(data)
    species = ["setosa", "versicolor", "virginica"]
    return {"prediction": species[int(prediction[0])], "model_version": "v2"}
```

### 17. Build a new image (tag it as v2)
```bash
docker build -t iris-classifier:v2 .
minikube image load iris-classifier:v2
```

### 18. Update the Deployment Image Version

Update it directly via the command line (which more closely resembles a real CI/CD scenario):
```bash
kubectl set image deployment/iris-classifier-deployment iris-classifier=iris-classifier:v2
```

### 19. Watch the rolling update process in real time
Run this command now and observe the changes to the Pods:
```bash
kubectl rollout status deployment/iris-classifier-deployment
```

Open another terminal window and run the following commands quickly several times in a row:
```bash
kubectl get pods
```

 - As the old Pods(v1) are gradually shut down and the new Pods(v2) are gradually started up, at least one Pod remains running throughout the entire process.
 - The principle behind "zero downtime updates."

### 20. View Update History and Roll Back
In a real production environment, “After a new version goes live, we discover an issue and need to roll back immediately.”
```bash
kubectl rollout history deployment/iris-classifier-deployment
```

Roll back to the previous version
```bash
kubectl rollout undo deployment/iris-classifier-deployment
```

Test the API again, the `model_version` field is gone (indicating that it has reverted to v1):
```bash
curl -X POST http://127.0.0.1:50748/predict -H "Content-Type: application/json" -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

### 21. Conclusion
 - Trained a classification model
 - Wrapped it as a service using FastAPI
 - Wrote a Dockerfile to containerize it
 - Deployed it to Kubernetes and configured two replicas for high availability
 - Conducted rolling updates and rollback drills.