import io
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from openpyxl import Workbook

from selfhosted.config import RAYON_TOLERANCE_METRES, VERSION
from selfhosted.db import (
    init_db, insert_pointage, get_pointages, set_verifie,
    get_pointage, update_pointage,
    get_employes, get_employe, add_employe, update_employe, delete_employe,
    get_clients, get_client, get_client_by_nom, add_client, update_client, delete_client,
    get_kv, set_kv,
    get_planning, get_planning_item, add_planning, update_planning, delete_planning
)
from selfhosted.calcul import calculer_heures_couts
from selfhosted.planning import planning_vs_reel_semaine, JOURS

app = FastAPI(title="cesu-pointage-geoloc")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()


def distance_metres(lat1, lng1, lat2, lng2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# ============ Pointage (public) ============

@app.get("/")
async def racine():
    return RedirectResponse("/static/index.html")


@app.get("/api/config")
async def config_publique():
    return {
        "salariees": [e["nom"] for e in get_employes(only_actifs=True)],
        "clients": [c["nom"] for c in get_clients(only_actifs=True)]
    }


@app.get("/api/version")
async def version_api():
    return {"version": VERSION}


@app.get("/api/bandeau")
async def bandeau_public():
    return {
        "actif": get_kv("bandeau_actif", "0") == "1",
        "message": get_kv("bandeau_message", ""),
        "type": get_kv("bandeau_type", "info")
    }


@app.get("/api/consignes")
async def consignes_api(client: str = None):
    if not client:
        return {"nom": "", "prenom": "", "conditions_medicales": "",
                "contact_urgence_nom": "", "contact_urgence_telephone": "",
                "consignes": "Sélectionnez un client."}
    c = get_client_by_nom(client)
    if not c:
        return {"nom": client, "prenom": "", "conditions_medicales": "",
                "contact_urgence_nom": "", "contact_urgence_telephone": "",
                "consignes": "Client inconnu."}
    return {
        "nom": c["nom"], "prenom": c["prenom"] or "",
        "conditions_medicales": c["conditions_medicales"] or "",
        "contact_urgence_nom": c["contact_urgence_nom"] or "",
        "contact_urgence_telephone": c["contact_urgence_telephone"] or "",
        "consignes": c["consignes"] or ""
    }


@app.get("/consignes", response_class=HTMLResponse)
async def consignes_publiques(request: Request, client: str = None):
    c = get_client_by_nom(client) if client else None
    return templates.TemplateResponse("consignes_public.html", {"request": request, "c": c})


@app.post("/api/pointage")
async def pointage(request: Request):
    try:
        data = await request.json()
        type_ = data.get("type")
        salariee = data.get("salariee")
        client = data.get("client")
        lat = data.get("lat")
        lng = data.get("lng")
        precision = data.get("precision")
        raison = data.get("raisonEchecGeoloc")

        if not type_ or not salariee or not client:
            return JSONResponse({"ok": False, "error": "Champs manquants."}, status_code=400)

        ref = get_client_by_nom(client)
        distance = None
        detail = ""

        if not ref:
            statut = "ERREUR — client inconnu"
            detail = f'Le client "{client}" n\'existe pas dans la configuration.'
        elif lat is not None and lng is not None:
            distance = distance_metres(lat, lng, ref["lat"], ref["lng"])
            statut = "OK" if distance <= RAYON_TOLERANCE_METRES else "À VÉRIFIER — hors zone"
        else:
            statut = "À VÉRIFIER — position indisponible"
            detail = raison or "Raison non précisée par le téléphone"

        insert_pointage(
            horodatage=datetime.now().isoformat(timespec="seconds"),
            type_=type_, salariee=salariee, client=client,
            lat=lat, lng=lng, precision=precision,
            distance=round(distance) if distance is not None else None,
            statut=statut, detail=detail
        )

        return {"ok": True, "statut": statut, "distance": round(distance) if distance is not None else None}

    except Exception as e:
        return JSONResponse({"ok": False, "error": f"Erreur serveur : {e}"}, status_code=500)


# ============ Admin — tableau de bord ============

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, mois: str = None):
    mois = mois or datetime.now().strftime("%Y-%m")
    resume = calculer_heures_couts(mois)
    total_cout = sum(r["cout"] for r in resume if r["cout"] is not None)

    anomalies = get_pointages(only_unverified_issues=True)
    recents = get_pointages(limit=20)

    return templates.TemplateResponse("admin.html", {
        "request": request, "mois": mois, "resume": resume, "total_cout": round(total_cout, 2),
        "anomalies": anomalies, "recents": recents
    })


