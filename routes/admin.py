from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from models import (
    User, District, EPS, Affection, Edition,
    FicheJournaliere, LigneConsultation, ServiceDiagnostic, Completude
)
from extensions import db

admin_bp = Blueprint('admin', __name__)
PERIODES = ['J-2', 'J-1', 'J', 'J+1', 'J+2', 'J+3']


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Acces reserve aux administrateurs.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_edition_active():
    return Edition.query.filter_by(active=True).order_by(Edition.annee.desc()).first()


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    edition = get_edition_active()
    if not edition:
        return render_template('admin/dashboard.html', edition=None, stats={}, periodes=PERIODES)

    total_q = db.session.query(
        func.sum(LigneConsultation.cas_simples),
        func.sum(LigneConsultation.hospitalises),
        func.sum(LigneConsultation.evacues),
        func.sum(LigneConsultation.decedes)
    ).join(FicheJournaliere).filter(FicheJournaliere.edition_id == edition.id).first()

    total_simples = total_q[0] or 0
    total_hospit = total_q[1] or 0
    total_evacues = total_q[2] or 0
    total_decedes = total_q[3] or 0
    total_consultants = total_simples + total_hospit + total_evacues

    nb_eps = EPS.query.filter_by(actif=True).count()
    completude = []
    for p in PERIODES:
        nb = FicheJournaliere.query.filter_by(edition_id=edition.id, periode=p).count()
        completude.append({
            'periode': p,
            'nb_soumis': nb,
            'nb_attendus': nb_eps,
            'pct': round(nb / nb_eps * 100, 1) if nb_eps > 0 else 0
        })

    top_aff = db.session.query(
        Affection.libelle,
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).label('total')
    ).join(LigneConsultation).join(FicheJournaliere).filter(
        FicheJournaliere.edition_id == edition.id
    ).group_by(Affection.libelle).order_by(
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).desc()
    ).limit(10).all()

    fiches_recentes = FicheJournaliere.query.filter_by(
        edition_id=edition.id
    ).order_by(FicheJournaliere.date_saisie.desc()).limit(10).all()

    by_district = db.session.query(
        District.nom,
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).label('total')
    ).join(EPS, District.id == EPS.district_id).join(
        FicheJournaliere, EPS.id == FicheJournaliere.eps_id
    ).join(LigneConsultation).filter(
        FicheJournaliere.edition_id == edition.id
    ).group_by(District.nom).order_by(
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).desc()
    ).all()

    mpe = db.session.query(
        Affection.libelle,
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).label('total')
    ).join(LigneConsultation).join(FicheJournaliere).filter(
        FicheJournaliere.edition_id == edition.id,
        Affection.is_mpe == True
    ).group_by(Affection.libelle).all()

    stats = {
        'total_consultants': total_consultants,
        'total_simples': total_simples,
        'total_hospit': total_hospit,
        'total_evacues': total_evacues,
        'total_decedes': total_decedes,
        'completude': completude,
        'top_affections': top_aff,
        'by_district': by_district,
        'mpe': mpe,
        'fiches_recentes': fiches_recentes,
        'nb_eps': nb_eps,
        'nb_users': User.query.filter_by(actif=True).count(),
    }

    return render_template('admin/dashboard.html', edition=edition, stats=stats, periodes=PERIODES)


@admin_bp.route('/eps')
@login_required
@admin_required
def liste_eps():
    districts = District.query.order_by(District.ordre).all()
    eps_list = EPS.query.join(District).order_by(District.ordre, EPS.ordre).all()
    return render_template('admin/eps.html', eps_list=eps_list, districts=districts)


