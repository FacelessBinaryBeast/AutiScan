# AutiScan

AutiScan is a lightweight, privacy-focused autism screening web app that uses a trained machine learning model (Random Forest) to provide a screening assessment based on an AQ-10 questionnaire and basic demographic information. This repository contains the web UI (Flask), the model training script, pre-trained model files, and the static/templates used by the site.

> Important: This project provides a screening tool — not a medical diagnosis. Results are indicative only. Consult a qualified clinician for diagnostic evaluation.

## Table of contents
- Project overview
- Quick start
- Project structure
- How it works (short)
- API / Routes
- Retraining the model
- Dependencies
- Troubleshooting
- License & credits

## Try the Live Web App 🌐  
[autiscan.onrender.com](https://autiscan.onrender.com)


## Project overview

AutiScan collects basic demographic data and 10 short Autism Spectrum Quotient (AQ-10) items via a web form, computes an AQ score, and feeds encoded features to a Random Forest classifier to estimate the probability that the participant displays autism spectrum traits. The UI is implemented with Flask templates and minimal client-side JavaScript.

## Quick start (Windows / PowerShell)

1. Create a virtual environment and install deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. (Optional) If you don't have pre-built model files or want to retrain, run the training script:

```powershell
python train_model.py
```

This will create `autism_model.joblib` and `label_encoders.joblib` in the project root.

3. Run the Flask app:

```powershell
python app.py
# or if using flask CLI: set FLASK_APP=app.py; flask run
```

4. Open your browser at http://127.0.0.1:5000 and click "Start Screening".

## Project structure

- `app.py` — Flask application entry point. Routes include `/`, `/credits`, `/prediction`, and `/predict` (POST). Loads `autism_model.joblib` and `label_encoders.joblib` at startup.
- `train_model.py` — Contains dataset preprocessing, label encoding, model training (CPU via scikit-learn RandomForestClassifier or optional GPU via cuML if available), saving of model and encoders, and `predict_autism` helper used by `app.py`.
- `train.csv` — Training dataset used by `train_model.py` (not included if removed for privacy; present in repo root here).
- `autism_model.joblib` — Saved sklearn/cuML model used for inference.
- `label_encoders.joblib` — Saved label encoder dictionary used to encode categorical fields for inference.
- `templates/` — Jinja templates: `index.html`, `prediction.html`, `result.html`, `credits.html`.
- `static/styles.css` — Site styles.
- `script.js` — Small site scripts (smooth scrolling, feature animations).
- `requirements.txt` — Key Python dependencies.

## How it works (short)

1. The user opens the form at `/prediction` and provides demographics and the 10 AQ items.
2. Client-side JavaScript computes the AQ total and appends hidden `result` and `age_desc` fields to the form.
3. The form posts to `/predict` (POST). `app.py` validates fields and calls `predict_autism` (from `train_model.py`) to prepare features and run model inference.
4. The server renders `result.html` with the boolean prediction, probability (as a percent), and AQ score.

## API / Routes

- `GET /` — Home page (landing).
- `GET /credits` — Credits / team page.
- `GET /prediction` — Screening form (AQ-10 + demographics).
- `POST /predict` — Accepts form data, returns results page. If model files are missing, returns JSON error and 500 status.

Payload (form fields expected): age, gender, ethnicity, jaundice, autism (family history), used_app_before, country_of_res, A1_Score ... A10_Score (each 0/1), plus `result` (AQ total, added by client JS) and `age_desc` (added by client JS).

## Retraining the model

To retrain with the provided `train.csv`:

```powershell
python train_model.py
```

Notes:
- `train_model.py` will preprocess categorical features using `LabelEncoder` instances and numeric columns (age, A1..A10, result).
- By default the script uses scikit-learn RandomForestClassifier on CPU. If RAPIDS (cudf, cuml, cupy) are installed and CUDA is available it will attempt GPU training.
- After training it writes `autism_model.joblib` and `label_encoders.joblib` to the project root for `app.py` to load at runtime.

## Dependencies

See `requirements.txt`. Main packages:
- Python >= 3.8
- numpy, pandas
- scikit-learn
- joblib

Optional GPU acceleration (RAPIDS): `cudf`, `cuml`, `cupy` — only required if you want GPU training.

## Troubleshooting

- If the web app prints "Model not loaded. Please train the model first." or returns an error at `/predict`, ensure `autism_model.joblib` and `label_encoders.joblib` exist in the project root. Run `python train_model.py` to generate them.
- If you get encoding errors on prediction, make sure the label encoder saved in `label_encoders.joblib` was created from the same set of categories as your production inputs; otherwise unseen labels will cause an error.
- If you want to run Flask with debug off in production, set `debug=False` in `app.py` or use a production WSGI server like Gunicorn (Windows users: consider deploying on a Linux server/container).

## Security & privacy notes

- This tool stores no user data on the server by default — the form posts only to the backend and returns results. If you plan to add storage, ensure secure handling of PII and follow local regulations.
- This is an educational screening tool — it is not clinically validated as a diagnostic instrument.

## Contributing

If you'd like to contribute improvements (better preprocessing, model explainability, tests, or CI), please fork and open a PR. Suggested improvements:
- Add unit tests for `train_model.py` preprocessing and `predict_autism`.
- Add Dockerfile and GitHub Actions for CI.
- Add input validation and more robust handling for unseen categorical values (e.g., use `OrdinalEncoder` with fallback, or persist category maps).

## Credits

Project authors are listed in `templates/credits.html`.

## License

GNU GPL V3.0 . For more details check the LICENSE.md file

---

If you want, I can also add a small CONTRIBUTING.md, a basic LICENSE file, or add unit tests for `train_model.py`'s `preprocess_data` and `predict_autism` functions. Tell me which next step you prefer.
