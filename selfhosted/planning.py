from datetime import datetime, timedelta

from db import get_planning, get_pointages

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def semaine_courante_dates():
    aujourdhui = datetime.now().date()
    lundi = aujourdhui - timedelta(days=aujourdhui.weekday())
    return [lundi + timedelta(days=i) for i in range(7)]


def planning_vs_reel_semaine():
    """
    Pour chaque créneau récurrent défini dans /admin/planning, vérifie si un
    pointage 'Arrivée' correspondant existe bien à la date attendue de la
    semaine en cours. Permet de distinguer un jour sans pointage prévu (normal)
    d'un jour prévu mais non pointé (oubli ou absence à clarifier).
    """
    dates = semaine_courante_dates()
    planning = get_planning()
    pointages = get_pointages()

    resultat = []
    for p in planning:
        date_prevue = dates[p["jour_semaine"]]
        date_str = date_prevue.isoformat()
        pointe = any(
            pt["salariee"] == p["employe"] and pt["client"] == p["client"]
            and pt["type"] == "Arrivée" and pt["horodatage"].startswith(date_str)
            for pt in pointages
        )
        resultat.append({
            "jour": JOURS[p["jour_semaine"]],
            "date": date_prevue.strftime("%d/%m"),
            "employe": p["employe"],
            "client": p["client"],
            "heure_debut": p["heure_debut"],
            "heure_fin": p["heure_fin"],
            "pointe": pointe,
            "passe": date_prevue <= datetime.now().date(),
        })
    return resultat
