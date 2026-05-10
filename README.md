# AI Traffic Management & Accident Prediction

A full-stack traffic safety analytics platform built with Flask, MySQL, and machine learning.

## 🚦 Project Overview

This application ingests traffic incident data, trains a predictive model, and delivers:

- Traffic risk prediction with accident risk classification
- Interactive Leaflet-based risk maps
- Dataset upload and management
- Alerts and incident monitoring
- Exportable reports in CSV and PDF formats

## 🧰 Tech Stack

- Python 3
- Flask web framework
- MySQL database
- scikit-learn, pandas, NumPy for ML
- Leaflet for interactive mapping
- Chart.js for analytics visualizations

## ✅ Features

- Admin authentication and dashboard analytics
- Dataset CRUD and CSV upload support
- Model training and real-time prediction endpoint
- Map visualizations of traffic risk
- Alerts dashboard and alert resolution flow
- Report export capabilities

## 🚀 Setup & Installation

1. Clone the repository:

```bash
git clone https://github.com/Tushar-Sati/ai-traffic-management.git
cd ai-traffic-management
```

2. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Create the MySQL database and tables:

```powershell
mysql -u root -p < database/schema.sql
```

5. Copy the environment template and set your database credentials:

```powershell
copy .env.example .env
```

Edit `.env` with your MySQL settings.

6. Seed sample data (optional):

```powershell
python seed_sample_data.py
```

7. Train the model:

```powershell
python train_model.py
```

8. Run the application:

```powershell
python app.py
```

9. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## 🔐 Default Admin Credentials

- Username: `admin`
- Password: `admin123`

## 📁 Repository Structure

- `app.py` — main Flask application
- `config.py` — application configuration
- `db.py` — database helper and connection utilities
- `routes/` — Flask route modules
- `templates/` — HTML templates
- `static/` — CSS and JavaScript assets
- `dataset/` — sample data and upload storage
- `database/schema.sql` — database schema definition
- `train_model.py` — model training script
- `seed_sample_data.py` — sample data loader

## 📌 Notes

- Do not commit sensitive `.env` data.
- The `.gitignore` already excludes local environment files and logs.

## 📄 License

This repository is available under the MIT License.
