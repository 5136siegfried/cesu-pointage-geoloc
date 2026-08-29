from datetime import datetime

from selfhosted.db import get_pointages, get_employes


def calculer_heures_couts(mois: str):
    """
    Reconstitue les heures travaillées par salariée pour un mois donné (format 'YYYY-MM'),
    en appariant chaque 'Arrivée' avec le 'Départ' suivant. Un pointage qui ne trouve pas
    sa paire (départ manquant, doublon...) est compté à part dans "pointages_incomplets"
    plutôt que faussé silencieusement dans le total d'heures.
    """
    rows = get_pointages(mois=mois)
    rows = sorted(rows, key=lambda r: (r["salariee"], r["horodatage"]))

    employes = {e["nom"]: e for e in get_employes()}
    par_salariee = {}
    en_cours = {}  # salariee -> datetime de l'arrivée en attente d'un départ

    for r in rows:
        sal = r["salariee"]
        par_salariee.setdefault(sal, {"minutes": 0.0, "incomplets": 0})
        try:
            ts = datetime.fromisoformat(r["horodatage"])
        except ValueError:
            continue

        if r["type"] == "Arrivée":
            if sal in en_cours:
                # Deux arrivées sans départ entre les deux : la précédente est incomplète.
                par_salariee[sal]["incomplets"] += 1
            en_cours[sal] = ts
        elif r["type"] == "Départ":
            if sal in en_cours:
                delta_minutes = (ts - en_cours.pop(sal)).total_seconds() / 60
                if delta_minutes > 0:
                    par_salariee[sal]["minutes"] += delta_minutes
                else:
                    par_salariee[sal]["incomplets"] += 1
            else:
                par_salariee[sal]["incomplets"] += 1

    # Un départ jamais arrivé (shift en cours au moment du calcul) compte aussi comme incomplet.
    for sal in en_cours:
        par_salariee.setdefault(sal, {"minutes": 0.0, "incomplets": 0})
        par_salariee[sal]["incomplets"] += 1

    resultat = []
    for sal, data in par_salariee.items():
        heures = round(data["minutes"] / 60, 2)
        employe_row = employes.get(sal)
        taux = employe_row["taux_horaire"] if employe_row is not None else None
        taux = taux if taux else None
        cout = round(heures * taux, 2) if taux else None
        resultat.append({
            "salariee": sal,
            "heures": heures,
            "taux_horaire": taux,
            "cout": cout,
            "pointages_incomplets": data["incomplets"]
        })

    resultat.sort(key=lambda r: r["salariee"])
    return resultat
