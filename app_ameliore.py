from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf.csrf import CSRFProtect, CSRFError, validate_csrf
from datetime import datetime, timedelta, timezone
from functools import wraps
from collections import defaultdict
import time
import os
import bleach

from flask_admin.form import ImageUploadField, FileUploadField
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename





# Initialisation de l'application Flask
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 Mo

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'votre-cle-secrete-a-changer-en-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///arcop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Sécurité des sessions
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'

# CSRF - activé uniquement sur les routes marquées (@csrf.protect)
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = False

# Fix pour Render PostgreSQL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

# Initialisation des extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# ===========================
# CONFIGURATION ADMIN
# ===========================

# Identifiants admin
# En production : définir ADMIN_USERNAME et ADMIN_PASSWORD_HASH (hash généré avec generate_password_hash)
# En développement : définir ADMIN_PASSWORD en clair dans les variables d'environnement
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')

_password_hash_env = os.environ.get('ADMIN_PASSWORD_HASH')
_password_plain_env = os.environ.get('ADMIN_PASSWORD')

if _password_hash_env:
    ADMIN_PASSWORD_HASH = _password_hash_env
elif _password_plain_env:
    ADMIN_PASSWORD_HASH = generate_password_hash(_password_plain_env)
else:
    # Aucun mot de passe défini : générer un hash aléatoire (login impossible sans config)
    import secrets
    _tmp = secrets.token_urlsafe(32)
    ADMIN_PASSWORD_HASH = generate_password_hash(_tmp)
    print("⚠️  ADMIN_PASSWORD non défini. Définissez ADMIN_PASSWORD dans vos variables d'environnement.")

# Anti-bruteforce : suivi des tentatives de connexion par IP
_login_attempts: dict = defaultdict(list)
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 900  # 15 minutes

def _is_rate_limited(ip: str) -> bool:
    """Vérifie si l'IP est bloquée après trop de tentatives."""
    now = time.time()
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < _LOCKOUT_SECONDS]
    return len(_login_attempts[ip]) >= _MAX_ATTEMPTS

def _record_failed_attempt(ip: str) -> None:
    """Enregistre une tentative de connexion échouée."""
    _login_attempts[ip].append(time.time())

def login_required(f):
    """Décorateur pour protéger les routes admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ===========================
# MODÈLES DE BASE DE DONNÉES
# ===========================

class Actualite(db.Model):
    """Modèle pour les actualités"""
    __tablename__ = 'actualites'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    extrait = db.Column(db.String(300))
    image_url = db.Column(db.String(500))
    categorie = db.Column(db.String(100))  # Changement climatique, Éducation, Santé, etc.
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)
    publie = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Actualite {self.titre}>'


class Document(db.Model):
    """Modèle pour les documents (publications, rapports, etc.)"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(100))  # Documents ARCOP, Politiques, Autres
    fichier_url = db.Column(db.String(500))
    type_fichier = db.Column(db.String(50))  # PDF, Word, etc.
    taille_fichier = db.Column(db.String(50))  # Ex: 2.5 MB
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)
    telechargements = db.Column(db.Integer, default=0)
    publie = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Document {self.titre}>'


class Membre(db.Model):
    """Modèle pour les membres de l'ARCOP"""
    __tablename__ = 'membres'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    fonction = db.Column(db.String(100))
    organisation = db.Column(db.String(200))
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    email = db.Column(db.String(100))
    telephone = db.Column(db.String(50))
    ordre = db.Column(db.Integer, default=0)  # Pour l'ordre d'affichage
    actif = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Membre {self.nom}>'


class Partenaire(db.Model):
    """Modèle pour les partenaires"""
    __tablename__ = 'partenaires'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    site_web = db.Column(db.String(200))
    type_partenaire = db.Column(db.String(100))  # Technique, Financier, etc.
    ordre = db.Column(db.Integer, default=0)
    actif = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Partenaire {self.nom}>'


class Projet(db.Model):
    """Modèle pour les projets"""
    __tablename__ = 'projets'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    categorie = db.Column(db.String(100))  # Éducation, Santé, Agroécologie, etc.
    objectifs = db.Column(db.Text)
    resultats = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    budget = db.Column(db.String(100))
    statut = db.Column(db.String(50), default='En cours')  # En cours, Terminé, Planifié
    partenaires = db.Column(db.String(500))
    publie = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Projet {self.titre}>'


