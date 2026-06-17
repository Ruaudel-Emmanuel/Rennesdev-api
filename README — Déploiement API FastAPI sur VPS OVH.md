<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# README — Déploiement API FastAPI sur VPS OVH

## Architecture

```
Internet
   │
   ▼
Nginx (80/443 — HTTPS Let's Encrypt)
   │
   ▼
Uvicorn + FastAPI (127.0.0.1:8001)
   │
   ▼
Stripe API / n8n
```



\---

## Prérequis

* VPS Linux (Ubuntu 25.04)
* Python 3.13
* Nginx installé
* Un domaine avec sous-domaine `api.` pointant vers l'IP du VPS
* Certificat SSL (Let's Encrypt)

\---

## Structure du projet

```
/home/user/var/www/api-backend/
├── app/
│   ├── \_\_init\_\_.py
│   ├── main.py
│   ├── api/
│   │   ├── \_\_init\_\_.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── \_\_init\_\_.py
│   │       └── payments.py
│   └── core/
│       ├── \_\_init\_\_.py
│       ├── config.py
│       └── logging.py
├── .env
├── .venv/
├── logs/
├── static/
└── storage/
```



\---

## Installation

### 1\. Créer la structure

```bash
cd \~/var/www/api-backend/app
mkdir -p api/v1 core
touch \_\_init\_\_.py api/\_\_init\_\_.py api/v1/\_\_init\_\_.py core/\_\_init\_\_.py
```



### 2\. Créer le venv et installer les dépendances

```bash
cd \~/var/www/api-backend
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install fastapi "uvicorn\[standard]" pydantic pydantic-settings stripe httpx python-dotenv
```



### 3\. Configurer le .env

```bash
nano \~/var/www/api-backend/.env
```

Variables nécessaires :

```env
APP\_NAME=api-backend
APP\_VERSION=0.1.0
ENVIRONMENT=production

STRIPE\_SECRET\_KEY=sk\_live\_...
STRIPE\_WEBHOOK\_SECRET=whsec\_...

N8N\_ORDERS\_WEBHOOK\_URL=https://n8n.example.com/webhook/orders
```



\---

## Service systemd

Fichier : `/etc/systemd/system/api-backend.service`

```ini
\[Unit]
Description=API FastAPI
After=network.target

\[Service]
Type=simple
User=user
Group=user
WorkingDirectory=/home/user/var/www/api-backend
Environment="PATH=/home/user/var/www/api-backend/.venv/bin"
ExecStart=/home/user/var/www/api-backend/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=3

\[Install]
WantedBy=multi-user.target
```

Démarrage :

```bash
sudo systemctl daemon-reload
sudo systemctl enable api-backend
sudo systemctl start api-backend
sudo systemctl status api-backend --no-pager
```



\---

## Nginx — reverse proxy

Fichier : `/etc/nginx/sites-available/api.example.com`

```nginx
server {
    server\_name api.example.com;

    location / {
        proxy\_pass http://127.0.0.1:8001;
        proxy\_http\_version 1.1;
        proxy\_set\_header Host $host;
        proxy\_set\_header X-Real-IP $remote\_addr;
        proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for;
        proxy\_set\_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl\_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl\_certificate\_key /etc/letsencrypt/live/api.example.com/privkey.pem;
}

server {
    listen 80;
    server\_name api.example.com;
    return 301 https://$host$request\_uri;
}
```

Activation :

```bash
sudo ln -s /etc/nginx/sites-available/api.example.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```



\---

## Endpoints disponibles

|Méthode|URL|Description|
|-|-|-|
|GET|`/health`|Vérification que l'API tourne|
|POST|`/api/v1/payments/session-conseil`|Crée une Stripe Checkout Session|
|POST|`/api/v1/payments/webhook`|Reçoit les événements Stripe|



\---

## Flux de paiement

```
\[Bouton front]
    ↓ POST /api/v1/payments/session-conseil
\[FastAPI → Stripe API]
    ↓ retourne checkout\_url
\[Redirect → Stripe Checkout]
    ↓ paiement confirmé
\[Stripe → POST /api/v1/payments/webhook]
\[FastAPI vérifie signature whsec\_...]
    ↓ checkout.session.completed
\[FastAPI → POST n8n webhook]
    ↓
\[n8n → email confirmation + lien calendrier]
```



\---

## Webhook Stripe

À déclarer sur dashboard.stripe.com :

* **URL** : `https://api.example.com/api/v1/payments/webhook`
* **Événement** : `checkout.session.completed`
* Copier le `whsec\_...` généré dans le `.env`

\---

## Commandes utiles

```bash
# Statut du service
sudo systemctl status api-backend --no-pager

# Logs en temps réel
sudo journalctl -u api-backend -f

# Redémarrer après modification du .env
sudo systemctl restart api-backend

# Tester l'API
curl https://api.example.com/health

# Tester le paiement
curl -X POST https://api.example.com/api/v1/payments/session-conseil \\
  -H "Content-Type: application/json"
```



\---

## Erreurs fréquentes

|Erreur|Cause|Solution|
|-|-|-|
|`Permission denied` sur mkdir|Dossier appartenant à root|`sudo chown -R user:user \~/var/www/api-backend`|
|`address already in use`|Service déjà actif sur le port|Normal — le service tourne déjà|
|`secret\_key\_required`|Clé publishable au lieu de secrète|Utiliser `sk\_live\_...` dans le `.env`|
|`Could not connect`|Service en cours de redémarrage|Attendre 2s et relancer le curl|
|`WorkingDirectory` incorrect|Chemin absolu différent du chemin affiché|Vérifier avec `pwd` et corriger le service systemd|



