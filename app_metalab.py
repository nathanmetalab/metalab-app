import streamlit as st
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="METALAB - Tablet Edition v6.2", layout="wide")

# Style CSS
st.markdown("""
    <style>
    .header-style {
        background-color: #2c3e50;
        padding: 20px;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    </style>
    <div class="header-style">
        <h1>METALAB - GESTION COMMERCIALE (TABLET)</h1>
    </div>
    """, unsafe_allow_html=True)

# --- COORDONNÉES ÉMETTEUR (Alignées sur version PC) ---
MON_NOM = "METALAB - AMOUROUX Nathan"
MON_ADRESSE = "11 Les Bois Labbé, 63700 Saint Eloy les Mines"
MON_SIRET = "123 456 789 00012"
MON_TEL = "07.83.45.57.93"
MON_MAIL = "metalab-chaudronnerie@outlook.fr"
MON_ASSURANCE = "MAAF Assurances - Contrat N° 987654321"

# --- INTERFACE ---
col_emetteur, col_client = st.columns(2)

with col_emetteur:
    st.subheader("📌 VOTRE ENTREPRISE")
    st.info(f"**{MON_NOM}**\n\n{MON_ADRESSE}\n\nSIRET : {MON_SIRET}")

with col_client:
    st.subheader("👤 CLIENT")
    client_nom = st.text_input("Nom du Client")
    client_adresse = st.text_input("Adresse Client")
    client_tel = st.text_input("Téléphone Client")

st.write("---")
intitule_prestation = st.text_input("📝 OBJET DE LA PRESTATION", placeholder="Ex: Fabrication portail acier")

# --- OPTIONS TVA & PAIEMENT ---
col_opt1, col_opt2, col_opt3 = st.columns(3)
with col_opt1:
    tva_active = st.checkbox("Facturer TVA (20%)")
with col_opt2:
    acompte_pct = st.number_input("Acompte devis (%)", min_value=0, max_value=100, value=30)
with col_opt3:
    deja_paye = st.number_input("Déjà réglé (€)", min_value=0.0, step=10.0, value=0.0)

# --- TABLEAU DE SAISIE ---
st.subheader("📦 DÉTAIL DES ARTICLES")
h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([3, 1, 0.7, 1, 0.8, 1])
h_col1.write("**DESCRIPTION**")
h_col2.write("**UNITÉ**")
h_col3.write("**QTÉ**")
h_col4.write("**P.U. HT**")
h_col5.write("**REMISE %**")
h_col6.write("**TOTAL HT**")

rows_data = []
total_remises_global = 0
total_ht_apres_remise = 0

for r in range(10):
    c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 0.7, 1, 0.8, 1])
    desc = c1.text_input(f"D{r}", key=f"d_{r}", label_visibility="collapsed")
    unit = c2.selectbox(f"U{r}", ["Heures", "Forfait", "Matière", "Km", "U"], key=f"u_{r}", label_visibility="collapsed")
    qty = c3.number_input(f"Q{r}", min_value=0.0, step=1.0, key=f"q_{r}", label_visibility="collapsed")
    price = c4.number_input(f"P{r}", min_value=0.0, step=0.01, key=f"p_{r}", label_visibility="collapsed")
    rem_p = c5.number_input(f"R{r}", min_value=0.0, max_value=100.0, step=1.0, key=f"r_{r}", label_visibility="collapsed")
    
    brut = qty * price
    v_remise = brut * (rem_p / 100)
    ligne_net = brut - v_remise
    c6.markdown(f"**{ligne_net:.2f} €**")
    
    if desc:
        rows_data.append({'desc': desc, 'unit': unit, 'qty': qty, 'price': price, 'remise': rem_p, 'total': ligne_net})
        total_ht_apres_remise += ligne_net
        total_remises_global += v_remise

# --- CALCULS FINAUX ---
total_final = total_ht_apres_remise * 1.20 if tva_active else total_ht_apres_remise
reste_a_regler = total_final - deja_paye

st.write("---")
res1, res2 = st.columns([2, 1])
with res2:
    if total_remises_global > 0:
        st.write(f"Économie client : -{total_remises_global:.2f} €")
    st.write(f"### TOTAL HT : {total_ht_apres_remise:.2f} €")
    if tva_active:
        st.write(f"TVA (20%) : {total_ht_apres_remise*0.2:.2f} €")
    st.success(f"## {'TOTAL TTC' if tva_active else 'NET À PAYER'} : {total_final:.2f} €")
    if deja_paye > 0:
        st.error(f"Reste à régler : {reste_a_regler:.2f} €")

