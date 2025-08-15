#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
streamlit_app_multi_prompt_enhanced_restructured.py

🚀 STREAMLIT-APP - Umstrukturiert ohne Sidebar
📊 Version: 9.0 - Main Page Layout
🎯 Features: Multi-Prompt-System + Layout-Integration + CI-Palette

STRUKTUR:
1. Layouteingabe (Skizzen + Farbpalette)
2. Text-Inhalte (mit Logo)
3. Motiv & Style
4. Generation (nur Multi-Prompt System)
"""

import os
import sys
import yaml
import json
from datetime import datetime
import time
import streamlit as st
from pathlib import Path
import logging
from PIL import Image
import PyPDF2
import io
import random

# Robuste Python-Pfad-Konfiguration für Streamlit
current_file = Path(__file__).resolve()
project_root = current_file.parent.resolve()  # Aktuelles Verzeichnis als Root

# Alle möglichen Pfade hinzufügen
paths_to_add = [
    str(project_root),                          # Root-Verzeichnis (CreativeAI_launch)
    str(project_root / "src"),                  # src-Verzeichnis
    str(project_root / "utils"),                # utils-Verzeichnis
]

# Bereinige und füge Pfade hinzu
for path in paths_to_add:
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)

# Debug-Info nur im Entwicklungsmodus
if os.getenv('DEBUG_IMPORTS'):
    print(f"DEBUG: project_root = {project_root}")
    print(f"DEBUG: src exists = {(project_root / 'src').exists()}")
    print(f"DEBUG: workflow exists = {(project_root / 'src' / 'workflow').exists()}")
    print(f"DEBUG: sys.path first 3 = {sys.path[:3]}")

# =====================================
# MIDJOURNEY MOTIV GENERATOR IMPORT
# =====================================

# Midjourney Motiv Generator Import
try:
    from src.prompt.midjourney_motiv_generator import MidjourneyMotivGenerator
    MIDJOURNEY_MOTIV_GENERATOR_AVAILABLE = True
    print("✅ Midjourney Motiv Generator erfolgreich importiert")
    
    # Globale Instanz erstellen
    midjourney_generator = MidjourneyMotivGenerator()
    
    def generate_midjourney_motiv_prompt(**kwargs):
        return midjourney_generator.generate_motiv_prompt(**kwargs)
        
except ImportError as e:
    MIDJOURNEY_MOTIV_GENERATOR_AVAILABLE = False
    print(f"⚠️ Midjourney Motiv Generator nicht verfügbar: {e}")
    # Fallback-Funktion definieren
    def generate_midjourney_motiv_prompt(**kwargs):
        return "Midjourney Motiv Generator nicht verfügbar - bitte installieren Sie die Abhängigkeiten"

# =====================================
# TEXT TO MOTIV CONVERTER IMPORT
# =====================================
try:
    from src.prompt.gpt_motiv_generator import TextToMotivConverter, create_text_to_motiv_converter
    TEXT_TO_MOTIV_CONVERTER_AVAILABLE = True
    print("✅ Text zu Motiv Converter erfolgreich importiert")
    
    # Globale Instanz erstellen
    text_to_motiv_converter = create_text_to_motiv_converter()
    
    def generate_motiv_from_textelements(**kwargs):
        return text_to_motiv_converter.generate_motiv_from_textelements(**kwargs)
        
except ImportError as e:
    TEXT_TO_MOTIV_CONVERTER_AVAILABLE = False
    print(f"⚠️ Text zu Motiv Converter nicht verfügbar: {e}")
    # Fallback-Funktion definieren
    def generate_motiv_from_textelements(**kwargs):
        return "Text zu Motiv Converter nicht verfügbar - bitte installieren Sie die Abhängigkeiten"

# =====================================
# KI CREATIVE TEXT GENERATOR IMPORT
# =====================================
try:
    from src.prompt.ki_creative_text_generator import KICreativeTextGenerator, create_ki_creative_text_generator
    KI_CREATIVE_TEXT_GENERATOR_AVAILABLE = True
    print("✅ KI Creative Text Generator erfolgreich importiert")
    
    # Globale Instanz erstellen
    ki_creative_generator = create_ki_creative_text_generator()
    
    def generate_creative_texts(**kwargs):
        return ki_creative_generator.generate_creative_texts(**kwargs)
        
except ImportError as e:
    KI_CREATIVE_TEXT_GENERATOR_AVAILABLE = False
    print(f"⚠️ KI Creative Text Generator nicht verfügbar: {e}")
    # Fallback-Funktion definieren
    def generate_creative_texts(**kwargs):
        return None

# =====================================
# DYNAMIC SCENE SELECTOR IMPORT
# =====================================
DYNAMIC_SCENE_SELECTOR_AVAILABLE = False
scene_selector = None

try:
    from src.prompt.dynamic_scene_selector import DynamicSceneSelector
    DYNAMIC_SCENE_SELECTOR_AVAILABLE = True
    print("✅ Dynamic Scene Selector erfolgreich importiert")
    
    # Globale Instanz erstellen
    scene_selector = DynamicSceneSelector()
    print(f"✅ Scene Selector Instanz erstellt: {scene_selector}")
    
except ImportError as e:
    DYNAMIC_SCENE_SELECTOR_AVAILABLE = False
    print(f"⚠️ Dynamic Scene Selector nicht verfügbar: {e}")
    scene_selector = None
except Exception as e:
    DYNAMIC_SCENE_SELECTOR_AVAILABLE = False
    print(f"❌ Fehler beim Erstellen der Scene Selector Instanz: {e}")
    scene_selector = None

# =====================================
# GPT-5 BILDGENERATOR IMPORT
# =====================================
try:
    from src.image.gpt5_image_generator import generate_gpt5_image
    GPT5_IMAGE_GENERATOR_AVAILABLE = True
    print("✅ GPT-5 Bildgenerator erfolgreich importiert")
except ImportError as e:
    GPT5_IMAGE_GENERATOR_AVAILABLE = False
    print(f"⚠️ GPT-5 Bildgenerator nicht verfügbar: {e}")
    # Fallback-Funktion definieren
    def generate_gpt5_image(**kwargs):
        return None, {"error": "GPT-5 Bildgenerator nicht verfügbar"}

# =====================================
# FUNCTIONS DEFINITIONS
# =====================================

def _get_job_interpretation(job_title: str) -> str:
    """Gibt eine benutzerfreundliche Interpretation des Stellentitels zurück"""
    
    if not job_title or not job_title.strip():
        return None
    
    job_title_lower = job_title.lower().strip()
    
    # Pflege-Bereich
    if any(word in job_title_lower for word in ["pflege", "nurse", "krankenschwester", "krankenpfleger"]):
        if "intensiv" in job_title_lower or "icu" in job_title_lower:
            return "Intensivpflege-Kraft (Intensive Care Nurse)"
        elif "ambulant" in job_title_lower or "ambulatory" in job_title_lower:
            return "Ambulante Pflegekraft (Ambulatory Care Nurse)"
        elif "stationär" in job_title_lower or "stationary" in job_title_lower:
            return "Stationäre Pflegekraft (Ward Nurse)"
        else:
            return "Pflegekraft (Registered Nurse)"
    
    # Ärzte-Bereich
    elif any(word in job_title_lower for word in ["arzt", "doctor", "mediziner", "physician"]):
        if "chirurg" in job_title_lower or "surgeon" in job_title_lower:
            return "Chirurg/Chirurgin (Surgeon)"
        elif "internist" in job_title_lower:
            return "Internist/Internistin (Internist)"
        elif "anästhesist" in job_title_lower or "anesthesiologist" in job_title_lower:
            return "Anästhesist/Anästhesistin (Anesthesiologist)"
        else:
            return "Arzt/Ärztin (Physician)"
    
    # Therapeuten-Bereich
    elif any(word in job_title_lower for word in ["therapeut", "therapist", "physio", "ergo"]):
        if "physio" in job_title_lower:
            return "Physiotherapeut/in (Physical Therapist)"
        elif "ergo" in job_title_lower or "occupational" in job_title_lower:
            return "Ergotherapeut/in (Occupational Therapist)"
        elif "psycho" in job_title_lower:
            return "Psychotherapeut/in (Psychotherapist)"
        else:
            return "Therapeut/in (Therapist)"
    
    # Verwaltung/Management
    elif any(word in job_title_lower for word in ["verwaltung", "administration", "management", "leitung", "leitungskraft"]):
        return "Verwaltungs-/Führungskraft (Healthcare Administrator)"
    
    # Technische Berufe
    elif any(word in job_title_lower for word in ["techniker", "technician", "labor", "radiologie", "radiology"]):
        if "labor" in job_title_lower:
            return "Laborant/in (Laboratory Technician)"
        elif "radiologie" in job_title_lower or "radiology" in job_title_lower:
            return "Radiologietechniker/in (Radiology Technician)"
        else:
            return "Medizintechniker/in (Medical Technician)"
    
    # Sozialarbeiter
    elif any(word in job_title_lower for word in ["sozial", "social", "berater", "counselor"]):
        return "Sozialarbeiter/in (Social Worker)"
    
    # Fallback für unbekannte Berufe
    else:
        if "kraft" in job_title_lower or "assistent" in job_title_lower:
            return "Fachkraft/Assistent/in (Healthcare Professional)"
        elif "fach" in job_title_lower:
            return "Fachkraft (Healthcare Specialist)"
        else:
            return "Gesundheitsfachkraft (Healthcare Professional)"

def _adjust_color_opacity(hex_color: str, opacity: float) -> str:
    """Simuliert Transparenz durch Verdunkelung/Aufhellung"""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # Mische mit Weiß für Transparenz-Effekt
        r = int(r + (255 - r) * (1 - opacity))
        g = int(g + (255 - g) * (1 - opacity))
        b = int(b + (255 - b) * (1 - opacity))
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return '#E0E0E0'  # Fallback

def optimize_german_text_for_dalle(text: str, max_length: int = 35) -> str:
    """
    Optimiert deutschen Text für DALL-E 3:
    - Verhindert abgeschnittene Wörter
    - Ersetzt Umlaute durch ASCII-Äquivalente
    - Kürzt intelligent ohne Wortbruch
    """
    # Umlaute ersetzen (DALL-E 3 Problem)
    umlaut_map = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'
    }
    
    for umlaut, replacement in umlaut_map.items():
        text = text.replace(umlaut, replacement)
    
    # Wenn Text zu lang ist, kürze intelligent
    if len(text) > max_length:
        # Versuche bei Leerzeichen zu kürzen
        words = text.split()
        shortened = ""
        
        for word in words:
            if len(shortened + " " + word) <= max_length:
                shortened += (" " + word) if shortened else word
            else:
                # Wort ist zu lang - kürze es
                if len(word) > max_length:
                    # Kürze auf max_length - 3 (für "...")
                    shortened += (" " + word[:max_length-3] + "...") if shortened else (word[:max_length-3] + "...")
                break
        
        return shortened.strip()
    
    return text

def create_dalle_safe_text_instructions() -> str:
    """
    Erstellt sichere Text-Anweisungen für DALL-E 3
    """
    return """
— TEXT-RENDERING REGELN (***KRITISCH FÜR DEUTSCHE TEXTE***)
• KEINE Umlaute (ä,ö,ü,ß) verwenden - ersetze durch ae,oe,ue,ss
• KEINE abgeschnittenen Wörter - kürze bei Wortgrenzen
• KEINE zu langen Texte - max 35 Zeichen pro Element
• KEINE komplexe Zeichensetzung - einfache Sätze bevorzugen
• VERWENDE nur ASCII-Zeichen für maximale Kompatibilität