class Evenement(db.Model):
    """Modèle pour l'agenda/événements"""
    __tablename__ = 'evenements'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(100))  # agroecologie, formation, climat, sante, etc.
    lieu = db.Column(db.String(200))
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime)
    couleur = db.Column(db.String(7), default='#2d862d')  # Couleur pour l'agenda
    publie = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Evenement {self.titre}>'


class Photo(db.Model):
    """Modèle pour la galerie photos"""
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    categorie = db.Column(db.String(100))
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    publie = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Photo {self.titre}>'


class Video(db.Model):
    """Modèle pour la vidéothèque"""
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url_video = db.Column(db.String(500), nullable=False)  # Lien YouTube/Vimeo
    miniature_url = db.Column(db.String(500))  # Image miniature uploadée
    categorie = db.Column(db.String(100))
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    publie = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Video {self.titre}>'


class MessageContact(db.Model):
    """Messages reçus via le formulaire de contact"""
    __tablename__ = 'messages_contact'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(50))
    objet = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    lu = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<MessageContact {self.nom} - {self.objet}>'


class Abonne(db.Model):
    """Abonnés à la newsletter"""
    __tablename__ = 'abonnes'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Abonne {self.email}>'


# ===========================
# VUES PERSONNALISÉES ADMIN
# ===========================

class SecureModelView(ModelView):
    """Vue de modèle sécurisée avec authentification"""

    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

    def handle_view_exception(self, exc):
        """Journalise toutes les exceptions admin et affiche un message d'erreur convivial."""
        import traceback
        app.logger.error('Erreur admin (%s): %s\n%s', self.__class__.__name__, exc, traceback.format_exc())
        flash(f'Erreur lors de l\'opération : {exc}', 'error')
        return True


class SecureAdminIndexView(AdminIndexView):
    """Page d'accueil admin sécurisée"""
    
    @expose('/')
    def index(self):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))

        # Statistiques
        stats = {
            'actualites': Actualite.query.count(),
            'documents': Document.query.count(),
            'membres': Membre.query.filter_by(actif=True).count(),
            'partenaires': Partenaire.query.filter_by(actif=True).count(),
            'projets': Projet.query.count(),
            'evenements': Evenement.query.count(),
            'photos': Photo.query.count(),
            'videos': Video.query.count()
        }

        # Dernières actualités
        dernieres_actus = Actualite.query.order_by(Actualite.date_publication.desc()).limit(5).all()

        # Prochains événements
        prochains_events = Evenement.query.filter(
            Evenement.date_debut >= datetime.now(timezone.utc).replace(tzinfo=None)
        ).order_by(Evenement.date_debut).limit(5).all()

        return self.render('admin/index.html', stats=stats, dernieres_actus=dernieres_actus, prochains_events=prochains_events)


class ActualiteAdmin(SecureModelView):
    """Administration des actualités"""
    column_list = ['titre', 'categorie', 'date_publication', 'publie']
    column_searchable_list = ['titre', 'contenu', 'extrait']
    column_filters = ['publie', 'categorie', 'date_publication']
    column_labels = {
        'titre': 'Titre',
        'contenu': 'Contenu',
        'extrait': 'Extrait',
        'image_url': 'Image',
        'categorie': 'Catégorie',
        'date_publication': 'Date de publication',
        'publie': 'Publié'
    }
    form_excluded_columns = ['date_publication']
    form_extra_fields = {
        'image_url': ImageUploadField(
            'Image',
            base_path=os.path.join(app.root_path, 'static/uploads'),
            relative_path='actualites/',
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
        )
    }
    form_widget_args = {
        'contenu': {
            'rows': 10
        },
        'extrait': {
            'rows': 3
        }
    }
    column_default_sort = ('date_publication', True)
    can_export = True


