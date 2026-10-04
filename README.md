# 🌱 Smart Agriculture Prediction System

A Machine Learning based web application that recommends suitable crops based on soil and environmental conditions.

## 📌 Project Overview

The Smart Agriculture Prediction System uses Machine Learning to analyze agricultural parameters such as:

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- Soil pH
- Rainfall

Based on these inputs, the system predicts a suitable crop using a trained Random Forest classification model.

The project provides a user-friendly web interface where users can register, log in, enter agricultural parameters, receive crop recommendations, and view their prediction history.

---

## 🎯 Objectives

- Develop a Machine Learning based crop recommendation system.
- Analyze soil and environmental parameters.
- Compare multiple Machine Learning algorithms.
- Select the best-performing model.
- Develop a web-based prediction interface.
- Store user prediction history.
- Provide a simple and user-friendly agricultural decision-support system.

---

## 🧠 Machine Learning Algorithms

The following algorithms were evaluated:

| Algorithm | Accuracy |
|-----------|----------|
| Decision Tree | 97.95% |
| Random Forest | 99.55% |
| K-Nearest Neighbors | 97.95% |
| Support Vector Machine | 98.41% |

Random Forest achieved the highest accuracy on the held-out test set and was selected as the final prediction model.

> Note: The reported accuracy represents performance on the project's held-out test split and should not be interpreted as guaranteed real-world prediction accuracy.

---

## 📊 Dataset

The primary Machine Learning dataset used in this project is the Crop Recommendation dataset containing agricultural soil and environmental parameters.

Features:

- N
- P
- K
- Temperature
- Humidity
- pH
- Rainfall

Target:

- Crop Label

The project also contains a custom Smart Agriculture dataset created for project analysis and reference.

---

## 🛠️ Technologies Used

### Programming Language

- Python

### Machine Learning

- Scikit-learn
- Pandas
- NumPy
- Joblib

### Web Development

- Flask
- HTML
- CSS
- JavaScript

### Database

- SQLite

### Development Environment

- Visual Studio Code
- Python Virtual Environment

---

## 🏗️ System Architecture

```text
                 User
                   |
                   v
          Web Application
             HTML/CSS/JS
                   |
                   v
              Flask App
                   |
          +--------+--------+
          |                 |
          v                 v
    ML Prediction       SQLite Database
          |                 |
          v                 v
   Random Forest       User & History
          |
          v
   Recommended Crop