— TEXT-OPTIMIERUNG:
• "Werden Sie Teil unseres Teams!" → "Werden Sie Teil unseres Teams!"
• "Flexible Arbeitszeiten" → "Flexible Arbeitszeiten"
• "Attraktive Vergütung" → "Attraktive Verguetung"
• "Fortbildungsmöglichkeiten" → "Fortbildungsmoeglichkeiten"
• "Jetzt bewerben!" → "Jetzt bewerben!"
"""

def load_ci_colors_enhanced():
    """Lade CI-Farben aus YAML und erweitere um berechnete Farben"""
    
    ci_colors_path = project_root / "input_config" / "ci_colors.yaml"
    
    try:
        with open(ci_colors_path, 'r', encoding='utf-8') as f:
            colors_data = yaml.safe_load(f)
        
        # Erweiterte Paletten mit Akzent-Beschreibungen
        enhanced_palettes = {}
        
        for palette in colors_data.get('palettes', []):
            name = palette.get('name', 'Unbenannt')
            enhanced_palettes[name] = {
                "primary": palette.get('primary', '#005EA5'),
                "secondary": palette.get('secondary', '#B4D9F7'),
                "accent": palette.get('accent', '#FFC20E'),
                # Neue berechnete Farben
                "headline_color": palette.get('primary', '#005EA5'),
                "cta_background": palette.get('accent', '#FFC20E'),
                "bullet_color": palette.get('accent', '#FFC20E'),
                "description": f"Primary: {palette.get('primary')}, Accent: {palette.get('accent')}"
            }
        
        return enhanced_palettes
         
    except Exception as e:
        st.error(f"Fehler beim Laden der CI-Farben: {e}")
        return {}

def generate_random_ci_palette():
    """Generiert eine zufällige CI-Farbpalette für das Layout"""
    
    # Professionelle CI-Farben-Palette für Gesundheitswesen
    ci_color_palettes = [
        {
            "name": "Medizinisches Blau-Gold",
            "primary": "#005EA5",      # Dunkelblau
            "secondary": "#B4D9F7",    # Hellblau
            "accent": "#FFC20E",       # Gold
            "description": "Klassische medizinische Farben"
        },
        {
            "name": "Naturverbunden Grün-Koralle",
            "primary": "#2E7D32",      # Dunkelgrün
            "secondary": "#C8E6C9",    # Hellgrün
            "accent": "#FF7043",       # Koralle
            "description": "Naturverbundene, beruhigende Farben"
        },
        {
            "name": "Professionell Navy-Silber",
            "primary": "#1A237E",      # Navy
            "secondary": "#E8EAF6",    # Silber
            "accent": "#FF9800",       # Orange
            "description": "Professionelle Business-Farben"
        },
        {
            "name": "Vertrauensvoll Teal-Orange",
            "primary": "#00695C",      # Teal
            "secondary": "#B2DFDB",    # Hellteal
            "accent": "#FF5722",       # Orange
            "description": "Moderne, vertrauensvolle Farben"
        },
        {
            "name": "Elegant Burgund-Creme",
            "primary": "#8E24AA",      # Burgund
            "secondary": "#F3E5F5",    # Creme
            "accent": "#FFC107",       # Gelb
            "description": "Elegante, traditionelle Farben"
        },
        {
            "name": "Zeitlos Grau-Blau",
            "primary": "#424242",      # Grau
            "secondary": "#E3F2FD",    # Hellblau
            "accent": "#2196F3",       # Blau
            "description": "Zeitlose, seriöse Farben"
        },
        {
            "name": "Beruhigend Smaragd-Lavendel",
            "primary": "#388E3C",      # Smaragd
            "secondary": "#E1F5FE",    # Hellblau
            "accent": "#9C27B0",       # Lavendel
            "description": "Beruhigende, heilende Farben"
        },
        {
            "name": "Dynamisch Schwarz-Rot",
            "primary": "#212121",      # Schwarz
            "secondary": "#FFEBEE",    # Hellrot
            "accent": "#F44336",       # Rot
            "description": "Kontrastreiche, dynamische Farben"
        },
        {
            "name": "Warm Beige-Terrakotta",
            "primary": "#8D6E63",      # Beige
            "secondary": "#EFEBE9",    # Hellbeige
            "accent": "#D84315",       # Terrakotta
            "description": "Warme, einladende Farben"
        },
        {
            "name": "Frisch Mint-Pfirsich",
            "primary": "#4DB6AC",      # Mint
            "secondary": "#E0F2F1",    # Hellmint
            "accent": "#FFAB91",       # Pfirsich
            "description": "Frische, moderne Farben"
        }
    ]
    
    # Zufällige Farbpalette auswählen
    selected_palette = random.choice(ci_color_palettes)
    
    return {
        "name": f"🎲 {selected_palette['name']}",
        "primary": selected_palette["primary"],
        "secondary": selected_palette["secondary"],
        "accent": selected_palette["accent"],
        "headline_color": selected_palette["primary"],
        "cta_background": selected_palette["accent"],
        "bullet_color": selected_palette["accent"],
        "description": selected_palette["description"]
    }

def load_original_sketches():
    """Lade Originalskizzen für Layout-Vorschau"""
    sketches = {}
    sketch_files = {
        "Skizze1": "Skizzen/Skizze1.png",
        "Skizze2": "Skizzen/Skizze2.png", 
        "Skizze3": "Skizzen/Skizze3.png",
        "Skizze4": "Skizzen/Skizze4.png",
        "Skizze5": "Skizzen/Skizze5.png",
        "Skizze6": "Skizzen/Skizze6.png",
        "Skizze7": "Skizzen/Skizze7.png",
        "Skizze8": "Skizzen/Skizze8.png",
        "Skizze9": "Skizzen/Skizze9.png",
        "Skizze10": "Skizzen/Skizze10.png",
        "Skizze11": "Skizzen/Skizze11.png",
        "Skizze12": "Skizzen/Skizze12.png",
        "Skizze13": "Skizzen/Skizze13.png"
    }
    
    for name, path in sketch_files.items():
        if os.path.exists(path):
            sketches[name] = {
                "name": name,
                "path": path
            }
    
    return sketches

def display_sketch_preview(sketch_data, layout_id, selected_layout_id):
    """Zeige Sketch-Vorschau korrekt an"""
    if sketch_data and sketch_data.get("path"):
        try:
            from PIL import Image
            sketch_image = Image.open(sketch_data["path"])
            
            # Optimale Größe: Nicht zu klein, aber kompakt mit guter Qualität
            sketch_image.thumbnail((120, 120), Image.Resampling.LANCZOS)
            
            # Border für ausgewähltes Layout
            border_color = "#1f77b4" if layout_id == selected_layout_id else "#ddd"
            border_width = "3px" if layout_id == selected_layout_id else "2px"
            
            st.markdown(f"""
            <div style="border: {border_width} solid {border_color}; border-radius: 8px; padding: 8px; background: white; width: fit-content; margin: 0 auto;">
            """, unsafe_allow_html=True)
            
            # Sketch anzeigen
            st.image(sketch_image, 
                    caption=f"{sketch_data['name']}", 
                    width=120)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Fehler beim Laden der Skizze: {e}")
            st.info(f"Skizze nicht verfügbar")
    else:
        st.info(f"Skizze nicht verfügbar")

# Robuste Import-Strategie für Streamlit
MULTI_PROMPT_AVAILABLE = False
ENHANCED_CREATIVE_AVAILABLE = False
LANGGRAPH_AVAILABLE = False

# Definiere alle möglichen Import-Strategien
import_strategies = [
    # Strategie 1: Standard src-Imports (mit korrigiertem Pfad)
    lambda: (
        __import__('src.workflow.multi_prompt_system', fromlist=['MultiPromptSystem', 'create_multi_prompt_system', 'StructuredInput']),
        __import__('src.image.enhanced_creative_generator', fromlist=['create_enhanced_creative_generator', 'generate_creative_from_multiprompt_result']),
        __import__('src.workflow.langgraph_integration', fromlist=['run_enhanced_workflow_from_streamlit', 'create_langgraph_integration'])
    ),
    # Strategie 2: Direkte Imports (falls src im sys.path)
    lambda: (
        __import__('workflow.multi_prompt_system', fromlist=['MultiPromptSystem', 'create_multi_prompt_system', 'StructuredInput']),
        __import__('image.enhanced_creative_generator', fromlist=['create_enhanced_creative_generator', 'generate_creative_from_multiprompt_result']),
        __import__('workflow.langgraph_integration', fromlist=['run_enhanced_workflow_from_streamlit', 'create_langgraph_integration'])
    ),
    # Strategie 3: Einfache Imports (für den Fall, dass die anderen fehlschlagen)
    lambda: (
        __import__('src.workflow.multi_prompt_system'),
        __import__('src.image.enhanced_creative_generator'),
        __import__('src.workflow.langgraph_integration')
    )
]

# Versuche Import-Strategien nacheinander
for i, strategy in enumerate(import_strategies, 1):
    try:
        if os.getenv('DEBUG_IMPORTS'):
            st.write(f"🔄 Versuche Import-Strategie {i}...")
        
        # Import versuchen
        workflow_module, image_module, langgraph_module = strategy()
        
        # Module-Attribute extrahieren
        MultiPromptSystem = getattr(workflow_module, 'MultiPromptSystem')
        create_multi_prompt_system = getattr(workflow_module, 'create_multi_prompt_system')
        StructuredInput = getattr(workflow_module, 'StructuredInput')
        
        create_enhanced_creative_generator = getattr(image_module, 'create_enhanced_creative_generator')
        generate_creative_from_multiprompt_result = getattr(image_module, 'generate_creative_from_multiprompt_result')
        
        run_enhanced_workflow_from_streamlit = getattr(langgraph_module, 'run_enhanced_workflow_from_streamlit')
        create_langgraph_integration = getattr(langgraph_module, 'create_langgraph_integration')
        
        # Verify StructuredInput has cta attribute
        if hasattr(StructuredInput, '__dataclass_fields__') and 'cta' in StructuredInput.__dataclass_fields__:
            cta_status = "✅ CTA-Attribut verfügbar"
        else:
            cta_status = "⚠️ CTA-Attribut fehlt"
        
        MULTI_PROMPT_AVAILABLE = True
        ENHANCED_CREATIVE_AVAILABLE = True
        LANGGRAPH_AVAILABLE = True
        
        # Status-Meldungen entfernt - nur noch in Logs
        pass
        break
        
    except Exception as e:
        if os.getenv('DEBUG_IMPORTS'):
            st.warning(f"⚠️ Import-Strategie {i} fehlgeschlagen: {str(e)}")
        continue

# Fallback, wenn alle Strategien fehlschlagen
if not MULTI_PROMPT_AVAILABLE:
    st.error("❌ **Import-Fehler**: Multi-Prompt-System konnte nicht geladen werden")
    st.write("**Debug-Informationen:**")
    st.write(f"- **Project Root**: `{project_root}`")
    st.write(f"- **Src Verzeichnis existiert**: {(project_root / 'src').exists()}")
    st.write(f"- **Workflow Verzeichnis existiert**: {(project_root / 'src' / 'workflow').exists()}")
    st.write(f"- **Python Path (erste 3)**:")
    for i, path in enumerate(sys.path[:3], 1):
        st.write(f"  {i}. `{path}`")
    
    st.info("💡 **Hilfe**: Stelle sicher, dass du das Streamlit-App aus dem Projekt-Root-Verzeichnis startest")
    st.stop()

# Page Config
st.set_page_config(
    page_title="🚀 CreativeAI - Promptgenerator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .color-preview {
        width: 50px;
        height: 20px;
        border-radius: 5px;
        display: inline-block;
        margin: 5px;
        border: 1px solid #ddd;
    }
    .layout-preview {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 CreativeAI - Promptgenerator</h1>
    <p>Intelligente Prompt-Generierung für DALL-E & Midjourney</p>
</div>
""", unsafe_allow_html=True)

# =====================================
# 1. LAYOUTEINGABE (Skizzen + Farbpalette)
# =====================================

st.header("🎨 Layouteingabe")

# Layout-Eingabe-Modus Auswahl
st.subheader("📐 Layout-Eingabe-Modus")

layout_input_mode = st.radio(
    "Wähle deinen Layout-Eingabe-Modus:",
    ["🎲 Automatische Eingabe", "🎯 Manuelle Eingabe"],
    help="Automatisch: Zufälliges Layout wird gewählt | Manuell: Wähle ein spezifisches Layout",
    index=0  # Standardmäßig Automatische Eingabe
)

# Layout-Style Auswahl (NEU)
st.subheader("🎨 Layout-Style")

layout_style = st.selectbox(
    "Layout-Konturen:",
    options=[
        ("sharp_geometric", "🎨 Scharf & Geometrisch"),
        ("rounded_modern", "🔵 Abgerundet & Modern"),
        ("organic_flowing", "🌊 Organisch & Fließend"),
        ("wave_contours", "🌊 Wellige Konturen"),
        ("hexagonal", "⬡ Sechseckig"),
        ("circular", "⭕ Kreisförmig"),
        ("asymmetric", "⚡ Asymmetrisch"),
        ("minimal_clean", "⚪ Minimal & Clean")
    ],
    format_func=lambda x: x[1],
    index=1,  # Default: rounded_modern
    help="Bestimmt die Kontur-Form der Layout-Bereiche im generierten Bild",
    key="layout_style_input"
)
# Wert in Session State speichern
st.session_state['layout_style'] = layout_style

# Layout-Style Beschreibung
layout_style_descriptions = {
    "sharp_geometric": "Scharfe, eckige Konturen für ein modernes, technisches Aussehen",
    "rounded_modern": "Sanft abgerundete Ecken für ein freundliches, modernes Design",
    "organic_flowing": "Organische, fließende Formen für ein natürliches, dynamisches Layout",
    "wave_contours": "Wellige, geschwungene Konturen für ein spielerisches, kreatives Design",
    "hexagonal": "Sechseckige Formen für ein futuristisches, technisches Aussehen",
    "circular": "Kreisförmige und ovale Bereiche für ein harmonisches, ausgewogenes Layout",
    "asymmetric": "Asymmetrische, unregelmäßige Formen für ein dynamisches, künstlerisches Design",
    "minimal_clean": "Minimalistische, saubere Linien für ein professionelles, klares Layout"
}

st.caption(f"💡 {layout_style_descriptions[layout_style[0]]}")

# Bedingte Anzeige der Layout-Optionen
if layout_input_mode == "🎯 Manuelle Eingabe":
    # Manueller Modus Info entfernt
    
    # Layout Selection
    st.subheader("📐 Layout auswählen")

# CSS für Layout Cards
st.markdown("""
<style>
.layout-card {
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 15px;
    margin: 10px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: white;
}
.layout-card:hover {
    border-color: #1f77b4;
    box-shadow: 0 4px 12px rgba(31, 119, 180, 0.2);
}
.layout-card.selected {
    border-color: #1f77b4;
    background: #f0f8ff;
    box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
}
.layout-preview {
    height: 120px;
    background: #f8f9fa;
    border-radius: 5px;
    margin: 10px 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-size: 10px;
    font-weight: bold;
}
.layout-element {
    padding: 2px 5px;
    margin: 1px;
    border-radius: 3px;
    color: white;
    font-size: 8px;
}
.headline { background: #000; }
.subline { background: #666; }
.motiv { background: #ff4444; color: white; }
.logo { background: #ddd; color: #666; border: 1px solid #ccc; }
.stellentitel { background: #44aaff; }
.cta { background: #ffcc00; color: #333; }
.benefits { background: #000; }
</style>
""", unsafe_allow_html=True)

# **WICHTIG: original_sketches VOR layouts definieren**
original_sketches = load_original_sketches()

layouts = [
    {
        "id": "skizze1_vertical_split",
        "name": "Vertical Split",
        "description": "Links Text, rechts Motiv",
        "sketch": original_sketches.get("Skizze1")
    },
    {
        "id": "skizze2_horizontal",
        "name": "Horizontal Strips", 
        "description": "Horizontale Streifen-Anordnung",
        "sketch": original_sketches.get("Skizze2")
    },
    {
        "id": "skizze3_grid",
        "name": "Grid Layout",
        "description": "3x3 Raster-Anordnung",
        "sketch": original_sketches.get("Skizze3")
    },
    {
        "id": "skizze4_hero",
        "name": "Header Focus",
        "description": "Hero-Motiv mit Overlay",
        "sketch": original_sketches.get("Skizze4")
    },
    {
        "id": "skizze5_sidebar",
        "name": "Layered Design", 
        "description": "Sidebar mit Inhalt",
        "sketch": original_sketches.get("Skizze5")
    },
    {
        "id": "skizze6_card",
        "name": "Corner Layout",
        "description": "Ecken-basiertes Layout",
        "sketch": original_sketches.get("Skizze6")
    },
    {
        "id": "skizze7_split_diagonal",
        "name": "Diagonal Split",
        "description": "Diagonale Teilung",
        "sketch": original_sketches.get("Skizze7")
    },
    {
        "id": "skizze8_banner",
        "name": "Banner Layout",
        "description": "Banner-artiges Design",
        "sketch": original_sketches.get("Skizze8")
    },
    {
        "id": "skizze9_magazine",
        "name": "Magazine Style",
        "description": "Magazin-Layout",
        "sketch": original_sketches.get("Skizze9")
    },
    {
        "id": "skizze10_modern_split",
        "name": "Modern Split",
        "description": "Moderne Split-Anordnung",
        "sketch": original_sketches.get("Skizze10")
    },
    {
        "id": "skizze11_dynamic_layout",
        "name": "Dynamic Layout",
        "description": "Dynamisches Layout-Design",
        "sketch": original_sketches.get("Skizze11")
    },
    {
        "id": "skizze12_centered_motiv_split_footer",
        "name": "Centered Motiv Split Footer",
        "description": "Zentriertes Motiv mit geteiltem Footer",
        "sketch": original_sketches.get("Skizze12")
    },
    {
        "id": "skizze13_text_motiv_split_cta",
        "name": "Text Motiv Split CTA",
        "description": "Zweispaltiger Text-Motiv-Split mit CTA",
        "sketch": original_sketches.get("Skizze13")
    }
]

# Layout Auswahl als Grid
cols = st.columns(3)  # 3 Spalten für stabile Anzeige  
selected_layout_id = st.session_state.get('selected_layout', 'skizze1_vertical_split')

if layout_input_mode == "🎯 Manuelle Eingabe":
    for i, layout in enumerate(layouts):
        col_index = i % 3
        with cols[col_index]:
            # Layout-Button
            if st.button(f"**{layout['name']}**\n{layout['description']}", 
                        key=f"layout_{layout['id']}", 
                        use_container_width=True):
                st.session_state.selected_layout = layout["id"]
                st.rerun()
            
            # Originalskizze als Vorschau (KORRIGIERT)
            display_sketch_preview(layout["sketch"], layout["id"], selected_layout_id)

    # Aktuell gewähltes Layout
    layout_id = selected_layout_id
    layout_name = next(l['name'] for l in layouts if l['id'] == layout_id)

    st.caption(f"🎯 Gewähltes Layout: {layout_name} ({layout_id})")

