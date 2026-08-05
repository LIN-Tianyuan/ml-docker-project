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
## Train the model → Package it as an API → Build a Docker image
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
