import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# 1. Load the Kaggle dataset
data = pd.read_csv("dataset/Crop_recommendation.csv")

print("Dataset loaded successfully!")
print("Dataset shape:", data.shape)

# 2. Separate input features and target
X = data[
    [
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall"
    ]
]

y = data["label"]

print("\nInput features:")
print(X.head())

print("\nTarget values:")
print(y.head())

# 3. Split the dataset into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining data size:", X_train.shape)
print("Testing data size:", X_test.shape)

# 4. Create the Decision Tree model
model = DecisionTreeClassifier(random_state=42)

# 5. Train the model
model.fit(X_train, y_train)

print("\nDecision Tree model trained successfully!")

# 6. Make predictions on test data
y_pred = model.predict(X_test)

# 7. Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\nDecision Tree Accuracy:")
print(accuracy)

# 8. Display detailed performance
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 9. Create the Random Forest model
rf_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# 10. Train the Random Forest model
rf_model.fit(X_train, y_train)

print("\nRandom Forest model trained successfully!")

# 11. Make predictions
rf_pred = rf_model.predict(X_test)

# 12. Calculate accuracy
rf_accuracy = accuracy_score(y_test, rf_pred)

print("\nRandom Forest Accuracy:")
print(rf_accuracy)

# 13. Display classification report
print("\nRandom Forest Classification Report:")
print(classification_report(y_test, rf_pred))


# 14. Scale the features for KNN
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 15. Create the KNN model
knn_model = KNeighborsClassifier(n_neighbors=5)

# 16. Train the KNN model
knn_model.fit(X_train_scaled, y_train)

print("\nKNN model trained successfully!")

# 17. Make predictions
knn_pred = knn_model.predict(X_test_scaled)

# 18. Calculate accuracy
knn_accuracy = accuracy_score(y_test, knn_pred)

print("\nKNN Accuracy:")
print(knn_accuracy)

# 19. Display classification report
print("\nKNN Classification Report:")
print(classification_report(y_test, knn_pred))


# 20. Create the SVM model
svm_model = SVC(kernel="rbf")

# 21. Train the SVM model using scaled data
svm_model.fit(X_train_scaled, y_train)

print("\nSVM model trained successfully!")

# 22. Make predictions
svm_pred = svm_model.predict(X_test_scaled)

# 23. Calculate accuracy
svm_accuracy = accuracy_score(y_test, svm_pred)

print("\nSVM Accuracy:")
print(svm_accuracy)

# 24. Display classification report
print("\nSVM Classification Report:")
print(classification_report(y_test, svm_pred))


# 25. Create models folder if it doesn't exist
os.makedirs("models", exist_ok=True)

# 26. Save the Random Forest model
joblib.dump(rf_model, "models/crop_prediction_model.pkl")

print("\nRandom Forest model saved successfully!")
print("Saved file: models/crop_prediction_model.pkl")