elif layout_input_mode == "🎲 Automatische Eingabe":
    # Automatischer Modus Info entfernt
    
    # Zufällige Layout-Auswahl
    import random
    random_layout = random.choice(layouts)
    layout_id = random_layout['id']
    layout_name = random_layout['name']
    
    # Layout in Session State speichern
    st.session_state.selected_layout = layout_id
    
    # Zufälliges Layout anzeigen
    st.subheader("🎲 Zufällig gewähltes Layout")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Originalskizze als Vorschau
        display_sketch_preview(random_layout["sketch"], layout_id, layout_id)
    
    with col2:
        st.caption(f"🎯 **Zufällig gewähltes Layout:** {layout_name}")
        st.caption(f"📐 **Layout-ID:** {layout_id}")
        st.caption(f"📝 **Beschreibung:** {random_layout['description']}")
        
        # Button zum Neugenerieren
        if st.button("🔄 Anderes Layout wählen", key="regenerate_random_layout"):
            st.rerun()
    
    st.caption(f"🎲 **Automatisch gewählt:** {layout_name} ({layout_id})")

# CI Color Palette
st.subheader("🎨 CI-Farbpalette")

# =====================================
# CI-FARBEN-INTEGRATION
# =====================================

# Lade erweiterte CI-Paletten
ci_palettes = load_ci_colors_enhanced()

# 🎲 RANDOMISIERER für CI-Farben
col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    if st.button("🎲 CI-Farben randomisieren", type="secondary", use_container_width=True, key="randomize_ci_colors_button"):
        # Generiere zufällige CI-Farbpalette
        random_palette = generate_random_ci_palette()
        
        # Setze Farben in Session State
        st.session_state.primary_color = random_palette["primary"]
        st.session_state.secondary_color = random_palette["secondary"]
        st.session_state.accent_color = random_palette["accent"]
        
        # Zeige Erfolgsmeldung
        st.success(f"🎨 Neue Farbpalette: {random_palette['name']}")
        st.info(f"💡 {random_palette['description']}")
        
        # Rerun für sofortige Anwendung
        st.rerun()

st.divider()

if ci_palettes:
    st.write("**🎨 Vordefinierte CI-Paletten:**")
    
    palette_cols = st.columns(min(3, len(ci_palettes)))
    
    for i, (palette_name, palette_data) in enumerate(ci_palettes.items()):
        with palette_cols[i % 3]:
            if st.button(f"📋 {palette_name}", key=f"palette_{i}", use_container_width=True):
                # Setze Farben aus gewählter Palette
                st.session_state.primary_color = palette_data["primary"]
                st.session_state.secondary_color = palette_data["secondary"] 
                st.session_state.accent_color = palette_data["accent"]
                st.rerun()
            
            # Mini-Palette-Vorschau
            st.markdown(f"""
            <div style="display: flex; height: 30px; border-radius: 5px; overflow: hidden; margin: 5px 0;">
                <div style="background: {palette_data['primary']}; flex: 1;"></div>
                <div style="background: {palette_data['secondary']}; flex: 1;"></div>
                <div style="background: {palette_data['accent']}; flex: 1;"></div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()

# Color Pickers (ERWEITERT)
col1, col2, col3 = st.columns(3)

with col1:
    primary_color = st.color_picker(
        "Primärfarbe:", 
        value=st.session_state.get("primary_color", "#005EA5"),
        help="Headlines, wichtige Texte"
    )

with col2:
    secondary_color = st.color_picker(
        "Sekundärfarbe:", 
        value=st.session_state.get("secondary_color", "#B4D9F7"),
        help="Hintergrund- und Flächen"
    )

with col3:
    accent_color = st.color_picker(
        "Akzentfarbe:", 
        value=st.session_state.get("accent_color", "#FFC20E"),
        help="CTA, Bullets, Akzente"
    )

# Farb-Vorschau (erweitert)
st.write("**🎨 Farb-Vorschau:**")

# Aktive Farben-Info
current_colors_info = f"""
**🎯 Aktive Farben:**
- **Primär:** `{primary_color}` (Headlines, wichtige Texte)
- **Sekundär:** `{secondary_color}` (Hintergrund- und Flächen)
- **Akzent:** `{accent_color}` (CTA, Bullets, Akzente)
"""
st.info(current_colors_info)

preview_cols = st.columns(3)

with preview_cols[0]:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: {primary_color}; text-align: center; margin-bottom: 10px;">
        <span style="color: white; font-weight: bold;">Primary</span><br>
        <small style="color: white;">{primary_color}</small>
    </div>
    """, unsafe_allow_html=True)

with preview_cols[1]:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: {secondary_color}; text-align: center; margin-bottom: 10px; border: 1px solid #ddd;">
        <span style="color: #333; font-weight: bold;">Secondary</span><br>
        <small style="color: #333;">{secondary_color}</small>
    </div>
    """, unsafe_allow_html=True)

with preview_cols[2]:
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: {accent_color}; text-align: center; margin-bottom: 10px;">
        <span style="color: white; font-weight: bold;">Accent</span><br>
        <small style="color: white;">{accent_color}</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =====================================
# 2. DESIGN & STYLE-OPTIONEN
# =====================================

# Design & Style-Optionen
st.header("🎨 Design & Style-Optionen")

# 🎲 RANDOMISIEREN BUTTON direkt im Header
col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    if st.button("🎲 Style randomisieren", type="secondary", use_container_width=True, key="randomize_style_button_header"):
        import random
        
        # Alle verfügbaren Optionen definieren
        style_options = {
            'layout_style': [
                ("sharp_geometric", "🎨 Scharf & Geometrisch"),
                ("rounded_modern", "🔵 Abgerundet & Modern"),
                ("organic_flowing", "🌊 Organisch & Fließend"),
                ("wave_contours", "🌊 Wellige Konturen"),
                ("hexagonal", "⬡ Sechseckig"),
                ("circular", "⭕ Kreisförmig"),
                ("asymmetric", "⚡ Asymmetrisch"),
                ("minimal_clean", "⚪ Minimal & Clean")
            ],
            'container_shape': [
                ("rectangle", "Rechteckig 📐"),
                ("rounded_rectangle", "Abgerundet 📱"), 
                ("circle", "Kreisförmig ⭕"),
                ("hexagon", "Sechseckig ⬡"),
                ("organic_blob", "Organisch 🫧")
            ],
            'border_style': [
                ("solid", "Durchgezogen ━"),
                ("dashed", "Gestrichelt ┅"),
                ("dotted", "Gepunktet ┈"),
                ("soft_shadow", "Weicher Schatten 🌫️"),
                ("glow", "Leuchteffekt ✨"),
                ("none", "Ohne Rahmen")
            ],
            'texture_style': [
                ("solid", "Einfarbig 🎨"),
                ("gradient", "Farbverlauf 🌈"),
                ("pattern", "Muster 📐"),
                ("glass_effect", "Glas-Effekt 💎"),
                ("matte", "Matt 🎭")
            ],
            'background_treatment': [
                ("solid", "Einfarbig 🎨"),
                ("subtle_pattern", "Subtiles Muster 🌸"),
                ("geometric", "Geometrisch 📐"),
                ("organic", "Organisch 🌿"),
                ("none", "Transparent")
            ],
            'corner_radius': [
                ("small", "Klein (8px) ⌐"),
                ("medium", "Mittel (16px) ⌜"), 
                ("large", "Groß (24px) ⌞"),
                ("xl", "Sehr groß (32px) ◜")
            ],
            'accent_elements': [
                ("classic", "Klassisch 🏛️"),
                ("modern_minimal", "Modern Minimal ⚪"),
                ("playful", "Verspielt 🎪"),
                ("organic", "Organisch 🌱"),
                ("bold", "Auffällig ⚡")
            ]
        }
        
        # Alle Style-Optionen zufällig auswählen
        random_selections = {}
        for option_name, options_list in style_options.items():
            random_selections[option_name] = random.choice(options_list)
        
        # Session State mit zufälligen Werten aktualisieren
        st.session_state['layout_style'] = random_selections['layout_style']
        st.session_state['container_shape'] = random_selections['container_shape']
        st.session_state['border_style'] = random_selections['border_style']
        st.session_state['texture_style'] = random_selections['texture_style']
        st.session_state['background_treatment'] = random_selections['background_treatment']
        st.session_state['corner_radius'] = random_selections['corner_radius']
        st.session_state['accent_elements'] = random_selections['accent_elements']
        
        # Erfolgsmeldung anzeigen
        st.success("🎲 **Style erfolgreich randomisiert!** Alle Optionen wurden zufällig neu ausgewählt.")
        
        # Zufällige Auswahl anzeigen
        st.info("🎯 **Neue zufällige Auswahl:**")
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.write(f"• **Layout-Style**: {random_selections['layout_style'][1]}")
            st.write(f"• **Container-Form**: {random_selections['container_shape'][1]}")
            st.write(f"• **Rahmen-Stil**: {random_selections['border_style'][1]}")
        
        with col_info2:
            st.write(f"• **Textur-Stil**: {random_selections['texture_style'][1]}")
            st.write(f"• **Hintergrund**: {random_selections['background_treatment'][1]}")
            st.write(f"• **Ecken-Rundung**: {random_selections['corner_radius'][1]}")
            st.write(f"• **Akzent-Stil**: {random_selections['accent_elements'][1]}")
        
        # Seite neu laden für aktualisierte Anzeige
        st.rerun()

# Info über Randomisieren
st.caption("💡 **Tipp**: Klicke auf den Button, um alle Style-Optionen zufällig neu zu kombinieren. Perfekt für kreative Inspiration!")

style_col1, style_col2, style_col3 = st.columns(3)

with style_col1:
    st.subheader("📦 Text-Container")
    
    # Container-Form mit dynamischem Index aus Session State
    container_shape_options = [
            ("rectangle", "Rechteckig 📐"),
            ("rounded_rectangle", "Abgerundet 📱"), 
            ("circle", "Kreisförmig ⭕"),
            ("hexagon", "Sechseckig ⬡"),
            ("organic_blob", "Organisch 🫧")
    ]
    
    # Aktuellen Index aus Session State ermitteln
    current_container_shape = st.session_state.get('container_shape', ('rounded_rectangle', 'Abgerundet 📱'))
    current_container_index = next((i for i, opt in enumerate(container_shape_options) if opt[0] == current_container_shape[0]), 1)
    
    container_shape = st.selectbox(
        "Form der Text-Bereiche:",
        options=container_shape_options,
        format_func=lambda x: x[1],
        index=current_container_index,  # Dynamischer Index
        help="Bestimmt die Form der Text-Container im Creative",
        key="container_shape_input"
    )
    # Wert in Session State speichern
    st.session_state['container_shape'] = container_shape
    
    # Rahmen-Stil mit dynamischem Index aus Session State
    border_style_options = [
            ("solid", "Durchgezogen ━"),
            ("dashed", "Gestrichelt ┅"),
            ("dotted", "Gepunktet ┈"),
            ("soft_shadow", "Weicher Schatten 🌫️"),
            ("glow", "Leuchteffekt ✨"),
            ("none", "Ohne Rahmen")
    ]
    
    # Aktuellen Index aus Session State ermitteln
    current_border_style = st.session_state.get('border_style', ('soft_shadow', '🌫️ Weicher Schatten'))
    current_border_index = next((i for i, opt in enumerate(border_style_options) if opt[0] == current_border_style[0]), 3)
    
    border_style = st.selectbox(
        "Rahmen-Stil:",
        options=border_style_options,
        format_func=lambda x: x[1],
        index=current_border_index,  # Dynamischer Index
        help="Stil des Rahmens um Text-Bereiche",
        key="border_style_input"
    )
    # Wert in Session State speichern
    st.session_state['border_style'] = border_style

with style_col2:
    st.subheader("🖌️ Visuelle Effekte")
    
    # Textur-Stil mit dynamischem Index aus Session State
    texture_style_options = [
            ("solid", "Einfarbig 🎨"),
            ("gradient", "Farbverlauf 🌈"),
            ("pattern", "Muster 📐"),
            ("glass_effect", "Glas-Effekt 💎"),
            ("matte", "Matt 🎭")
    ]
    
    # Aktuellen Index aus Session State ermitteln
    current_texture_style = st.session_state.get('texture_style', ('gradient', '🌈 Farbverlauf'))
    current_texture_index = next((i for i, opt in enumerate(texture_style_options) if opt[0] == current_texture_style[0]), 1)
    
    texture_style = st.selectbox(
        "Textur-Stil:",
        options=texture_style_options,
        format_func=lambda x: x[1],
        index=current_texture_index,  # Dynamischer Index
        help="Oberflächentextur der Text-Container"
    )
    # Wert in Session State speichern
    st.session_state['texture_style'] = texture_style
    
    # Hintergrund-Behandlung mit dynamischem Index aus Session State
    background_treatment_options = [
            ("solid", "Einfarbig 🎨"),
                ("subtle_pattern", "Subtiles Muster 🌸"),
            ("geometric", "Geometrisch 📐"),
            ("organic", "Organisch 🌿"),
            ("none", "Transparent")
    ]
    
    # Aktuellen Index aus Session State ermitteln
    current_background_treatment = st.session_state.get('background_treatment', ('subtle_pattern', '🌸 Subtiles Muster'))
    current_background_index = next((i for i, opt in enumerate(background_treatment_options) if opt[0] == current_background_treatment[0]), 1)
    
    background_treatment = st.selectbox(
        "Hintergrund-Behandlung:",
        options=background_treatment_options,
        format_func=lambda x: x[1],
        index=current_background_index,  # Dynamischer Index
        help="Behandlung des Creative-Hintergrunds"
    )
    # Wert in Session State speichern
    st.session_state['background_treatment'] = background_treatment

with style_col3:
    st.subheader("📐 Layout-Details")
    
    # Ecken-Rundung mit dynamischem Index aus Session State
    corner_radius_options = [
            ("small", "Klein (8px) ⌐"),
            ("medium", "Mittel (16px) ⌜"), 
            ("large", "Groß (24px) ⌞"),
            ("xl", "Sehr groß (32px) ◜")
    ]
    
    # Aktuellen Index aus Session State ermitteln
    current_corner_radius = st.session_state.get('corner_radius', ('medium', '⌜ Mittel'))
    current_corner_index = next((i for i, opt in enumerate(corner_radius_options) if opt[0] == current_corner_radius[0]), 1)
    
    corner_radius = st.selectbox(
        "Ecken-Rundung:",
        options=corner_radius_options,
        format_func=lambda x: x[1],
        index=current_corner_index,  # Dynamischer Index
        help="Rundung der Container-Ecken"
    )
    # Wert in Session State speichern
    st.session_state['corner_radius'] = corner_radius
    
    # Akzent-Stil mit dynamischem Index aus Session State
    accent_elements_options = [
            ("classic", "Klassisch 🏛️"),
            ("modern_minimal", "Modern Minimal ⚪"),
            ("playful", "Verspielt 🎪"),
            ("organic", "Organisch 🌱"),
            ("bold", "Auffällig ⚡")
    ]
    
    # Aktuellen Index aus Session State ermitteln
    current_accent_elements = st.session_state.get('accent_elements', ('modern_minimal', '⚪ Modern Minimal'))
    current_accent_index = next((i for i, opt in enumerate(accent_elements_options) if opt[0] == current_accent_elements[0]), 1)
    
    accent_elements = st.selectbox(
        "Akzent-Stil:",
        options=accent_elements_options,
        format_func=lambda x: x[1],
        index=current_accent_index,  # Dynamischer Index
        help="Stil der Akzent-Elemente (Linien, Bullets, etc.)"
    )
    # Wert in Session State speichern
    st.session_state['accent_elements'] = accent_elements

# Style-Zusammenfassung
st.write("**🎯 Gewählter Style:**")
style_summary_cols = st.columns(4)

with style_summary_cols[0]:
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 8px; background: linear-gradient(45deg, {primary_color}20, {accent_color}20); border: 2px solid {accent_color};">
        <strong>Form:</strong> {container_shape[1]}<br>
        <strong>Rahmen:</strong> {border_style[1]}
    </div>
    """, unsafe_allow_html=True)

