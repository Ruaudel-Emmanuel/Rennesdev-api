# API FastAPI sur OVH

README générique pour déployer une API FastAPI sur un VPS OVH avec `systemd`, `Nginx`, HTTPS et DNS. Le montage recommandé consiste à faire tourner l’application avec Uvicorn sur `127.0.0.1`, puis à la publier via Nginx sur `80/443`, avec supervision par `systemd` et un pointage DNS propre vers le serveur.[cite:681][cite:689][cite:812]

## Objectif

Ce dépôt sert de base pour exposer une API Python en production avec :

- FastAPI pour l’application web.
- Uvicorn pour le serveur ASGI.
- `systemd` pour le lancement automatique et la supervision.
- Nginx pour le reverse proxy et HTTPS.
- Un sous-domaine dédié pointé vers le VPS.[cite:682][cite:808]

## Architecture

```text
Internet
  ↓
Nginx :80 / :443
  ↓
Uvicorn / FastAPI sur 127.0.0.1:8001
```

Ce schéma évite d’exposer directement Uvicorn sur Internet et permet de gérer proprement TLS, redirections et virtual hosts dans Nginx.[cite:681][cite:629]

## Pré-requis

- Un VPS OVH sous Linux.
- Python 3 installé.
- `python3-venv`, `pip`, `git`, `curl`.
- Nginx installé.
- Un nom de domaine ou sous-domaine.
- Un accès DNS pour faire pointer le sous-domaine vers le VPS.[cite:808][cite:809]

## Installation

### 1. Préparer le serveur

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx git curl
```

### 2. Déployer le projet

```bash
sudo mkdir -p /var/www/api-project
sudo chown $USER:$USER /var/www/api-project
cd /var/www/api-project

git clone <REPO_GIT> .
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
# ou: python -m pip install -r requirements.txt
```

### 3. Vérifier localement

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Dans un second terminal :

```bash
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/
```

Tester directement depuis le VPS permet de valider l’application avant d’ajouter la couche `systemd`, Nginx et DNS.[cite:682][cite:809]

## Service systemd

Créer `/etc/systemd/system/api-project.service` :

```ini
[Unit]
Description=FastAPI service
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/api-project
Environment="PATH=/var/www/api-project/.venv/bin"
ExecStart=/var/www/api-project/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Activer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable api-project
sudo systemctl start api-project
sudo systemctl status api-project --no-pager
```

Vérifier ensuite :

```bash
curl http://127.0.0.1:8001/health
```

Le modèle courant pour FastAPI sur VPS est un service `systemd` simple qui lance Uvicorn depuis le venv et redémarre automatiquement en cas d’erreur.[cite:497][cite:689][cite:681]

## Nginx

Créer un vhost, par exemple `/etc/nginx/sites-available/api.example.com` :

```nginx
server {
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}
```

Activer la configuration :

```bash
sudo ln -s /etc/nginx/sites-available/api.example.com /etc/nginx/sites-enabled/api.example.com
sudo nginx -t
sudo systemctl reload nginx
```

Le reverse proxy Nginx vers `127.0.0.1:8001` avec les headers `Host` et `X-Forwarded-*` correspond au déploiement de production standard d’une API FastAPI sur VPS.[cite:681][cite:629][cite:812]

## HTTPS

Si le certificat n’existe pas encore :

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com
```

Une configuration Nginx avec Let’s Encrypt permet d’ajouter rapidement HTTPS et la redirection automatique depuis HTTP.[cite:812][cite:808]

## DNS

Configurer le sous-domaine pour pointer vers le VPS :

- `A` → `api.example.com` → `IPv4 du VPS`
- `AAAA` → vide, ou `IPv6 du VPS` si l’IPv6 est utilisée

Vérifications :

```bash
dig +short api.example.com
dig +short api.example.com @1.1.1.1
dig +short api.example.com @8.8.8.8
dig +short AAAA api.example.com
```

Une erreur fréquente vient d’un ancien enregistrement `A` ou `AAAA` qui continue d’envoyer le trafic vers un autre hébergement, même quand Nginx et l’application sont correctement configurés sur le VPS.[cite:775][cite:769][cite:772]

## Tests utiles

### Test applicatif direct

```bash
curl http://127.0.0.1:8001/health
```

### Test Nginx local HTTP

```bash
curl -H "Host: api.example.com" http://127.0.0.1/health
```

### Test Nginx local HTTPS

```bash
curl -k --resolve api.example.com:443:127.0.0.1 https://api.example.com/health
```

### Test public

```bash
curl -k https://api.example.com/health
```

Le test `--resolve` est particulièrement utile pour vérifier le bon vhost HTTPS localement sans dépendre de la propagation DNS publique.[cite:812]

## Logs et maintenance

### Service applicatif

```bash
sudo systemctl status api-project --no-pager
sudo journalctl -u api-project -n 50 --no-pager
sudo journalctl -u api-project -f
```

### Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart nginx
```

## Erreurs fréquentes

### `No module named uvicorn`

Le venv a été recréé, mais les dépendances n’ont pas été réinstallées.

### `address already in use`

Le port est déjà occupé par un ancien process Uvicorn, un conteneur Docker ou un autre service.

### `conflicting server name`

Deux fichiers Nginx déclarent le même `server_name` pour le même port.

### `404` ou mauvaise page publique

Le DNS ne pointe pas encore vers le VPS, ou un enregistrement `AAAA` envoie encore l’IPv6 vers une ancienne machine.[cite:775][cite:769]

### `405 Method Not Allowed` avec `curl -I`

La commande envoie une requête `HEAD`. Le endpoint est souvent disponible en `GET` uniquement.

## Résultat attendu

Quand tout est correctement configuré :

```bash
curl -k https://api.example.com/health
```

retourne :

```json
{"status":"ok"}
```

## Variables à adapter

- `api-project`
- `app.main:app`
- `api.example.com`
- `/var/www/api-project`
- `8001`
- `deploy`
- `IPv4 du VPS`
- `IPv6 du VPS`
