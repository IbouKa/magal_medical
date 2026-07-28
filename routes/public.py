from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import func
from models import (
    Edition, District, EPS, Affection,
    FicheJournaliere, LigneConsultation, ServiceDiagnostic, Completude
)
from extensions import db

public_bp = Blueprint('public', __name__)

PERIODES_ORDER = {'J-2': 0, 'J-1': 1, 'J': 2, 'J+1': 3, 'J+2': 4, 'J+3': 5}


def get_edition_active():
    return Edition.query.filter_by(active=True).order_by(Edition.annee.desc()).first()


@public_bp.route('/presentation')
def presentation():
    return render_template('public/presentation.html')


@public_bp.route('/')
def index():
    # Rediriger directement les non-admin vers leurs stats filtrées
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('user.mes_stats'))
    return redirect(url_for('public.stats'))


@public_bp.route('/statistiques')
def stats():
    # Rediriger les utilisateurs non-admin connectés vers leurs stats filtrées par EPS
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('user.mes_stats'))

    edition = get_edition_active()
    if not edition:
        return render_template('public/stats.html', edition=None, stats={})

    periodes = ['J-2', 'J-1', 'J', 'J+1', 'J+2', 'J+3']
    selected_periode = request.args.get('periode', '')
    selected_district = request.args.get('district', '')

    # Statistiques globales
    query = db.session.query(
        func.sum(LigneConsultation.cas_simples),
        func.sum(LigneConsultation.hospitalises),
        func.sum(LigneConsultation.evacues),
        func.sum(LigneConsultation.decedes)
    ).join(FicheJournaliere).filter(FicheJournaliere.edition_id == edition.id)

    if selected_periode:
        query = query.filter(FicheJournaliere.periode == selected_periode)

    if selected_district:
        query = query.join(EPS, FicheJournaliere.eps_id == EPS.id).filter(
            EPS.district_id == int(selected_district)
        )

    result = query.first()
    total_simples = result[0] or 0
    total_hospit = result[1] or 0
    total_evacues = result[2] or 0
    total_decedes = result[3] or 0
    total_consultants = total_simples + total_hospit + total_evacues

    # Top 10 affections
    top_aff_query = db.session.query(
        Affection.libelle,
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).label('total')
    ).join(LigneConsultation).join(FicheJournaliere).filter(
        FicheJournaliere.edition_id == edition.id
    )
    if selected_periode:
        top_aff_query = top_aff_query.filter(FicheJournaliere.periode == selected_periode)
    if selected_district:
        top_aff_query = top_aff_query.join(EPS, FicheJournaliere.eps_id == EPS.id).filter(
            EPS.district_id == int(selected_district)
        )
    top_affections = top_aff_query.group_by(Affection.libelle).order_by(func.sum(
        LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues
    ).desc()).limit(10).all()

    # Données par période
    periode_data = []
    for p in periodes:
        q = db.session.query(
            func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues)
        ).join(FicheJournaliere).filter(
            FicheJournaliere.edition_id == edition.id,
            FicheJournaliere.periode == p
        )
        if selected_district:
            q = q.join(EPS, FicheJournaliere.eps_id == EPS.id).filter(
                EPS.district_id == int(selected_district)
            )
        total_p = q.scalar() or 0
        periode_data.append({'periode': p, 'total': total_p})

    # Données par district
    district_data = db.session.query(
        District.nom,
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).label('total')
    ).join(EPS, District.id == EPS.district_id).join(
        FicheJournaliere, EPS.id == FicheJournaliere.eps_id
    ).join(LigneConsultation).filter(
        FicheJournaliere.edition_id == edition.id
    )
    if selected_periode:
        district_data = district_data.filter(FicheJournaliere.periode == selected_periode)
    district_data = district_data.group_by(District.nom).order_by(
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).desc()
    ).all()

    # MPE
    mpe_query = db.session.query(
        Affection.libelle,
        func.sum(LigneConsultation.cas_simples + LigneConsultation.hospitalises + LigneConsultation.evacues).label('total')
    ).join(LigneConsultation).join(FicheJournaliere).filter(
        FicheJournaliere.edition_id == edition.id,
        Affection.is_mpe == True
    )
    if selected_periode:
        mpe_query = mpe_query.filter(FicheJournaliere.periode == selected_periode)
    mpe_data = mpe_query.group_by(Affection.libelle).all()

    # Complétude
    nb_eps_attendus = EPS.query.filter_by(actif=True).count()
    if selected_periode:
        nb_soumis = FicheJournaliere.query.filter_by(
            edition_id=edition.id, periode=selected_periode
        ).count()
    else:
        nb_soumis = db.session.query(
            func.count(func.distinct(FicheJournaliere.eps_id))
        ).filter_by(edition_id=edition.id).scalar() or 0

    completude_pct = round((nb_soumis / nb_eps_attendus * 100), 1) if nb_eps_attendus > 0 else 0

    districts = District.query.filter_by(actif=True).order_by(District.ordre).all()

    stats_data = {
        'total_consultants': total_consultants,
        'total_simples': total_simples,
        'total_hospit': total_hospit,
        'total_evacues': total_evacues,
        'total_decedes': total_decedes,
        'top_affections': top_affections,
        'periode_data': periode_data,
        'district_data': district_data,
        'mpe_data': mpe_data,
        'nb_eps_attendus': nb_eps_attendus,
        'nb_soumis': nb_soumis,
        'completude_pct': completude_pct,
    }

    return render_template('public/stats.html',
                           edition=edition,
                           stats=stats_data,
                           periodes=periodes,
                           selected_periode=selected_periode,
                           selected_district=selected_district,
                           districts=districts)