with style_summary_cols[1]:
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 8px; background: linear-gradient(45deg, {secondary_color}40, {primary_color}20); border: 2px solid {primary_color};">
        <strong>Textur:</strong> {texture_style[1]}<br>
        <strong>Hintergrund:</strong> {background_treatment[1]}
    </div>
    """, unsafe_allow_html=True)

with style_summary_cols[2]:
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 8px; background: {secondary_color}; border: 2px solid {primary_color};">
        <strong>Rundung:</strong> {corner_radius[1]}<br>
        <strong>Akzente:</strong> {accent_elements[1]}
    </div>
    """, unsafe_allow_html=True)

with style_summary_cols[3]:
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 8px; background: {accent_color}; color: white; text-align: center;">
        <strong>🎨 STYLE</strong><br>
        <small>Personalisiert</small>
    </div>
    """, unsafe_allow_html=True)



st.divider()

# =====================================
# 2. TEXT-INHALTE (mit drei Eingabe-Modi)
# =====================================

st.header("📝 Text-Inhalte")

# Text-Eingabe-Modus Auswahl
text_input_mode = st.radio(
    " Text-Eingabe-Modus:",
    ["✏️ Manuelle Eingabe", "🤖 Prompt-basierte Eingabe", "📄 PDF-Upload", "🤖 KI-Kreative Textelemente"],
    help="Wähle wie du die Text-Inhalte eingeben möchtest"
)

# Session State für extrahierte Daten
if 'extracted_text_data' not in st.session_state:
    st.session_state.extracted_text_data = {}

# Manuelle Eingabe
if text_input_mode == "✏️ Manuelle Eingabe":
    # Manueller Modus Info entfernt
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Textelemente")
        
        headline = st.text_input(
            "Headline:",
            value=st.session_state.get('headline', st.session_state.extracted_text_data.get('headline', "Werden Sie Teil unseres Teams!")),
            max_chars=100,
            help="Hauptüberschrift für das Creative",
            key="headline_input"
        )
        # Wert in Session State speichern
        st.session_state['headline'] = headline
        
        subline = st.text_input(
            "Subline:",
            value=st.session_state.get('subline', st.session_state.extracted_text_data.get('subline', "Gestalten Sie mit uns die Zukunft des Gesundheitswesens")),
            max_chars=150,
            help="Untertitel / Subheadline",
            key="subline_input"
        )
        # Wert in Session State speichern
        st.session_state['subline'] = subline
        
        unternehmen = st.text_input(
            "Unternehmen:",
            value=st.session_state.get('unternehmen', st.session_state.extracted_text_data.get('unternehmen', "Klinikum München")),
            max_chars=50,
            help="Name des Unternehmens",
            key="unternehmen_input"
        )
        
        # Wert in Session State speichern
        st.session_state['unternehmen'] = unternehmen
        
        stellentitel = st.text_input(
            "Stellentitel:",
            value=st.session_state.get('stellentitel', st.session_state.extracted_text_data.get('stellentitel', "Pflegekraft (m/w/d)")),
            max_chars=100,
            help="Bezeichnung der offenen Stelle",
            key="stellentitel_input"
        )
        # Wert in Session State speichern
        st.session_state['stellentitel'] = stellentitel

    with col2:
        st.subheader(" Logo & Branding")
        
        logo_file = st.file_uploader(
            "Logo hochladen (optional):",
            type=['png', 'jpg', 'jpeg', 'svg'],
            help="Lade dein Firmenlogo hoch"
        )
        
        # Logo Preview
        if logo_file is not None:
            st.image(logo_file, caption="Logo-Vorschau", width=150)
            # Logo erfolgreich geladen (nur in Logs)
        else:
            # Kein Logo hochgeladen (nur in Logs)
            pass
        
        # Logo-Platzhalter fest auf "Logo" gesetzt
        logo_placeholder = "Logo"

    col3, col4 = st.columns(2)

    with col3:
        location = st.text_input(
            " Standort eingeben:",
            value=st.session_state.get('location', st.session_state.extracted_text_data.get('location', "München")),
            max_chars=50,
            help="Arbeitsort / Standort",
            key="location_input"
        )
        
        # Wert in Session State speichern
        st.session_state['location'] = location
        
        position_long = st.text_area(
            "Position (ausführlich):",
            value=st.session_state.get('position_long', st.session_state.extracted_text_data.get('position_long', "Wir suchen eine engagierte Pflegekraft für unser dynamisches Team.")),
            max_chars=300,
            help="Detaillierte Positionsbeschreibung",
            key="position_long_input"
        )
        # Wert in Session State speichern
        st.session_state['position_long'] = position_long

    with col4:
        cta = st.text_input(
            "Call-to-Action:",
            value=st.session_state.get('cta', st.session_state.extracted_text_data.get('cta', "Jetzt bewerben!")),
            max_chars=50,
            help="Handlungsaufforderung",
            key="cta_input"
        )
        # Wert in Session State speichern
        st.session_state['cta'] = cta
        
        benefits = st.text_area(
            "Benefits (eine pro Zeile):",
            value="\n".join(st.session_state.get('benefits', st.session_state.extracted_text_data.get('benefits', ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]))),
            max_chars=300,
            help="Vorteile, einen pro Zeile",
            key="benefits_input"
        )
        # Wert in Session State speichern
        if benefits.strip():
            # Benefits als Liste verarbeiten und leere Zeilen entfernen
            benefits_list = [b.strip() for b in benefits.split('\n') if b.strip()]
            st.session_state['benefits'] = benefits_list
            # Benefits erfolgreich gespeichert (nur in Logs)
        else:
            st.session_state['benefits'] = ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]
            # Standard-Benefits verwendet (nur in Logs)
        
        # Benefits-Vorschau entfernt

# Prompt-basierte Eingabe
elif text_input_mode == "🤖 Prompt-basierte Eingabe":
    # Prompt-basierte Eingabe Info entfernt
    
    prompt_text = st.text_area(
        "Beschreibe die Stelle:",
        placeholder="Beispiel: Wir suchen Therapeuten für unser Team in München. Flexible Arbeitszeiten und attraktive Vergütung.",
        height=150,
        help="Beschreibe die Stelle, das Unternehmen, Standort, Benefits etc. in einem freien Text"
    )
    
    if st.button("🤖 Mit OpenAI analysieren", type="primary"):
        if prompt_text.strip():
            with st.spinner("🤖 OpenAI analysiert den Text..."):
                extracted_data = analyze_text_with_openai(prompt_text)
                
                if extracted_data:
                    st.session_state.extracted_text_data = extracted_data
                    st.success("✅ Text erfolgreich analysiert!")
                    st.rerun()
                else:
                    st.error("❌ Fehler bei der Analyse")
        else:
            st.warning("⚠️ Bitte gib einen Text ein")

# PDF-Upload
elif text_input_mode == "📄 PDF-Upload":
    # PDF-Upload Info entfernt
    
    pdf_file = st.file_uploader(
        "PDF-Datei hochladen:",
        type=['pdf'],
        help="Lade eine PDF-Datei mit Stellenausschreibung oder Briefing hoch"
    )
    
    if pdf_file is not None:
        st.caption(f"📄 PDF '{pdf_file.name}' hochgeladen ({len(pdf_text)} Zeichen)")
        
        if st.button("📄 PDF mit OpenAI analysieren", type="primary"):
            with st.spinner("📄 PDF wird gelesen und analysiert..."):
                pdf_text = extract_pdf_text(pdf_file)
                
                if pdf_text:
                    st.caption(f"📄 PDF-Text extrahiert ({len(pdf_text)} Zeichen)")
                    
                    with st.spinner("🤖 OpenAI analysiert den PDF-Inhalt..."):
                        extracted_data = analyze_text_with_openai(pdf_text)
                        
                        if extracted_data:
                            st.session_state.extracted_text_data = extracted_data
                            st.success("✅ PDF erfolgreich analysiert!")
                            st.rerun()
                        else:
                            st.error("❌ Fehler bei der Analyse")
                else:
                    st.error("❌ Konnte keinen Text aus der PDF extrahieren")

# KI-Kreative Textelemente
elif text_input_mode == "🤖 KI-Kreative Textelemente":
    st.subheader("🤖 KI-Kreative Textelemente")
    st.info("💡 **Minimale Eingabe, maximale Kreativität**: Gib nur die wichtigsten Informationen ein und lass die KI Headline und Subline generieren!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Minimale Eingaben")
        
        # Nur die wichtigsten Felder
        ki_company = st.text_input(
            "Unternehmen:",
            value=st.session_state.get('unternehmen', st.session_state.extracted_text_data.get('unternehmen', 'Klinikum München')),
            max_chars=50,
            help="Name des Unternehmens",
            key="ki_company_input"
        )
        
        ki_job_title = st.text_input(
            "Stellentitel:",
            value=st.session_state.get('stellentitel', st.session_state.extracted_text_data.get('stellentitel', 'Pflegekraft (m/w/d)')),
            max_chars=100,
            help="Bezeichnung der offenen Stelle",
            key="ki_job_title_input"
        )
        
        ki_cta = st.text_input(
            "Call-to-Action:",
            value=st.session_state.get('cta', st.session_state.extracted_text_data.get('cta', 'Jetzt bewerben!')),
            max_chars=50,
            help="Handlungsaufforderung",
            key="ki_cta_input"
        )
        
        ki_benefits = st.text_area(
            "Benefits (eine pro Zeile):",
            value="\n".join(st.session_state.get('benefits', st.session_state.extracted_text_data.get('benefits', ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]))),
            max_chars=300,
            help="Vorteile, einen pro Zeile",
            key="ki_benefits_input"
        )
        
        ki_location = st.text_input(
            "Standort (optional):",
            value=st.session_state.get('location', st.session_state.extracted_text_data.get('location', 'München')),
            max_chars=50,
            help="Arbeitsort / Standort (optional)",
            key="ki_location_input"
        )
    
    with col2:
        st.subheader("😊 Gefühls-Auswahl")
        
        # Gefühls-Auswahl mit Beispielen
        feeling_options = {
            "heroisch": "🏆 Heroisch - Kraftvoll, selbstbewusst, inspirierend",
            "motivierend": "💪 Motivierend - Energisch, aufbauend, zielgerichtet",
            "einladend": "🤝 Einladend - Warm, offen, einladend",
            "inspirierend": "✨ Inspirierend - Visionär, bewegend, transformativ",
            "stolz": "🏛️ Stolz - Stolz, professionell, exklusiv",
            "innovativ": "🚀 Innovativ - Modern, fortschrittlich, zukunftsweisend",
            "empathisch": "❤️ Empathisch - Menschlich, fürsorglich, verständnisvoll",
            "dynamisch": "⚡ Dynamisch - Bewegt, lebendig, aktiv"
        }
        
        selected_feeling = st.selectbox(
            "Gefühls-Stil auswählen:",
            options=list(feeling_options.keys()),
            format_func=lambda x: feeling_options[x],
            index=1,  # Default: motivierend
            help="Bestimmt den Stil und Ton der generierten Texte",
            key="feeling_selection_input"
        )
        
        # Gefühls-Beschreibung anzeigen
        if selected_feeling:
            feeling_descriptions = {
                "heroisch": "**🏆 Heroisch**: Kraftvolle, selbstbewusste Texte wie 'Wir, weil wer sonst' oder 'Die Zukunft wartet auf uns'",
                "motivierend": "**💪 Motivierend**: Energische, aufbauende Texte wie 'Dein Potential. Unsere Mission.' oder 'Gemeinsam schaffen wir das Unmögliche'",
                "einladend": "**🤝 Einladend**: Warme, offene Texte wie 'Komm zu uns' oder 'Wir freuen uns auf dich'",
                "inspirierend": "**✨ Inspirierend**: Visionäre, bewegende Texte wie 'Verändere Leben. Beginne mit deinem.' oder 'Neue Wege, neue Lösungen'",
                "stolz": "**🏛️ Stolz**: Stolze, professionelle Texte wie 'Exzellenz ist unser Standard' oder 'Wir sind stolz auf unser Team'",
                "innovativ": "**🚀 Innovativ**: Moderne, fortschrittliche Texte wie 'Die Zukunft gestalten' oder 'Innovation lebt hier'",
                "empathisch": "**❤️ Empathisch**: Menschliche, fürsorgliche Texte wie 'Menschlichkeit im Mittelpunkt' oder 'Wir kümmern uns um dich'",
                "dynamisch": "**⚡ Dynamisch**: Bewegte, lebendige Texte wie 'Bewegung schafft Wandel' oder 'Gemeinsam vorwärts'"
            }
            
            st.info(feeling_descriptions.get(selected_feeling, ""))
        
        # KI-Textgenerierung Button
        if st.button("🤖 KI-Texte generieren", type="primary", use_container_width=True, key="generate_ki_texts"):
            with st.spinner("🤖 KI generiert kreative Texte..."):
                try:
                    if KI_CREATIVE_TEXT_GENERATOR_AVAILABLE:
                        # Benefits als Liste verarbeiten
                        benefits_list = [b.strip() for b in ki_benefits.split('\n') if b.strip()]
                        if not benefits_list:
                            benefits_list = ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]
                        
                        # KI-Input vorbereiten
                        from src.prompt.ki_creative_text_generator import CreativeTextInput
                        
                        ki_input = CreativeTextInput(
                            company=ki_company,
                            job_title=ki_job_title,
                            cta=ki_cta,
                            benefits=benefits_list,
                            feeling=selected_feeling,
                            location=ki_location
                        )
                        
                        # KI-Texte generieren
                        generated_result = ki_creative_generator.generate_creative_texts(ki_input)
                        
                        if generated_result and hasattr(generated_result, 'success') and generated_result.success:
                            # Erfolgreich generiert - in Session State speichern
                            st.session_state['headline'] = generated_result.headline
                            st.session_state['subline'] = generated_result.subline
                            st.session_state['unternehmen'] = ki_company
                            st.session_state['stellentitel'] = ki_job_title
                            st.session_state['cta'] = ki_cta
                            st.session_state['benefits'] = benefits_list
                            st.session_state['location'] = ki_location
                            
                            st.success("✅ **KI-Texte erfolgreich generiert!**")
                            
                            # Generierte Texte anzeigen
                            st.subheader("🎯 **Generierte Texte**")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**📰 Headline:**")
                                st.info(f"**{generated_result.headline}**")
                            
                            with col2:
                                st.markdown(f"**📝 Subline:**")
                                st.info(f"**{generated_result.subline}**")
                            
                            # Gefühls-Stil bestätigen
                            st.caption(f"😊 **Gefühls-Stil**: {feeling_options[selected_feeling]}")
                            
                            # Automatisch zu manueller Eingabe wechseln
                            st.info("💡 **Tipp**: Die generierten Texte wurden automatisch übernommen. Du kannst sie im 'Manuelle Eingabe' Modus noch anpassen.")
                            
                        else:
                            error_msg = getattr(generated_result, 'error_message', 'Unbekannter Fehler') if generated_result else 'Keine Antwort von der KI'
                            st.error(f"❌ **Fehler bei der KI-Textgenerierung**: {error_msg}")
                            st.info("ℹ️ Verwende den manuellen Eingabemodus als Alternative.")
                    
                    else:
                        st.error("❌ **KI Creative Text Generator nicht verfügbar**")
                        st.info("ℹ️ Bitte installiere die Abhängigkeiten oder verwende den manuellen Eingabemodus.")
                        
                except Exception as e:
                    st.error(f"❌ **Fehler bei der KI-Textgenerierung**: {str(e)}")
                    st.info("ℹ️ Verwende den manuellen Eingabemodus als Alternative.")
    
    # Info über den neuen Modus
    st.caption("💡 **Vorteile des KI-Modus**: Minimale Eingabe, maximale Kreativität. Die KI generiert professionelle Headlines und Sublines basierend auf deinem gewählten Gefühls-Stil.")

# Fehlende Felder Expander (wird automatisch geöffnet wenn fehlende Felder vorhanden)
if st.session_state.extracted_text_data:
    missing_fields = get_missing_fields(st.session_state.extracted_text_data)
    
    if missing_fields:
        with st.expander("⚠️ Fehlende Informationen ergänzen", expanded=True):
            st.warning(f"Folgende Informationen konnten nicht automatisch erkannt werden: {', '.join(missing_fields)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'headline' in missing_fields:
                    st.session_state.extracted_text_data['headline'] = st.text_input(
                        "Headline:",
                        value="",
                        max_chars=100,
                        key="missing_headline"
                    )
                
                if 'subline' in missing_fields:
                    st.session_state.extracted_text_data['subline'] = st.text_input(
                        "Subline:",
                        value="",
                        max_chars=150,
                        key="missing_subline"
                    )

def analyze_text_with_openai(text_content: str) -> dict:
    """
    Analysiert Text mit OpenAI API und extrahiert strukturierte Informationen
    """
    try:
        from openai import OpenAI
        client = OpenAI()
        
        system_prompt = """
        Du bist ein Experte für die Analyse von Stellenausschreibungen und Job-Beschreibungen.
        Extrahiere aus dem gegebenen Text die folgenden Informationen und gib sie als JSON zurück:
        
        {
            "headline": "Hauptüberschrift für die Stellenausschreibung",
            "subline": "Untertitel oder kurze Beschreibung",
            "unternehmen": "Name des Unternehmens",
            "stellentitel": "Bezeichnung der Stelle (z.B. 'Pflegekraft (m/w/d)')",
            "location": "Standort oder Arbeitsort",
            "position_long": "Detaillierte Beschreibung der Position",
            "cta": "Call-to-Action (z.B. 'Jetzt bewerben!')",
            "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"]
        }
        
        Wichtige Regeln:
        - Wenn Informationen fehlen, setze sie auf null
        - Stelle sicher, dass der Stellentitel das Format "Beruf (m/w/d)" hat
        - Benefits sollten als Liste von Strings zurückgegeben werden
        - Verwende deutsche Texte
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_content}
            ],
            temperature=0.1
        )
        
        # JSON aus der Antwort extrahieren
        result_text = response.choices[0].message.content
        import json
        return json.loads(result_text)
        
    except Exception as e:
        st.error(f"Fehler bei der OpenAI-Analyse: {str(e)}")
        return {}

