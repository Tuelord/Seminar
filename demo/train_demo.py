"""
demo/train_demo.py
A minimal scikit-learn + MLflow training demo.
Run:  python train_demo.py
"""
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MLFLOW_TRACKING_URI = "http://localhost:5000"
EXPERIMENT_NAME = "iris-demo"

def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    params = {"n_estimators": 50, "max_depth": 4, "random_state": 42}

    with mlflow.start_run():
        mlflow.log_params(params)

        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        acc = accuracy_score(y_test, model.predict(X_test))
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(model, "model")

        print(f"Accuracy: {acc:.4f}  -- model logged to MLflow")

if __name__ == "__main__":
    main()
