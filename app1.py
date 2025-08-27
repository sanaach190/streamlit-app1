import streamlit as st
import pandas as pd
from datetime import datetime
import os
import openpyxl

st.set_page_config(page_title="Calcul Performance Turbine", layout="centered")

st.title("📊 Application de calcul de performance - Turbine")
st.write("Veuillez remplir les informations pour calculer les indicateurs de performance.")

with st.form("formulaire"):
    st.subheader("🔧 Informations générales")
    utilisateur = st.text_input("Nom de l'utilisateur")
    turbine = st.text_input("Nom ou référence de la turbine")
    date = st.date_input("Date de l’essai")
    heure_debut = st.time_input("Heure de début")
    heure_fin = st.time_input("Heure de fin")
    heures_marche = st.number_input("Heures de marche", min_value=0.0, step=0.1)
    charge = st.number_input("Charge (%)", min_value=0.0, max_value=100.0, step=1.0)

    st.subheader("🌡 Conditions atmosphériques")
    temp_adm = st.number_input("Température admission (°C)", min_value=-50.0, step=0.1)
    tref = st.number_input("Température de référence (°C)", value=15.0, step=0.1)
    patm = st.number_input("Pression atmosphérique (bar)", min_value=0.0, step=0.001)
    pref = st.number_input("Pression de référence (bar)", value=1.013, step=0.001)

    st.subheader("⛽ Données fioul")
    compteur_debut = st.number_input("Compteur début (L)", min_value=0.0)
    compteur_fin = st.number_input("Compteur fin (L)", min_value=0.0)
    densite_15 = st.number_input("Densité à 15°C (g/L)", min_value=0.0)
    vcf = st.number_input("VCF (facteur de correction volumique)", min_value=0.0)
    pci = st.number_input("PCI (kJ/kg)", min_value =0.0)

    st.subheader("⚡ Données énergétiques")
    energie_initiale = st.number_input("Énergie initiale (kWh)", min_value=0.0)
    energie_finale = st.number_input("Énergie finale (kWh)", min_value=0.0)
    puissance_brute = st.number_input("Puissance brute (kW)", min_value=0.0)
    perte_transfo = st.number_input("Perte transformateur (kWh)", min_value=0.0)
    consommation_aux = st.number_input("Consommation auxiliaire (kWh)", min_value=0.0)
    puissance_nette = st.number_input("Puissance nette (kW)", min_value=0.0)
    st.subheader("⚙ Facteurs divers (manuels)")
    kp = st.number_input("Facteur vieillissement (k_p)", min_value=0.0, value=1.0, step=0.01)
    aH = st.number_input("Correction humidité (aH)", min_value=0.0, value=1.0, step=0.01)
    aPF = st.number_input("Correction facteur de puissance (aPF)", min_value=0.0, value=1.0, step=0.01)
    aDPA = st.number_input("Correction dérivée pression atm. (aDPA)", min_value=0.0, value=1.0, step=0.01)
    aDPE = st.number_input("Correction dérivée pression échappement (aDPE)", min_value=0.0, value=1.0, step=0.01)
    aTA = st.number_input("Correction température ambiante (ATA)", min_value=0.0, value=1.0, step=0.01)
    aPA = st.number_input("Correction pression atmosphérique (APA)", min_value=0.0, value=1.0, step=0.01)
    submit = st.form_submit_button("Calculer")