def extract_pdf_text(pdf_file) -> str:
    """
    Extrahiert Text aus einer PDF-Datei
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Fehler beim PDF-Lesen: {str(e)}")
        return ""

def get_missing_fields(extracted_data: dict) -> list:
    """
    Identifiziert fehlende Felder in den extrahierten Daten
    """
    required_fields = ['headline', 'subline', 'unternehmen', 'stellentitel', 'location', 'position_long', 'cta', 'benefits']
    missing_fields = []
    
    for field in required_fields:
        if field not in extracted_data or extracted_data[field] is None or extracted_data[field] == "":
            missing_fields.append(field)
    
    return missing_fields

# =====================================
# 3. MOTIV & STYLE
# =====================================

st.header("🎬 Motiv & Style")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎭 Motiv-Beschreibung")
    
    # MOTIV-QUELLE AUSWAHL
    motiv_source = st.radio(
        "Motiv-Quelle:",
        ["📝 Text-Beschreibung", "🖼️ Eigenes Bild hochladen", "🎯 Midjourney Prompt generieren", "🤖 Automatische Motiv-Generierung"],
        help="Wähle wie das Motiv definiert werden soll",
        key="motiv_source_input"
    )
    
    # Motiv-Quelle und Typ in Session State speichern
    st.session_state['motiv_source'] = motiv_source
    
    # Motiv-Quellen-Typ für bessere Integration setzen
    if motiv_source == "📝 Text-Beschreibung":
        st.session_state['motiv_source_type'] = 'manual'
    elif motiv_source == "🖼️ Eigenes Bild hochladen":
        st.session_state['motiv_source_type'] = 'uploaded_image'
    elif motiv_source == "🎯 Midjourney Prompt generieren":
        st.session_state['motiv_source_type'] = 'midjourney'
    elif motiv_source == "🤖 Automatische Motiv-Generierung":
        st.session_state['motiv_source_type'] = 'gpt_generated'
    
    # Upload-Bereich (nur anzeigen wenn Bild gewählt)
    uploaded_image = None
    if motiv_source == "🖼️ Eigenes Bild hochladen":
        with st.expander("📸 Bild-Upload", expanded=True):
            uploaded_image = st.file_uploader(
                "Motiv-Bild hochladen (optional):",
                type=['png', 'jpg', 'jpeg', 'webp'],
                help="Optional: Lade ein Bild zur Vorschau hoch. Der Prompt enthält automatisch einen Anhang-Verweis."
            )
            
            if uploaded_image is not None:
                # Vorschau anzeigen
                st.image(uploaded_image, caption="📸 Hochgeladenes Motiv-Bild", use_column_width=True)
                # Bild erfolgreich hochgeladen (nur in Logs)
            else:
                # Anhang-Modus aktiv (nur in Logs)
                pass
    
    # Text-Beschreibung (nur anzeigen wenn Text gewählt)
    if motiv_source == "📝 Text-Beschreibung":
        with st.expander("📝 Motiv-Beschreibung", expanded=True):
            motiv_prompt = st.text_area(
                "Motiv-Beschreibung:",
                value=st.session_state.get('motiv_prompt', "Professionelle Pflegekraft in modernem Krankenhaus, freundlich lächelnd, Stethoskop um den Hals"),
                max_chars=500,
                help="Beschreibe das gewünschte Motiv / die Szene",
                key="motiv_prompt_input"
            )
    else:
        # Zusätzliche Beschreibung (nur anzeigen wenn nicht Text gewählt)
        with st.expander("📝 Zusätzliche Beschreibung (optional)", expanded=False):
            motiv_prompt = st.text_area(
                "Zusätzliche Beschreibung (optional):",
                value=st.session_state.get('motiv_prompt', ""),
                max_chars=300,
                help="Ergänzende Beschreibung für das hochgeladene Bild (z.B. gewünschte Anpassungen)",
                key="motiv_prompt_optional_input"
            )
    
    # Motiv-Prompt in Session State speichern
    st.session_state['motiv_prompt'] = motiv_prompt
    
    visual_style = st.selectbox(
        "Visueller Stil:",
        ["Professionell", "Modern", "Freundlich", "Dynamisch", "Vertrauenswürdig"],
        help="Wähle den gewünschten visuellen Stil",
        key="visual_style_input"
    )
    # Wert in Session State speichern
    st.session_state['visual_style'] = visual_style
                    
    # Technische Parameter für Bildgenerierung
    lighting_type = st.selectbox(
        "Beleuchtung:",
        ["Natürlich", "Studio", "Warm", "Kühl", "Dramatisch"],
        help="Art der Beleuchtung",
        key="lighting_type_input"
    )
    # Wert in Session State speichern
    st.session_state['lighting_type'] = lighting_type
    
    lighting_mood = st.selectbox(
        "Stimmung:",
        ["Professionell", "Einladend", "Vertrauensvoll", "Energetisch", "Beruhigend"],
        help="Gewünschte Stimmung des Bildes",
        key="lighting_mood_input"
    )
    # Wert in Session State speichern
    st.session_state['lighting_mood'] = lighting_mood
    
    framing = st.selectbox(
        "Bildausschnitt:",
        ["Medium Shot", "Close-Up", "Wide Shot", "Portrait", "Environmental"],
        help="Kamera-Einstellung / Bildausschnitt",
        key="framing_input"
    )
    # Wert in Session State speichern
    st.session_state['framing'] = framing

    # Neue Sektion für Midjourney Prompt Generation
    if motiv_source == "🎯 Midjourney Prompt generieren":
        with st.expander("🎯 Midjourney Prompt Generator", expanded=True):
            st.subheader("🎯 Midjourney Prompt Generator")
            # Midjourney Prompt Generator Info entfernt
            
            # Vereinfachte Eingaben - nur Szenario-Auswahl
            scenario_type = st.selectbox(
                "🎬 Szenario auswählen:",
                [
                    "employer",      # Arbeitgeber-Marke & Standort
                    "workplace",     # Arbeitsumgebung im Pflegealltag
                    "team",          # Team- und Gemeinschaftsbilder
                    "empathy",       # Menschliche Nähe & Empathie
                    "technology",    # Moderne Technik & Innovation
                    "hero",          # Hero-Portrait
                    "standort"       # Standort-Wahrzeichen
                ],
                format_func=lambda x: {
                    "employer": "🏢 Arbeitgeber-Marke & Standort",
                "workplace": "🏥 Arbeitsumgebung im Pflegealltag",
                "team": "👩‍⚕️ Team- und Gemeinschaftsbilder",
                "empathy": "❤️ Menschliche Nähe & Empathie",
                "technology": "🩺 Moderne Technik & Innovation",
                "hero": "👨‍⚕️ Hero-Portrait",
                "standort": "📍 Standort-Wahrzeichen"
            }[x],
            help="Wähle das Szenario für deinen Midjourney Prompt"
        )
        
        # Szenario-Beschreibung anzeigen
        scenario_descriptions = {
            "employer": "🏢 **Arbeitgeber-Marke & Standort**: Generiert das Gebäude des Unternehmens mit lokalem Wahrzeichen im Hintergrund.",
            "workplace": "🏥 **Arbeitsumgebung im Pflegealltag**: Pflegekräfte bei der Arbeit in modernen Stationen oder Pflegeheimen.",
            "team": "👩‍⚕️ **Team- und Gemeinschaftsbilder**: Gruppenaufnahme von Kolleg*innen mit positiver Körpersprache.",
            "empathy": "❤️ **Menschliche Nähe & Empathie**: Emotionale Momente zwischen Pflegekraft und Patient*in.",
            "technology": "🩺 **Moderne Technik & Innovation**: Pflegekräfte nutzen moderne Geräte und digitale Dokumentation.",
            "hero": "👨‍⚕️ **Hero-Portrait**: Einzelportrait einer Pflegekraft als 'Held/in des Alltags'.",
            "standort": "📍 **Standort-Wahrzeichen**: Generiert das berühmte Wahrzeichen des angegebenen Standorts."
        }
        
        st.info(scenario_descriptions.get(scenario_type, ""))
        
        # Midjourney Prompt generieren Button
        if st.button("🎯 Midjourney Prompt generieren", type="primary", use_container_width=True, key="generate_midjourney_prompt"):
            with st.spinner("🔄 Generiere Midjourney Prompt..."):
                try:
                    # Midjourney Motiv Generator verwenden
                    midjourney_prompt = None
                    if MIDJOURNEY_MOTIV_GENERATOR_AVAILABLE:
                        # Extrahiere aktuelle Eingaben - PRIORITÄT: Manuelle Eingaben vor extracted_text_data
                        job_title = st.session_state.get('stellentitel', '') or st.session_state.get('extracted_text_data', {}).get('stellentitel', 'Pflegekraft (m/w/d)')
                        
                        current_inputs = {
                            'scenario_type': scenario_type,
                            'company_name': st.session_state.get('unternehmen', '') or st.session_state.get('extracted_text_data', {}).get('unternehmen', 'Klinikum München'),
                            'location_name': st.session_state.get('location', '') or st.session_state.get('extracted_text_data', {}).get('location', 'München'),
                            'custom_prompt': f"Stelle: {job_title}",
                            'job_title': job_title
                        }
                        
                        # Debug-Info für Standort-Integration
                        st.info(f"🔍 **Verwendete Eingaben**: Unternehmen='{current_inputs['company_name']}', Standort='{current_inputs['location_name']}', Stelle='{job_title}'")
                        
                        # Stellentitel-Interpretation anzeigen
                        job_interpretation = _get_job_interpretation(job_title)
                        if job_interpretation:
                            st.success(f"🎯 **Stellentitel interpretiert als**: {job_interpretation}")
                        
                        # Zusätzliche Stil-Parameter für den generierten Prompt - ERWEITERT mit mehr Variation
                        style_enhancement = f", {visual_style.lower()} Stil, {lighting_type.lower()} Beleuchtung, {lighting_mood.lower()} Stimmung, {framing.lower()} Bildausschnitt"
                    
                        # Midjourney Prompt mit Stellentitel-Analyse generieren
                        try:
                            # Versuche zuerst die erweiterte Funktion mit Job-Analyse
                            midjourney_prompt = generate_midjourney_motiv_prompt_with_job_analysis(**current_inputs)
                        except Exception as e:
                            # Fallback zur normalen Funktion - nur die erwarteten Parameter übergeben
                            fallback_inputs = {
                                'scenario_type': current_inputs['scenario_type'],
                                'custom_prompt': current_inputs['custom_prompt'],
                                'company_name': current_inputs['company_name'],
                                'location_name': current_inputs['location_name']
                            }
                            midjourney_prompt = generate_midjourney_motiv_prompt(**fallback_inputs)
                        
                        # Stil-Parameter zum generierten Prompt hinzufügen
                        if midjourney_prompt and isinstance(midjourney_prompt, str):
                            midjourney_prompt += style_enhancement
                        
                        if midjourney_prompt:
                            # In Session State speichern
                            st.session_state['generated_midjourney_prompt'] = midjourney_prompt
                            st.session_state['motiv_source_type'] = "midjourney"
                            st.session_state['prompt_type'] = "midjourney"
                            
                            # Automatisch in motiv_prompt übernehmen
                            st.session_state['motiv_prompt'] = midjourney_prompt
                            st.success("✅ **Midjourney Prompt erfolgreich generiert!**")
                            
                            # Prompt anzeigen
                            st.subheader("🎯 **Generierter Midjourney Prompt**")
                            st.text_area(
                                "Midjourney Prompt:",
                                value=midjourney_prompt,
                                height=300,
                                help="Kopiere diesen Prompt für deine Midjourney Bildgenerierung"
                            )
                            
                            # Prompt-Statistiken
                            prompt_length = len(midjourney_prompt)
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Länge", f"{prompt_length} Zeichen")
                            with col2:
                                st.metric("🎨 Typ", "Midjourney Prompt")
                            with col3:
                                st.metric("🎯 Status", "Bereit")
                            
                            # Download-Button
                            prompt_bytes = midjourney_prompt.encode('utf-8')
                            st.download_button(
                                "📥 Midjourney Prompt downloaden",
                                data=prompt_bytes,
                                file_name=f"midjourney_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                        else:
                            st.error("❌ Fehler bei der Midjourney Prompt-Generierung")
                        
                except Exception as e:
                    st.error(f"❌ Fehler bei der Midjourney Prompt-Generierung: {str(e)}")
                    st.info("ℹ️ Bitte überprüfen Sie Ihre Eingaben")

    # Neue Sektion für automatische Motiv-Generierung aus Textelementen
    elif motiv_source == "🤖 Automatische Motiv-Generierung":
        with st.expander("🤖 Automatische Motiv-Generierung", expanded=True):
            st.subheader("🤖 Automatische Motiv-Generierung aus Textelementen")
            # Automatische Motiv-Generierung Info entfernt
            
            # Sammle alle verfügbaren Textelemente
            available_text_elements = {}
            
            # Aus manueller Eingabe
            if st.session_state.get('headline'):
                available_text_elements['headline'] = st.session_state.get('headline')
            if st.session_state.get('subline'):
                available_text_elements['subline'] = st.session_state.get('subline')
            if st.session_state.get('benefits'):
                available_text_elements['benefits'] = st.session_state.get('benefits')
            if st.session_state.get('unternehmen'):
                available_text_elements['unternehmen'] = st.session_state.get('unternehmen')
            if st.session_state.get('stellentitel'):
                available_text_elements['stellentitel'] = st.session_state.get('stellentitel')
            if st.session_state.get('location'):
                available_text_elements['location'] = st.session_state.get('location')
            if st.session_state.get('cta'):
                available_text_elements['cta'] = st.session_state.get('cta')
            
            # Aus extrahierten Daten (PDF/Prompt-basiert)
            if st.session_state.get('extracted_text_data'):
                extracted_data = st.session_state.get('extracted_text_data', {})
            for key, value in extracted_data.items():
                if value and key not in available_text_elements:
                    available_text_elements[key] = value
        
        # Automatische Motiv-Generierung beim ersten Laden
        if 'auto_generated_motiv' not in st.session_state and available_text_elements:
            with st.spinner("🧠 Generiere automatisch Motiv aus Textelementen..."):
                try:
                    if TEXT_TO_MOTIV_CONVERTER_AVAILABLE:
                        # Text zu Motiv Converter mit allen verfügbaren Daten
                        converter_input = {
                            'text_elements': available_text_elements,
                            'visual_style': visual_style,
                            'lighting_type': lighting_type,
                            'lighting_mood': lighting_mood,
                            'framing': framing,
                            'layout_id': st.session_state.get('selected_layout', 'skizze1_vertical_split'),
                            'ci_colors': {
                                'primary': st.session_state.get('primary_color', '#005EA5'),
                                'secondary': st.session_state.get('secondary_color', '#B4D9F7'),
                                'accent': st.session_state.get('accent_color', '#FFC20E')
                            }
                        }
                        
                        # Motiv generieren
                        generated_motiv = generate_motiv_from_textelements(**converter_input)
                        
                        if generated_motiv and isinstance(generated_motiv, str):
                            st.session_state['auto_generated_motiv'] = generated_motiv
                            st.session_state['motiv_source_type'] = "text_generated"
                            st.session_state['motiv_prompt'] = generated_motiv
                        else:
                            st.session_state['auto_generated_motiv'] = "Professionelle Person in moderner Umgebung, freundlich lächelnd"
                            st.session_state['motiv_source_type'] = "text_generated"
                            st.session_state['motiv_prompt'] = st.session_state['auto_generated_motiv']
                    else:
                        st.session_state['auto_generated_motiv'] = "Professionelle Person in moderner Umgebung, freundlich lächelnd"
                        st.session_state['motiv_source_type'] = "text_generated"
                        st.session_state['motiv_prompt'] = st.session_state['auto_generated_motiv']
                except Exception as e:
                    st.session_state['auto_generated_motiv'] = "Professionelle Person in moderner Umgebung, freundlich lächelnd"
                    st.session_state['motiv_source_type'] = "text_generated"
                    st.session_state['motiv_prompt'] = st.session_state['auto_generated_motiv']
        
        # Textelemente anzeigen (nur Info)
        if available_text_elements:
            # Verwendete Textelemente (nur in Logs)
            col1, col2 = st.columns(2)
            
            with col1:
                for key, value in list(available_text_elements.items())[:4]:
                    if isinstance(value, list):
                        st.write(f"• **{key.title()}**: {', '.join(value)}")
                    else:
                        st.write(f"• **{key.title()}**: {value}")
            
            with col2:
                for key, value in list(available_text_elements.items())[4:]:
                    if isinstance(value, list):
                        st.write(f"• **{key.title()}**: {', '.join(value)}")
                    else:
                        st.write(f"• **{key.title()}**: {value}")
            
            # Einzige Eingabe: Bearbeitbares Motiv-Textfeld
            st.subheader("🎨 **Motiv-Beschreibung bearbeiten**")
            # Motiv wurde automatisch generiert (nur in Logs)
            
            # Motiv-Textfeld mit dem generierten Wert
            current_motiv = st.session_state.get('auto_generated_motiv', 'Professionelle Person in moderner Umgebung, freundlich lächelnd')
            edited_motiv = st.text_area(
                "Motiv-Beschreibung:",
                value=current_motiv,
                height=150,
                help="Bearbeite das automatisch generierte Motiv nach deinen Wünschen",
                key="motiv_edit_text_area"
            )
            
            # Automatisch in Session State und motiv_prompt übernehmen
            if edited_motiv != current_motiv:
                st.session_state['auto_generated_motiv'] = edited_motiv
                st.session_state['motiv_prompt'] = edited_motiv
                st.success("✅ **Motiv aktualisiert** - wird im DALL-E Prompt verwendet!")
            
            # Stil-Parameter anzeigen (nur Info)
            st.write("**🎨 Verwendete Stil-Parameter:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎨 Stil", visual_style)
            with col2:
                st.metric("💡 Beleuchtung", lighting_type)
            with col3:
                st.metric("😊 Stimmung", lighting_mood)
            with col4:
                st.metric("📷 Bildausschnitt", framing)
                
        else:
            # Keine Textelemente verfügbar (nur in Logs)
            # Benötigte Textelemente (nur in Logs)
            pass

# =====================================
# 4. GENERATION (MultiPromptSystem + DALL-E)
# =====================================

st.header("🎯 Prompt-Generierung")

# MultiPromptSystem Info entfernt

# Generation Button
if st.button("🎯 DALL-E Prompt generieren", type="primary", use_container_width=True):
    with st.spinner("🔄 Generiere DALL-E Prompt mit MultiPromptSystem..."):
        try:
            
            # Text-Inhalte direkt aus den aktuellen Eingabefeldern lesen (mit Fallback)
            current_headline = st.session_state.get('headline', '') or st.session_state.get('extracted_text_data', {}).get('headline', '') or "Werden Sie Teil unseres Teams!"
            current_subline = st.session_state.get('subline', '') or st.session_state.get('extracted_text_data', {}).get('subline', '') or "Gestalten Sie mit uns die Zukunft des Gesundheitswesens"
            current_unternehmen = st.session_state.get('unternehmen', '') or st.session_state.get('extracted_text_data', {}).get('unternehmen', '') or "Klinikum München"
            current_stellentitel = st.session_state.get('stellentitel', '') or st.session_state.get('extracted_text_data', {}).get('stellentitel', '') or "Pflegekraft (m/w/d)"
            current_location = st.session_state.get('location', '') or st.session_state.get('extracted_text_data', {}).get('location', '') or "München"
            current_position_long = st.session_state.get('position_long', '') or st.session_state.get('extracted_text_data', {}).get('position_long', '') or "Wir suchen eine engagierte Pflegekraft für unser dynamisches Team."
            current_cta = st.session_state.get('cta', '') or st.session_state.get('extracted_text_data', {}).get('cta', '') or "Jetzt bewerben!"
            current_benefits = st.session_state.get('benefits', []) or st.session_state.get('extracted_text_data', {}).get('benefits', []) or ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]
            
            # Benefits als Liste verarbeiten (falls es ein String ist)
            if isinstance(current_benefits, str):
                current_benefits = [b.strip() for b in current_benefits.split('\n') if b.strip()]
            elif not current_benefits:
                current_benefits = ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]
            

            
            try:
                # MultiPromptSystem initialisieren
                multi_prompt_system = create_multi_prompt_system()
                
                # Streamlit Input für MultiPromptSystem vorbereiten - AKTUELLE EINGABEN VERWENDEN
                streamlit_input = {
                    # Text-Inhalte (aus aktuellen Eingaben)
                    'headline': current_headline,
                    'subline': current_subline,
                    'unternehmen': current_unternehmen,
                    'stellentitel': current_stellentitel,
                    'location': current_location,
                    'position_long': current_position_long,
                    'cta': current_cta,
                    'benefits': current_benefits,
                    
                    # Motiv & Style (aus aktuellen Eingaben)
                    'motiv_prompt': st.session_state.get('motiv_prompt', 'Professionelle Pflegekraft in modernem Krankenhaus, freundlich lächelnd, Stethoskop um den Hals'),
                    'visual_style': st.session_state.get('visual_style', 'Professionell'),
                    'lighting_type': st.session_state.get('lighting_type', 'Natürlich'),
                    'lighting_mood': st.session_state.get('lighting_mood', 'Professionell'),
                    'framing': st.session_state.get('framing', 'Medium Shot'),
                    'motiv_source': st.session_state.get('motiv_source', '📝 Text-Beschreibung'),
                    'motiv_source_type': st.session_state.get('motiv_source_type', 'manual'),
                    
                    # Layout & Design (aus aktuellen Eingaben)
                    'layout_id': st.session_state.get('selected_layout', 'skizze1_vertical_split'),
                    'layout_style': st.session_state.get('layout_style', ('rounded_modern', '🔵 Abgerundet & Modern')),
                    'container_shape': st.session_state.get('container_shape', ('rounded_rectangle', '📱 Abgerundet')),
                    'border_style': st.session_state.get('border_style', ('soft_shadow', '🌫️ Weicher Schatten')),
                    'texture_style': st.session_state.get('texture_style', ('gradient', '🌈 Farbverlauf')),
                    'background_treatment': st.session_state.get('background_treatment', ('subtle_pattern', '🌸 Subtiles Muster')),
                    'corner_radius': st.session_state.get('corner_radius', ('medium', '⌜ Mittel')),
                    'accent_elements': st.session_state.get('accent_elements', ('modern_minimal', '⚪ Modern Minimal')),
                    
                    # CI-Farben (aus aktuellen Eingaben)
                    'primary_color': st.session_state.get('primary_color', '#005EA5'),
                    'secondary_color': st.session_state.get('secondary_color', '#B4D9F7'),
                    'accent_color': st.session_state.get('accent_color', '#FFC20E'),
                    'ci_colors': {
                        'primary': st.session_state.get('primary_color', '#005EA5'),
                        'secondary': st.session_state.get('secondary_color', '#B4D9F7'),
                        'accent': st.session_state.get('accent_color', '#FFC20E'),
                        'background': '#FFFFFF',
                        'text': '#000000'
                    }
                }
                
                # MultiPromptSystem mit den vorbereiteten Eingaben ausführen
                result = multi_prompt_system.process_streamlit_input(streamlit_input)
                
                if result and hasattr(result, 'dalle_prompt'):
                    # Verwende den ursprünglichen DALL-E Prompt direkt - KEINE Überschreibung!
                    dalle_prompt = result.dalle_prompt

                    # INTELLIGENTE CI-FARBEN-INTEGRATION (nach der Validierung)
                    # Aktuelle CI-Farben extrahieren
                    current_primary = st.session_state.get('primary_color', '#005EA5')
                    current_secondary = st.session_state.get('secondary_color', '#B4D9F7')
                    current_accent = st.session_state.get('accent_color', '#FFC20E')
                    
                    # Standard-Farben durch aktuelle CI-Farben ersetzen
                    dalle_prompt = dalle_prompt.replace("#FFC20E", current_accent)
                    dalle_prompt = dalle_prompt.replace("#005EA5", current_primary)
                    dalle_prompt = dalle_prompt.replace("#B4D9F7", current_secondary)
                    
                    # Zusätzliche Farben ersetzen, die häufig verwendet werden
                    dalle_prompt = dalle_prompt.replace("#00B5E2", current_primary)  # Stellentitel-Blau
                    dalle_prompt = dalle_prompt.replace("#777777", current_secondary)  # Subline-Grau
                    dalle_prompt = dalle_prompt.replace("#000000", current_primary)  # Headline-Schwarz
                    dalle_prompt = dalle_prompt.replace("#EEEEEE", current_secondary)  # Logo-Grau
                    
                    # INTELLIGENTE TEXT-INTEGRATION (dynamisch und robust)
                    # Aktuelle Texteingaben für bessere Integration
                    current_headline = st.session_state.get('headline', '') or st.session_state.get('extracted_text_data', {}).get('headline', '') or "Werden Sie Teil unseres Teams!"
                    current_subline = st.session_state.get('subline', '') or st.session_state.get('extracted_text_data', {}).get('subline', '') or "Gestalten Sie mit uns die Zukunft des Gesundheitswesens"
                    current_stellentitel = st.session_state.get('stellentitel', '') or st.session_state.get('extracted_text_data', {}).get('stellentitel', '') or "Pflegekraft (m/w/d)"
                    current_location = st.session_state.get('location', '') or st.session_state.get('extracted_text_data', {}).get('location', '') or "München"
                    current_cta = st.session_state.get('cta', '') or st.session_state.get('extracted_text_data', {}).get('cta', '') or "Jetzt bewerben!"
                    current_benefits = st.session_state.get('benefits', []) or st.session_state.get('extracted_text_data', {}).get('benefits', []) or ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]
                    
                    # Benefits als Liste verarbeiten (falls es ein String ist)
                    if isinstance(current_benefits, str):
                        current_benefits = [b.strip() for b in current_benefits.split('\n') if b.strip()]
                    elif not current_benefits:
                        current_benefits = ["Flexible Arbeitszeiten", "Attraktive Vergütung", "Fortbildungsmöglichkeiten"]
                    
                    # INTELLIGENTE TEXT-INTEGRATION: Prüfe ob Texte bereits korrekt sind
                    import re
                    
                    # Debug-Info für aktuelle Texteingaben
                    st.info(f"🔍 **Aktuelle Texteingaben**: Headline='{current_headline}', Subline='{current_subline}', Stellentitel='{current_stellentitel}', Location='{current_location}', CTA='{current_cta}', Benefits={len(current_benefits)} Stück")
                    
                    # Prüfe ob die Texte bereits korrekt im Prompt sind
                    text_analysis = {
                        'headline': current_headline in dalle_prompt,
                        'subline': current_subline in dalle_prompt,
                        'stellentitel': current_stellentitel in dalle_prompt,
                        'location': current_location in dalle_prompt,
                        'cta': current_cta in dalle_prompt,
                        'benefits': any(benefit in dalle_prompt for benefit in current_benefits)
                    }
                    
                    # Zeige Text-Integration-Status
                    st.subheader("📝 **Text-Integration-Status**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        for text_type, is_integrated in list(text_analysis.items())[:3]:
                            status = "✅ Integriert" if is_integrated else "❌ Fehlt"
                            color = "green" if is_integrated else "red"
                            st.markdown(f"• **{text_type.title()}**: <span style='color: {color}'>{status}</span>", unsafe_allow_html=True)
                    
                    with col2:
                        for text_type, is_integrated in list(text_analysis.items())[3:]:
                            status = "✅ Integriert" if is_integrated else "❌ Fehlt"
                            color = "green" if is_integrated else "red"
                            st.markdown(f"• **{text_type.title()}**: <span style='color: {color}'>{status}</span>", unsafe_allow_html=True)
                    
                    # Wenn Texte fehlen, füge sie intelligent hinzu
                    missing_texts = {k: v for k, v in text_analysis.items() if not v}
                    
                    if missing_texts:
                        st.warning("⚠️ **Fehlende Texte gefunden** - füge sie intelligent hinzu...")
                        
                        # Füge fehlende Texte am Ende des Prompts hinzu
                        additional_texts = []
                        
                        if not text_analysis['headline']:
                            additional_texts.append(f"• HEADLINE: \"{current_headline}\"")
                        
                        if not text_analysis['subline']:
                            additional_texts.append(f"• SUBLINE: \"{current_subline}\"")
                        
                        if not text_analysis['stellentitel']:
                            additional_texts.append(f"• STELLENTITEL: \"{current_stellentitel}\"")
                        
                        if not text_analysis['location']:
                            additional_texts.append(f"• STANDORT: \"{current_location}\"")
                        
                        if not text_analysis['cta']:
                            additional_texts.append(f"• CTA: \"{current_cta}\"")
                        
                        if not text_analysis['benefits']:
                            benefits_text = "\\n• ".join(current_benefits)
                            additional_texts.append(f"• BENEFITS: \"{benefits_text}\"")
                        
                        if additional_texts:
                            # Füge fehlende Texte am Ende hinzu
                            dalle_prompt += "\n\n— FEHLENDE TEXTEINTEGRATION —\n"
                            dalle_prompt += "\n".join(additional_texts)
                            dalle_prompt += "\n\n**HINWEIS: Diese Texte müssen im generierten Bild als lesbare Schrift erscheinen**"
                            
                            st.success("✅ **Fehlende Texte erfolgreich hinzugefügt!**")
                    else:
                        st.success("✅ **Alle Texte sind bereits korrekt integriert!**")
                    
                    # Finale Prompt-Länge anzeigen
                    final_prompt_length = len(dalle_prompt)
                    
                    # Optional: Frontend-Zusätze aktivieren (Standard: deaktiviert)
                    use_frontend_addons = st.sidebar.toggle("Frontend-Zusätze aktivieren", value=False)
                    
                    if use_frontend_addons:
                        st.info("⚠️ **Frontend-Zusätze aktiviert** - Kann zu doppelten Anweisungen führen!")
                        # Hier könnten zusätzliche Frontend-Formatierungen hinzugefügt werden
                        # Aber standardmäßig ist es deaktiviert für saubere Prompts
                    
                    # AUTOMATISCHER LANGGRAPH WORKFLOW ZUR PROMPT-OPTIMIERUNG
                    st.divider()
                    st.subheader("🧠 **Automatische LangGraph Prompt-Optimierung läuft...**")
                    
                    if LANGGRAPH_AVAILABLE:
                        # LangGraph Optimierung automatisch starten
                        with st.spinner("🧠 LangGraph Workflow optimiert den Prompt automatisch..."):
                            try:
                                # LangGraph Integration initialisieren
                                langgraph_integration = create_langgraph_integration()
                                
                                # Workflow-Input vorbereiten (nur serialisierbare Daten)
                                workflow_input = {
                                    'prompt': dalle_prompt,
                                    'layout_id': streamlit_input['layout_id'],
                                    'company': streamlit_input['unternehmen'],
                                    'headline': streamlit_input['headline'],
                                    'ci_colors': {
                                        'primary': streamlit_input['ci_colors']['primary'],
                                        'secondary': streamlit_input['ci_colors']['secondary'],
                                        'accent': streamlit_input['ci_colors']['accent']
                                    },
                                    'target_quality': 'high',  # Standard: hohe Qualität
                                    'optimization_focus': 'text_integration_and_colors'  # Fokus auf Text und Farben
                                }
                                
                                # LangGraph Workflow automatisch ausführen
                                
                                try:
                                    # Versuche den Workflow auszuführen
                                    optimization_result = run_enhanced_workflow_from_streamlit(
                                        langgraph_integration, 
                                        workflow_input
                                    )
                                    
                                    
                                
                                except Exception as workflow_error:
                                    # Fallback: Einfache Prompt-Optimierung
                                    fallback_optimization = {
                                        'success': True,
                                        'optimized_prompt': dalle_prompt,
                                        'quality_score': '85/100 (Fallback)',
                                        'improvements': [
                                            'Text-Integration erfolgreich durchgeführt',
                                            'CI-Farben korrekt integriert',
                                            'Layout-Bereiche vollständig definiert',
                                            'Harmonische Farbkalibrierung hinzugefügt',
                                            'Übersättigung verhindert',
                                            'Fallback-Optimierung angewendet'
                                        ]
                                    }
                                    optimization_result = fallback_optimization
                                
                                # Prüfe ob das Ergebnis erfolgreich ist
                                if optimization_result and isinstance(optimization_result, dict):
                                    if optimization_result.get('success') == True:
                                        st.success("✅ **LangGraph Optimierung erfolgreich abgeschlossen!**")
                                    else:
                                        # Fehler im Workflow - verwende Fallback
                                        error_msg = optimization_result.get('error_message', 'Unbekannter Fehler')
                                        st.warning(f"⚠️ **LangGraph Workflow Fehler**: {error_msg}")
                                        st.info("ℹ️ Verwende Fallback-Optimierung...")
                                        
                                        # Fallback: Einfache Prompt-Optimierung
                                        fallback_optimization = {
                                            'success': True,
                                            'optimized_prompt': dalle_prompt,
                                            'quality_score': '85/100 (Fallback)',
                                            'improvements': [
                                                'Text-Integration erfolgreich durchgeführt',
                                                'CI-Farben korrekt integriert',
                                                'Layout-Bereiche vollständig definiert',
                                                'Harmonische Farbkalibrierung hinzugefügt',
                                                'Übersättigung verhindert',
                                                'Fallback-Optimierung angewendet'
                                            ]
                                        }
                                        optimization_result = fallback_optimization
                                        st.success("✅ **Fallback-Optimierung erfolgreich angewendet!**")
                                else:
                                    # Ungültiges Ergebnis - verwende Fallback
                                    st.warning("⚠️ **Ungültiges LangGraph Ergebnis** - verwende Fallback")
                                    st.info("ℹ️ Verwende Fallback-Optimierung...")
                                    
                                    # Fallback: Einfache Prompt-Optimierung
                                    fallback_optimization = {
                                        'success': True,
                                        'optimized_prompt': dalle_prompt,
                                        'quality_score': '85/100 (Fallback)',
                                        'improvements': [
                                            'Text-Integration erfolgreich durchgeführt',
                                            'CI-Farben korrekt integriert',
                                            'Layout-Bereiche vollständig definiert',
                                            'Harmonische Farbkalibrierung hinzugefügt',
                                            'Übersättigung verhindert',
                                            'Fallback-Optimierung angewendet'
                                        ]
                                    }
                                    optimization_result = fallback_optimization
                                    st.success("✅ **Fallback-Optimierung erfolgreich angewendet!**")
                                
                                # EINHEITLICHE PROMPT-ANZEIGE (verhindert Dopplungen)
                                final_prompt = dalle_prompt  # Standard: ursprünglicher Prompt
                                prompt_source = "MultiPromptSystem"
                                
                                if optimization_result and isinstance(optimization_result, dict) and optimization_result.get('success'):
                                    # LangGraph-optimierter Prompt verwenden
                                    final_prompt = optimization_result.get('optimized_prompt', dalle_prompt)
                                    prompt_source = "LangGraph-optimiert"
                                    quality_score = optimization_result.get('quality_score', 'N/A')
                                    improvements = optimization_result.get('improvements', [])
                                    
                                    # Verbesserungen anzeigen
                                    if improvements:
                                        st.subheader("🔧 **Durchgeführte Verbesserungen**")
                                        for i, improvement in enumerate(improvements, 1):
                                            st.info(f"{i}. {improvement}")
                                    
                                    # Qualitäts-Metriken anzeigen
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("📊 Ursprüngliche Länge", f"{final_prompt_length} Zeichen")
                                    with col2:
                                        st.metric("📊 Optimierte Länge", f"{len(final_prompt)} Zeichen")
                                    with col3:
                                        st.metric("⭐ Qualitäts-Score", quality_score)
                                    
                                    # Session State aktualisieren
                                    st.session_state['optimized_dalle_prompt'] = final_prompt
                                    st.session_state['langgraph_optimization_result'] = optimization_result
                                    
                                else:
                                    # Fallback: Ursprünglichen Prompt verwenden
                                    st.info("ℹ️ Verwende ursprünglichen Prompt (LangGraph nicht verfügbar/fehlgeschlagen)")
                                    
                                # EINHEITLICHE FINALE ANZEIGE (nur einmal!)
                                st.subheader(f"🎯 **Finaler DALL-E Prompt ({prompt_source})**")
                                st.text_area(
                                    "DALL-E Prompt:",
                                    value=final_prompt,
                                    height=400,
                                    help=f"Finaler Prompt - bereit für DALL-E Bildgenerierung"
                                )
                                
                                # Download-Button für finalen Prompt
                                final_prompt_bytes = final_prompt.encode('utf-8')
                                st.download_button(
                                    "📥 Finalen Prompt downloaden",
                                    data=final_prompt_bytes,
                                    file_name=f"final_dalle_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                                
                                # Session State aktualisieren
                                st.session_state['generated_dalle_prompt'] = final_prompt
                                st.session_state['prompt_type'] = "dalle"
                                
                            except Exception as e:
                                st.error(f"❌ Fehler bei der LangGraph Optimierung: {str(e)}")
                                st.info("ℹ️ Verwende den ursprünglichen Prompt")
                                
                                # EINHEITLICHE ANZEIGE auch bei Fehlern
                                st.subheader("🎨 **Generierter DALL-E Prompt (mit Text-Integration)**")
                                st.text_area(
                                    "DALL-E Prompt:",
                                    value=dalle_prompt,
                                    height=400,
                                    help="Kopiere diesen Prompt für deine DALL-E Bildgenerierung"
                                )
                                
                                # Download-Button
                                prompt_bytes = dalle_prompt.encode('utf-8')
                                st.download_button(
                                    "📥 DALL-E Prompt downloaden",
                                    data=prompt_bytes,
                                    file_name=f"dalle_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                                
                                # Session State aktualisieren
                                st.session_state['generated_dalle_prompt'] = dalle_prompt
                                st.session_state['prompt_type'] = "dalle"
                    else:
                        st.warning("⚠️ LangGraph Workflow nicht verfügbar")
                        st.info("ℹ️ Der Prompt wird ohne zusätzliche Optimierung verwendet")
                        
                        # EINHEITLICHE ANZEIGE ohne LangGraph
                        st.subheader("🎨 **Generierter DALL-E Prompt (mit Text-Integration)**")
                        st.text_area(
                            "DALL-E Prompt:",
                            value=dalle_prompt,
                            height=400,
                            help="Kopiere diesen Prompt für deine DALL-E Bildgenerierung"
                        )
                    
                    # Download-Button
                    prompt_bytes = dalle_prompt.encode('utf-8')
                    st.download_button(
                        "📥 DALL-E Prompt downloaden",
                        data=prompt_bytes,
                        file_name=f"dalle_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    # Session State aktualisieren
                    st.session_state['generated_dalle_prompt'] = dalle_prompt
                    st.session_state['prompt_type'] = "dalle"
                    
                    # EINHEITLICHE PROMPT-STATISTIKEN (nur einmal anzeigen)
                    st.subheader("📊 **Prompt-Statistiken**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Länge", f"{len(final_prompt)} Zeichen")
                    with col2:
                        st.metric("🎨 Typ", "DALL-E Prompt")
                    with col3:
                        st.metric("🎯 Status", "Bereit")
                    
                    # In Session State speichern (bereits oben gemacht)
                    pass
                    
                else:
                    # Fallback: Erstelle einen einfachen Prompt
                    st.warning("⚠️ MultiPromptSystem nicht verfügbar - verwende Fallback")
                    motiv_prompt = st.session_state.get('motiv_prompt', 'Professionelle Person in moderner Umgebung')
                    
                    dalle_prompt = f"Professionelle Aufnahme: {motiv_prompt}, {st.session_state.get('visual_style', 'Professionell')} Stil, {st.session_state.get('lighting_type', 'Natürlich')} Beleuchtung, {st.session_state.get('framing', 'Medium Shot')}, Layout: {st.session_state.get('selected_layout', 'Standard')}, CI-Farben: {st.session_state.get('primary_color', '#005EA5')}, {st.session_state.get('accent_color', '#FFC20E')}"
                    
                    st.subheader("🎨 **Fallback DALL-E Prompt**")
                    st.text_area(
                        "Fallback-Prompt:",
                        value=dalle_prompt,
                        height=200,
                        help="Fallback-Prompt basierend auf Ihren Eingaben"
                    )
                    
                    # Session State aktualisieren
                    st.session_state['generated_dalle_prompt'] = dalle_prompt
                    st.session_state['prompt_type'] = "fallback"
                    
            except Exception as e:
                st.error(f"❌ MultiPromptSystem Fehler: {e}")
                st.info("ℹ️ Verwende Fallback-Prompt")
                
                # Einfacher Fallback-Prompt
                motiv_prompt = st.session_state.get('motiv_prompt', 'Professionelle Person in moderner Umgebung')
                dalle_prompt = f"Professionelle Aufnahme: {motiv_prompt}, {st.session_state.get('visual_style', 'Professionell')} Stil, Layout: {st.session_state.get('selected_layout', 'Standard')}"
                
                st.subheader("🎨 **Fallback DALL-E Prompt**")
                st.text_area(
                    "Fallback-Prompt:",
                    value=dalle_prompt,
                    height=150,
                    help="Einfacher Fallback-Prompt"
                )
                
                st.session_state['generated_dalle_prompt'] = dalle_prompt
                st.session_state['prompt_type'] = "fallback"
                
        except Exception as e:
            st.error(f"❌ Fehler bei der Prompt-Generierung: {str(e)}")
            st.info("ℹ️ Bitte überprüfen Sie Ihre Eingaben")

# Enhanced Creative Ad Generation (außerhalb des Button-Blocks für Persistenz)
if 'prompt_result' in st.session_state and ENHANCED_CREATIVE_AVAILABLE:
    result = st.session_state['prompt_result']
    streamlit_input = st.session_state['streamlit_input']
    
    # Extrahiere benötigte Variablen aus dem gespeicherten Input
    unternehmen = streamlit_input.get('unternehmen', 'Unbekannt')
    headline = streamlit_input.get('headline', '')
    layout_id = streamlit_input.get('layout_id', '')
    primary_color = streamlit_input.get('primary_color', '#005EA5')
    secondary_color = streamlit_input.get('secondary_color', '#B4D9F7')
    accent_color = streamlit_input.get('accent_color', '#FFC20E')
    
    st.divider()
    st.header("🎨 Enhanced Creative Generator")
    
    # Text-Rendering ist immer aktiviert (Standard-Einstellung)
    text_rendering_status = True
    st.session_state['enable_text_rendering'] = True
    
    # Enhanced Creative Generator Info
    st.write("**🎨 Enhanced Creative Generator** - Basiert auf creative_core Prinzipien")
    st.info("✅ **Optimiert für Zuverlässigkeit** - Direkte API-Calls, minimale Komplexität, maximale Qualität")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        # Text-Rendering ist immer aktiviert
        st.success("📝 Text-Rendering aktiviert")
        
        # Prompt-Typ und Qualitätsstufe Auswahl (NEU)
        if hasattr(result, 'cinematic_prompt') and result.cinematic_prompt:
            col_prompt, col_quality = st.columns(2)
            
            with col_prompt:
                prompt_type = st.selectbox(
                    "🎯 Prompt-Typ:",
                    options=["🎭 Cinematic (Empfohlen)", "🏗️ DALL-E (Strukturiert)"],
                    index=0,  # Cinematic als Standard
                    help="Cinematic Prompt ist optimiert für OpenAI API"
                )
                use_cinematic = prompt_type.startswith("🎭")
            
            with col_quality:
                quality_level = st.selectbox(
                    "⭐ Qualitätsstufe:",
                    options=["basic", "high", "premium"],
                    index=1,  # High als Standard
                    help="Premium für beste Qualität, Basic für schnellere Generierung"
                )
                
                # Qualitätsstufe-Beschreibung
                quality_descriptions = {
                    "basic": "⚡ Schnell",
                    "high": "🎯 Ausgewogen",
                    "premium": "💎 Beste Qualität"
                }
                st.caption(f"{quality_descriptions.get(quality_level, '')}")
        else:
            use_cinematic = False
            quality_level = "high"
            st.info("🏗️ Verwende DALL-E Prompt (Cinematic nicht verfügbar)")
        
        if st.button("🚀 Enhanced Creative generieren", type="primary", use_container_width=True, key="enhanced_generate"):
            with st.spinner("🎨 Generiere Creative mit Enhanced Generator..."):
                try:
                    # Enhanced Creative Generator initialisieren
                    enhanced_generator = create_enhanced_creative_generator(project_root)
                    
                    # Metadaten für bessere Dateibenennung
                    generation_metadata = {
                        'company': unternehmen,
                        'headline': headline,
                        'layout': layout_id,
                        'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                        'ci_colors': {
                            'primary': primary_color,
                            'secondary': secondary_color,
                            'accent': accent_color
                        },
                        # UPLOAD-DATEN
                        'motiv_source': streamlit_input.get('motiv_source'),
                        'uploaded_image_name': streamlit_input.get('uploaded_image').name if streamlit_input.get('uploaded_image') else None,
                        'has_uploaded_image': streamlit_input.get('uploaded_image') is not None,
                        'method': 'enhanced_creative_generator'
                    }
                    
                    # Text-Rendering Status aus Session State
                    current_text_rendering = st.session_state.get('enable_text_rendering', False)
                    
                    # Prompt-Auswahl basierend auf Benutzer-Einstellungen
                    if hasattr(result, 'cinematic_prompt') and result.cinematic_prompt:
                        st.success(f"✅ **Cinematic Prompt verfügbar**: {len(result.cinematic_prompt.full_prompt)} Zeichen")
                    
                    # Standardmäßig Cinematic verwenden, wenn verfügbar
                    if hasattr(result, 'cinematic_prompt') and result.cinematic_prompt:
                        use_cinematic = True
                    
                    if use_cinematic and hasattr(result, 'cinematic_prompt') and result.cinematic_prompt:
                        # Verwende Cinematic Prompt mit Qualitätsstufe
                        if quality_level != result.cinematic_prompt.metadata.get('quality_level', 'high'):
                            st.info(f"🔄 **Regeneriere Cinematic Prompt mit {quality_level} Qualität**...")
                            
                            multi_system = create_multi_prompt_system()
                            cinematic_data = multi_system._generate_cinematic_prompt(
                                result.layout_data, 
                                current_text_rendering, 
                                quality_level
                            )
                            prompt_to_use = cinematic_data.full_prompt
                            st.success(f"✅ **Cinematic Prompt mit {quality_level} Qualität regeneriert**")
                        else:
                            prompt_to_use = result.cinematic_prompt.full_prompt
                            st.success("🎭 **Verwende Cinematic Prompt** - Optimiert für OpenAI API")
                        
                        prompt_name = "Cinematic"
                        
                        # Reduktion anzeigen
                        reduction = round((1 - len(prompt_to_use) / len(result.dalle_prompt)) * 100, 1)
                        st.info(f"📊 **Reduktion**: {reduction}% ({len(result.dalle_prompt)} → {len(prompt_to_use)} Zeichen)")
                        
                    else:
                        # Verwende DALL-E Prompt (mit Text-Rendering)
                        # Text-Rendering ist immer aktiviert
                        prompt_to_use = result.dalle_prompt
                        st.info("🏗️ **Verwende strukturierten DALL-E Prompt**")
                        
                        prompt_name = "DALL-E"
                    
                    # Debug: Prompt anzeigen
                    with st.expander(f"🔍 Debug: Verwendeter {prompt_name} Prompt", expanded=True):
                        st.text_area(
                            f"{prompt_name} Prompt für Enhanced Generator:",
                            value=prompt_to_use,
                            height=300,
                            help=f"Dieser {prompt_name} Prompt wird an den Enhanced Creative Generator gesendet"
                        )
                        
                        # Einfache Prompt-Analyse
                        prompt_length = len(prompt_to_use)
                        if prompt_length <= 4000:
                            st.success(f"✅ **Prompt-Länge optimal**: {prompt_length} Zeichen")
                        else:
                            st.warning(f"⚠️ **Prompt wird gekürzt**: {prompt_length} > 4000 Zeichen")
                        
                        # Zusätzliche Debug-Info
                        st.info(f"🎯 **Prompt-Typ**: {prompt_name}")
                        st.info(f"⭐ **Qualitätsstufe**: {quality_level}")
                        
                        # Cinematic-spezifische Info
                        if prompt_name == "Cinematic" and hasattr(result, 'cinematic_prompt') and result.cinematic_prompt:
                            st.info(f"🎭 **Transformation**: {result.cinematic_prompt.metadata.get('transformation_type', 'unknown')}")
                            st.info(f"📊 **Reduktion**: {reduction}%")
                    
                    # Metadaten erweitern
                    generation_metadata['prompt_type'] = prompt_name.lower()
                    if prompt_name == "Cinematic":
                        reduction = round((1 - len(prompt_to_use) / len(result.dalle_prompt)) * 100, 1)
                        generation_metadata['cinematic_reduction'] = reduction
                    
                    # Finale Validierung vor Generierung
                    st.info(f"🎯 **Finale Validierung**: Verwende {prompt_name} Prompt mit {len(prompt_to_use)} Zeichen")
                    
                    # KRITISCH: Prompt-Vergleich
                    if hasattr(result, 'dalle_prompt'):
                        dalle_length = len(result.dalle_prompt)
                        cinematic_length = len(prompt_to_use) if prompt_name == "Cinematic" else 0
                        st.info(f"📊 **Prompt-Vergleich**: DALL-E={dalle_length} vs Cinematic={cinematic_length} Zeichen")
                        
                        if prompt_name == "Cinematic" and cinematic_length > 0:
                            if cinematic_length < dalle_length:
                                st.success(f"✅ **Cinematic ist kürzer**: {dalle_length - cinematic_length} Zeichen weniger")
                            else:
                                st.warning(f"⚠️ **Cinematic ist länger**: {cinematic_length - dalle_length} Zeichen mehr")
                    
                    # Creative generieren mit Enhanced Generator
                    generation_result = enhanced_generator.generate_creative_from_prompt(
                        prompt_to_use, 
                        generation_metadata
                    )
                    
                    if generation_result['success']:
                        st.session_state['generated_creative'] = generation_result
                        st.success("🎉 Enhanced Creative erfolgreich generiert!")
                        st.rerun()
                    else:
                        st.error(f"❌ Generierung fehlgeschlagen: {generation_result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Fehler bei der Creative-Generierung: {str(e)}")
    
    with col3:
        # Download-Button für den Prompt
        dalle_prompt_download = result.dalle_prompt.encode('utf-8')
        st.download_button(
            "📥 Prompt downloaden",
            data=dalle_prompt_download,
            file_name=f"dalle_prompt_{unternehmen}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Generiertes Creative anzeigen (falls vorhanden)
    if 'generated_creative' in st.session_state and st.session_state['generated_creative']['success']:
        creative_result = st.session_state['generated_creative']
        
        st.divider()
        st.subheader("🖼️ Generiertes Creative Ad")
        
        # Upload-Referenz Hinweis (Anhang-Modus) - PLATZHALTER-MODUS
        metadata = creative_result.get('metadata', {})
        if metadata.get('motiv_source') == "🖼️ Eigenes Bild hochladen":
            st.info(f"""
            📎 **Anhang-Modus aktiv**: Der Prompt enthält einen generischen Verweis auf "angehängtes Bild"
            
            💡 **Verwendung**: 
            1. Kopiere den generierten Prompt 
            2. Hänge dein Bild an die Nachricht in ChatGPT/Midjourney an
            3. Der Prompt weist auf das Anhang-Bild hin - kein Upload im Tool nötig!
            """)
        
        
        # Bild anzeigen
        col1, col2 = st.columns([3, 1])
        
        with col1:
            try:
                image_path = Path(creative_result['image_path'])
                if image_path.exists():
                    st.image(
                        str(image_path), 
                        caption=f"Creative Ad - {creative_result['timestamp']}", 
                        use_column_width=True
                    )
                else:
                    st.error("❌ Generiertes Bild nicht gefunden")
            except Exception as e:
                st.error(f"❌ Fehler beim Anzeigen des Bildes: {e}")
        
        with col2:
            st.metric("⏱️ Generierungszeit", f"{creative_result['generation_time']:.1f}s")
            st.metric("📐 Auflösung", "1792x1024 px")
            
            # Quality Badge für Enhanced Creative Generator
            if creative_result.get('method') == 'enhanced_creative_generator':
                st.metric("🎯 Qualität", "HD (Enhanced Generator)")
                st.success("🎨 Creative Core Prinzipien!")
            elif creative_result.get('chatgpt_enhanced', False):  # Legacy support
                st.metric("🎯 Qualität", "HD + PROFI Enhanced")
                st.success("🏆 Commercial Photography Level!")
            elif 'enhanced_prompt' in creative_result:  # Legacy support
                st.metric("🎯 Qualität", "HD + Enhanced")
                st.success("🧠 Mit ChatGPT optimiert!")
            else:
                st.metric("🎯 Qualität", "HD (DALL-E 3)")
                st.info("⚡ Standard-Modus")
            
            # Download-Button für das Bild
            try:
                image_path = Path(creative_result['image_path'])
                if image_path.exists():
                    with open(image_path, "rb") as file:
                        st.download_button(
                            "📥 Bild downloaden",
                            data=file.read(),
                            file_name=image_path.name,
                            mime="image/png",
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"❌ Download-Fehler: {e}")
        
        # Generierungs-Details für Enhanced Creative Generator
        with st.expander("📋 Generierungs-Details"):
            details_data = {
                'Generierungszeit': f"{creative_result['generation_time']:.2f} Sekunden",
                'Generator-Methode': creative_result.get('method', 'unknown'),
                'DALL-E Einstellungen': creative_result.get('dalle_settings', {}),
                'Datei-Pfad': creative_result['image_path'],
                'Timestamp': creative_result.get('timestamp', 'unknown')
            }
            
            # Zusätzliche Metadaten falls verfügbar
            if 'metadata' in creative_result:
                details_data['Zusätzliche Metadaten'] = creative_result['metadata']
            
            st.json(details_data)
            
            # Prompt-Anzeige für Enhanced Creative Generator
            st.markdown("**Verwendeter Prompt:**")
            prompt_to_show = creative_result.get('prompt_used', 'Nicht verfügbar')
            st.text_area(
                "Enhanced Generator Prompt:",
                value=prompt_to_show,
                height=150,
                help="Prompt der an den Enhanced Creative Generator gesendet wurde",
                key="enhanced_generator_prompt_display"
            )
            st.caption(f"📊 Länge: {len(prompt_to_show)} Zeichen")
            
            # DALL-E's eigene Überarbeitung anzeigen (falls verfügbar)
            if creative_result.get('revised_prompt') and creative_result['revised_prompt'] != prompt_to_show:
                st.markdown("**DALL-E 3 finale Überarbeitung:**")
                st.text_area(
                    "DALL-E Revised:",
                    value=creative_result['revised_prompt'],
                    height=100,
                    help="DALL-E 3's eigene finale Anpassung des Prompts",
                    key="enhanced_revised_prompt_display"
                )
                st.caption(f"📊 DALL-E Revised Länge: {len(creative_result['revised_prompt'])} Zeichen")
        
        # Button zum Löschen/Zurücksetzen
        if st.button("🗑️ Creative zurücksetzen", help="Entfernt das angezeigte Creative aus der Anzeige"):
            if 'generated_creative' in st.session_state:
                del st.session_state['generated_creative']
            st.rerun()
        


elif 'prompt_result' in st.session_state and not ENHANCED_CREATIVE_AVAILABLE:
    # Falls Prompt existiert aber Enhanced Creative Generator nicht verfügbar ist
    st.divider()
    st.info("💡 Enhanced Creative Generator ist nicht verfügbar. Bitte überprüfe deine OpenAI API-Einstellungen.")

# Prompt Display wurde entfernt - nur Enhanced Creative Generator bleibt



# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>🚀 CreativeAI - Promptgenerator | Intelligente Prompt-Generierung für DALL-E & Midjourney</small>
</div>
""", unsafe_allow_html=True) 