@admin_bp.route('/eps/nouveau', methods=['GET', 'POST'])
@login_required
@admin_required
def nouveau_eps():
    districts = District.query.order_by(District.ordre).all()
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip().upper()
        type_eps = request.form.get('type_eps', 'poste_sante')
        district_id = request.form.get('district_id')
        responsable = request.form.get('responsable', '').strip()
        telephone = request.form.get('telephone', '').strip()
        code = request.form.get('code', '').strip().upper()
        if not nom or not district_id:
            flash('Nom et district sont obligatoires.', 'danger')
        elif EPS.query.filter_by(nom=nom).first():
            flash('Un EPS avec ce nom existe deja.', 'warning')
        else:
            eps = EPS(nom=nom, type_eps=type_eps, district_id=int(district_id),
                      responsable=responsable, telephone=telephone, code=code or None)
            db.session.add(eps)
            db.session.commit()
            flash('EPS cree avec succes.', 'success')
            return redirect(url_for('admin.liste_eps'))
    return render_template('admin/eps_form.html', eps=None, districts=districts, action='Creer')


@admin_bp.route('/eps/<int:eps_id>/modifier', methods=['GET', 'POST'])
@login_required
@admin_required
def modifier_eps(eps_id):
    eps = db.session.get(EPS, eps_id)
    if not eps:
        flash('EPS introuvable.', 'danger')
        return redirect(url_for('admin.liste_eps'))
    districts = District.query.order_by(District.ordre).all()
    if request.method == 'POST':
        eps.nom = request.form.get('nom', '').strip().upper()
        eps.type_eps = request.form.get('type_eps', 'poste_sante')
        eps.district_id = int(request.form.get('district_id'))
        eps.responsable = request.form.get('responsable', '').strip()
        eps.telephone = request.form.get('telephone', '').strip()
        eps.code = request.form.get('code', '').strip().upper() or None
        eps.actif = bool(request.form.get('actif'))
        db.session.commit()
        flash('EPS modifie.', 'success')
        return redirect(url_for('admin.liste_eps'))
    return render_template('admin/eps_form.html', eps=eps, districts=districts, action='Modifier')


@admin_bp.route('/utilisateurs')
@login_required
@admin_required
def liste_utilisateurs():
    users = User.query.order_by(User.role, User.username).all()
    return render_template('admin/utilisateurs.html', users=users)


