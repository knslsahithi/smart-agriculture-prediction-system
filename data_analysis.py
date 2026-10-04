import pandas as pd

# Load the dataset
data = pd.read_csv("dataset/ml_dataset_saps.csv")

# Display the first 5 rows
print("\nFirst 5 rows:")
print(data.head())

# Display number of rows and columns
print("\nDataset shape:")
print(data.shape)

# Display column names
print("\nColumn names:")
print(data.columns.tolist())

# Display information about the dataset
print("\nDataset information:")
print(data.info())

# Check missing values
print("\nMissing values:")
print(data.isnull().sum())

# Check duplicate records
print("\nDuplicate records:")
print(data.duplicated().sum())