class DocumentAdmin(SecureModelView):
    """Administration des documents"""
    column_list = ['titre', 'categorie', 'type_fichier', 'date_publication', 'telechargements', 'publie']
    column_searchable_list = ['titre', 'description']
    column_filters = ['categorie', 'type_fichier', 'publie']
    column_labels = {
        'titre': 'Titre',
        'description': 'Description',
        'categorie': 'Catégorie',
        'fichier_url': 'Fichier',
        'type_fichier': 'Type de fichier',
        'taille_fichier': 'Taille',
        'date_publication': 'Date de publication',
        'telechargements': 'Téléchargements',
        'publie': 'Publié'
    }
    form_extra_fields = {
        'fichier_url': FileUploadField(
            'Fichier',
            base_path=os.path.join(app.root_path, 'static/uploads'),
            relative_path='documents/',
            allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv']
        )
    }
    column_default_sort = ('date_publication', True)


class MembreAdmin(SecureModelView):
    """Administration des membres"""
    column_list = ['nom', 'fonction', 'organisation', 'ordre', 'actif']
    column_searchable_list = ['nom', 'fonction', 'organisation']
    column_filters = ['actif', 'organisation']
    column_labels = {
        'nom': 'Nom',
        'fonction': 'Fonction',
        'organisation': 'Organisation',
        'bio': 'Biographie',
        # 'photo_url': 'URL Photo',
        'email': 'Email',
        'telephone': 'Téléphone',
        'ordre': 'Ordre d\'affichage',
        'actif': 'Actif'
    }
    form_extra_fields = {
        'photo_url': ImageUploadField(
            'Photo',
            base_path=os.path.join(app.root_path, 'static/uploads'),
            relative_path='membres/',
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
        )
    }
    column_default_sort = 'ordre'


class PartenaireAdmin(SecureModelView):
    """Administration des partenaires"""
    column_list = ['nom', 'type_partenaire', 'ordre', 'actif']
    column_searchable_list = ['nom', 'description']
    column_filters = ['type_partenaire', 'actif']
    column_labels = {
        'nom': 'Nom',
        'description': 'Description',
        'logo_url': 'Logo',
        'site_web': 'Site web',
        'type_partenaire': 'Type de partenaire',
        'ordre': 'Ordre d\'affichage',
        'actif': 'Actif'
    }
    form_extra_fields = {
        'logo_url': ImageUploadField(
            'Logo',
            base_path=os.path.join(app.root_path, 'static/uploads'),
            relative_path='partenaires/',
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
        )
    }
    column_default_sort = 'ordre'


class ProjetAdmin(SecureModelView):
    """Administration des projets"""
    column_list = ['titre', 'categorie', 'statut', 'date_debut', 'date_fin', 'publie']
    column_searchable_list = ['titre', 'description', 'objectifs']
    column_filters = ['categorie', 'statut', 'publie']
    column_labels = {
        'titre': 'Titre',
        'description': 'Description',
        'categorie': 'Catégorie',
        'objectifs': 'Objectifs',
        'resultats': 'Résultats',
        'image_url': 'Image',
        'date_debut': 'Date de début',
        'date_fin': 'Date de fin',
        'budget': 'Budget',
        'statut': 'Statut',
        'partenaires': 'Partenaires',
        'publie': 'Publié'
    }
    form_extra_fields = {
        'image_url': ImageUploadField(
            'Image',
            base_path=os.path.join(app.root_path, 'static/uploads'),
            relative_path='projets/',
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
        )
    }
    form_widget_args = {
        'description': {'rows': 5},
        'objectifs': {'rows': 5},
        'resultats': {'rows': 5}
    }


class EvenementAdmin(SecureModelView):
    """Administration des événements"""
    column_list = ['titre', 'categorie', 'lieu', 'date_debut', 'date_fin', 'publie']
    column_searchable_list = ['titre', 'description', 'lieu']
    column_filters = ['publie', 'categorie', 'date_debut']
    column_labels = {
        'titre': 'Titre',
        'description': 'Description',
        'categorie': 'Catégorie',
        'lieu': 'Lieu',
        'date_debut': 'Date de début',
        'date_fin': 'Date de fin',
        'couleur': 'Couleur',
        'publie': 'Publié'
    }
    form_choices = {
        'categorie': [
            ('agroecologie', 'Agroécologie'),
            ('formation', 'Formation'),
            ('climat', 'Changement climatique'),
            ('sante', 'Santé'),
            ('education', 'Éducation'),
            ('partenariat', 'Partenariat'),
            ('autre', 'Autre')
        ]
    }
    column_default_sort = ('date_debut', True)


