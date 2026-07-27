from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from sqlalchemy import func
from models import (
    EPS, Affection, Edition,
    FicheJournaliere, LigneConsultation, ServiceDiagnostic
)
from extensions import db

user_bp = Blueprint('user', __name__)
PERIODES = ['J-2', 'J-1', 'J', 'J+1', 'J+2', 'J+3']


def get_edition_active():
    return Edition.query.filter_by(active=True).order_by(Edition.annee.desc()).first()


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.eps_id and not current_user.is_admin:
            flash("Votre compte n'est pas associe a un EPS.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    edition = get_edition_active()
    eps = current_user.eps
    if not eps:
        flash("Aucun EPS associe a votre compte.", "warning")
        return redirect(url_for('auth.login'))

    fiches = []
    if edition:
        fiches = FicheJournaliere.query.filter_by(
            eps_id=eps.id, edition_id=edition.id
        ).order_by(FicheJournaliere.periode).all()

    periodes_soumises = {f.periode for f in fiches}

    summary = []
    for p in PERIODES:
        fiche = next((f for f in fiches if f.periode == p), None)
        total = fiche.get_total_consultants() if fiche else 0
        decedes = fiche.get_total_decedes() if fiche else 0
        summary.append({
            'periode': p,
            'soumis': p in periodes_soumises,
            'total': total,
            'decedes': decedes,
            'fiche_id': fiche.id if fiche else None
        })

    return render_template('user/dashboard.html',
                           eps=eps, edition=edition,
                           summary=summary,
                           periodes=PERIODES)


@user_bp.route('/saisie', methods=['GET', 'POST'])
@login_required
@user_required
def saisie():
    edition = get_edition_active()
    eps = current_user.eps
    if not eps or not edition:
        flash("Edition inactive ou EPS non configure.", "warning")
        return redirect(url_for('user.dashboard'))

    periode = request.args.get('periode', PERIODES[2])
    if periode not in PERIODES:
        periode = PERIODES[2]

    affections = Affection.query.filter_by(actif=True).order_by(Affection.numero).all()

    fiche = FicheJournaliere.query.filter_by(
        eps_id=eps.id, edition_id=edition.id, periode=periode
    ).first()

    lignes_map = {}
    if fiche:
        for ligne in fiche.lignes:
            lignes_map[ligne.affection_id] = ligne

    if request.method == 'POST':
        periode_post = request.form.get('periode', periode)
        if periode_post not in PERIODES:
            periode_post = PERIODES[2]
        observations = request.form.get('observations', '')

        fiche = FicheJournaliere.query.filter_by(
            eps_id=eps.id, edition_id=edition.id, periode=periode_post
        ).first()

        if not fiche:
            fiche = FicheJournaliere(
                eps_id=eps.id,
                edition_id=edition.id,
                periode=periode_post,
                saisi_par=current_user.nom_complet or current_user.username,
                statut='soumis'
            )
            db.session.add(fiche)
            db.session.flush()
        else:
            fiche.date_saisie = datetime.utcnow()

        fiche.observations = observations

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

            ligne.cas_simples = max(0, simples)
            ligne.hospitalises = max(0, hospit)
            ligne.evacues = max(0, evacues)
            ligne.decedes = max(0, decedes)

        db.session.commit()
        flash(f'Fiche {periode_post} enregistree avec succes.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/saisie.html',
                           eps=eps, edition=edition,
                           fiche=fiche, affections=affections,
                           lignes_map=lignes_map,
                           periodes=PERIODES,
                           selected_periode=periode)


@user_bp.route('/mes-fiches')
@login_required
@user_required
def mes_fiches():
    edition = get_edition_active()
    eps = current_user.eps
    fiches = []
    if eps and edition:
        fiches = FicheJournaliere.query.filter_by(
            eps_id=eps.id, edition_id=edition.id
        ).order_by(FicheJournaliere.periode).all()
    return render_template('user/mes_fiches.html', eps=eps, edition=edition, fiches=fiches)


@user_bp.route('/fiche/<int:fiche_id>')
@login_required
@user_required
def voir_fiche(fiche_id):
    fiche = db.session.get(FicheJournaliere, fiche_id)
    if not fiche:
        abort(404)

    # Strict ownership check — un non-admin ne peut voir que les fiches de son EPS
    if not current_user.is_admin and fiche.eps_id != current_user.eps_id:
        abort(403)

    affections = Affection.query.filter_by(actif=True).order_by(Affection.numero).all()
    lignes_map = {l.affection_id: l for l in fiche.lignes}

    return render_template('user/voir_fiche.html',
                           fiche=fiche,
                           affections=affections,
                           lignes_map=lignes_map)


# ─────────────────────────────────────────────────────────────────────────────
# STATISTIQUES — filtrées par EPS (structure de l'utilisateur)
# ─────────────────────────────────────────────────────────────────────────────
@user_bp.route('/mes-stats')
@login_required
@user_required
def mes_stats():
    edition = get_edition_active()
    eps = current_user.eps
    if not eps:
        flash("Aucun EPS associe a votre compte.", "warning")
        return redirect(url_for('user.dashboard'))

    total_simples = total_hospit = total_evacues = total_decedes = 0
    total_consultants = 0
    periode_data = []
    top_affections = []
    mpe_data = []

    if edition:
        # Totaux globaux pour cet EPS
        result = db.session.query(
            func.sum(LigneConsultation.cas_simples),
            func.sum(LigneConsultation.hospitalises),
            func.sum(LigneConsultation.evacues),
            func.sum(LigneConsultation.decedes)
        ).join(FicheJournaliere).filter(
            FicheJournaliere.eps_id == eps.id,
            FicheJournaliere.edition_id == edition.id
        ).first()

        total_simples  = result[0] or 0
        total_hospit   = result[1] or 0
        total_evacues  = result[2] or 0
        total_decedes  = result[3] or 0
        total_consultants = total_simples + total_hospit + total_evacues

        # Données par période pour cet EPS
        for p in PERIODES:
            q = db.session.query(
                func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues),
                func.sum(LigneConsultation.decedes)
            ).join(FicheJournaliere).filter(
                FicheJournaliere.eps_id == eps.id,
                FicheJournaliere.edition_id == edition.id,
                FicheJournaliere.periode == p
            ).first()
            total_p   = q[0] or 0
            decedes_p = q[1] or 0
            fiche_p = FicheJournaliere.query.filter_by(
                eps_id=eps.id, edition_id=edition.id, periode=p
            ).first()
            periode_data.append({
                'periode': p,
                'total': total_p,
                'decedes': decedes_p,
                'soumis': fiche_p is not None,
                'fiche_id': fiche_p.id if fiche_p else None
            })

        # Top 10 affections pour cet EPS
        top_affections = db.session.query(
            Affection.libelle,
            func.sum(
                LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues
            ).label('total')
        ).join(LigneConsultation).join(FicheJournaliere).filter(
            FicheJournaliere.eps_id == eps.id,
            FicheJournaliere.edition_id == edition.id
        ).group_by(Affection.libelle).order_by(
            func.sum(
                LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues
            ).desc()
        ).limit(10).all()

        # MPE pour cet EPS
        mpe_data = db.session.query(
            Affection.libelle,
            func.sum(
                LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues
            ).label('total'),
            func.sum(LigneConsultation.decedes).label('decedes')
        ).join(LigneConsultation).join(FicheJournaliere).filter(
            FicheJournaliere.eps_id == eps.id,
            FicheJournaliere.edition_id == edition.id,
            Affection.is_mpe == True
        ).group_by(Affection.libelle).all()

    stats_data = {
        'total_consultants': total_consultants,
        'total_simples': total_simples,
        'total_hospit': total_hospit,
        'total_evacues': total_evacues,
        'total_decedes': total_decedes,
        'top_affections': top_affections,
        'periode_data': periode_data,
        'mpe_data': mpe_data,
    }

    return render_template('user/mes_stats.html',
                           eps=eps,
                           edition=edition,
                           stats=stats_data,
                           periodes=PERIODES)
