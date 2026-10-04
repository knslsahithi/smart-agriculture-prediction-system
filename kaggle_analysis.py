import pandas as pd

# Load Kaggle dataset
data = pd.read_csv("dataset/Crop_recommendation.csv")

print("\nFirst 5 rows:")
print(data.head())

print("\nDataset shape:")
print(data.shape)

print("\nColumn names:")
print(data.columns.tolist())

print("\nDataset information:")
print(data.info())

print("\nMissing values:")
print(data.isnull().sum())

print("\nDuplicate records:")
print(data.duplicated().sum())

print("\nCrop distribution:")
print(data["label"].value_counts())