@app.post("/admin/verifier/{pointage_id}")
async def verifier(pointage_id: int):
    set_verifie(pointage_id, True)
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/pointage/{pid}", response_class=HTMLResponse)
async def fiche_pointage(request: Request, pid: int):
    return templates.TemplateResponse("pointage_detail.html", {
        "request": request,
        "p": get_pointage(pid),
        "employes": get_employes(),  # tous, y compris inactifs, au cas où le pointage les référence
        "clients": [c["nom"] for c in get_clients()]  # tous, y compris inactifs
    })


@app.post("/admin/pointage/{pid}/edit")
async def modifier_pointage(
    pid: int,
    horodatage: str = Form(...),
    type: str = Form(...),
    salariee: str = Form(...),
    client: str = Form(...),
    statut: str = Form(...),
    detail: str = Form(""),
    verifie: str = Form(None)
):
    update_pointage(pid, horodatage, type, salariee, client, statut, detail, verifie is not None)
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/export.xlsx")
async def export_excel(mois: str = None):
    mois = mois or datetime.now().strftime("%Y-%m")
    resume = calculer_heures_couts(mois)
    detail = get_pointages(mois=mois)

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Résumé"
    ws1.append(["Salariée", "Heures travaillées", "Taux horaire (€)", "Coût total (€)", "Pointages incomplets"])
    total_cout = 0
    for r in resume:
        ws1.append([r["salariee"], r["heures"], r["taux_horaire"] or "", r["cout"] or "", r["pointages_incomplets"]])
        if r["cout"]:
            total_cout += r["cout"]
    ws1.append([])
    ws1.append(["TOTAL", "", "", round(total_cout, 2), ""])

    ws2 = wb.create_sheet("Détail pointages")
    ws2.append(["Horodatage", "Type", "Salariée", "Client", "Distance (m)", "Statut", "Détail", "Vérifié"])
    for p in detail:
        ws2.append([
            p["horodatage"], p["type"], p["salariee"], p["client"],
            p["distance"], p["statut"], p["detail"], "Oui" if p["verifie"] else "Non"
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=pointage-cesu-{mois}.xlsx"}
    )


# ============ Admin — employés ============

@app.get("/admin/employes", response_class=HTMLResponse)
async def liste_employes(request: Request):
    return templates.TemplateResponse("employes.html", {"request": request, "employes": get_employes()})


@app.post("/admin/employes")
async def creer_employe(
    nom: str = Form(...), taux_horaire: float = Form(...),
    telephone: str = Form(""), numero_secu: str = Form(""),
    date_naissance: str = Form(""), adresse: str = Form(""), notes: str = Form("")
):
    add_employe(nom, taux_horaire, telephone, numero_secu, date_naissance, adresse, notes)
    return RedirectResponse("/admin/employes", status_code=303)


@app.get("/admin/employes/{emp_id}", response_class=HTMLResponse)
async def fiche_employe(request: Request, emp_id: int):
    e = get_employe(emp_id)
    return templates.TemplateResponse("employe_detail.html", {"request": request, "e": e})


@app.post("/admin/employes/{emp_id}/edit")
async def modifier_employe(
    emp_id: int,
    nom: str = Form(...),
    taux_horaire: float = Form(...),
    telephone: str = Form(""),
    numero_secu: str = Form(""),
    date_naissance: str = Form(""),
    adresse: str = Form(""),
    notes: str = Form(""),
    actif: str = Form(None)
):
    update_employe(emp_id, nom, taux_horaire, telephone, numero_secu, date_naissance, adresse, notes, actif is not None)
    return RedirectResponse("/admin/employes", status_code=303)


@app.post("/admin/employes/{emp_id}/supprimer")
async def supprimer_employe(emp_id: int):
    delete_employe(emp_id)
    return RedirectResponse("/admin/employes", status_code=303)


# ============ Admin — planning ============

@app.get("/admin/planning", response_class=HTMLResponse)
async def planning_admin(request: Request):
    return templates.TemplateResponse("planning.html", {
        "request": request,
        "planning": get_planning(),
        "jours": JOURS,
        "suivi_semaine": planning_vs_reel_semaine(),
        "employes": get_employes(only_actifs=True),
        "clients": [c["nom"] for c in get_clients(only_actifs=True)]
    })


@app.post("/admin/planning")
async def creer_planning(
    employe: str = Form(...), client: str = Form(...), jour_semaine: int = Form(...),
    heure_debut: str = Form(...), heure_fin: str = Form(...), notes: str = Form("")
):
    add_planning(employe, client, jour_semaine, heure_debut, heure_fin, notes)
    return RedirectResponse("/admin/planning", status_code=303)


@app.get("/admin/planning/{pid}", response_class=HTMLResponse)
async def fiche_planning(request: Request, pid: int):
    return templates.TemplateResponse("planning_detail.html", {
        "request": request,
        "p": get_planning_item(pid),
        "jours": JOURS,
        "employes": get_employes(only_actifs=True),
        "clients": [c["nom"] for c in get_clients(only_actifs=True)]
    })


@app.post("/admin/planning/{pid}/edit")
async def modifier_planning(
    pid: int, employe: str = Form(...), client: str = Form(...), jour_semaine: int = Form(...),
    heure_debut: str = Form(...), heure_fin: str = Form(...), notes: str = Form("")
):
    update_planning(pid, employe, client, jour_semaine, heure_debut, heure_fin, notes)
    return RedirectResponse("/admin/planning", status_code=303)


@app.post("/admin/planning/{pid}/supprimer")
async def supprimer_planning(pid: int):
    delete_planning(pid)
    return RedirectResponse("/admin/planning", status_code=303)


# ============ Admin — clients (sites) ============

@app.get("/admin/clients", response_class=HTMLResponse)
async def liste_clients(request: Request):
    return templates.TemplateResponse("clients.html", {"request": request, "clients": get_clients()})


@app.post("/admin/clients")
async def creer_client(
    nom: str = Form(...), lat: float = Form(...), lng: float = Form(...),
    prenom: str = Form(""), conditions_medicales: str = Form(""),
    contact_urgence_nom: str = Form(""), contact_urgence_telephone: str = Form(""),
    consignes: str = Form(""), notes: str = Form("")
):
    add_client(nom, lat, lng, prenom, conditions_medicales, contact_urgence_nom,
               contact_urgence_telephone, consignes, notes)
    return RedirectResponse("/admin/clients", status_code=303)


@app.get("/admin/clients/{cid}", response_class=HTMLResponse)
async def fiche_client(request: Request, cid: int):
    return templates.TemplateResponse("client_detail.html", {"request": request, "c": get_client(cid)})


@app.post("/admin/clients/{cid}/edit")
async def modifier_client(
    cid: int, nom: str = Form(...), lat: float = Form(...), lng: float = Form(...),
    prenom: str = Form(""), conditions_medicales: str = Form(""),
    contact_urgence_nom: str = Form(""), contact_urgence_telephone: str = Form(""),
    consignes: str = Form(""), notes: str = Form(""), actif: str = Form(None)
):
    update_client(cid, nom, lat, lng, prenom, conditions_medicales, contact_urgence_nom,
                  contact_urgence_telephone, consignes, notes, actif is not None)
    return RedirectResponse("/admin/clients", status_code=303)


@app.post("/admin/clients/{cid}/supprimer")
async def supprimer_client(cid: int):
    delete_client(cid)
    return RedirectResponse("/admin/clients", status_code=303)


# ============ Admin — bandeau d'alerte ============

@app.get("/admin/bandeau", response_class=HTMLResponse)
async def bandeau_admin(request: Request):
    return templates.TemplateResponse("bandeau.html", {
        "request": request,
        "actif": get_kv("bandeau_actif", "0") == "1",
        "message": get_kv("bandeau_message", ""),
        "type": get_kv("bandeau_type", "info")
    })


@app.post("/admin/bandeau")
async def enregistrer_bandeau(message: str = Form(""), type: str = Form("info"), actif: str = Form(None)):
    set_kv("bandeau_message", message)
    set_kv("bandeau_type", type)
    set_kv("bandeau_actif", "1" if actif is not None else "0")
    return RedirectResponse("/admin/bandeau", status_code=303)
