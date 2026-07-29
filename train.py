from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load the classic Iris dataset
X, y = load_iris(return_X_y=True)

# Train a Simple Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the model to a file
joblib.dump(model, "model.joblib")
print("Model training is complete; it has been saved as model.joblib.")