class PhotoAdmin(SecureModelView):
    """Administration de la galerie photos"""
    column_list = ['titre', 'categorie', 'date_ajout', 'publie']
    column_searchable_list = ['titre', 'description']
    column_filters = ['publie', 'categorie']
    column_labels = {
        'titre': 'Titre',
        'description': 'Description',
        'image_url': 'Photo',
        'categorie': 'Catégorie',
        'date_ajout': 'Date d\'ajout',
        'publie': 'Publié'
    }
    form_excluded_columns = ['date_ajout']
    form_extra_fields = {
        'image_url': ImageUploadField(
            'Photo',
            base_path=os.path.join(app.root_path, 'static/uploads'),
            relative_path='galerie/',
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
        )
    }
    form_choices = {
        'categorie': [
            ('activites', 'Activités'),
            ('formations', 'Formations'),
            ('evenements', 'Événements'),
            ('terrain', 'Sur le terrain'),
            ('partenaires', 'Partenaires'),
            ('autre', 'Autre')
        ]
    }
    column_default_sort = ('date_ajout', True)


class VideoAdmin(SecureModelView):
    """Administration de la vidéothèque"""
    column_list = ['titre', 'categorie', 'date_ajout', 'publie']
    column_searchable_list = ['titre', 'description']
    column_filters = ['publie', 'categorie']
    column_labels = {
        'titre': 'Titre',
        'description': 'Description',
        'url_video': 'Lien vidéo (YouTube/Vimeo)',
        'miniature_url': 'Miniature',
        'categorie': 'Catégorie',
        'date_ajout': 'Date d\'ajout',
        'publie': 'Publié'
    }
    form_excluded_columns = ['date_ajout']
    form_extra_fields = {
        'miniature_url': ImageUploadField(
            'Miniature',
            base_path=os.path.join(app.root_path, 'static/uploads'),
            relative_path='videos/',
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
        )
    }
    form_choices = {
        'categorie': [
            ('presentation', 'Présentation'),
            ('formation', 'Formation'),
            ('terrain', 'Sur le terrain'),
            ('evenement', 'Événement'),
            ('temoignage', 'Témoignage'),
            ('autre', 'Autre')
        ]
    }
    form_widget_args = {
        'description': {'rows': 4}
    }
    column_default_sort = ('date_ajout', True)


class MessageContactAdmin(SecureModelView):
    """Administration des messages de contact"""
    column_list = ['nom', 'email', 'objet', 'date_envoi', 'lu']
    column_searchable_list = ['nom', 'email', 'objet']
    column_filters = ['lu', 'date_envoi']
    column_labels = {
        'nom': 'Nom',
        'email': 'Email',
        'telephone': 'Téléphone',
        'objet': 'Objet',
        'message': 'Message',
        'date_envoi': 'Date d\'envoi',
        'lu': 'Lu'
    }
    can_create = False
    can_edit = True
    can_delete = True
    column_default_sort = ('date_envoi', True)
    form_widget_args = {
        'message': {'rows': 6}
    }


class AbonneAdmin(SecureModelView):
    """Administration des abonnés newsletter"""
    column_list = ['email', 'date_inscription', 'actif']
    column_searchable_list = ['email']
    column_filters = ['actif', 'date_inscription']
    column_labels = {
        'email': 'Email',
        'date_inscription': 'Date d\'inscription',
        'actif': 'Actif'
    }
    can_create = False
    column_default_sort = ('date_inscription', True)
    can_export = True


# ===========================
# CONFIGURATION FLASK-ADMIN
# ===========================

admin = Admin(
    app, 
    name='ARCOP Admin', 
    template_mode='bootstrap4',
    index_view=SecureAdminIndexView(),
    base_template='admin/base_custom.html'
)

# Ajout des modèles à l'interface admin
admin.add_view(ActualiteAdmin(Actualite, db.session, name='Actualités', category='Contenu'))
admin.add_view(DocumentAdmin(Document, db.session, name='Documents', category='Contenu'))
admin.add_view(ProjetAdmin(Projet, db.session, name='Projets', category='Contenu'))
admin.add_view(EvenementAdmin(Evenement, db.session, name='Événements', category='Contenu'))
admin.add_view(MembreAdmin(Membre, db.session, name='Membres', category='Organisation'))
admin.add_view(PhotoAdmin(Photo, db.session, name='Galerie Photos', category='Multimedias'))
admin.add_view(VideoAdmin(Video, db.session, name='Vidéos', category='Multimedias'))
admin.add_view(PartenaireAdmin(Partenaire, db.session, name='Partenaires', category='Organisation'))
admin.add_view(MessageContactAdmin(MessageContact, db.session, name='Messages Contact', category='Communications'))
admin.add_view(AbonneAdmin(Abonne, db.session, name='Newsletter', category='Communications'))


