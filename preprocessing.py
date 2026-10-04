import pandas as pd

# Load the dataset
data = pd.read_csv("dataset/ml_dataset_saps.csv")

print("Original columns:")
print(data.columns.tolist())

# Remove unnecessary spaces from column names
data.columns = data.columns.str.strip()

print("\nCleaned columns:")
print(data.columns.tolist())

# Remove the serial number column
data = data.drop(columns=["Sno."])

print("\nDataset after removing Sno.:")
print(data.head())

# Display categorical columns
print("\nCategorical columns:")
print(data[["Soil Type", "Season", "Crop Label"]].head())

# Display unique values
print("\nSoil Types:")
print(data["Soil Type"].unique())

print("\nSeasons:")
print(data["Season"].unique())

print("\nCrop Labels:")
print(data["Crop Label"].unique())

# Display number of different crops
print("\nNumber of different crops:")
print(data["Crop Label"].nunique())