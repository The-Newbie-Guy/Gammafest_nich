import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")
train = pd.read_csv('/workspace/train.csv')
test = pd.read_csv('/workspace/test.csv')
sample_sub = pd.read_csv('/workspace/sample submission.csv')

print(f"Train shape: {train.shape}")
print(f"Test shape: {test.shape}")

# Features available in both train and test
common_features = ['is_home', 'neutral', 'confederation_team', 'confederation_opp', 
                   'population_team', 'population_opp', 'gdp_per_capita_team', 'gdp_per_capita_opp',
                   'altitude_venue', 'distance_travel_team', 'distance_travel_opp', 'temperature_venue']

# Create features
def prepare_features(df, is_train=True):
    df = df.copy()
    
    # Fill missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
    
    # Encode categorical variables
    le_conf_team = LabelEncoder()
    le_conf_opp = LabelEncoder()
    
    # Fit on combined data to handle all categories
    all_conf_team = list(df['confederation_team'].fillna('Unknown').unique())
    all_conf_opp = list(df['confederation_opp'].fillna('Unknown').unique())
    
    le_conf_team.fit(all_conf_team)
    le_conf_opp.fit(all_conf_opp)
    
    df['confederation_team_enc'] = le_conf_team.transform(df['confederation_team'].fillna('Unknown'))
    df['confederation_opp_enc'] = le_conf_opp.transform(df['confederation_opp'].fillna('Unknown'))
    
    # Gender encoding
    df['gender_enc'] = (df['gender'] == 'M').astype(int)
    
    return df

train = prepare_features(train, is_train=True)
test = prepare_features(test, is_train=False)

# Select features for modeling
feature_cols = ['is_home', 'neutral', 'confederation_team_enc', 'confederation_opp_enc',
                'population_team', 'population_opp', 'gdp_per_capita_team', 'gdp_per_capita_opp',
                'altitude_venue', 'distance_travel_team', 'distance_travel_opp', 'temperature_venue',
                'gender_enc']

X_train = train[feature_cols]
y_train_goals = train['team_goals']
y_train_opp = train['opp_goals']

X_test = test[feature_cols]

print("\nTraining models...")

# Train models for team_goals and opp_goals
model_goals = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
model_opp = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)

model_goals.fit(X_train, y_train_goals)
model_opp.fit(X_train, y_train_opp)

# Predict
pred_goals = model_goals.predict(X_test)
pred_opp = model_opp.predict(X_test)

# Round predictions
pred_goals = np.round(pred_goals).astype(int)
pred_opp = np.round(pred_opp).astype(int)

# Ensure non-negative
pred_goals = np.maximum(pred_goals, 0)
pred_opp = np.maximum(pred_opp, 0)

# Create submission
submission = pd.DataFrame({
    'Id': test['Id'],
    'team_goals': pred_goals,
    'opp_goals': pred_opp
})

submission.to_csv('/workspace/submission.csv', index=False)
print(f"\nSubmission saved! Shape: {submission.shape}")
print(submission.head(10))
