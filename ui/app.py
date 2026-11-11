"""Interface TicketAssist ; communiquer avec l’API uniquement."""
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from ticket_agent.config import valeurs_env
from ui.client import ApiError, Client

st.set_page_config(page_title="TicketAssist", layout="wide")
st.title("TicketAssist")
st.caption("Qualification, validation humaine et suivi des tickets IT")
local = valeurs_env(Path.cwd() / ".env")
with st.sidebar:
    st.header("Connexion")
    url = st.text_input("Adresse de l’API", os.getenv("TICKET_API_URL", "http://127.0.0.1:8000"))
    key = st.text_input("Clé API", value=os.getenv("TICKET_UI_KEY", local.get("TICKET_API_KEY_CLIENT", "")), type="password")
    st.caption("Clé client : création et consultation. Clé admin : validation et changements de statut.")
try:
    client = Client(url, key)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
try:
    client.health()
    st.success("API prête : modèle chargé")
except ApiError as exc:
    st.warning(str(exc))
    st.info("La consultation reste possible si le modèle est indisponible mais que la base fonctionne.")

creation, suivi, documentation = st.tabs(["Créer un ticket", "Suivi et validation", "Documentation"])

with creation:
    with st.form("creation", clear_on_submit=False):
        titre = st.text_input("Titre", max_chars=160)
        description = st.text_area("Description", height=140, max_chars=2000)
        col1, col2 = st.columns(2)
        impact = col1.selectbox("Impact", ["individuel", "equipe", "organisation"])
        urgence = col2.selectbox("Urgence", ["faible", "normale", "critique"], index=1)
        analyser = st.form_submit_button("Analyser")
        creer = st.form_submit_button("Créer pour validation humaine")
    if analyser or creer:
        payload = {"titre": titre, "description": description, "impact": impact, "urgence": urgence}
        if len(titre.strip()) < 3 or len(description.strip()) < 10:
            st.error("Saisir un titre d’au moins 3 caractères et une description d’au moins 10 caractères.")
        else:
            try:
                if creer:
                    ticket = client.create(payload)
                    st.session_state["derniere_analyse"] = ticket["analyse"]
                    st.success(f"Ticket créé : {ticket['id']} — A_VALIDER")
                else:
                    st.session_state["derniere_analyse"] = client.analyze(payload)
            except ApiError as exc:
                st.error(str(exc))
    if "derniere_analyse" in st.session_state:
        r = st.session_state["derniere_analyse"]
        st.subheader("Dernière proposition calculée")
        c1, c2, c3 = st.columns(3)
        c1.metric("Catégorie", r["categorie"] or "À qualifier")
        c2.metric("Confiance", f"{r['confiance']:.1%}")
        c3.metric("Priorité", r["priorite"])
        st.write("Équipe proposée :", r["equipe"])
        st.info(r["reponse_initiale"])
        if r["escalade"]:
            st.warning("Escalade : " + ", ".join(r["motifs_escalade"]))
        st.caption("Toute création reste A_VALIDER jusqu’à confirmation d’un opérateur administrateur.")

with suivi:
    statut = st.selectbox("Filtre de statut", ["Tous", "A_VALIDER", "NOUVEAU", "EN_COURS", "RESOLU"])
    page = st.number_input("Page", min_value=1, step=1, value=1)
    st.button("Actualiser la liste")
    try:
        liste = client.tickets(None if statut == "Tous" else statut, (int(page) - 1) * 20)
        st.caption(f"{liste['total']} ticket(s) ; 20 par page")
        if liste["items"]:
            tableau = pd.DataFrame([{"id": t["id"], "titre": t["titre"], "statut": t["statut"],
                                     "priorite": t["analyse"]["priorite"], "equipe": t["equipe_validee"] or t["analyse"]["equipe"]}
                                    for t in liste["items"]])
            st.dataframe(tableau, use_container_width=True)
            st.bar_chart(tableau["statut"].value_counts().rename("tickets"))
            st.caption("Graphique limité aux tickets de la page courante.")
        else:
            st.info("Aucun ticket sur cette page.")
    except ApiError as exc:
        st.error(str(exc))
    identifiant = st.text_input("Identifiant du ticket à ouvrir")
    if st.button("Ouvrir le ticket"):
        try:
            st.session_state["ticket_ouvert"] = client.get(identifiant.strip())
        except ApiError as exc:
            st.session_state.pop("ticket_ouvert", None)
            st.error(str(exc))
    if "ticket_ouvert" in st.session_state:
        t = st.session_state["ticket_ouvert"]
        st.subheader(t["titre"])
        st.write(t["description"])
        st.write("Statut :", t["statut"], " — Version :", t["version"])
        st.write("Priorité :", t["analyse"]["priorite"], " — Équipe :", t["equipe_validee"] or t["analyse"]["equipe"])
        st.dataframe(pd.DataFrame(t["historique"]), use_container_width=True)
        if t["resolution"]:
            st.info(t["resolution"])
        actions = {"A_VALIDER": "valider", "NOUVEAU": "demarrer", "EN_COURS": "resoudre", "RESOLU": "reouvrir"}
        with st.form("transition"):
            categorie = st.selectbox("Catégorie confirmée pour la validation", ["acces", "logiciel", "materiel", "reseau"])
            resolution = st.text_area("Compte rendu de résolution", max_chars=2000)
            appliquer = st.form_submit_button("Appliquer : " + actions[t["statut"]])
        if appliquer:
            body = {"action": actions[t["statut"]], "version": t["version"]}
            if t["statut"] == "A_VALIDER":
                body["categorie"] = categorie
            if t["statut"] == "EN_COURS":
                body["resolution"] = resolution
            try:
                st.session_state["ticket_ouvert"] = client.update(t["id"], body)
                st.rerun()
            except ApiError as exc:
                st.error(str(exc))

with documentation:
    st.markdown("""
### Fonctionnement
La classification propose une catégorie. La priorité vient de la matrice impact × urgence.
L’opérateur valide la catégorie et suit les transitions : A_VALIDER → NOUVEAU → EN_COURS → RESOLU.
La réouverture ramène un ticket résolu à EN_COURS. Aucune action technique sur un poste n’est exécutée.

### Données et limites
Le modèle livré se reconstruit sur des tickets **simulés**. Un corpus réel autorisé est nécessaire
pour conclure sur des performances métier. Un score élevé ne garantit pas une catégorie correcte.
Une clé client n’autorise pas les actions d’administration. Ce démonstrateur ne gère pas des comptes individuels.
    """)