# --- FONCTION PDF (Version Pro détaillée) ---
def generer_pdf(items, ht, t_rem, final, type_doc, objet):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Header
    c.setFont("Helvetica-Bold", 12); c.drawString(40, 730, MON_NOM)
    c.setFont("Helvetica", 9); c.drawString(40, 715, MON_ADRESSE)
    c.drawString(40, 700, f"SIRET : {MON_SIRET} | Tel : {MON_TEL}")
    
    # Titre & Date
    c.setFont("Helvetica-Bold", 18); c.drawRightString(550, 780, type_doc.upper())
    c.setFont("Helvetica", 10); c.drawRightString(550, 760, f"Le : {datetime.now().strftime('%d/%m/%Y')}")

    # Bloc Client
    c.rect(320, 650, 230, 85)
    c.setFont("Helvetica-Bold", 10); c.drawString(330, 720, "DESTINATAIRE :")
    c.setFont("Helvetica", 9); c.drawString(330, 705, client_nom.upper())
    c.drawString(330, 690, client_adresse[:45]); c.drawString(330, 675, f"Tel : {client_tel}")

    # Objet
    c.line(40, 630, 550, 630); c.setFont("Helvetica-Bold", 10)
    c.drawString(40, 615, f"OBJET : {objet}"); c.line(40, 610, 550, 610)

    # Tableau
    y = 580
    c.setFont("Helvetica-Bold", 8)
    c.drawString(45, y, "Description"); c.drawRightString(320, y, "Qté")
    c.drawRightString(360, y, "Unité"); c.drawRightString(420, y, "P.U. HT")
    c.drawRightString(480, y, "Rem %"); c.drawRightString(545, y, "Total HT")
    y -= 5; c.line(40, y, 550, y); y -= 15

    c.setFont("Helvetica", 9)
    for item in items:
        c.drawString(45, y, item['desc'][:45])
        c.drawRightString(320, y, str(item['qty']))
        c.drawRightString(360, y, item['unit'])
        c.drawRightString(420, y, f"{item['price']:.2f}")
        c.drawRightString(480, y, f"{item['remise']}%" if item['remise'] > 0 else "-")
        c.drawRightString(545, y, f"{item['total']:.2f} €")
        y -= 15

    # Totaux
    y -= 20; c.line(350, y+15, 550, y+15)
    if t_rem > 0:
        c.setFillColor(colors.HexColor("#27ae60"))
        c.drawString(350, y, "Total remises :"); c.drawRightString(545, y, f"- {t_rem:.2f} €")
        y -= 15; c.setFillColor(colors.black)
    
    c.drawString(350, y, "Total HT Net :"); c.drawRightString(545, y, f"{ht:.2f} €")
    y -= 15
    if tva_active:
        c.drawString(350, y, "TVA (20%) :"); c.drawRightString(545, y, f"{ht*0.20:.2f} €")
        y -= 15; c.setFont("Helvetica-Bold", 11); c.drawString(350, y, "TOTAL TTC :")
    else:
        c.setFont("Helvetica-Bold", 11); c.drawString(350, y, "NET À PAYER :")
    c.drawRightString(545, y, f"{final:.2f} €")

    # Acompte / Reste
    if type_doc == "Devis":
        ac_m = final * (acompte_pct / 100)
        y -= 20; c.setFont("Helvetica", 10); c.drawString(350, y, f"Acompte ({acompte_pct}%):"); c.drawRightString(545, y, f"{ac_m:.2f} €")
    elif deja_paye > 0:
        y -= 20; c.setFont("Helvetica", 10); c.setFillColor(colors.blue); c.drawString(350, y, "Déjà réglé :"); c.drawRightString(545, y, f"- {deja_paye:.2f} €")
        y -= 15; c.setFont("Helvetica-Bold", 11); c.setFillColor(colors.red); c.drawString(350, y, "SOLDE À RÉGLER :"); c.drawRightString(545, y, f"{reste_a_regler:.2f} €")

    if not tva_active:
        c.setFillColor(colors.black); c.setFont("Helvetica-Oblique", 8); c.drawString(40, y, "TVA non applicable, art. 293 B du CGI")

    # Pied de page
    c.setFillColor(colors.black); c.setFont("Helvetica", 8)
    c.drawString(40, 50, f"Assurance : {MON_ASSURANCE} | Valide France Métropolitaine")
    
    c.save(); buffer.seek(0)
    return buffer

# --- BOUTONS ---
col_btn1, col_btn2 = st.columns(2)
if col_btn1.button("📄 GÉNÉRER DEVIS"):
    if not client_nom: st.error("Nom client requis")
    else:
        pdf = generer_pdf(rows_data, total_ht_apres_remise, total_remises_global, total_final, "Devis", intitule_prestation)
        st.download_button("⬇️ Télécharger Devis", pdf, f"Devis_{client_nom}.pdf", "application/pdf")

if col_btn2.button("💰 GÉNÉRER FACTURE"):
    if not client_nom: st.error("Nom client requis")
    else:
        pdf = generer_pdf(rows_data, total_ht_apres_remise, total_remises_global, total_final, "Facture", intitule_prestation)
        st.download_button("⬇️ Télécharger Facture", pdf, f"Facture_{client_nom}.pdf", "application/pdf")