@public_bp.route('/api/stats')
def api_stats():
    """API JSON pour les statistiques — filtrées par EPS pour les non-admin."""
    edition = get_edition_active()
    if not edition:
        return jsonify({'error': 'Aucune édition active'}), 404

    # Totaux par affection (filtrés par EPS pour les utilisateurs non-admin connectés)
    base_filter = [FicheJournaliere.edition_id == edition.id]
    if current_user.is_authenticated and not current_user.is_admin:
        if current_user.eps_id:
            base_filter.append(FicheJournaliere.eps_id == current_user.eps_id)

    data = db.session.query(
        Affection.numero,
        Affection.libelle,
        Affection.categorie,
        func.sum(LigneConsultation.cas_simples).label('cas_simples'),
        func.sum(LigneConsultation.hospitalises).label('hospitalises'),
        func.sum(LigneConsultation.evacues).label('evacues'),
        func.sum(LigneConsultation.decedes).label('decedes'),
    ).join(LigneConsultation).join(FicheJournaliere).filter(
        *base_filter
    ).group_by(Affection.numero, Affection.libelle, Affection.categorie).all()

    result = []
    for row in data:
        total = (row.cas_simples or 0) + (row.hospitalises or 0) + (row.evacues or 0)
        result.append({
            'numero': row.numero,
            'affection': row.libelle,
            'categorie': row.categorie,
            'cas_simples': row.cas_simples or 0,
            'hospitalises': row.hospitalises or 0,
            'evacues': row.evacues or 0,
            'decedes': row.decedes or 0,
            'total': total
        })

    return jsonify({
        'edition': edition.annee,
        'affections': sorted(result, key=lambda x: x['total'], reverse=True)
    })


@public_bp.route('/api/stats/periodes')
def api_stats_periodes():
    """Données par période — filtrées par EPS pour les non-admin."""
    edition = get_edition_active()
    if not edition:
        return jsonify({'error': 'Aucune édition active'}), 404

    # Filtre EPS pour les utilisateurs non-admin connectés
    eps_filter = None
    if current_user.is_authenticated and not current_user.is_admin and current_user.eps_id:
        eps_filter = current_user.eps_id

    periodes = ['J-2', 'J-1', 'J', 'J+1', 'J+2', 'J+3']
    data = []
    for p in periodes:
        filters = [
            FicheJournaliere.edition_id == edition.id,
            FicheJournaliere.periode == p
        ]
        if eps_filter:
            filters.append(FicheJournaliere.eps_id == eps_filter)

        result = db.session.query(
            func.sum(LigneConsultation.cas_simples).label('simples'),
            func.sum(LigneConsultation.hospitalises).label('hospit'),
            func.sum(LigneConsultation.evacues).label('evacues'),
            func.sum(LigneConsultation.decedes).label('decedes'),
        ).join(FicheJournaliere).filter(*filters).first()
        data.append({
            'periode': p,
            'simples': result.simples or 0,
            'hospitalises': result.hospit or 0,
            'evacues': result.evacues or 0,
            'decedes': result.decedes or 0,
        })

    return jsonify({'edition': edition.annee, 'periodes': data})
