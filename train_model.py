import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import warnings
warnings.filterwarnings('ignore')

# Try importing RAPIDS cuML for GPU support
try:
    import cudf
    import cupy as cp
    from cuml.ensemble import RandomForestClassifier as cuRF
    CUDA_AVAILABLE = True
    print("CUDA is available! Using GPU acceleration...")
except ImportError:
    from sklearn.ensemble import RandomForestClassifier
    CUDA_AVAILABLE = False
    print("CUDA is not available. Using CPU instead...")

def preprocess_data(df):
    # Create label encoders dictionary
    label_encoders = {}
    
    # Columns to encode
    categorical_columns = ['gender', 'ethnicity', 'jaundice', 'autism', 'country_of_res', 
                         'used_app_before', 'age_desc', 'relation']

    # Encode categorical variables
    for column in categorical_columns:
        label_encoders[column] = LabelEncoder()
        # Handle missing values with a default category
        df[column] = df[column].fillna('Unknown')
        df[column] = label_encoders[column].fit_transform(df[column])

    # Handle numeric columns
    numeric_columns = ['age'] + [f'A{i}_Score' for i in range(1, 11)] + ['result']
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
        df[column] = df[column].fillna(df[column].mean())

    return df, label_encoders

def train_model(use_cuda=True):
    # Read the dataset
    print("Loading dataset...")
    df = pd.read_csv('train.csv')
    
    # Preprocess the data
    print("Preprocessing data...")
    df, label_encoders = preprocess_data(df)
    
    # Define features and target
    feature_columns = ['age', 'gender', 'ethnicity', 'jaundice', 'autism', 'used_app_before', 
                   'country_of_res', 'age_desc'] + \
                  [f'A{i}_Score' for i in range(1, 11)] + ['result']

    
    X = df[feature_columns]
    y = df['Class/ASD']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if CUDA_AVAILABLE and use_cuda:
        print("Training model on GPU...")
        # Convert to CUDA DataFrame
        X_train_cuda = cudf.DataFrame.from_pandas(X_train)
        y_train_cuda = cudf.Series(y_train)
        X_test_cuda = cudf.DataFrame.from_pandas(X_test)
        y_test_cuda = cudf.Series(y_test)
        
        # Initialize and train the model
        model = cuRF(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train_cuda, y_train_cuda)
        
        # Calculate accuracy
        accuracy = model.score(X_test_cuda, y_test_cuda)
    else:
        print("Training model on CPU...")
        # Initialize and train the model
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Calculate accuracy
        accuracy = model.score(X_test, y_test)
    
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    # Save the model and label encoders
    print("Saving model and encoders...")
    joblib.dump(model, 'autism_model.joblib')
    joblib.dump(label_encoders, 'label_encoders.joblib')
    
    return model, label_encoders

def predict_autism(model, label_encoders, input_data):
    # Remove features not used in training
    allowed_features = ['age', 'gender', 'ethnicity', 'jaundice', 'autism', 
                        'used_app_before'] + \
                        [f'A{i}_Score' for i in range(1, 11)] + ['result']
    
    input_data = {key: input_data[key] for key in allowed_features}

    # Encode categorical fields
    for column, encoder in label_encoders.items():
        if column in input_data:
            input_data[column] = encoder.transform([input_data[column]])[0]

    # Convert to DataFrame and predict
    features = pd.DataFrame([input_data])
    prediction = model.predict(features)
    probability = model.predict_proba(features)

    return {
        'prediction': bool(prediction[0]),
        'probability': float(probability[0][1])
    }


if __name__ == "__main__":
    # Train the model
    model, encoders = train_model(use_cuda=True)
    
    # Example prediction
    sample_input = {
        'age': 25,
        'gender': 'm',
        'ethnicity': 'White-European',
        'jaundice': 'no',
        'autism': 'no',
        'used_app_before': 'no',
        'A1_Score': 1,
        'A2_Score': 1,
        'A3_Score': 1,
        'A4_Score': 1,
        'A5_Score': 1,
        'A6_Score': 1,
        'A7_Score': 1,
        'A8_Score': 1,
        'A9_Score': 1,
        'A10_Score': 1,
        'result': 10
    }
    
    result = predict_autism(model, encoders, sample_input)
    print("\nSample Prediction:")
    print(f"Autism Prediction: {'Positive' if result['prediction'] else 'Negative'}")
    print(f"Probability: {result['probability']*100:.2f}%")