# ===========================
# ROUTES ADMIN
# ===========================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Page de connexion admin"""
    if request.method == 'POST':
        # Validation CSRF manuelle
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception:
            flash('Token de sécurité invalide. Veuillez réessayer.', 'error')
            return render_template('admin/login.html')

        ip = request.remote_addr

        if _is_rate_limited(ip):
            flash('Trop de tentatives. Réessayez dans 15 minutes.', 'error')
            return render_template('admin/login.html')

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            session.permanent = True
            flash('Connexion réussie !', 'success')
            return redirect('/admin')
        else:
            _record_failed_attempt(ip)
            flash('Identifiants incorrects', 'error')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Déconnexion admin"""
    session.pop('admin_logged_in', None)
    flash('Vous êtes déconnecté', 'info')
    return redirect(url_for('index'))


# ===========================
# SÉCURITÉ : HEADERS HTTP
# ===========================

@app.after_request
def add_security_headers(response):
    """Ajoute les headers de sécurité à toutes les réponses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https:; "
        "frame-src https://www.youtube.com https://www.youtube-nocookie.com;"
    )
    return response


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Gestion des erreurs CSRF."""
    flash('Token de sécurité invalide. Veuillez réessayer.', 'error')
    return redirect(url_for('admin_login'))


# ===========================
# SÉCURITÉ : FILTRE SANITIZE (anti-XSS)
# ===========================

_ALLOWED_TAGS = [
    'p', 'br', 'b', 'i', 'strong', 'em', 'u', 'a',
    'ul', 'ol', 'li', 'h2', 'h3', 'h4', 'blockquote', 'span'
]
_ALLOWED_ATTRS = {
    'a': ['href', 'title', 'target'],
    '*': ['class'],
}

@app.template_filter('sanitize')
def sanitize_html(value):
    """Nettoie le HTML pour prévenir les injections XSS tout en gardant le formatage."""
    if not value:
        return ''
    return bleach.clean(value, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS, strip=True)


# ===========================
# ROUTES DU SITE PUBLIC
# ===========================

@app.route('/')
def index():
    """Page d'accueil"""
    actualites = Actualite.query.filter_by(publie=True).order_by(Actualite.date_publication.desc()).limit(9).all()
    evenements = Evenement.query.filter_by(publie=True).order_by(Evenement.date_debut).limit(9).all()
    partenaires = Partenaire.query.filter_by(actif=True).order_by(Partenaire.ordre).limit(6).all()
    return render_template('index.html', actualites=actualites, evenements=evenements, partenaires=partenaires)


@app.route('/arcop/presentation')
def presentation():
    """Page de présentation de l'ARCOP"""
    return render_template('arcop/presentation.html')


@app.route('/arcop/mot-president')
def mot_president():
    """Mot du président"""
    return render_template('arcop/mot_president.html')


@app.route('/arcop/membres')
def membres():
    """Liste des membres de l'ARCOP"""
    membres_list = Membre.query.filter_by(actif=True).order_by(Membre.ordre).all()
    return render_template('arcop/membres.html', membres=membres_list)


@app.route('/arcop/initiatives')
def initiatives():
    """Initiatives développées"""
    return render_template('arcop/initiatives.html')


@app.route('/partenaires-projets')
def partenaires_projets():
    """Page partenaires et projets"""
    partenaires = Partenaire.query.filter_by(actif=True).all()
    projets = Projet.query.filter_by(publie=True).all()
    return render_template('partenaires_projets.html', partenaires=partenaires, projets=projets)


@app.route('/documentations/doc-arcop')
def doc_arcop():
    """Documents de l'ARCOP"""
    documents = Document.query.filter_by(categorie='Documents ARCOP', publie=True).all()
    return render_template('documentations/doc_arcop.html', documents=documents)


