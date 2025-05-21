import os
import glob
import pandas as pd
from sklearn.metrics import accuracy_score
import joblib

MODEL_DIR = "models"
MODEL_PATTERN = "iris_*_model_batch*.pkl" 
TEST_DATA_PATH = "data/iris.data"

model_files = glob.glob(os.path.join(MODEL_DIR, MODEL_PATTERN))

if not model_files:
    print("No saved model found in 'models/' directory.")
    print("Files in 'models/':", os.listdir("models"))
    raise FileNotFoundError("No model matching pattern 'iris_*_model_batch*.pkl'")

def extract_batch_number(path):
    name = os.path.basename(path)
    return int(name.split("batch")[-1].split(".pkl")[0])

model_files.sort(key=extract_batch_number)
latest_model_path = model_files[-1]

print(f"Loading model: {latest_model_path}")
model = joblib.load(latest_model_path)

df = pd.read_csv(TEST_DATA_PATH, header=None)
df.columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']
df.dropna(inplace=True)

label_map = {"Iris-setosa": 0, "Iris-versicolor": 1, "Iris-virginica": 2}
df['label'] = df['class'].map(label_map)

X = df[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
y = df['label']

y_pred = model.predict(X)
acc = accuracy_score(y, y_pred)

print(f"Final accuracy using model '{os.path.basename(latest_model_path)}': {acc:.2%}")