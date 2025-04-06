from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
from train_model import predict_autism
import os

app = Flask(__name__)

# Load the trained model and encoders
try:
    model = joblib.load('autism_model.joblib')
    encoders = joblib.load('label_encoders.joblib')
    MODEL_LOADED = True
    print("Model and encoders loaded successfully!")
except Exception as e:
    MODEL_LOADED = False
    print(f"Error loading model: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/prediction')
def prediction_form():
    return render_template('prediction.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not MODEL_LOADED:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.'
        }), 500

    try:
        print("Received form data:", request.form)  # Debug print
        
        # Get form data with error handling
        required_fields = ['age', 'gender', 'ethnicity', 'jaundice', 'autism', 
                         'used_app_before', 'country_of_res', 'result', 'age_desc']
        
        # Check for missing required fields
        missing_fields = [field for field in required_fields if field not in request.form]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Get form data
        data = {
            'age': float(request.form['age']),
            'gender': request.form['gender'],
            'ethnicity': request.form['ethnicity'],
            'jaundice': request.form['jaundice'],
            'autism': request.form['autism'],
            'used_app_before': request.form['used_app_before'],
            'country_of_res': request.form['country_of_res'],
            'result': int(request.form['result']),
            'age_desc': request.form['age_desc']
        }

        # Add AQ scores
        aq_score = 0
        for i in range(1, 11):
            score_field = f'A{i}_Score'
            if score_field not in request.form:
                return jsonify({
                    'error': f'Missing AQ score: {score_field}'
                }), 400
            data[score_field] = int(request.form[score_field])

        print("Processed data:", data)  # Debug print
        
        # Make prediction using the model
        try:
            result = predict_autism(model, encoders, data)
            print("Prediction result:", result)  # Debug print
            
            # Return result page with detailed information
            return render_template('result.html', 
                                prediction=result['prediction'],
                                probability=result['probability'] * 100,
                                score=data['result'],
                                age=data['age'],
                                gender=data['gender'],
                                ethnicity=data['ethnicity'],
                                country=data['country_of_res'])
        except Exception as e:
            print(f"Prediction error: {str(e)}")  # Debug print
            return jsonify({
                'error': f'Error making prediction: {str(e)}'
            }), 500

    except Exception as e:
        print(f"Form processing error: {str(e)}")  # Debug print
        return jsonify({
            'error': f'Error processing form data: {str(e)}'
        }), 400

#if __name__ == '__main__':
 #   app.run(debug=True) 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)



    