@app.route('/documentations/politiques-lois')
def politiques_lois():
    """Politiques et lois agro-sylvo-pastorales"""
    documents = Document.query.filter_by(categorie='Politiques et Lois', publie=True).all()
    return render_template('documentations/politiques_lois.html', documents=documents)


@app.route('/documentations/autres-publications')
def autres_pub():
    """Autres publications"""
    documents = Document.query.filter_by(categorie='Autres Publications', publie=True).all()
    return render_template('documentations/autres_pub.html', documents=documents)


@app.route('/agroecologie')
def agroecologie():
    """Page agroécologie"""
    projets = Projet.query.filter_by(categorie='Agroécologie', publie=True).all()
    return render_template('agroecologie.html', projets=projets)


@app.route('/actualite')
def actualite():
    """Page des actualités"""
    page = request.args.get('page', 1, type=int)
    actualites = Actualite.query.filter_by(publie=True).order_by(
        Actualite.date_publication.desc()
    ).paginate(page=page, per_page=9, error_out=False)
    return render_template('actualite.html', actualites=actualites)


@app.route('/actualite/<int:id>')
def actualite_detail(id):
    """Détail d'une actualité"""
    actu = Actualite.query.get_or_404(id)
    return render_template('actualite_detail.html', actualite=actu)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Page de contact"""
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except Exception:
            flash('Token de sécurité invalide. Veuillez réessayer.', 'error')
            return redirect(url_for('contact'))

        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        telephone = request.form.get('telephone', '').strip()
        objet = request.form.get('objet', '').strip()
        message_text = request.form.get('message', '').strip()

        if not all([nom, email, objet, message_text]):
            flash('Veuillez remplir tous les champs obligatoires.', 'error')
            return redirect(url_for('contact'))

        msg = MessageContact(
            nom=nom,
            email=email,
            telephone=telephone,
            objet=objet,
            message=message_text
        )
        db.session.add(msg)
        db.session.commit()
        flash('Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/agenda')
@app.route('/evenements')
def evenements():
    """Page agenda - tous les événements"""
    evenements_list = Evenement.query.filter_by(publie=True).order_by(Evenement.date_debut).all()
    return render_template('evenement.html', evenements=evenements_list)


# ===========================
# ROUTES L'ARCOP
# ===========================

@app.route('/arcop/histoire')
def histoire():
    """Notre histoire"""
    return render_template('arcop/histoire.html')


@app.route('/arcop/mission-vision-valeurs')
def mission_vision_valeurs():
    """Mission, vision et valeurs"""
    return render_template('arcop/mission_vision_valeurs.html')


@app.route('/arcop/collaborateurs')
def collaborateurs():
    """Nos collaborateurs"""
    collaborateurs_list = Membre.query.filter_by(actif=True).order_by(Membre.ordre).all()
    return render_template('arcop/collaborateurs.html', collaborateurs=collaborateurs_list)


@app.route('/arcop/don')
def don():
    """Faire un don"""
    return render_template('arcop/don.html')


@app.route('/arcop/emplois')
def emplois():
    """Offres d'emplois"""
    return render_template('arcop/emplois.html')


# ===========================
# ROUTES DOMAINES
# ===========================

@app.route('/domaines/education')
def domaines_education():
    """Domaine éducation"""
    return render_template('domaines/education.html')


@app.route('/domaines/humanitaire')
def domaines_humanitaire():
    """Domaine humanitaire"""
    return render_template('domaines/humanitaire.html')


@app.route('/domaines/sante')
def domaines_sante():
    """Domaine santé"""
    return render_template('domaines/sante.html')


@app.route('/domaines/changement-climatique')
def domaines_changement_climatique():
    """Domaine changement climatique"""
    return render_template('domaines/changement_climatique.html')


@app.route('/domaines/agroecologie')
def domaines_agroecologie():
    """Domaine agroécologie"""
    return render_template('domaines/agroecologie.html')


@app.route('/domaines/formation')
def domaines_formation():
    """Domaine formation professionnelle"""
    return render_template('domaines/formation.html')


# ===========================
# ROUTES PROJETS
# ===========================

@app.route('/projets/education')
def projets_education():
    """Projets éducation"""
    projets = Projet.query.filter_by(categorie='Éducation', publie=True).all()
    return render_template('projets/education.html', projets=projets)


