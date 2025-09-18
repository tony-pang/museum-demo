# Museum Attendance vs City Population MVP

This project builds a harmonized database of the world’s most visited museums (2,000,000+ annual visitors), enriches with city populations, and exposes data and a simple linear regression via an API and a Jupyter notebook. Everything runs in Docker.

## Quickstart
1. Copy env and adjust if needed:
```
cp .env.example .env
```
2. Build and run:
```
docker compose up --build
```
3. Services:
- API: http://localhost:8000 (docs at http://localhost:8000/docs)
- JupyterLab: http://localhost:8888 (token in logs)

## Structure
```
src/
  api/
    main.py
  clients/
    wikipedia.py
    wikidata.py
  core/
    config.py
    logging.py
  db/
    __init__.py
    models.py
    session.py
  etl/
    pipeline.py
  ml/
    features.py
    model.py
    plots.py
  utils/
    __init__.py

notebooks/
  analysis.ipynb

docker/
  api.Dockerfile
  notebook.Dockerfile

docker-compose.yml
requirements.txt
.env.example
README.md
```

## Notes
- MVP uses SQLite for simplicity and reproducibility.
- Data sources: Wikipedia API and Wikidata SPARQL. ETL and modeling are modular for scaling.
