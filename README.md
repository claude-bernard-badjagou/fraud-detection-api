# Fraud Detection API

API de détection de fraude basée sur le dataset IEEE-CIS, avec un modèle XGBoost/LightGBM et un dashboard Streamlit.

## Architecture

```
api-fraude-detection/
├── app/
│   ├── main.py            # Endpoints FastAPI
│   ├── model.py           # Chargement et inférence du modèle
│   ├── monitoring.py      # Logs et statistiques de production
│   ├── preprocessing.py   # Prétraitement des features
│   └── schemas.py         # Schémas Pydantic (request/response)
├── model/
│   ├── model.json         # Modèle XGBoost sérialisé
│   ├── model_config.json  # Configuration du modèle (features, seuil, métriques)
│   ├── feature_cols.json  # Liste des colonnes utilisées
│   └── threshold.joblib   # Seuil de décision optimisé
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
- **Modèle** : XGBoost (ensemble XGBoost + LightGBM)
- **Frontend** : Streamlit + Plotly
- **Python** : 3.12
- **Déploiement** : Docker / Railway

## Installation locale

```bash
# Cloner le repo
git clone <url-du-repo>
cd api-fraude-detection

# Installer les dépendances
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

| Méthode | Route              | Description                           |
|---------|--------------------|---------------------------------------|
| GET     | /health            | Statut de l'API et du modèle          |
| GET     | /model/info        | Informations détaillées du modèle     |
| POST    | /predict           | Prédiction sur une transaction        |
| POST    | /predict/batch     | Prédiction sur un lot de transactions |
| GET     | /monitoring/stats  | Statistiques de production            |

## Exemple de requête

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

## Performance du modèle

- **AUC-ROC** : 0.9269
- **Dataset** : IEEE-CIS Fraud Detection
- **Déséquilibre** : 96.5% légitimes / 3.5% fraudes (ratio 1:27)
- **Seuil de décision** : optimisé pour maximiser le F1-score

## Production

L'API est déployée sur Railway.