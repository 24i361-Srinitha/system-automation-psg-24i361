
import pandas as pd # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.tree import DecisionTreeClassifier # type: ignore
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix # type: ignore

data = pd.read_csv(r"C:\Users\pl\Documents\GitHub\system-automation-psg-24i361\Day 2\data\day2_sample.csv")
X = data[['temperature', 'pressure', 'vibration', 'current', 'rpm']]
y = data['state']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = DecisionTreeClassifier(random_state=42)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred, zero_division=0))

print("Confusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

new_data = pd.DataFrame([{
    'temperature': 75.0,
    'pressure': 5.5,
    'vibration': 2.8,
    'current': 16.0,
    'rpm': 2500
}])

prediction = model.predict(new_data)
print("\nPredicted State:", prediction[0])