if submit:
    # Calculs de base
    volume_apparent = compteur_fin - compteur_debut
    volume_corrige = volume_apparent * vcf
    masse_fioul = volume_corrige * densite_15  # kg

    energie_produite = energie_finale - energie_initiale
    puissance_nette = puissance_brute - perte_transfo - consommation_aux

    # Facteurs de correction atmosphériques
    aTA = (273 + tref) / (273 + temp_adm) if (273 + temp_adm) != 0 else 1
    aPA = patm / pref if pref > 0 else 1


    facteurs_denominateur = aH * aPF * aPA * aDPA * aDPE * kp

    # Calcul rendement mesuré
    rendement_mesure = (puissance_nette * 3600) / (masse_fioul * pci) if masse_fioul > 0 else 0


    # Consommation spécifique (g/kWh)
    conso_specifique = (masse_fioul ) / energie_produite if energie_produite > 0 else 0

    # Heat Rate Mesuré (kJ/kWh)
    HRM = ((masse_fioul * pci ) / energie_produite) / 1000 if energie_produite > 0 else 0


    # PMC et HRMC
    PMC = (puissance_nette * aTA) / facteurs_denominateur if facteurs_denominateur > 0 else 0
    HRMC = (HRM * aTA ) / facteurs_denominateur if facteurs_denominateur > 0 else 0
    rendement_corrige = 3600 / HRMC if HRMC > 0 else 0
    # Affichage résultats
    st.success("✅ Résultats :")
    st.write(f"Volume apparent : *{volume_apparent:.2f} L*")
    st.write(f"Volume corrigé : *{volume_corrige:.2f} L*")
    st.write(f"Masse fioul : *{masse_fioul:.2f} kg*")
    st.write(f"Énergie produite : *{energie_produite:.2f} kWh*")
    st.write(f"Consommation spécifique corrigée : *{conso_specifique:.2f} g/kWh*")
    st.write(f"PMC (Puissance corrigée) : *{PMC:.2f} kW*")
    st.write(f"HRM : *{HRM:.2f} kJ/kWh*")
    st.write(f"HRMC : *{HRMC:.2f} kJ/kWh*")
    st.write(f"Rendement mesuré : *{rendement_mesure*100:.2f} %*")
    st.write(f"Rendement corrigé : *{rendement_corrige*100:.2f} %*")
    # Sauvegarde Excel
    donnees = {
        "Utilisateur": utilisateur,
        "Date": date.strftime("%Y-%m-%d"),
        "Heure début": heure_debut.strftime("%H:%M"),
        "Heure fin": heure_fin.strftime("%H:%M"),
        "Turbine": turbine,
        "Compteur début (L)": compteur_debut,
        "Compteur fin (L)": compteur_fin,
        "Volume apparent (L)": volume_apparent,
        "VCF": vcf,
        "Volume corrigé (L)": volume_corrige,
        "Densité 15°C (g/L)": densite_15,
        "Masse fioul (kg)": masse_fioul,
        "Énergie initiale (kWh)": energie_initiale,
        "Énergie finale (kWh)": energie_finale,
        "Énergie produite (kWh)": energie_produite,
        "Puissance brute (kW)": puissance_brute,
        "Puissance nette (kW)": puissance_nette,
        "Perte transformateur (kWh)": perte_transfo,
        "Consommation auxiliaire (kWh)": consommation_aux,
        "Température admission (°C)": temp_adm,
        "Pression atmosphérique (bar)": patm,
        "Facteur ATA": aTA,
        "Facteur APA": aPA,
        "Correction humidité (aH)": aH,
        "Correction facteur puissance (aPF)": aPF,
        "Correction dérivée pression atm. (aDPA)": aDPA,
        "Correction dérivée pression échappement (aDPE)": aDPE,
        "Facteur KP": kp,
        "PCI (kJ/kg)": pci,
        "Consommation spécifique corrigée (g/kWh)": conso_specifique,
        "PMC (kW)": PMC,
        "HRM (kJ/kWh)": HRM,
        "HRMC (kJ/kWh)": HRMC,
        "Rendement mesuré (%)": rendement_mesure * 100,
        "Rendement corrigé (%)": rendement_corrige * 100,
        "Horodatage": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    fichier_excel = "historique.xlsx"
    df = pd.DataFrame([donnees])

    if os.path.exists(fichier_excel):
        ancien = pd.read_excel(fichier_excel)
        df = pd.concat([ancien, df], ignore_index=True)

    df.to_excel(fichier_excel, index=False)
    st.success(f"✅ Données enregistrées dans *{fichier_excel}*")
