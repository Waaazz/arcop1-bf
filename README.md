# 🌾 ARCOP - Site Web Officiel

Association pour le Renforcement des Compétences des Organisations Paysannes

## 📋 Table des matières

1. [Description](#description)
2. [Fonctionnalités](#fonctionnalités)
3. [Technologies utilisées](#technologies-utilisées)
4. [Installation locale](#installation-locale)
5. [Configuration](#configuration)
6. [Déploiement](#déploiement)
7. [Interface d'administration](#interface-dadministration)
8. [Structure du projet](#structure-du-projet)

## 📖 Description

Site web institutionnel de l'ARCOP avec interface d'administration pour gérer facilement :
- Actualités
- Documents et publications
- Membres de l'organisation
- Partenaires et projets
- Événements et agenda
- Contenus éditoriaux

## ✨ Fonctionnalités

### Site public
- ✅ Page d'accueil dynamique avec dernières actualités
- ✅ Présentation de l'organisation
- ✅ Gestion des membres
- ✅ Publications et documentation
- ✅ Partenaires et projets
- ✅ Agenda des événements
- ✅ Formulaire de contact
- ✅ Newsletter
- ✅ Design responsive (mobile, tablette, desktop)

### Interface d'administration
- ✅ Gestion des actualités (CRUD)
- ✅ Gestion des documents
- ✅ Gestion des membres
- ✅ Gestion des partenaires
- ✅ Gestion des projets
- ✅ Gestion de l'agenda
- ✅ Interface intuitive avec Flask-Admin

## 🛠 Technologies utilisées

- **Backend**: Flask 3.0.3
- **Base de données**: SQLAlchemy (SQLite en dev, PostgreSQL en prod)
- **Migrations**: Flask-Migrate
- **Admin**: Flask-Admin
- **Frontend**: HTML5, CSS3, JavaScript
- **Déploiement**: Gunicorn, Render/Railway/Heroku

## 💻 Installation locale

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- virtualenv (recommandé)

### Étapes d'installation

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd arcop_website

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Copier le fichier de configuration
cp .env.example .env

# 6. Initialiser la base de données
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 7. Créer des données de test (optionnel)
flask init-db

# 8. Lancer l'application
python app.py
```

Le site sera accessible sur : **http://127.0.0.1:5000**

L'interface admin sera sur : **http://127.0.0.1:5000/admin**

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
SECRET_KEY=votre-cle-secrete-tres-longue
DATABASE_URL=sqlite:///arcop.db
FLASK_APP=app.py
FLASK_ENV=development
```

### En production (PostgreSQL)

```env
SECRET_KEY=votre-cle-secrete-production
DATABASE_URL=postgresql://user:password@host:5432/database
FLASK_ENV=production
```

## 🚀 Déploiement

### Option 1: Render.com (Recommandé)

Le fichier `render.yaml` est déjà configuré.

**Étapes:**

1. Créez un compte sur [Render.com](https://render.com)
2. Connectez votre dépôt GitHub
3. Cliquez sur "New Web Service"
4. Sélectionnez votre dépôt
5. Render détectera automatiquement le fichier `render.yaml`
6. Cliquez sur "Deploy"

**✅ Déploiement automatique à chaque push GitHub !**

### Option 2: Railway

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Login
railway login

# Créer un nouveau projet
railway init

# Déployer
railway up
```

### Option 3: Heroku

```bash
# Installer Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Créer l'application
heroku create arcop-website

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:mini

# Déployer
git push heroku main

# Migrer la base de données
heroku run flask db upgrade

# Créer les données initiales
heroku run flask init-db
```

### Option 4: cPanel (hébergement traditionnel)

1. **Uploader les fichiers**
   - Compressez votre projet en .zip
   - Uploadez via File Manager de cPanel
   - Décompressez dans le dossier public_html

2. **Configurer Python**
   - Activez Python App dans cPanel
   - Sélectionnez Python 3.8+
   - Configurez le fichier d'entrée : `app.py`

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**
   - Créez une base PostgreSQL depuis cPanel
   - Configurez DATABASE_URL dans .env

5. **Redémarrer l'application**

## 🔐 Interface d'administration

### Accès

L'interface admin est accessible sur : `/admin`

Par défaut, il n'y a **pas d'authentification** sur Flask-Admin.

### Ajouter une authentification (IMPORTANT pour la production)

Modifiez `app.py` et ajoutez :

```python
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager, current_user

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app, index_view=SecureAdminIndexView())
```

### Gestion des contenus

Dans l'admin, vous pouvez :

**Actualités**
- Créer/Modifier/Supprimer des actualités
- Ajouter des images
- Publier ou masquer

**Documents**
- Uploader des PDF, Word, etc.
- Classer par catégorie
- Gérer la visibilité

**Membres**
- Ajouter des membres de l'organisation
- Gérer l'ordre d'affichage
- Ajouter photos et biographies

**Événements**
- Créer des événements pour l'agenda
- Définir dates et lieux
- Personnaliser les couleurs

## 📁 Structure du projet

```
arcop_website/
│
├── app.py                      # Application principale Flask
├── requirements.txt            # Dépendances Python
├── .env.example                # Configuration exemple
├── render.yaml                 # Config Render
├── Procfile                    # Config Heroku/Railway
├── README.md                   # Ce fichier
│
├── static/                     # Fichiers statiques
│   ├── css/
│   │   └── style.css           # Styles CSS
│   ├── js/
│   │   └── script.js           # JavaScript
│   └── images/                 # Images du site
│
├── templates/                  # Templates HTML
│   ├── base.html               # Template de base
│   ├── index.html              # Page d'accueil
│   ├── arcop/
│   │   ├── presentation.html
│   │   ├── mot_president.html
│   │   ├── membres.html
│   │   └── initiatives.html
│   ├── contact.html
│   └── ...
│
├── migrations/                 # Migrations base de données
└── instance/                   # Fichiers d'instance (config locale)
```

## 🔄 Mise à jour du site en production

### Avec GitHub + Render/Railway

```bash
# 1. Modifier votre code
# 2. Commiter les changements
git add .
git commit -m "Description des modifications"

# 3. Pousser vers GitHub
git push origin main

# ✅ Le site se met à jour automatiquement !
```

### Avec cPanel

1. Modifiez les fichiers localement
2. Compressez les fichiers modifiés en .zip
3. Uploadez via File Manager
4. Remplacez les anciens fichiers
5. Redémarrez l'application Python

## 📊 Commandes utiles

```bash
# Créer une migration après modification des modèles
flask db migrate -m "Description"

# Appliquer les migrations
flask db upgrade

# Revenir à une migration précédente
flask db downgrade

# Réinitialiser la base avec données de test
flask init-db

# Lancer en mode production
gunicorn app:app
```

## 🐛 Résolution de problèmes

### Problème : Base de données inexistante

```bash
flask db init
flask db migrate
flask db upgrade
```

### Problème : Module introuvable

```bash
pip install -r requirements.txt
```

### Problème : PostgreSQL sur Render

Vérifiez que `DATABASE_URL` commence par `postgresql://` (et non `postgres://`)

## 📞 Support

Pour toute question ou problème :
- 📧 Email : contact@arcop.bf
- 🌐 Site : www.arcop.bf

## 📝 Licence

© 2024 ARCOP - Tous droits réservés

---

**Développé avec ❤️ pour l'ARCOP**
