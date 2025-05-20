import os
import glob
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

MODEL_DIR = "models"
model_files = glob.glob(os.path.join(MODEL_DIR, "iris_rf_model_batch*.pkl"))

if not model_files:
    raise FileNotFoundError("No saved model found in 'models/' directory.")

def extract_batch_number(path):
    basename = os.path.basename(path)
    num = basename.replace("iris_rf_model_batch", "").replace(".pkl", "")
    return int(num)

model_files.sort(key=extract_batch_number)
latest_model_path = model_files[-1]

print(f"Loading model: {latest_model_path}")
model = joblib.load(latest_model_path)

df = pd.read_csv("data/iris.data", header=None)
df.columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']
df.dropna(inplace=True)

le = LabelEncoder()
df['label'] = le.fit_transform(df['class'])

X = df[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
y = df['label']

y_pred = model.predict(X)
acc = accuracy_score(y, y_pred)

print(f"Final accuracy using model '{os.path.basename(latest_model_path)}': {acc:.2%}")