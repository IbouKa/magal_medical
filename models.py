"""
Modèles de données - Gestion médicale Grand Magal de Touba
Région Médicale de Diourbel
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager


# ─────────────────────────────────────────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='responsable')
    nom_complet = db.Column(db.String(150), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    eps_id = db.Column(db.Integer, db.ForeignKey('eps.id'), nullable=True)

    eps = db.relationship('EPS', backref='users', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─────────────────────────────────────────────────────────────────────────────
# DISTRICT
# ─────────────────────────────────────────────────────────────────────────────
class District(db.Model):
    __tablename__ = 'districts'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    ordre = db.Column(db.Integer, default=0)
    actif = db.Column(db.Boolean, default=True)

    eps_list = db.relationship('EPS', backref='district', lazy=True)

    def __repr__(self):
        return f'<District {self.nom}>'


# ─────────────────────────────────────────────────────────────────────────────
# EPS (Etablissement de Prestation de Soins)
# ─────────────────────────────────────────────────────────────────────────────
class EPS(db.Model):
    __tablename__ = 'eps'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=True)
    nom = db.Column(db.String(150), nullable=False)
    type_eps = db.Column(db.String(30), nullable=False, default='poste_sante')
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    responsable = db.Column(db.String(150), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    actif = db.Column(db.Boolean, default=True)
    ordre = db.Column(db.Integer, default=0)

    fiches = db.relationship('FicheJournaliere', backref='eps', lazy=True,
                              cascade='all, delete-orphan')
    services_diag = db.relationship('ServiceDiagnostic', backref='eps', lazy=True,
                                     cascade='all, delete-orphan')

    @property
    def type_label(self):
        labels = {
            'poste_sante': 'Poste de Santé',
            'centre_sante': 'Centre de Santé',
            'hopital': 'Hôpital',
            'district': 'District Sanitaire'
        }
        return labels.get(self.type_eps, self.type_eps)

    @property
    def prefixe(self):
        if self.type_eps == 'poste_sante':
            return 'PS'
        elif self.type_eps == 'centre_sante':
            return 'CS'
        elif self.type_eps == 'hopital':
            return 'Hôpital'
        return 'DS'

    def __repr__(self):
        return f'<EPS {self.nom}>'


# ─────────────────────────────────────────────────────────────────────────────
# AFFECTION
# ─────────────────────────────────────────────────────────────────────────────
class Affection(db.Model):
    __tablename__ = 'affections'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    libelle = db.Column(db.String(200), nullable=False)
    categorie = db.Column(db.String(50), default='autres')
    is_mpe = db.Column(db.Boolean, default=False)
    actif = db.Column(db.Boolean, default=True)

    lignes = db.relationship('LigneConsultation', backref='affection', lazy=True)

    def __repr__(self):
        return f'<Affection {self.numero}. {self.libelle}>'


# ─────────────────────────────────────────────────────────────────────────────
# EDITION
# ─────────────────────────────────────────────────────────────────────────────
class Edition(db.Model):
    __tablename__ = 'editions'

    id = db.Column(db.Integer, primary_key=True)
    annee = db.Column(db.Integer, unique=True, nullable=False)
    libelle = db.Column(db.String(100), nullable=True)
    date_magal = db.Column(db.Date, nullable=True)
    active = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    fiches = db.relationship('FicheJournaliere', backref='edition', lazy=True)
    services_diag = db.relationship('ServiceDiagnostic', backref='edition', lazy=True)

    def __repr__(self):
        return f'<Edition {self.annee}>'


# ─────────────────────────────────────────────────────────────────────────────
# FICHE JOURNALIERE
# ─────────────────────────────────────────────────────────────────────────────
class FicheJournaliere(db.Model):
    __tablename__ = 'fiches_journalieres'

    id = db.Column(db.Integer, primary_key=True)
    eps_id = db.Column(db.Integer, db.ForeignKey('eps.id'), nullable=False)
    edition_id = db.Column(db.Integer, db.ForeignKey('editions.id'), nullable=False)
    # Période: J-2, J-1, J, J+1, J+2, J+3
    periode = db.Column(db.String(10), nullable=False)
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    saisi_par = db.Column(db.String(100), nullable=True)
    observations = db.Column(db.Text, nullable=True)
    # Statut: brouillon, soumis, valide
    statut = db.Column(db.String(20), default='soumis')

    # Contrainte unique par EPS + Edition + Période
    __table_args__ = (
        db.UniqueConstraint('eps_id', 'edition_id', 'periode', name='uq_fiche_eps_edition_periode'),
    )

    lignes = db.relationship('LigneConsultation', backref='fiche', lazy=True,
                              cascade='all, delete-orphan')

    def get_total_consultants(self):
        total = 0
        for l in self.lignes:
            total += (l.cas_simples or 0) + (l.hospitalises or 0) + (l.evacues or 0)
        return total

    def get_total_decedes(self):
        return sum(l.decedes or 0 for l in self.lignes)

    def get_total_hospitalises(self):
        return sum(l.hospitalises or 0 for l in self.lignes)

    def get_total_evacues(self):
        return sum(l.evacues or 0 for l in self.lignes)

    def __repr__(self):
        return f'<Fiche {self.eps_id} {self.periode}>'


# ─────────────────────────────────────────────────────────────────────────────
# LIGNE CONSULTATION (détail par affection)
# ─────────────────────────────────────────────────────────────────────────────
class LigneConsultation(db.Model):
    __tablename__ = 'lignes_consultation'

    id = db.Column(db.Integer, primary_key=True)
    fiche_id = db.Column(db.Integer, db.ForeignKey('fiches_journalieres.id'), nullable=False)
    affection_id = db.Column(db.Integer, db.ForeignKey('affections.id'), nullable=False)

    # Données principales
    cas_simples = db.Column(db.Integer, default=0)
    hospitalises = db.Column(db.Integer, default=0)
    evacues = db.Column(db.Integer, default=0)
    decedes = db.Column(db.Integer, default=0)

    @property
    def total(self):
        return (self.cas_simples or 0) + (self.hospitalises or 0) + (self.evacues or 0)

    def __repr__(self):
        return f'<Ligne {self.affection_id}: {self.total}>'


# ─────────────────────────────────────────────────────────────────────────────
# SERVICE D'AIDE AU DIAGNOSTIC
# ─────────────────────────────────────────────────────────────────────────────
class ServiceDiagnostic(db.Model):
    __tablename__ = 'services_diagnostic'

    id = db.Column(db.Integer, primary_key=True)
    eps_id = db.Column(db.Integer, db.ForeignKey('eps.id'), nullable=False)
    edition_id = db.Column(db.Integer, db.ForeignKey('editions.id'), nullable=False)
    periode = db.Column(db.String(10), nullable=False)
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow)

    # Laboratoire
    labo_nb_malades = db.Column(db.Integer, default=0)
    labo_nb_examens = db.Column(db.Integer, default=0)
    labo_poches_sang = db.Column(db.Integer, default=0)

    # Radiologie
    radio_nb_malades = db.Column(db.Integer, default=0)
    radio_nb_films = db.Column(db.Integer, default=0)
    radio_nb_examens = db.Column(db.Integer, default=0)

    # Echographie
    echo_nb_malades = db.Column(db.Integer, default=0)
    echo_nb_films = db.Column(db.Integer, default=0)

    # Scanner
    scanner_nb_malades = db.Column(db.Integer, default=0)
    scanner_nb_films = db.Column(db.Integer, default=0)

    # Bloc opératoire
    bloc_nb_interventions = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('eps_id', 'edition_id', 'periode', name='uq_svc_eps_edition_periode'),
    )

    def __repr__(self):
        return f'<ServiceDiag {self.eps_id} {self.periode}>'


# ─────────────────────────────────────────────────────────────────────────────
# COMPLETUDE (Tracking des soumissions)
# ─────────────────────────────────────────────────────────────────────────────
class Completude(db.Model):
    __tablename__ = 'completude'

    id = db.Column(db.Integer, primary_key=True)
    eps_id = db.Column(db.Integer, db.ForeignKey('eps.id'), nullable=False)
    edition_id = db.Column(db.Integer, db.ForeignKey('editions.id'), nullable=False)
    periode = db.Column(db.String(10), nullable=False)
    envoye = db.Column(db.Boolean, default=False)
    raison_non_envoi = db.Column(db.String(200), nullable=True)
    date_envoi = db.Column(db.DateTime, nullable=True)

    eps_rel = db.relationship('EPS', backref='completudes', lazy=True)
    edition_rel = db.relationship('Edition', backref='completudes', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('eps_id', 'edition_id', 'periode', name='uq_comp_eps_edition_periode'),
    )


# ─────────────────────────────────────────────────────────────────────────────
# IMPORT LOG (historique des imports Excel)
# ─────────────────────────────────────────────────────────────────────────────
class ImportLog(db.Model):
    __tablename__ = 'import_logs'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=True)
    date_import = db.Column(db.DateTime, default=datetime.utcnow)
    fait_par = db.Column(db.String(100), nullable=True)
    nb_created = db.Column(db.Integer, default=0)
    nb_updated = db.Column(db.Integer, default=0)
    nb_skipped = db.Column(db.Integer, default=0)
    nb_total = db.Column(db.Integer, default=0)
    statut = db.Column(db.String(20), default='ok')  # ok / erreur

    lignes = db.relationship('ImportLogLigne', backref='import_log', lazy=True,
                              cascade='all, delete-orphan',
                              order_by='ImportLogLigne.row_num')

    def __repr__(self):
        return f'<ImportLog {self.id} {self.filename}>'


class ImportLogLigne(db.Model):
    __tablename__ = 'import_log_lignes'

    id = db.Column(db.Integer, primary_key=True)
    import_log_id = db.Column(db.Integer, db.ForeignKey('import_logs.id'), nullable=False)
    row_num = db.Column(db.Integer, nullable=False)
    # statut : ok | cree | mis_a_jour | ignore | avertissement | erreur
    statut = db.Column(db.String(20), nullable=False, default='ok')
    eps_nom = db.Column(db.String(150), nullable=True)
    periode = db.Column(db.String(10), nullable=True)
    affection = db.Column(db.String(200), nullable=True)
    edition_annee = db.Column(db.Integer, nullable=True)
    message = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<ImportLogLigne row={self.row_num} statut={self.statut}>'


# ─────────────────────────────────────────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────────────────────────────────────────
def seed_data():
    """Initialise les données de référence si elles n'existent pas."""

    # Edition active
    if not Edition.query.filter_by(annee=2025).first():
        edition = Edition(
            annee=2025,
            libelle='Grand Magal de Touba Edition 2025',
            active=True
        )
        db.session.add(edition)
        db.session.flush()

    edition = Edition.query.filter_by(annee=2025).first()

    # Districts
    districts_data = [
        ('HOPITAL NDAMATOU', 1),
        ('DISTRICT BAMBEY', 2),
        ('DISTRICT DIOURBEL', 3),
        ('HR DIOURBEL', 4),
        ('DISTRICT MBACKE', 5),
        ('HOP MATLABOUL FAWZAINY', 6),
        ('DISTRICT DAROU MOUSTY', 7),
        ('DISTRICT TOUBA', 8),
        ('HOPITAL CH KHADIM', 9),
        ('DISTRICT GOSSAS', 10),
    ]

    districts_map = {}
    for nom, ordre in districts_data:
        d = District.query.filter_by(nom=nom).first()
        if not d:
            d = District(nom=nom, ordre=ordre)
            db.session.add(d)
            db.session.flush()
        districts_map[nom] = d

    # EPS par district
    eps_data = [
        # (nom, type_eps, district_nom, ordre)
        # DISTRICT TOUBA
        ('PS KHAIRA', 'poste_sante', 'DISTRICT TOUBA', 1),
        ('CS DAROU MARNANE', 'centre_sante', 'DISTRICT TOUBA', 2),
        ('PS DAROU MINAME', 'poste_sante', 'DISTRICT TOUBA', 3),
        ('CS DAROU TANSIL', 'centre_sante', 'DISTRICT TOUBA', 4),
        ('PS GUEDE BOUSSO', 'poste_sante', 'DISTRICT TOUBA', 5),
        ('PS MADIYANA 1', 'poste_sante', 'DISTRICT TOUBA', 6),
        ('PS MADIYANA 2', 'poste_sante', 'DISTRICT TOUBA', 7),
        ('CS KEUR NIANG', 'centre_sante', 'DISTRICT TOUBA', 8),
        ('PS GOUYE MBINDE', 'poste_sante', 'DISTRICT TOUBA', 9),
        ('PS NDINDY', 'poste_sante', 'DISTRICT TOUBA', 10),
        ('CS S SALIOU 28', 'centre_sante', 'DISTRICT TOUBA', 11),
        ('CS DAROU KHOUDOSS', 'centre_sante', 'DISTRICT TOUBA', 12),
        ('CS NDINDY', 'centre_sante', 'DISTRICT TOUBA', 13),
        ('PS TINDODY', 'poste_sante', 'DISTRICT TOUBA', 14),
        ('PS DAROU RAHMANE', 'poste_sante', 'DISTRICT TOUBA', 15),
        ('PS MBOUSSOBE', 'poste_sante', 'DISTRICT TOUBA', 16),
        ('PS OUMOUL KHOURA', 'poste_sante', 'DISTRICT TOUBA', 17),
        ('PS SAHM', 'poste_sante', 'DISTRICT TOUBA', 18),
        ('PS GUEDE KAW', 'poste_sante', 'DISTRICT TOUBA', 19),
        ('PS THIAWENE', 'poste_sante', 'DISTRICT TOUBA', 20),
        ('PS HELIPORT', 'poste_sante', 'DISTRICT TOUBA', 21),
        ('PS SOURAH', 'poste_sante', 'DISTRICT TOUBA', 22),
        ('PS BAGDAD', 'poste_sante', 'DISTRICT TOUBA', 23),
        ('PS LANSARR', 'poste_sante', 'DISTRICT TOUBA', 24),
        ('TOUBA HLM', 'poste_sante', 'DISTRICT TOUBA', 25),
        ('PS DAROU KARIM', 'poste_sante', 'DISTRICT TOUBA', 26),
        ('PS DAROU KHOUDOSS', 'poste_sante', 'DISTRICT TOUBA', 27),
        ('PS KEUR GOL', 'poste_sante', 'DISTRICT TOUBA', 28),
        ('PS BOBOREL', 'poste_sante', 'DISTRICT TOUBA', 29),
        ('PS DIALYBATOU', 'poste_sante', 'DISTRICT TOUBA', 30),
        # HOPITAL NDAMATOU
        ('HOPITAL NDAMATOU', 'hopital', 'HOPITAL NDAMATOU', 1),
        # HOPITAL CH KHADIM
        ('HOPITAL CH KHADIM', 'hopital', 'HOPITAL CH KHADIM', 1),
        # HOP MATLABOUL FAWZAINY
        ('HOP MATLABOUL FAWZAINY', 'hopital', 'HOP MATLABOUL FAWZAINY', 1),
        # HR DIOURBEL
        ('HR DIOURBEL', 'hopital', 'HR DIOURBEL', 1),
        # DISTRICT BAMBEY
        ('DISTRICT BAMBEY', 'district', 'DISTRICT BAMBEY', 1),
        # DISTRICT DIOURBEL
        ('DISTRICT DIOURBEL', 'district', 'DISTRICT DIOURBEL', 1),
        # DISTRICT MBACKE
        ('DISTRICT MBACKE', 'district', 'DISTRICT MBACKE', 1),
        # DISTRICT DAROU MOUSTY
        ('DISTRICT DAROU MOUSTY', 'district', 'DISTRICT DAROU MOUSTY', 1),
        # DISTRICT GOSSAS
        ('DISTRICT GOSSAS', 'district', 'DISTRICT GOSSAS', 1),
    ]

    eps_map = {}
    for i, (nom, type_eps, district_nom, ordre) in enumerate(eps_data):
        existing = EPS.query.filter_by(nom=nom).first()
        if not existing:
            district = districts_map.get(district_nom)
            if district:
                code = f'EPS{str(i+1).zfill(3)}'
                eps = EPS(
                    nom=nom,
                    code=code,
                    type_eps=type_eps,
                    district_id=district.id,
                    ordre=ordre
                )
                db.session.add(eps)
                db.session.flush()
                eps_map[nom] = eps
        else:
            eps_map[nom] = existing

    # Affections (depuis la BD Excel)
    affections_data = [
        (1, 'Coups et blessures', 'traumatisme', False),
        (2, 'Accidents domestiques', 'traumatisme', False),
        (3, 'Accidents circulation auto', 'traumatisme', False),
        (4, 'Accidents circulation Moto', 'traumatisme', False),
        (5, 'Accident circulation Charrette', 'traumatisme', False),
        (6, 'Accident voie Publique', 'traumatisme', False),
        (7, 'Accidents de travail', 'traumatisme', False),
        (8, 'Autres accidents', 'traumatisme', False),
        (9, 'Affections cardiovasculaires (HTA..)', 'cardiovasculaire', False),
        (10, 'Cas de Paludisme confirmé (TDR+)', 'infectieux', False),
        (11, 'Affections Respiratoires', 'respiratoire', False),
        (12, 'Gastroentérite / Intoxication', 'digestif', False),
        (13, 'Affection appareil digestif', 'digestif', False),
        (14, 'Affection buco dentaires', 'autres', False),
        (15, 'Affections ORL', 'autres', False),
        (16, "Affections de l'oeil et annexes", 'autres', False),
        (17, 'Gynéco obstétrique', 'gynaeco', False),
        (18, 'Affections uro-génitales', 'autres', False),
        (19, 'Affection dermatologiques', 'dermatologique', False),
        (20, 'Affections ostéo articulaires', 'autres', False),
        (21, 'Maladies chroniques (diabète, drépanocytose...)', 'chronique', False),
        (22, 'Affections neuropsychiatriques', 'autres', False),
        (23, 'Syndrome infectieux', 'infectieux', False),
        (24, 'Coups de chaleur (céphalée, vertige...)', 'autres', False),
        (25, 'Atteintes neuromusculaires (fatigue...)', 'autres', False),
        (26, 'Autres affections à préciser', 'autres', False),
        (27, 'Cas suspect de Rougeole', 'mpe', True),
        (28, 'Méningite (cas suspect)', 'mpe', True),
        (29, 'PFA (Paralysie Flasque Aiguë)', 'mpe', True),
        (30, 'Cas suspects de Choléra', 'mpe', True),
        (31, '(COVID-19) Cas Suspects', 'mpe', True),
        (32, '(COVID-19) Cas confirmés', 'mpe', True),
    ]

    for numero, libelle, categorie, is_mpe in affections_data:
        if not Affection.query.filter_by(numero=numero).first():
            aff = Affection(
                numero=numero,
                libelle=libelle,
                categorie=categorie,
                is_mpe=is_mpe
            )
            db.session.add(aff)

    # Utilisateurs par défaut
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@magal-sante.sn',
            role='admin',
            nom_complet='Administrateur Système',
            actif=True
        )
        admin.set_password('admin2025')
        db.session.add(admin)

    # Utilisateur démo pour PS KHAIRA
    ps_khaira = EPS.query.filter_by(nom='PS KHAIRA').first()
    if ps_khaira and not User.query.filter_by(username='ps_khaira').first():
        user = User(
            username='ps_khaira',
            email='ps.khaira@magal-sante.sn',
            role='responsable',
            nom_complet='Responsable PS KHAIRA',
            eps_id=ps_khaira.id,
            actif=True
        )
        user.set_password('khaira2025')
        db.session.add(user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Seed data error (peut être normal si déjà existant): {e}")