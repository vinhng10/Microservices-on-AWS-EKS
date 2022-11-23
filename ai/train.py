import joblib
from pathlib import Path

import pandas as pd
from sklearn.datasets import make_moons
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.preprocessing import StandardScaler

SEED = 42

# Generate data:
data = make_moons(100, noise=0.3, random_state=SEED)
data = pd.DataFrame({
    "x": data[0][:, 0],
    "y": data[0][:, 1],
    "class": data[1].astype(int),
    "origin": ["original"] * (len(data[1]))
})

# Prepare data for training:
X, y = data[["x", "y"]].to_numpy(), data["class"].to_numpy()
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Train model:
model = GaussianProcessClassifier(1.0 * RBF(0.5))
model.fit(X, y)

# Save artifacts:
artifacts = Path("artifacts")
artifacts.mkdir(parents=True, exist_ok=True)
joblib.dump(scaler, artifacts / "scaler.joblib")
joblib.dump(model, artifacts / "model.joblib") 