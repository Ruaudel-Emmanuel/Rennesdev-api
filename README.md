# api-rennesdev

API FastAPI pour gérer :

- leads entrants depuis le site
- devis
- contrats
- liens de paiement Stripe
- factures
- commandes de prestations rapides
- automatisations vers n8n

## Stack

- FastAPI
- Uvicorn
- Pydantic Settings
- HTTPX
- Pytest
- Docker / Docker Compose

## Arborescence utile

```bash
app/
tests/
.env
.env.example
Dockerfile
docker-compose.yml
Makefile
pyproject.toml
README.md
```

## Prérequis

- Python 3.12+
- Docker + Docker Compose
- GNU Make (optionnel mais pratique)

## Installation locale

1. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Installer les dépendances

```bash
pip install -e .
pip install pytest
```

3. Copier le fichier d’environnement

```bash
cp .env.example .env
```

4. Lancer l’API

```bash
uvicorn app.main:app --reload
```

API disponible sur :

- http://127.0.0.1:8000
- docs Swagger : http://127.0.0.1:8000/docs
- healthcheck : http://127.0.0.1:8000/health

## Lancement avec Docker

Build + run :

```bash
docker compose up --build
```

API disponible sur :

- http://127.0.0.1:8000
- docs Swagger : http://127.0.0.1:8000/docs

## Commandes utiles

Lancer en local :

```bash
make dev
```

Lancer les tests :

```bash
make test
```

Formater plus tard si besoin :

```bash
make lint
```

## Variables d’environnement

Voir `.env.example`.

Variables importantes :

- `API_KEY`
- `N8N_LEADS_WEBHOOK_URL`
- `N8N_QUOTES_WEBHOOK_URL`
- `N8N_ORDERS_WEBHOOK_URL`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

## Endpoints principaux

- `POST /api/v1/leads`
- `POST /api/v1/quotes`
- `POST /api/v1/contracts`
- `POST /api/v1/payment-links`
- `POST /api/v1/payments/webhook/stripe`
- `POST /api/v1/invoices`
- `POST /api/v1/orders/consulting-session`

## Tests

Les tests utilisent `pytest` + `TestClient`.

Lancer :

```bash
pytest
```

Ou :

```bash
make test
```

## Notes

- Le client Stripe est encore en mode squelette.
- Le générateur PDF écrit pour l’instant un faux fichier texte.
- Les webhooks n8n sont appelés seulement si les URLs sont définies dans `.env`.