@admin_bp.route('/utilisateurs/nouveau', methods=['GET', 'POST'])
@login_required
@admin_required
def nouveau_utilisateur():
    eps_list = EPS.query.filter_by(actif=True).order_by(EPS.nom).all()
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '')
        role = request.form.get('role', 'responsable')
        nom_complet = request.form.get('nom_complet', '').strip()
        telephone = request.form.get('telephone', '').strip()
        eps_id = request.form.get('eps_id') or None
        if not username or not password:
            flash('Identifiant et mot de passe obligatoires.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash("Identifiant deja utilise.", 'warning')
        elif len(password) < 6:
            flash('Mot de passe trop court (min 6 caracteres).', 'danger')
        else:
            user = User(username=username, email=email, role=role,
                        nom_complet=nom_complet, telephone=telephone,
                        eps_id=int(eps_id) if eps_id else None)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Utilisateur cree.', 'success')
            return redirect(url_for('admin.liste_utilisateurs'))
    return render_template('admin/user_form.html', user=None, eps_list=eps_list, action='Creer')


@admin_bp.route('/utilisateurs/<int:user_id>/modifier', methods=['GET', 'POST'])
@login_required
@admin_required
def modifier_utilisateur(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('admin.liste_utilisateurs'))
    eps_list = EPS.query.filter_by(actif=True).order_by(EPS.nom).all()
    if request.method == 'POST':
        user.email = request.form.get('email', '').strip() or None
        user.role = request.form.get('role', 'responsable')
        user.nom_complet = request.form.get('nom_complet', '').strip()
        user.telephone = request.form.get('telephone', '').strip()
        eps_id = request.form.get('eps_id')
        user.eps_id = int(eps_id) if eps_id else None
        user.actif = bool(request.form.get('actif'))
        new_pw = request.form.get('new_password', '').strip()
        if new_pw:
            if len(new_pw) < 6:
                flash('Mot de passe trop court.', 'danger')
                return render_template('admin/user_form.html', user=user, eps_list=eps_list, action='Modifier')
            user.set_password(new_pw)
        db.session.commit()
        flash('Utilisateur modifie.', 'success')
        return redirect(url_for('admin.liste_utilisateurs'))
    return render_template('admin/user_form.html', user=user, eps_list=eps_list, action='Modifier')


@admin_bp.route('/editions')
@login_required
@admin_required
def liste_editions():
    editions = Edition.query.order_by(Edition.annee.desc()).all()
    return render_template('admin/editions.html', editions=editions)


@admin_bp.route('/editions/nouvelle', methods=['GET', 'POST'])
@login_required
@admin_required
def nouvelle_edition():
    if request.method == 'POST':
        annee_str = request.form.get('annee', '')
        libelle = request.form.get('libelle', '').strip()
        active = bool(request.form.get('active'))
        if not annee_str:
            flash("L'annee est obligatoire.", 'danger')
        elif Edition.query.filter_by(annee=int(annee_str)).first():
            flash("Cette edition existe deja.", 'warning')
        else:
            if active:
                Edition.query.update({'active': False})
            ed = Edition(annee=int(annee_str), libelle=libelle, active=active)
            db.session.add(ed)
            db.session.commit()
            flash('Edition creee.', 'success')
            return redirect(url_for('admin.liste_editions'))
    return render_template('admin/edition_form.html', edition=None)


@admin_bp.route('/editions/<int:ed_id>/activer', methods=['POST'])
@login_required
@admin_required
def activer_edition(ed_id):
    Edition.query.update({'active': False})
    ed = db.session.get(Edition, ed_id)
    if ed:
        ed.active = True
        db.session.commit()
        flash(f'Edition {ed.annee} activee.', 'success')
    return redirect(url_for('admin.liste_editions'))


@admin_bp.route('/rapports')
@login_required
@admin_required
def rapports():
    edition = get_edition_active()
    selected_periode = request.args.get('periode', '')
    selected_district = request.args.get('district', '')
    districts = District.query.order_by(District.ordre).all()

    query = db.session.query(
        Affection.numero,
        Affection.libelle,
        Affection.categorie,
        func.sum(LigneConsultation.cas_simples).label('simples'),
        func.sum(LigneConsultation.hospitalises).label('hospit'),
        func.sum(LigneConsultation.evacues).label('evacues'),
        func.sum(LigneConsultation.decedes).label('decedes'),
    ).join(LigneConsultation).join(FicheJournaliere)

    if edition:
        query = query.filter(FicheJournaliere.edition_id == edition.id)
    if selected_periode:
        query = query.filter(FicheJournaliere.periode == selected_periode)
    if selected_district:
        query = query.join(EPS, FicheJournaliere.eps_id == EPS.id).filter(
            EPS.district_id == int(selected_district)
        )

    data = query.group_by(
        Affection.numero, Affection.libelle, Affection.categorie
    ).order_by(Affection.numero).all()

    rapport = []
    for row in data:
        total = (row.simples or 0) + (row.hospit or 0) + (row.evacues or 0)
        rapport.append({
            'numero': row.numero,
            'libelle': row.libelle,
            'categorie': row.categorie,
            'simples': row.simples or 0,
            'hospit': row.hospit or 0,
            'evacues': row.evacues or 0,
            'decedes': row.decedes or 0,
            'total': total
        })

    return render_template('admin/rapports.html',
                           edition=edition,
                           rapport=rapport,
                           periodes=PERIODES,
                           districts=districts,
                           selected_periode=selected_periode,
                           selected_district=selected_district)


@admin_bp.route('/completude')
@login_required
@admin_required
def completude():
    edition = get_edition_active()
    selected_periode = request.args.get('periode', PERIODES[0])
    eps_list = EPS.query.filter_by(actif=True).join(District).order_by(District.ordre, EPS.ordre).all()

    soumis = set()
    if edition:
        fiches = FicheJournaliere.query.filter_by(
            edition_id=edition.id, periode=selected_periode
        ).all()
        soumis = {f.eps_id for f in fiches}

    data = []
    for eps in eps_list:
        data.append({
            'eps': eps,
            'soumis': eps.id in soumis,
        })

    nb_soumis = len(soumis)
    nb_total = len(eps_list)
    pct = round(nb_soumis / nb_total * 100, 1) if nb_total > 0 else 0

    return render_template('admin/completude.html',
                           edition=edition,
                           data=data,
                           periodes=PERIODES,
                           selected_periode=selected_periode,
                           nb_soumis=nb_soumis,
                           nb_total=nb_total,
                           pct=pct)


@admin_bp.route('/saisie-directe/<int:eps_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def saisie_directe(eps_id):
    """L'admin peut saisir/modifier les données de n'importe quel EPS."""
    edition = get_edition_active()
    eps = db.session.get(EPS, eps_id)
    if not eps or not edition:
        flash('EPS ou edition introuvable.', 'danger')
        return redirect(url_for('admin.completude'))

    periode = request.args.get('periode', PERIODES[2])
    affections = Affection.query.filter_by(actif=True).order_by(Affection.numero).all()

    fiche = FicheJournaliere.query.filter_by(
        eps_id=eps_id, edition_id=edition.id, periode=periode
    ).first()

    lignes_map = {}
    if fiche:
        for l in fiche.lignes:
            lignes_map[l.affection_id] = l

    if request.method == 'POST':
        periode = request.form.get('periode', periode)
        observations = request.form.get('observations', '')

        fiche = FicheJournaliere.query.filter_by(
            eps_id=eps_id, edition_id=edition.id, periode=periode
        ).first()
        if not fiche:
            fiche = FicheJournaliere(
                eps_id=eps_id, edition_id=edition.id,
                periode=periode, saisi_par=current_user.nom_complet or current_user.username
            )
            db.session.add(fiche)
            db.session.flush()

        fiche.observations = observations
        fiche.date_saisie = __import__('datetime').datetime.utcnow()

        for aff in affections:
            simples = int(request.form.get(f'simples_{aff.id}', 0) or 0)
            hospit = int(request.form.get(f'hospit_{aff.id}', 0) or 0)
            evacues = int(request.form.get(f'evacues_{aff.id}', 0) or 0)
            decedes = int(request.form.get(f'decedes_{aff.id}', 0) or 0)

            ligne = LigneConsultation.query.filter_by(
                fiche_id=fiche.id, affection_id=aff.id
            ).first()
            if not ligne:
                ligne = LigneConsultation(fiche_id=fiche.id, affection_id=aff.id)
                db.session.add(ligne)
            ligne.cas_simples = simples
            ligne.hospitalises = hospit
            ligne.evacues = evacues
            ligne.decedes = decedes

        db.session.commit()
        flash('Donnees enregistrees.', 'success')
        return redirect(url_for('admin.completude', periode=periode))

    return render_template('admin/saisie_directe.html',
                           eps=eps, edition=edition, fiche=fiche,
                           affections=affections, lignes_map=lignes_map,
                           periodes=PERIODES, selected_periode=periode)


@admin_bp.route('/api/completude-data')
@login_required
@admin_required
def api_completude_data():
    edition = get_edition_active()
    if not edition:
        return jsonify({})
    result = {}
    nb_eps = EPS.query.filter_by(actif=True).count()
    for p in PERIODES:
        nb = FicheJournaliere.query.filter_by(edition_id=edition.id, periode=p).count()
        result[p] = {'nb': nb, 'total': nb_eps,
                     'pct': round(nb / nb_eps * 100, 1) if nb_eps > 0 else 0}
    return jsonify(result)