@app.route('/projets/humanitaire')
def projets_humanitaire():
    """Projets humanitaire"""
    projets = Projet.query.filter_by(categorie='Humanitaire', publie=True).all()
    return render_template('projets/humanitaire.html', projets=projets)


@app.route('/projets/sante')
def projets_sante():
    """Projets santé"""
    projets = Projet.query.filter_by(categorie='Santé', publie=True).all()
    return render_template('projets/sante.html', projets=projets)


@app.route('/projets/changement-climatique')
def projets_changement_climatique():
    """Projets changement climatique"""
    projets = Projet.query.filter_by(categorie='Changement climatique', publie=True).all()
    return render_template('projets/changement_climatique.html', projets=projets)


@app.route('/projets/agroecologie')
def projets_agroecologie():
    """Projets agroécologie"""
    projets = Projet.query.filter_by(categorie='Agroécologie', publie=True).all()
    return render_template('projets/agroecologie.html', projets=projets)


@app.route('/projets/formation')
def projets_formation():
    """Projets formation professionnelle"""
    projets = Projet.query.filter_by(categorie='Formation professionnelle', publie=True).all()
    return render_template('projets/formation.html', projets=projets)


# ===========================
# ROUTES MULTIMEDIAS
# ===========================

@app.route('/multimedias/galerie')
def galerie():
    """Galerie photos"""
    page = request.args.get('page', 1, type=int)
    photos = Photo.query.filter_by(publie=True).order_by(
        Photo.date_ajout.desc()
    ).paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Photo.categorie).filter(
        Photo.publie == True, Photo.categorie != None
    ).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('multimedias/galerie.html', photos=photos, categories=categories)


@app.route('/multimedias/videos')
def videos():
    """Vidéothèque"""
    page = request.args.get('page', 1, type=int)
    videos_list = Video.query.filter_by(publie=True).order_by(
        Video.date_ajout.desc()
    ).paginate(page=page, per_page=9, error_out=False)
    return render_template('multimedias/videos.html', videos=videos_list)


