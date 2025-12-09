from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
import os

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'votre-cle-secrete-a-changer')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///arcop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix pour Render PostgreSQL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

# Initialisation des extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)
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
    actif = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Partenaire {self.nom}>'


class Projet(db.Model):
    """Modèle pour les projets"""
    __tablename__ = 'projets'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    objectifs = db.Column(db.Text)
    resultats = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    statut = db.Column(db.String(50))  # En cours, Terminé, Planifié
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
    lieu = db.Column(db.String(200))
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime)
    couleur = db.Column(db.String(7), default='#2d862d')  # Couleur pour l'agenda
    publie = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Evenement {self.titre}>'


# ===========================
# CONFIGURATION FLASK-ADMIN
# ===========================

admin = Admin(app, name='ARCOP Admin', template_mode='bootstrap4')

# Vues personnalisées pour l'admin
class ActualiteAdmin(ModelView):
    column_list = ['titre', 'date_publication', 'publie']
    column_searchable_list = ['titre', 'contenu']
    column_filters = ['publie', 'date_publication']
    form_excluded_columns = ['date_publication']


class DocumentAdmin(ModelView):
    column_list = ['titre', 'categorie', 'type_fichier', 'date_publication', 'publie']
    column_searchable_list = ['titre', 'description']
    column_filters = ['categorie', 'publie']


class MembreAdmin(ModelView):
    column_list = ['nom', 'fonction', 'organisation', 'actif']
    column_searchable_list = ['nom', 'fonction', 'organisation']
    column_filters = ['actif']


# Ajout des modèles à l'interface admin
admin.add_view(ActualiteAdmin(Actualite, db.session, name='Actualités'))
admin.add_view(DocumentAdmin(Document, db.session, name='Documents'))
admin.add_view(MembreAdmin(Membre, db.session, name='Membres'))
admin.add_view(ModelView(Partenaire, db.session, name='Partenaires'))
admin.add_view(ModelView(Projet, db.session, name='Projets'))
admin.add_view(ModelView(Evenement, db.session, name='Événements'))


# ===========================
# ROUTES DU SITE PUBLIC
# ===========================

@app.route('/')
def index():
    """Page d'accueil"""
    actualites = Actualite.query.filter_by(publie=True).order_by(Actualite.date_publication.desc()).limit(6).all()
    evenements = Evenement.query.filter_by(publie=True).order_by(Evenement.date_debut).limit(6).all()
    return render_template('index.html', actualites=actualites, evenements=evenements)


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
    return render_template('agroecologie.html')


@app.route('/actualite')
def actualite():
    """Page des actualités"""
    actualites = Actualite.query.filter_by(publie=True).order_by(Actualite.date_publication.desc()).all()
    return render_template('actualite.html', actualites=actualites)


@app.route('/actualite/<int:id>')
def actualite_detail(id):
    """Détail d'une actualité"""
    actu = Actualite.query.get_or_404(id)
    return render_template('actualite_detail.html', actualite=actu)


@app.route('/contact')
def contact():
    """Page de contact"""
    return render_template('contact.html')


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
    projets = Projet.query.filter_by(publie=True).all()
    return render_template('projets/education.html', projets=projets)


@app.route('/projets/humanitaire')
def projets_humanitaire():
    """Projets humanitaire"""
    projets = Projet.query.filter_by(publie=True).all()
    return render_template('projets/humanitaire.html', projets=projets)


@app.route('/projets/sante')
def projets_sante():
    """Projets santé"""
    projets = Projet.query.filter_by(publie=True).all()
    return render_template('projets/sante.html', projets=projets)


@app.route('/projets/changement-climatique')
def projets_changement_climatique():
    """Projets changement climatique"""
    projets = Projet.query.filter_by(publie=True).all()
    return render_template('projets/changement_climatique.html', projets=projets)


@app.route('/projets/agroecologie')
def projets_agroecologie():
    """Projets agroécologie"""
    projets = Projet.query.filter_by(publie=True).all()
    return render_template('projets/agroecologie.html', projets=projets)


@app.route('/projets/formation')
def projets_formation():
    """Projets formation professionnelle"""
    projets = Projet.query.filter_by(publie=True).all()
    return render_template('projets/formation.html', projets=projets)


# ===========================
# ROUTES MULTIMEDIAS
# ===========================

@app.route('/multimedias/galerie')
def galerie():
    """Galerie photos"""
    return render_template('multimedias/galerie.html')


@app.route('/multimedias/videos')
def videos():
    """Vidéothèque"""
    return render_template('multimedias/videos.html')


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
        print("La base de données contient déjà des données.")
        return
    
    # Créer des actualités de test
    actualites_test = [
        Actualite(
            titre="Renforcement des capacités des organisations membres",
            extrait="L'ARCOP a organisé une session de formation sur les techniques agroécologiques...",
            contenu="L'ARCOP a organisé une session de formation sur les techniques agroécologiques pour les membres. Cette formation a permis de renforcer les compétences de plus de 50 producteurs.",
            image_url="/static/images/formation.jpg"
        ),
        Actualite(
            titre="Promotion de l'agroécologie dans les zones rurales",
            extrait="Lancement d'un nouveau programme pour promouvoir les pratiques agroécologiques...",
            contenu="L'ARCOP lance un nouveau programme ambitieux pour promouvoir les pratiques agroécologiques durables dans les zones rurales du Burkina Faso.",
            image_url="/static/images/agroecologie.jpg"
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
            bio="Agronome de formation avec plus de 20 ans d'expérience...",
            ordre=1
        ),
        Membre(
            nom="Mme Fatou OUEDRAOGO",
            fonction="Secrétaire Générale",
            organisation="ARCOP",
            bio="Spécialiste en développement rural...",
            ordre=2
        ),
    ]
    
    for membre in membres_test:
        db.session.add(membre)
    
    db.session.commit()
    print("Base de données initialisée avec succès avec des données de test!")


# Context processor pour les variables globales
@app.context_processor
def inject_globals():
    """Injecte des variables globales dans tous les templates"""
    from datetime import datetime
    return {
        'current_year': datetime.now().year
    }


if __name__ == '__main__':
    app.run(debug=True)
