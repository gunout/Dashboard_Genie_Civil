# moment_force_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import sympy as sp
import math

# Configuration de la page
st.set_page_config(
    page_title="Calcul des Moments de Forces - Ouvrages d'Art",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #2E86AB, #A23B72, #F18F01);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        color: #2E86AB;
        border-bottom: 2px solid #A23B72;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .calculation-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .result-box {
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .formula-box {
        background-color: #f1f3f4;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #F18F01;
        font-family: 'Courier New', monospace;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class MomentForceCalculator:
    def __init__(self):
        self.forces = []
        self.materials = {
            "Béton C25/30": {"E": 30e9, "fc": 25e6, "weight": 2500},
            "Béton C30/37": {"E": 33e9, "fc": 30e6, "weight": 2500},
            "Acier S235": {"E": 210e9, "fy": 235e6, "weight": 7850},
            "Acier S355": {"E": 210e9, "fy": 355e6, "weight": 7850},
            "Acier S500": {"E": 210e9, "fy": 500e6, "weight": 7850},
            "Bois Classe C24": {"E": 11e9, "fm": 24e6, "weight": 420}
        }
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏗️ CALCUL DES MOMENTS DE FORCES - OUVRAGES D\'ART</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("**Outil professionnel pour le calcul et l'analyse des moments de forces dans les structures**")
        
        st.markdown("---")
    
    def create_sidebar(self):
        """Crée la sidebar avec les paramètres généraux"""
        st.sidebar.markdown("## ⚙️ PARAMÈTRES GÉNÉRAUX")
        
        # Sélection du type de structure
        structure_type = st.sidebar.selectbox(
            "Type de structure:",
            ["Poutre simple", "Poutre continue", "Portique", "Dalle", "Poteau", "Fondation"]
        )
        
        # Unités
        unit_system = st.sidebar.radio(
            "Système d'unités:",
            ["SI (m, N, Pa)", "Metric (cm, kN, MPa)"]
        )
        
        # Matériau
        material = st.sidebar.selectbox(
            "Matériau principal:",
            list(self.materials.keys())
        )
        
        # Coefficient de sécurité
        safety_factor = st.sidebar.slider(
            "Coefficient de sécurité γ:",
            min_value=1.0,
            max_value=2.0,
            value=1.5,
            step=0.1
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 OPTIONS D'AFFICHAGE")
        
        show_stress = st.sidebar.checkbox("Afficher les contraintes", value=True)
        show_deformation = st.sidebar.checkbox("Afficher les déformations", value=True)
        
        return {
            'structure_type': structure_type,
            'unit_system': unit_system,
            'material': material,
            'safety_factor': safety_factor,
            'show_stress': show_stress,
            'show_deformation': show_deformation
        }
    
    def calculate_moment_force(self, force, distance, angle=90):
        """Calcule le moment d'une force par rapport à un point"""
        # Conversion de l'angle en radians
        angle_rad = math.radians(angle)
        
        # Composante perpendiculaire de la force
        force_perp = force * math.sin(angle_rad)
        
        # Moment = Force × Distance
        moment = force_perp * distance
        
        return moment, force_perp
    
    def calculate_section_properties(self, width, height, section_type="rectangulaire"):
        """Calcule les propriétés de la section"""
        if section_type == "rectangulaire":
            area = width * height
            inertia = (width * height**3) / 12
            module_inertie = inertia / (height / 2)
        elif section_type == "circulaire":
            diameter = width
            area = (math.pi * diameter**2) / 4
            inertia = (math.pi * diameter**4) / 64
            module_inertie = inertia / (diameter / 2)
        elif section_type == "en I":
            # Simplifié pour l'exemple
            area = width * height * 0.8
            inertia = (width * height**3) / 12 * 0.7
            module_inertie = inertia / (height / 2)
        
        return area, inertia, module_inertie
    
    def create_force_input_section(self):
        """Section de saisie des forces"""
        st.markdown('<h3 class="section-header">📥 SAISIE DES FORCES ET CHARGES</h3>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Forces ponctuelles")
            
            with st.form("force_input_form"):
                col_f1, col_f2, col_f3 = st.columns(3)
                
                with col_f1:
                    force_value = st.number_input("Intensité (kN):", min_value=0.0, value=10.0, step=1.0)
                
                with col_f2:
                    distance = st.number_input("Distance (m):", min_value=0.0, value=2.0, step=0.5)
                
                with col_f3:
                    angle = st.number_input("Angle (°):", min_value=0.0, max_value=180.0, value=90.0, step=5.0)
                
                submitted = st.form_submit_button("Ajouter la force")
                
                if submitted and force_value > 0:
                    moment, force_perp = self.calculate_moment_force(force_value * 1000, distance, angle)
                    self.forces.append({
                        'type': 'ponctuelle',
                        'valeur': force_value,
                        'distance': distance,
                        'angle': angle,
                        'moment': moment,
                        'force_perp': force_perp
                    })
                    st.success(f"Force ajoutée! Moment = {moment/1000:.2f} kN.m")
        
        with col2:
            st.subheader("Charges réparties")
            
            with st.form("distributed_load_form"):
                col_d1, col_d2, col_d3 = st.columns(3)
                
                with col_d1:
                    load_value = st.number_input("Charge (kN/m):", min_value=0.0, value=5.0, step=1.0)
                
                with col_d2:
                    start_pos = st.number_input("Début (m):", min_value=0.0, value=0.0, step=0.5)
                
                with col_d3:
                    end_pos = st.number_input("Fin (m):", min_value=0.0, value=4.0, step=0.5)
                
                submitted_load = st.form_submit_button("Ajouter la charge répartie")
                
                if submitted_load and load_value > 0 and end_pos > start_pos:
                    length = end_pos - start_pos
                    force_equiv = load_value * length
                    moment_equiv = force_equiv * (start_pos + length/2)
                    
                    self.forces.append({
                        'type': 'répartie',
                        'valeur': load_value,
                        'debut': start_pos,
                        'fin': end_pos,
                        'longueur': length,
                        'force_equiv': force_equiv,
                        'moment_equiv': moment_equiv
                    })
                    st.success(f"Charge répartie ajoutée! Force équivalente = {force_equiv:.2f} kN")
        
        # Affichage des forces enregistrées
        if self.forces:
            st.markdown("#### 📋 FORCES ENREGISTRÉES")
            force_data = []
            for i, force in enumerate(self.forces):
                if force['type'] == 'ponctuelle':
                    force_data.append({
                        'Type': 'Ponctuelle',
                        'Valeur (kN)': force['valeur'],
                        'Distance (m)': force['distance'],
                        'Angle (°)': force['angle'],
                        'Moment (kN.m)': force['moment'] / 1000
                    })
                else:
                    force_data.append({
                        'Type': 'Répartie',
                        'Valeur (kN/m)': force['valeur'],
                        'Début-Fin (m)': f"{force['debut']}-{force['fin']}",
                        'Longueur (m)': force['longueur'],
                        'Moment équiv. (kN.m)': force['moment_equiv']
                    })
            
            df_forces = pd.DataFrame(force_data)
            st.dataframe(df_forces, use_container_width=True)
    
    def create_moment_calculation_section(self):
        """Section de calcul des moments"""
        st.markdown('<h3 class="section-header">🧮 CALCUL DES MOMENTS</h3>', 
                   unsafe_allow_html=True)
        
        if not self.forces:
            st.warning("⚠️ Veuillez ajouter des forces d'abord")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="calculation-card">', unsafe_allow_html=True)
            st.subheader("📊 Calcul du moment total")
            
            # Calcul du moment résultant
            total_moment = 0
            total_force = 0
            
            for force in self.forces:
                if force['type'] == 'ponctuelle':
                    total_moment += force['moment']
                    total_force += force['force_perp']
                else:
                    total_moment += force['moment_equiv'] * 1000  # Conversion en N.m
                    total_force += force['force_equiv'] * 1000   # Conversion en N
            
            st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
            st.metric("Moment total", f"{total_moment/1000:.2f} kN.m")
            st.metric("Force résultante", f"{total_force/1000:.2f} kN")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("</div>")
            
            # Diagramme des moments
            st.markdown("#### 📈 Diagramme des moments")
            
            # Génération des points pour le diagramme
            x_points = np.linspace(0, 10, 100)
            moment_points = np.zeros_like(x_points)
            
            for force in self.forces:
                if force['type'] == 'ponctuelle':
                    for i, x in enumerate(x_points):
                        if x >= force['distance']:
                            moment_points[i] += force['moment'] / 1000  # kN.m
                else:
                    for i, x in enumerate(x_points):
                        if x >= force['debut']:
                            if x <= force['fin']:
                                # Charge répartie - calcul progressif
                                moment_points[i] += force['valeur'] * (x - force['debut'])**2 / 2
                            else:
                                moment_points[i] += force['moment_equiv']
            
            fig_moment = go.Figure()
            fig_moment.add_trace(go.Scatter(
                x=x_points, y=moment_points,
                mode='lines',
                name='Moment fléchissant',
                line=dict(color='#A23B72', width=3)
            ))
            fig_moment.update_layout(
                title="Diagramme du moment fléchissant",
                xaxis_title="Position (m)",
                yaxis_title="Moment (kN.m)",
                height=400
            )
            st.plotly_chart(fig_moment, use_container_width=True)
        
        with col2:
            st.markdown('<div class="calculation-card">', unsafe_allow_html=True)
            st.subheader("🔍 Analyse des contraintes")
            
            # Paramètres de la section
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                section_type = st.selectbox("Type de section:", 
                                          ["rectangulaire", "circulaire", "en I"])
                width = st.number_input("Largeur (m):", min_value=0.01, value=0.3, step=0.05)
            
            with col_s2:
                height = st.number_input("Hauteur (m):", min_value=0.01, value=0.5, step=0.05)
                material_props = st.selectbox("Matériau:", list(self.materials.keys()))
            
            # Calcul des propriétés
            area, inertia, module_inertie = self.calculate_section_properties(width, height, section_type)
            
            # Contrainte maximale
            if total_moment > 0:
                contrainte_max = total_moment / module_inertie
                
                # Contrainte admissible
                if "Acier" in material_props:
                    contrainte_adm = self.materials[material_props]["fy"] / 1.15  # Coefficient sécurité acier
                else:
                    contrainte_adm = self.materials[material_props]["fc"] / 1.5   # Coefficient sécurité béton
                
                st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                st.metric("Contrainte max", f"{contrainte_max/1e6:.2f} MPa")
                st.metric("Contrainte adm", f"{contrainte_adm/1e6:.2f} MPa")
                
                # Vérification
                if contrainte_max <= contrainte_adm:
                    st.success("✅ Section ADMISE")
                else:
                    st.error("❌ Section INSUFFISANTE")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("</div>")
            
            # Visualisation de la section
            st.markdown("#### 🏗️ Visualisation de la section")
            
            fig_section = go.Figure()
            
            if section_type == "rectangulaire":
                fig_section.add_trace(go.Scatter(
                    x=[0, width, width, 0, 0],
                    y=[0, 0, height, height, 0],
                    fill="toself",
                    fillcolor='rgba(46, 134, 171, 0.6)',
                    line=dict(color='#2E86AB', width=2),
                    name="Section"
                ))
            elif section_type == "circulaire":
                # Approximation avec un polygone
                theta = np.linspace(0, 2*np.pi, 100)
                x_circle = width/2 + (width/2) * np.cos(theta)
                y_circle = height/2 + (height/2) * np.sin(theta)
                
                fig_section.add_trace(go.Scatter(
                    x=x_circle, y=y_circle,
                    fill="toself",
                    fillcolor='rgba(162, 59, 114, 0.6)',
                    line=dict(color='#A23B72', width=2),
                    name="Section"
                ))
            
            fig_section.update_layout(
                title=f"Section {section_type}",
                xaxis_title="Largeur (m)",
                yaxis_title="Hauteur (m)",
                yaxis=dict(scaleanchor="x", scaleratio=1),
                height=300
            )
            st.plotly_chart(fig_section, use_container_width=True)
    
    def create_structural_analysis(self):
        """Analyse structurelle avancée"""
        st.markdown('<h3 class="section-header">🔬 ANALYSE STRUCTURALE AVANCÉE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Flèche et déformation", "Stabilité", "Interaction des efforts"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Calcul de la flèche")
                
                # Paramètres pour le calcul de flèche
                longueur_poutre = st.number_input("Longueur de la poutre (m):", 
                                                min_value=1.0, value=6.0, step=0.5)
                
                material_def = st.selectbox("Matériau (déformation):", 
                                          list(self.materials.keys()))
                
                E = self.materials[material_def]["E"]
                
                if self.forces and longueur_poutre > 0:
                    # Calcul simplifié de la flèche maximale
                    # Pour une charge ponctuelle au centre
                    fleche_max = 0
                    for force in self.forces:
                        if force['type'] == 'ponctuelle':
                            # Formule pour charge au centre: f = (P*L³)/(48*E*I)
                            P = force['valeur'] * 1000  # N
                            # Estimation de l'inertie
                            I_est = 0.3 * 0.5**3 / 12  # Inertie estimée
                            fleche_force = (P * longueur_poutre**3) / (48 * E * I_est)
                            fleche_max += fleche_force
                    
                    fleche_adm = longueur_poutre / 500  # Flèche admissible
                    
                    st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                    st.metric("Flèche calculée", f"{fleche_max*1000:.2f} mm")
                    st.metric("Flèche admissible", f"{fleche_adm*1000:.2f} mm")
                    
                    if fleche_max <= fleche_adm:
                        st.success("✅ Flèche ADMISE")
                    else:
                        st.warning("⚠️ Flèche EXCESSIVE")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.subheader("Diagramme de déformation")
                
                # Simulation de la déformée
                x_def = np.linspace(0, 10, 50)
                deformation = 0.01 * np.sin(np.pi * x_def / 10)  # Forme sinusoïdale
                
                fig_def = go.Figure()
                fig_def.add_trace(go.Scatter(
                    x=x_def, y=deformation*1000,  # en mm
                    mode='lines',
                    name='Déformée',
                    line=dict(color='#F18F01', width=3)
                ))
                fig_def.add_trace(go.Scatter(
                    x=x_def, y=np.zeros_like(x_def),
                    mode='lines',
                    name='Position initiale',
                    line=dict(color='#2E86AB', width=2, dash='dash')
                ))
                fig_def.update_layout(
                    title="Diagramme de la déformée",
                    xaxis_title="Position (m)",
                    yaxis_title="Déformation (mm)",
                    height=400
                )
                st.plotly_chart(fig_def, use_container_width=True)
        
        with tab2:
            st.subheader("Analyse de stabilité")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Calcul du coefficient de sécurité
                charge_ultime = st.number_input("Charge ultime (kN):", 
                                              min_value=0.0, value=50.0, step=5.0)
                
                if self.forces:
                    charge_appliquee = sum([f['valeur'] for f in self.forces])
                    coeff_securite = charge_ultime / charge_appliquee if charge_appliquee > 0 else float('inf')
                    
                    st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                    st.metric("Coefficient de sécurité", f"{coeff_securite:.2f}")
                    
                    if coeff_securite >= 2.0:
                        st.success("✅ STABILITÉ EXCELLENTE")
                    elif coeff_securite >= 1.5:
                        st.info("🔶 STABILITÉ BONNE")
                    else:
                        st.error("🔴 STABILITÉ INSUFFISANTE")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.subheader("Mode de déversement")
                
                # Graphique de stabilité
                charge_range = np.linspace(0, charge_ultime, 50)
                deformation_range = 0.1 * (charge_range / charge_ultime)**2
                
                fig_stability = go.Figure()
                fig_stability.add_trace(go.Scatter(
                    x=deformation_range*1000, y=charge_range,
                    mode='lines',
                    name='Courbe charge-déformation',
                    line=dict(color='#A23B72', width=3)
                ))
                fig_stability.update_layout(
                    title="Courbe de stabilité",
                    xaxis_title="Déformation (mm)",
                    yaxis_title="Charge (kN)",
                    height=300
                )
                st.plotly_chart(fig_stability, use_container_width=True)
        
        with tab3:
            st.subheader("Interaction des efforts")
            
            # Diagramme d'interaction M-N
            N_range = np.linspace(-1000, 1000, 50)  # Effort normal
            M_range = 500 * (1 - (N_range/1000)**2)  # Moment résistant
            
            fig_interaction = go.Figure()
            fig_interaction.add_trace(go.Scatter(
                x=M_range, y=N_range,
                mode='lines',
                name='Courbe d\'interaction',
                line=dict(color='#2E86AB', width=3),
                fill='toself',
                fillcolor='rgba(46, 134, 171, 0.2)'
            ))
            
            # Point de calcul actuel
            if self.forces:
                M_calc = sum([f.get('moment', 0) for f in self.forces]) / 1000  # kN.m
                N_calc = 200  # Estimation d'effort normal
                
                fig_interaction.add_trace(go.Scatter(
                    x=[M_calc], y=[N_calc],
                    mode='markers',
                    name='Point de calcul',
                    marker=dict(color='red', size=10)
                ))
            
            fig_interaction.update_layout(
                title="Diagramme d'interaction Moment-Effort normal",
                xaxis_title="Moment (kN.m)",
                yaxis_title="Effort normal (kN)",
                height=400
            )
            st.plotly_chart(fig_interaction, use_container_width=True)
    
    def create_formulas_section(self):
        """Section des formules théoriques"""
        st.markdown('<h3 class="section-header">📚 FORMULES THÉORIQUES</h3>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔧 Moments de forces")
            st.markdown('<div class="formula-box">M = F × d × sin(θ)</div>', unsafe_allow_html=True)
            st.markdown("Où:")
            st.markdown("- **M** = Moment (N.m)")
            st.markdown("- **F** = Force (N)")
            st.markdown("- **d** = Distance (m)")
            st.markdown("- **θ** = Angle de la force (°)")
            
            st.markdown("#### 📐 Contrainte de flexion")
            st.markdown('<div class="formula-box">σ = M / (I/v)</div>', unsafe_allow_html=True)
            st.markdown("Où:")
            st.markdown("- **σ** = Contrainte (Pa)")
            st.markdown("- **M** = Moment (N.m)")
            st.markdown("- **I** = Inertie (m⁴)")
            st.markdown("- **v** = Distance à la fibre neutre (m)")
        
        with col2:
            st.markdown("#### 🏗️ Flèche des poutres")
            st.markdown("**Charge ponctuelle au centre:**")
            st.markdown('<div class="formula-box">f = (P × L³) / (48 × E × I)</div>', unsafe_allow_html=True)
            
            st.markdown("**Charge uniformément répartie:**")
            st.markdown('<div class="formula-box">f = (5 × q × L⁴) / (384 × E × I)</div>', unsafe_allow_html=True)
            
            st.markdown("#### 📊 Propriétés des sections")
            st.markdown("**Section rectangulaire:**")
            st.markdown('<div class="formula-box">I = (b × h³) / 12</div>', unsafe_allow_html=True)
            st.markdown('<div class="formula-box">W = (b × h²) / 6</div>', unsafe_allow_html=True)
    
    def generate_report(self):
        """Génère un rapport PDF (version corrigée sans caractères non-ASCII)"""
        # Simulation d'un rapport - en production utiliser reportlab
        report_content = "Rapport PDF simulation - En production, utiliser reportlab pour generer un vrai PDF"
        return report_content.encode('utf-8')
    
    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Header
        self.display_header()
        
        # Sidebar
        controls = self.create_sidebar()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📥 Saisie Forces", 
            "🧮 Calcul Moments", 
            "🔬 Analyse Structurale", 
            "📚 Formules",
            "💾 Export"
        ])
        
        with tab1:
            self.create_force_input_section()
        
        with tab2:
            self.create_moment_calculation_section()
        
        with tab3:
            self.create_structural_analysis()
        
        with tab4:
            self.create_formulas_section()
        
        with tab5:
            st.markdown("## 💾 Export des résultats")
            
            if self.forces:
                # Création du rapport
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📄 Télécharger le rapport (PDF)",
                        data=self.generate_report(),
                        file_name="rapport_moments.pdf",
                        mime="application/pdf"
                    )
                
                with col2:
                    # Export des données
                    force_data = []
                    for i, force in enumerate(self.forces):
                        if force['type'] == 'ponctuelle':
                            force_data.append({
                                'Type': 'Ponctuelle',
                                'Valeur_kN': force['valeur'],
                                'Distance_m': force['distance'],
                                'Angle_deg': force['angle'],
                                'Moment_kNm': force['moment'] / 1000
                            })
                        else:
                            force_data.append({
                                'Type': 'Répartie',
                                'Valeur_kN_m': force['valeur'],
                                'Debut_m': force['debut'],
                                'Fin_m': force['fin'],
                                'Moment_equiv_kNm': force['moment_equiv']
                            })
                    
                    df_export = pd.DataFrame(force_data)
                    csv_data = df_export.to_csv(index=False)
                    
                    st.download_button(
                        label="📊 Télécharger les données (CSV)",
                        data=csv_data,
                        file_name="donnees_moments.csv",
                        mime="text/csv"
                    )
            else:
                st.info("Ajoutez des forces pour pouvoir exporter les résultats")

# Lancement du dashboard
if __name__ == "__main__":
    calculator = MomentForceCalculator()
    calculator.run_dashboard()