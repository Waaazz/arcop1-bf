# 🚀 DÉMARRAGE RAPIDE - SITE ARCOP V2

## ✨ CE QUI A ÉTÉ FAIT

Votre site ARCOP a été **entièrement réadapté** avec la nouvelle navigation et le design que vous avez fourni :

✅ Navigation mise à jour avec 6 menus principaux et emojis
✅ Nouvelle page d'accueil complète avec tous les éléments de votre design
✅ 25 nouvelles routes et pages créées
✅ 32 fichiers templates au total
✅ Toutes les pages connectées à la base de données

## 📥 TÉLÉCHARGER ET INSTALLER

### 1. Téléchargez l'archive
Le fichier `arcop_website_v2.zip` contient tout le projet mis à jour.

### 2. Extraction et installation

```bash
# Extraire l'archive
unzip arcop_website_v2.zip
cd arcop_website

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Créer des données de test (optionnel)
flask init-db

# Lancer le serveur
python app.py
```

### 3. Accéder au site

- **Site web** : http://127.0.0.1:5000
- **Interface admin** : http://127.0.0.1:5000/admin

## 🖼️ IMAGES À AJOUTER

**IMPORTANT** : Ajoutez ces images dans le dossier `static/images/` :

```
static/images/
├── logo_arcop1.png          ← LOGO PRINCIPAL (pour le header)
├── logo_arcop.png           ← Logo secondaire (pour l'accueil)
├── img1.jpg                 ← Slideshow hero
├── img3.jpg                 ← Slideshow hero
├── img4.jpg                 ← Slideshow hero
└── partenaires/
    ├── p1.jpg à p6.jpg      ← Logos partenaires
```

**Sans ces images, le site affichera des images manquantes.**

## 📝 PERSONNALISATION RAPIDE

### Informations bancaires (pour les dons)
Fichier : `templates/arcop/don.html`
Ligne à modifier : Informations bancaires

### Histoire de l'ARCOP
Fichier : `templates/arcop/histoire.html`
Ajoutez votre contenu complet

### Contenu des domaines
Fichiers : `templates/domaines/*.html`
Développez chaque page selon vos besoins

## 🎯 NAVIGATION COMPLÈTE

```
🏠 ACCUEIL
🏛️ L'ARCOP
   ├─ Notre Histoire
   ├─ Mission, Vision et Valeurs
   ├─ Nos collaborateurs
   ├─ Faire un don
   └─ Offre d'emplois

🌿 DOMAINES
   ├─ Éducation
   ├─ Humanitaire
   ├─ Santé
   ├─ Changement climatique
   ├─ Agroécologie
   └─ Formation professionnelle

🤝 PROJETS
   ├─ Éducation
   ├─ Humanitaire
   ├─ Santé
   ├─ Changement climatique
   ├─ Agroécologie
   └─ Formation professionnelle

🎥 MULTIMÉDIAS
   ├─ Galerie photos
   ├─ Vidéothèque
   └─ Documentations

✉️ CONTACT
```

## 🔧 GESTION DU CONTENU

Utilisez l'interface d'administration Flask-Admin :

1. Accédez à http://127.0.0.1:5000/admin
2. Ajoutez du contenu dans :
   - **Actualités** : Pour alimenter la section actualités
   - **Documents** : Pour la page documentations
   - **Membres** : S'affichent dans "Nos collaborateurs"
   - **Projets** : S'affichent dans toutes les pages projets
   - **Partenaires** : Pour la section partenaires
   - **Événements** : Pour l'agenda

## 📋 CHECKLIST AVANT DÉPLOIEMENT

- [ ] Ajouter toutes les images manquantes
- [ ] Personnaliser les textes des pages
- [ ] Ajouter les informations bancaires dans la page "Don"
- [ ] Créer du contenu via l'interface admin
- [ ] Tester toutes les pages
- [ ] Vérifier la version mobile/responsive
- [ ] Configurer une clé secrète sécurisée dans .env
- [ ] Sécuriser l'interface admin (voir README.md)

## 📚 DOCUMENTATION COMPLÈTE

- **MISE_A_JOUR.md** : Détails complets de toutes les modifications
- **README.md** : Documentation technique complète
- **DEMARRAGE_RAPIDE.md** : Guide d'installation pas à pas
- **PROJET_COMPLET.md** : Vue d'ensemble du projet

## 🆘 BESOIN D'AIDE ?

1. Consultez le fichier **MISE_A_JOUR.md** pour les détails
2. Vérifiez la console du navigateur pour les erreurs
3. Consultez les logs du serveur Flask

---

**🎉 Votre site ARCOP version 2.0 est prêt !**

Bon développement ! 🚀
