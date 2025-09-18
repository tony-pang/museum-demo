# Museum Attendance vs City Population MVP

This project builds a harmonized database of the world's most visited museums, enriches with city populations, and exposes data and a simple linear regression via an API and a Jupyter notebook. Everything runs in Docker.

## Project Overview

A new world organization of museum management committees needs to correlate tourist attendance at their museums with the population of their respective cities. This MVP provides:

- **Harmonized Database**: Museum characteristics + city populations
- **Linear Regression Model**: Correlates city population with visitor influx
- **RESTful API**: Exposes data and model results
- **Interactive Analysis**: Jupyter notebook for visualization and insights
- **Dockerized Deployment**: Portable, reproducible environment

## Quickstart

### **Using Docker Compose**
```bash
docker compose up --build
```

### **Services**
- **API**: http://localhost:8000 (docs at http://localhost:8000/docs)
- **JupyterLab**: http://localhost:8888 (token in logs)
- **PostgreSQL**: localhost:5432 (museum_user/museum_pass)

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

## Data Validation & Fallback Strategies

### **Current Implementation**
- **Museum Data**: Fetched from Wikipedia API with year extraction from visitor counts
- **City Population**: Retrieved from Wikidata SPARQL queries
- **Data Cleaning**: NaN/inf values replaced with 0, numeric columns properly typed

## Scaling Considerations

### **Immediate (MVP)**
- Current PostgreSQL setup handles 10K+ museums
- FastAPI can serve 1000+ requests/minute
- Docker Compose suitable for single-server deployment

### **Production Scaling**
- **Database**: Add read replicas, connection pooling
- **API**: Load balancer, horizontal scaling (k8s)
- **Caching**: Redis for frequently accessed data
- **Monitoring**: Prometheus + Grafana
- **Data Pipeline**: Apache Airflow for scheduled ETL

## Testing Strategy

### **Test Types**
- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests with mock servers for external APIs
- **End-to-End Tests**: Full workflow tests (optional, requires external APIs)

### **Running Tests**

#### **Using Makefile**
```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests 
make test-integration

# Run with coverage
make test-coverage
```
- TODO use docker compose to setup a [mock server](https://www.mock-server.com/) and run these tests during CI/CD

## Notes
- Data sources: Wikipedia API and Wikidata SPARQL. ETL and modeling are modular for scaling.
- **Data Quality**: Currently processes all museums regardless of visitor count threshold
- **Year Handling**: Extracts year from data but doesn't filter by year
- **Testing**: Comprehensive test suite with mock servers for reliable CI/CD
