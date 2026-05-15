# Fraud Detection API

API de detection de fraude basee sur le dataset IEEE-CIS, avec un modele XGBoost/LightGBM et un dashboard Streamlit.

## Architecture

```
api-fraude-detection/
├── app/
│   ├── main.py            # Endpoints FastAPI
│   ├── model.py           # Chargement et inference du modele
│   ├── monitoring.py      # Logs et statistiques de production
│   ├── preprocessing.py   # Preprocessing des features
│   └── schemas.py         # Schemas Pydantic (request/response)
├── model/
│   ├── model.json         # Modele XGBoost serialise
│   ├── model_config.json  # Configuration du modele (features, seuil, metriques)
│   ├── feature_cols.json  # Liste des colonnes utilisees
│   └── threshold.joblib   # Seuil de decision optimise
├── tests/
│   └── test_api.py        # Tests unitaires de l'API
├── frontend.py            # Dashboard Streamlit
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── runtime.txt
```

## Stack technique

- **API** : FastAPI + Uvicorn
- **Modele** : XGBoost (ensemble XGBoost + LightGBM)
- **Frontend** : Streamlit + Plotly
- **Python** : 3.12
- **Deploiement** : Docker / Railway

## Installation locale

```bash
# Cloner le repo
git clone <url-du-repo>
cd api-fraude-detection

# Installer les dependances
pip install -r requirements.txt
```

## Lancement

### API seule

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Dashboard Streamlit

```bash
streamlit run frontend.py
```

### Avec Docker

```bash
docker-compose up --build
```

L'API est accessible sur `http://localhost:8000` et la documentation Swagger sur `http://localhost:8000/docs`.

## Endpoints

| Methode | Route              | Description                          |
|---------|--------------------|--------------------------------------|
| GET     | /health            | Statut de l'API et du modele         |
| GET     | /model/info        | Informations detaillees du modele    |
| POST    | /predict           | Prediction sur une transaction       |
| POST    | /predict/batch     | Prediction sur un lot de transactions|
| GET     | /monitoring/stats  | Statistiques de production           |

## Exemple de requete

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "TransactionAmt": 75.0,
    "ProductCD": 1,
    "card1": 4000,
    "card4": -999,
    "C1": 1.0,
    "C2": -999.0,
    "C6": -999.0,
    "C13": 1.0,
    "C14": 1.0,
    "D1": 14.0,
    "D4": -999.0,
    "D10": -999.0,
    "D15": 300.0
  }'
```

## Tests

```bash
pytest tests/
```

## Performance du modele

- **AUC-ROC** : 0.9269
- **Dataset** : IEEE-CIS Fraud Detection
- **Desequilibre** : 96.5% legitimes / 3.5% fraudes (ratio 1:27)
- **Seuil de decision** : optimise pour maximiser le F1-score

## Production

L'API est deployee sur Railway : `https://fraud-detection-api-production-9fb6.up.railway.app`