@app.route('/newsletter/inscription', methods=['POST'])
def newsletter_inscription():
    """Inscription à la newsletter"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash('Token de sécurité invalide. Veuillez réessayer.', 'error')
        return redirect(url_for('index'))

    email = request.form.get('email', '').strip()
    if not email:
        flash('Veuillez saisir une adresse email valide.', 'error')
        return redirect(url_for('index'))

    existing = Abonne.query.filter_by(email=email).first()
    if existing:
        if existing.actif:
            flash('Cette adresse email est déjà inscrite à notre newsletter.', 'info')
        else:
            existing.actif = True
            db.session.commit()
            flash('Votre inscription a été réactivée avec succès !', 'success')
    else:
        abonne = Abonne(email=email)
        db.session.add(abonne)
        db.session.commit()
        flash('Inscription réussie ! Merci de vous être abonné à notre newsletter.', 'success')

    return redirect(url_for('index'))


@app.route('/multimedias/documentations')
def documentations():
    """Documentations"""
    documents = Document.query.filter_by(publie=True).order_by(Document.date_publication.desc()).all()
    return render_template('multimedias/documentations.html', documents=documents)


# ===========================
# COMMANDES CLI
# ===========================

@app.cli.command()
def init_db():
    """Initialise la base de données avec des données de test"""
    db.create_all()
    
    # Vérifier si des données existent déjà
    if Actualite.query.first():
        print("✅ La base de données contient déjà des données.")
        return
    
    print("🔄 Création des données de test...")
    
    # Créer des actualités de test
    actualites_test = [
        Actualite(
            titre="Renforcement des capacités des organisations membres",
            extrait="L'ARCOP a organisé une session de formation sur les techniques agroécologiques...",
            contenu="L'ARCOP a organisé une session de formation sur les techniques agroécologiques pour les membres. Cette formation a permis de renforcer les compétences de plus de 50 producteurs.",
            categorie="Formation",
            image_url="/static/images/formation.jpg"
        ),
        Actualite(
            titre="Promotion de l'agroécologie dans les zones rurales",
            extrait="Lancement d'un nouveau programme pour promouvoir les pratiques agroécologiques...",
            contenu="L'ARCOP lance un nouveau programme ambitieux pour promouvoir les pratiques agroécologiques durables dans les zones rurales du Burkina Faso.",
            categorie="Agroécologie",
            image_url="/static/images/agroecologie.jpg"
        ),
        Actualite(
            titre="Action climatique pour un avenir durable",
            extrait="L'ARCOP met en œuvre des initiatives locales pour renforcer la résilience...",
            contenu="L'ARCOP met en œuvre des initiatives locales pour renforcer la résilience des communautés rurales face aux changements climatiques.",
            categorie="Changement climatique",
            image_url="/static/images/climat.jpg"
        ),
    ]
    
    for actu in actualites_test:
        db.session.add(actu)
    
    # Créer des membres de test
    membres_test = [
        Membre(
            nom="Dr. Amadou TRAORE",
            fonction="Président",
            organisation="ARCOP",
            bio="Agronome de formation avec plus de 20 ans d'expérience dans le développement rural.",
            ordre=1
        ),
        Membre(
            nom="Mme Fatou OUEDRAOGO",
            fonction="Secrétaire Générale",
            organisation="ARCOP",
            bio="Spécialiste en développement rural et renforcement des capacités.",
            ordre=2
        ),
        Membre(
            nom="M. Ibrahim SAWADOGO",
            fonction="Trésorier",
            organisation="ARCOP",
            bio="Expert en gestion financière et comptabilité.",
            ordre=3
        ),
    ]
    
    for membre in membres_test:
        db.session.add(membre)
    
    # Créer des événements de test
    evenements_test = [
        Evenement(
            titre="Atelier sur la gestion durable des sols",
            description="Formation des producteurs aux techniques de conservation des sols",
            categorie="agroecologie",
            lieu="Ouagadougou",
            date_debut=datetime(2025, 10, 25, 9, 0),
            couleur="#2d862d"
        ),
        Evenement(
            titre="Forum sur le changement climatique",
            description="Discussion sur les impacts climatiques et solutions locales",
            categorie="climat",
            lieu="Ouagadougou",
            date_debut=datetime(2026, 1, 10, 9, 0),
            couleur="#00bcd4"
        ),
        Evenement(
            titre="Formation en techniques agroécologiques",
            description="Session de formation avancée pour les producteurs",
            categorie="formation",
            lieu="Koudougou",
            date_debut=datetime(2026, 2, 15, 9, 0),
            couleur="#1e5a8e"
        ),
        Evenement(
            titre="Campagne santé communautaire",
            description="Sensibilisation sur la nutrition et la santé maternelle",
            categorie="sante",
            lieu="Ouahigouya",
            date_debut=datetime(2026, 3, 20, 9, 0),
            couleur="#e91e63"
        ),
    ]
    
    for event in evenements_test:
        db.session.add(event)
    
    db.session.commit()
    print("✅ Base de données initialisée avec succès!")
    print(f"   - {len(actualites_test)} actualités créées")
    print(f"   - {len(membres_test)} membres créés")
    print(f"   - {len(evenements_test)} événements créés")
    print("\n🔐 Identifiants admin par défaut:")
    print(f"   Username: {ADMIN_USERNAME}")
    print(f"   Password: {ADMIN_PASSWORD}")
    print("\n⚠️  CHANGEZ CES IDENTIFIANTS EN PRODUCTION!")


# Context processor pour les variables globales
@app.context_processor
def inject_globals():
    """Injecte des variables globales dans tous les templates"""
    def upload_url(filename):
        """Genere l'URL correcte pour un fichier uploade ou une URL existante"""
        if not filename:
            return ''
        # Si c'est deja une URL complete ou un chemin /static/, on le garde tel quel
        if filename.startswith(('http://', 'https://', '/static/', 'data:')):
            return filename
        # Sinon c'est un fichier uploade via ImageUploadField/FileUploadField
        return url_for('static', filename='uploads/' + filename)
    return {
        'current_year': datetime.now().year,
        'admin_logged_in': session.get('admin_logged_in', False),
        'upload_url': upload_url
    }


# Gestion des erreurs
@app.errorhandler(404)
def page_not_found(e):
    """Page 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Page 500"""
    import traceback
    app.logger.error('Erreur 500: %s\n%s', e, traceback.format_exc())
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)