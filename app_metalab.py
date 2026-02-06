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

# Style pour l'en-tête (équivalent au frame bleu de ton code PC)
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
    </style>
    <div class="header-style">
        <h1>METALAB - SYSTÈME AUTOMATISÉ</h1>
    </div>
    """, unsafe_allow_html=True)

# --- COORDONNÉES ÉMETTEUR ---
mon_nom = "METALAB"
mon_tel = "07.83.45.57.93"
mon_mail = "metalab-chaudronnerie.fr"

# --- INTERFACE ---
col_emetteur, col_client = st.columns(2)

with col_emetteur:
    st.subheader("📌 ÉMETTEUR")
    st.info(f"**{mon_nom}**\n\nTel : {mon_tel}\n\nEmail : {mon_mail}")

with col_client:
    st.subheader("👤 INFOS CLIENT")
    client_nom = st.text_input("Nom du Client", placeholder="Ex: Jean Dupont")
    client_num = st.text_input("N° Client", placeholder="Ex: CL-01")
    client_mail = st.text_input("Email Client", placeholder="client@mail.com")

# --- TABLEAU DE SAISIE ---
st.write("---")
st.subheader("📦 DÉTAIL DES PRESTATIONS")

# En-têtes des colonnes
h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([3, 1.5, 1, 1.5, 1, 1.5])
h_col1.write("**DESCRIPTION**")
h_col2.write("**UNITÉ**")
h_col3.write("**QTÉ**")
h_col4.write("**PRIX U. HT**")
h_col5.write("**REMISE %**")
h_col6.write("**TOTAL HT**")

rows_data = []

# Création des 10 lignes (comme dans ton code original)
for r in range(10):
    c1, c2, c3, c4, c5, c6 = st.columns([3, 1.5, 1, 1.5, 1, 1.5])
    
    desc = c1.text_input(f"Desc {r}", key=f"desc_{r}", label_visibility="collapsed")
    unit = c2.selectbox(f"Unit {r}", ["Heures", "Matière", "Prestation", "Pose chantier", "Déplacement KM"], key=f"unit_{r}", label_visibility="collapsed")
    qty = c3.number_input(f"Qty {r}", min_value=0.0, step=1.0, key=f"qty_{r}", label_visibility="collapsed")
    price = c4.number_input(f"Price {r}", min_value=0.0, step=0.01, key=f"price_{r}", label_visibility="collapsed")
    remise = c5.number_input(f"Rem {r}", min_value=0.0, max_value=100.0, step=1.0, key=f"rem_{r}", label_visibility="collapsed")
    
    # Calcul de la ligne
    ligne_ht = (qty * price) * (1 - remise/100)
    c6.markdown(f"**{ligne_ht:.2f} €**")
    
    if desc: # On n'enregistre que les lignes remplies
        rows_data.append({
            'desc': desc,
            'unit': unit,
            'qty': qty,
            'price': price,
            'remise': remise,
            'total': f"{ligne_ht:.2f} €"
        })

# --- RÉSUMÉ ET CALCULS ---
st.write("---")
total_ht = sum(float(item['total'].replace(' €', '')) for item in rows_data)
ttc = total_ht * 1.20

res_col1, res_col2 = st.columns([2, 1])

with res_col2:
    st.write(f"### TOTAL HT : {total_ht:.2f} €")
    st.success(f"## TOTAL TTC : {ttc:.2f} €")

# --- FONCTION GÉNÉRATION PDF (ADAPTÉE REPORTLAB) ---
def generer_pdf_data(items, ht, ttc, c_nom, c_num, c_mail):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    # Dessin du logo (si présent sur ton PC)
    # Note : Le logo doit être dans le même dossier que ce script
    if os.path.exists("logo.png"):
        c.drawImage("logo.png", 40, 740, width=150, preserveAspectRatio=True, mask='auto')
    
    c.setFont("Helvetica", 10)
    c.drawString(40, 730, f"Tel : {mon_tel}")
    c.drawString(40, 715, f"Email : {mon_mail}")
    c.line(40, 710, 550, 710)

    # Infos Client
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, 690, f"DEVIS")
    c.drawString(40, 675, f"Date : {date_str}")
    c.drawString(350, 690, f"CLIENT : {c_nom.upper()}")
    c.setFont("Helvetica", 10)
    c.drawString(350, 675, f"N° Client : {c_num}")
    c.drawString(350, 660, f"Email : {c_mail}")

    # Tableau PDF
    y = 620
    c.setFillColor(HexColor("#2c3e50")) 
    c.rect(40, y-5, 510, 20, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(45, y, "Description")
    c.drawString(210, y, "Unité")
    c.drawString(305, y, "Qté")
    c.drawString(355, y, "P.U. HT")
    c.drawString(425, y, "Remise")
    c.drawString(495, y, "Total HT")

    y -= 25
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    for item in items:
        c.drawString(45, y, item['desc'][:35])
        c.drawString(210, y, item['unit'])
        c.drawString(305, y, str(item['qty']))
        c.drawString(355, y, f"{item['price']}€")
        c.drawString(425, y, f"{item['remise']}%")
        c.drawString(495, y, item['total'])
        y -= 20

    # Totaux
    y -= 30
    c.line(350, y+10, 550, y+10)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, f"TOTAL HT : {ht:.2f} €")
    c.setFillColor(HexColor("#27ae60"))
    c.drawString(350, y-20, f"TOTAL TTC (TVA 20%) : {ttc:.2f} €")

    c.save()
    buffer.seek(0)
    return buffer

# --- BOUTONS ---
st.write("---")
if st.button("📝 PRÉPARER LE PDF"):
    if not client_nom:
        st.error("Veuillez saisir le nom du client.")
    else:
        pdf_file = generer_pdf_data(rows_data, total_ht, ttc, client_nom, client_num, client_mail)
        st.download_button(
            label="⬇️ TÉLÉCHARGER LE DEVIS",
            data=pdf_file,
            file_name=f"Devis_{client_nom}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )