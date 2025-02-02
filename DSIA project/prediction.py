import pandas as pd 
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
import joblib

# Read the data
data = pd.read_csv('data.csv')

# Check for missing values
print(data.isnull().sum())
# Define features and targets
features = ['min_sip','min_lumpsum','expense_ratio','fund_size_cr','fund_age_yr','sortino','alpha','sd','sharpe','beta']
targets = ['category','sub_category','scheme_name','amc_name']
label_encoders={}
for target in targets:
    le=LabelEncoder()
    data[target]=le.fit_transform(data[target])
    label_encoders[target]=le

joblib.dump(label_encoders,'label_encoder.pkl')
targets = ['category','sub_category','scheme_name','amc_name','returns_1yr','returns_3yr','returns_5yr']
# Separate features and targets
X = data[features]
y = data[targets]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Initialize and train the RandomForestRegressor
classifier = RandomForestRegressor(n_estimators=10, random_state=42)
imputer = SimpleImputer(strategy='mean')
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)
classifier.fit(X_train_imputed, y_train)

# Make predictions
y_prediction = classifier.predict(X_test_imputed)

# Calculate Mean Squared Error
mse = mean_squared_error(y_test, y_prediction)
print("Mean Squared Error:", mse)

# Save the trained model
joblib.dump(classifier, 'model1.pkl')
