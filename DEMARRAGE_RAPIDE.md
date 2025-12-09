# 🚀 GUIDE DE DÉMARRAGE RAPIDE - ARCOP

## 📦 Ce qui a été créé pour vous

Votre site web ARCOP est maintenant **100% prêt** avec :

✅ **Site public complet** (8 menus principaux)
✅ **Interface d'administration** (Flask-Admin)
✅ **Base de données** avec 6 modèles (Actualités, Documents, Membres, etc.)
✅ **Design responsive** (mobile, tablette, desktop)
✅ **Système de déploiement automatique**

---

## 🎯 ÉTAPE 1 : Installation locale (5 minutes)

```bash
# 1. Naviguer vers le dossier
cd arcop_website

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Initialiser la base de données
flask db init
flask db migrate -m "Initial"
flask db upgrade

# 6. Créer des données de test
flask init-db

# 7. Lancer le site
python app.py
```

**🎉 Votre site est accessible sur : http://127.0.0.1:5000**

**🔐 Interface admin : http://127.0.0.1:5000/admin**

---

## 🌐 ÉTAPE 2 : Déploiement en ligne (10 minutes)

### Option A : Render.com (Recommandé - Gratuit)

1. **Créer un compte GitHub** (si vous n'en avez pas)
   - Allez sur https://github.com
   - Créez un compte gratuit

2. **Créer un dépôt GitHub**
   ```bash
   # Dans le dossier arcop_website
   git init
   git add .
   git commit -m "Initial commit - Site ARCOP"
   git branch -M main
   ```
   
   - Créez un nouveau dépôt sur GitHub (nommez-le "arcop-website")
   - Suivez les instructions pour pousser votre code

3. **Déployer sur Render**
   - Allez sur https://render.com
   - Créez un compte (connexion avec GitHub)
   - Cliquez sur "New +" → "Web Service"
   - Sélectionnez votre dépôt "arcop-website"
   - Render détectera automatiquement le fichier `render.yaml`
   - Cliquez sur "Deploy"

4. **✅ C'est fait !**
   - Votre site sera en ligne en 2-3 minutes
   - Vous aurez une URL du type : `https://arcop-website.onrender.com`
   - **À chaque modification + push GitHub → le site se met à jour automatiquement**

### Option B : Railway (Alternative gratuite)

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Se connecter
railway login

# Créer et déployer
railway init
railway up
```

---

## 🔐 ÉTAPE 3 : Sécuriser l'admin (IMPORTANT !)

Par défaut, l'admin est **ouvert à tous**. Il faut le sécuriser pour la production.

**Solution simple :** Ajoutez un mot de passe basique

Modifiez `app.py` et ajoutez avant `admin = Admin(app, ...)` :

```python
from flask import request, redirect, url_for
from werkzeug.security import check_password_hash

# Hash du mot de passe (généré avec : werkzeug.security.generate_password_hash('votre_mot_de_passe'))
ADMIN_PASSWORD_HASH = 'pbkdf2:sha256:...'  # À générer

def check_admin_access():
    auth = request.authorization
    if not auth or not check_password_hash(ADMIN_PASSWORD_HASH, auth.password):
        return False
    return True

class SecureModelView(ModelView):
    def is_accessible(self):
        return check_admin_access()
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/admin/login')  # Créer une page de login

# Remplacez tous les ModelView par SecureModelView
admin.add_view(SecureModelView(Actualite, db.session))
# etc...
```

---

## 📝 ÉTAPE 4 : Gérer le contenu (Interface Admin)

1. **Accéder à l'admin** : `http://votre-site.com/admin`

2. **Ajouter une actualité**
   - Cliquez sur "Actualités" → "Create"
   - Remplissez le formulaire
   - Cochez "Publié" pour la rendre visible
   - Sauvegardez

3. **Ajouter un document**
   - Cliquez sur "Documents" → "Create"
   - Uploadez le fichier (PDF, Word, etc.)
   - Choisissez la catégorie
   - Sauvegardez

4. **Ajouter un membre**
   - Cliquez sur "Membres" → "Create"
   - Ajoutez les informations
   - Uploadez une photo (optionnel)
   - Définissez l'ordre d'affichage
   - Sauvegardez

---

## 🔄 ÉTAPE 5 : Mettre à jour le site

### Si vous utilisez GitHub + Render

```bash
# 1. Modifiez vos fichiers
# 2. Commitez les changements
git add .
git commit -m "Mise à jour du contenu"

# 3. Poussez vers GitHub
git push origin main

# ✅ Le site se met à jour automatiquement en 2-3 minutes !
```

### Si vous utilisez cPanel

1. Modifiez les fichiers localement
2. Compressez en .zip
3. Uploadez via File Manager
4. Remplacez les anciens fichiers
5. Redémarrez l'application

---

## 📊 Structure des données

Voici ce que vous pouvez gérer dans l'admin :

| Modèle | Description | Champs principaux |
|--------|-------------|-------------------|
| **Actualités** | Articles et news | Titre, contenu, image, date |
| **Documents** | PDF, rapports, études | Titre, fichier, catégorie |
| **Membres** | Membres de l'ARCOP | Nom, fonction, photo, bio |
| **Partenaires** | Partenaires et bailleurs | Nom, logo, description |
| **Projets** | Projets en cours/terminés | Titre, objectifs, dates |
| **Événements** | Agenda et calendrier | Titre, date, lieu |

---

## 🎨 Personnalisation du design

### Modifier les couleurs

Éditez `/static/css/style.css` :

```css
/* Couleur principale (vert) */
#2d862d → Remplacez par votre couleur

/* Couleur secondaire (bleu) */
#1e5a8e → Remplacez par votre couleur

/* Couleur accent (rouge) */
#c41e3a → Remplacez par votre couleur
```

### Modifier le logo

Remplacez le SVG dans `templates/base.html` par votre vraie image :

```html
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="ARCOP Logo">
```

---

## 🐛 Résolution de problèmes courants

### Problème : "Module not found"
```bash
pip install -r requirements.txt
```

### Problème : "Database not found"
```bash
flask db upgrade
flask init-db
```

### Problème : Site ne démarre pas sur Render
- Vérifiez les logs sur Render Dashboard
- Assurez-vous que `render.yaml` est présent
- Vérifiez que `requirements.txt` est complet

---

## 📞 Support

- 📧 **Email** : contact@arcop.bf
- 📱 **Téléphone** : +226 XX XX XX XX
- 🌐 **Site** : www.arcop.bf

---

## ✅ Checklist finale

Avant de mettre en production, vérifiez :

- [ ] Base de données créée et migrée
- [ ] Données de test ajoutées (ou vraies données)
- [ ] Variables d'environnement configurées (`.env`)
- [ ] Admin sécurisé avec mot de passe
- [ ] Logo ARCOP ajouté
- [ ] Coordonnées de contact mises à jour (footer, page contact)
- [ ] Site testé sur mobile
- [ ] Déploiement effectué sur Render/Railway
- [ ] URL personnalisée configurée (optionnel)

---

**🎉 Félicitations ! Votre site ARCOP est opérationnel !**

Pour toute question, consultez le `README.md` complet ou contactez le support technique.
