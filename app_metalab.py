import streamlit as st
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="METALAB - Expert v5.0", layout="wide")

# Style CSS pour l'interface
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
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    </style>
    <div class="header-style">
        <h1>METALAB - GESTION COMMERCIALE</h1>
    </div>
    """, unsafe_allow_html=True)

# --- COORDONNÉES ÉMETTEUR ---
mon_nom = "METALAB"
mon_siret = "123 456 789 00012"
mon_tel = "07.83.45.57.93"
mon_mail = "metalab-chaudronnerie.fr"

# --- INTERFACE ---
col_emetteur, col_client = st.columns(2)

with col_emetteur:
    st.subheader("📌 VOTRE ENTREPRISE")
    st.info(f"**{mon_nom}**\n\nSIRET : {mon_siret}\n\nTel : {mon_tel}\n\nEmail : {mon_mail}")

with col_client:
    st.subheader("👤 COORDONNÉES CLIENT")
    client_nom = st.text_input("Nom du Client", placeholder="Nom ou Entreprise")
    client_mail = st.text_input("Email Client", placeholder="client@exemple.com")
    client_num = st.text_input("N° Client / Projet", placeholder="ex: CL-2024-01")

# --- TABLEAU DE SAISIE ---
st.write("---")
st.subheader("📦 DÉTAIL DES PRESTATIONS")

h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([3, 1.2, 0.8, 1.2, 0.8, 1.2])
h_col1.write("**DESCRIPTION**")
h_col2.write("**UNITÉ**")
h_col3.write("**QTÉ**")
h_col4.write("**PRIX U. HT**")
h_col5.write("**REMISE %**")
h_col6.write("**TOTAL HT**")

rows_data = []

for r in range(10):
    c1, c2, c3, c4, c5, c6 = st.columns([3, 1.2, 0.8, 1.2, 0.8, 1.2])
    
    desc = c1.text_input(f"D{r}", key=f"desc_{r}", label_visibility="collapsed")
    unit = c2.selectbox(f"U{r}", ["Heures", "Matière", "Prestation", "Déplacement", "Forfait"], key=f"unit_{r}", label_visibility="collapsed")
    qty = c3.number_input(f"Q{r}", min_value=0.0, step=1.0, key=f"qty_{r}", label_visibility="collapsed")
    price = c4.number_input(f"P{r}", min_value=0.0, step=0.01, key=f"price_{r}", label_visibility="collapsed")
    remise = c5.number_input(f"R{r}", min_value=0.0, max_value=100.0, step=1.0, key=f"rem_{r}", label_visibility="collapsed")
    
    ligne_ht = (qty * price) * (1 - remise/100)
    c6.markdown(f"**{ligne_ht:.2f} €**")
    
    if desc:
        rows_data.append({
            'desc': desc, 'unit': unit, 'qty': qty, 
            'price': price, 'remise': remise, 'total': f"{ligne_ht:.2f} €"
        })

# --- RÉSUMÉ ---
st.write("---")
total_ht = sum((item['qty'] * item['price']) * (1 - item['remise']/100) for item in rows_data)
ttc = total_ht * 1.20

res_col1, res_col2 = st.columns([2, 1])
with res_col2:
    st.write(f"### TOTAL HT : {total_ht:.2f} €")
    st.success(f"## TOTAL TTC : {ttc:.2f} €")

# --- FONCTION GÉNÉRATION PDF ---
def generer_pdf(items, ht, ttc, c_nom, c_num, c_mail, type_doc):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    # Logo
    if os.path.exists("logo.png"):
        c.drawImage("logo.png", 40, 750, width=120, preserveAspectRatio=True, mask='auto')
    
    # Header Émetteur
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, 735, mon_nom)
    c.setFont("Helvetica", 9)
    c.drawString(40, 722, f"SIRET : {mon_siret}")
    c.drawString(40, 710, f"Tel : {mon_tel} | Email : {mon_mail}")
    c.line(40, 705, 550, 705)

    # Titre Document
    c.setFont("Helvetica-Bold", 16)
    c.drawString(400, 725, type_doc.upper())

    # Infos Client & Document
    c.rect(340, 640, 210, 60)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, 685, f"CLIENT : {c_nom.upper()}")
    c.setFont("Helvetica", 9)
    c.drawString(350, 670, f"Email : {c_mail}")
    c.drawString(350, 655, f"Réf : {c_num}")
    
    c.drawString(40, 685, f"Date : {date_str}")
    c.drawString(40, 670, f"Validité : 30 jours")

    # Tableau
    y = 600
    c.setFillColor(HexColor("#2c3e50")) 
    c.rect(40, y-5, 510, 20, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(45, y, "Description")
    c.drawString(495, y, "Total HT")

    y -= 25
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    for item in items:
        if y < 100: # Gestion simplifiée du saut de page
            c.showPage()
            y = 800
        c.drawString(45, y, item['desc'][:60])
        c.drawString(495, y, item['total'])
        y -= 20

    # Totaux
    y -= 30
    c.line(350, y+10, 550, y+10)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, f"TOTAL HT : {ht:.2f} €")
    c.setFillColor(HexColor("#27ae60"))
    c.drawString(350, y-20, f"TOTAL TTC (TVA 20%) : {ttc:.2f} €")

    # Mentions légales bas de page
    if type_doc == "Facture":
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(40, 50, "Pénalités de retard : 3 fois le taux légal. Indemnité forfaitaire de recouvrement : 40€")

    c.save()
    buffer.seek(0)
    return buffer

# --- ACTIONS ---
st.write("---")
btn_col1, btn_col2 = st.columns(2)

if btn_col1.button("📄 GÉNÉRER DEVIS"):
    if not client_nom:
        st.error("Nom du client obligatoire")
    else:
        pdf = generer_pdf(rows_data, total_ht, ttc, client_nom, client_num, client_mail, "Devis")
        st.download_button("⬇️ TÉLÉCHARGER LE DEVIS", pdf, f"Devis_{client_nom}.pdf", "application/pdf")

if btn_col2.button("💰 GÉNÉRER FACTURE"):
    if not client_nom:
        st.error("Nom du client obligatoire")
    else:
        pdf = generer_pdf(rows_data, total_ht, ttc, client_nom, client_num, client_mail, "Facture")
        st.download_button("⬇️ TÉLÉCHARGER LA FACTURE", pdf, f"Facture_{client_nom}.pdf", "application/pdf")