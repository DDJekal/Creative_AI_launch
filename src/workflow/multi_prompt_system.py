#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multi_prompt_system.py - 3-Stufen Multi-Prompt-System

🎯 ZWECK: Robuste Layout-Integration auf allen drei Ebenen
📊 ARCHITEKTUR: 3-Stufen-Pipeline für optimale Prompt-Generierung
🚀 ZIEL: Garantierte Layout-Anwendung + Text-Integration + Motiv-Positionierung

WORKFLOW:
Input-Processor → Layout-Integrator → Prompt-Finalizer
     ↓                    ↓                   ↓
Strukturiert         Wendet Layout       Generiert finale
Streamlit-Daten      Rules an           DALL-E/MJ-Prompts
"""

import os
import sys
import yaml
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# OpenAI für Multi-Prompt-Generation
import openai
from dotenv import load_dotenv
load_dotenv()

# Prompt Transformer für cinematische Prompts
from .prompt_transformer import create_prompt_transformer, CinematicPromptData

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _hex_to_color_description(hex_color: str) -> str:
    """Konvertiert Hex-Farben zu beschreibenden Namen für bessere AI-Verständlichkeit"""
    hex_color = hex_color.lower()
    
    # Farb-Mapping für bessere AI-Prompts
    color_mappings = {
        # Blau-Töne
        '#005ea5': 'tiefes Unternehmensblau',
        '#0066cc': 'professionelles Blau',
        '#4a90e2': 'modernes Himmelblau',
        '#b4d9f7': 'helles Akzentblau',
        '#e3f2fd': 'sanftes Pastellblau',
        
        # Grün-Töne  
        '#28a745': 'kräftiges Geschäftsgrün',
        '#20c997': 'modernes Mint',
        '#d4edda': 'sanftes Hellgrün',
        
        # Rot-Töne
        '#dc3545': 'kraftvolles Signalrot',
        '#ff6b6b': 'warmes Akzentrot',
        
        # Gelb/Orange-Töne
        '#ffc20e': 'lebendiges Akzentgelb',
        '#ff9500': 'energetisches Orange',
        '#ffcc00': 'strahlendes Gelb',
        
        # Grau-Töne
        '#6c757d': 'professionelles Grau',
        '#495057': 'dunkles Businessgrau',
        '#f8f9fa': 'helles Hintergrundgrau',
        '#e9ecef': 'neutrales Hellgrau',
        
        # Standard-Farben
        '#ffffff': 'reines Weiß',
        '#000000': 'tiefes Schwarz',
        '#333333': 'dunkles Anthrazit'
    }
    
    # Exakte Übereinstimmung
    if hex_color in color_mappings:
        return color_mappings[hex_color]
    
    # Farbbereich-Analyse für ähnliche Farben
    if hex_color.startswith('#'):
        try:
            # Konvertiere Hex zu RGB
            hex_clean = hex_color[1:]
            if len(hex_clean) == 3:
                hex_clean = ''.join([c*2 for c in hex_clean])
            
            r = int(hex_clean[0:2], 16)
            g = int(hex_clean[2:4], 16) 
            b = int(hex_clean[4:6], 16)
            
            # Bestimme dominante Farbe
            if r > g and r > b:
                if r > 200: return 'helles Rot'
                elif r > 100: return 'kräftiges Rot'
                else: return 'dunkles Rot'
            elif g > r and g > b:
                if g > 200: return 'helles Grün'
                elif g > 100: return 'lebendiges Grün'
                else: return 'dunkles Grün'
            elif b > r and b > g:
                if b > 200: return 'helles Blau'
                elif b > 100: return 'kräftiges Blau'
                else: return 'dunkles Blau'
            else:
                # Grau-Töne
                avg = (r + g + b) // 3
                if avg > 200: return 'helles Grau'
                elif avg > 100: return 'mittleres Grau'
                else: return 'dunkles Grau'
                
        except ValueError:
            pass
    
    return f'Farbe {hex_color}'

@dataclass
class StructuredInput:
    """Strukturierte Eingabedaten nach Input-Processing"""
    # Basic-Daten
    headline: str
    subline: str
    company: str
    location: str
    
    # Job-Daten
    stellentitel: str
    position_long: str
    benefits: List[str]
    cta: str  # Call-to-Action Text
    
    # Motiv-Daten
    motiv_prompt: str
    visual_style: str
    lighting_type: str
    lighting_mood: str
    framing: str
    motiv_source: str  # "📝 Text-Beschreibung" oder "🖼️ Eigenes Bild hochladen"
    
    # Layout & CI
    layout_id: str
    ci_colors: Dict[str, str]
    
    # Metadaten
    timestamp: str
    
    # Default-Arguments am Ende (alle optional)
    logo_file: Any = None  # Streamlit UploadedFile object oder None
    logo_placeholder: str = "[LOGO]"
    style_options: Optional[Dict[str, Any]] = None
    processing_stage: str = "input_processed"
    
    # Upload-Daten (NEU) - Am Ende wegen Default-Values
    uploaded_image: Optional[Any] = None  # Streamlit UploadedFile object
    uploaded_image_name: Optional[str] = None  # Für Referenz im Prompt

@dataclass
class LayoutIntegratedData:
    """Layout-integrierte Daten nach Layout-Integration"""
    # Input-Daten (inherited)
    structured_input: StructuredInput
    
    # Layout-Definition
    layout_definition: Dict[str, Any]
    
    # Text-Mapping (wo welcher Text platziert wird)
    text_placements: Dict[str, Dict[str, Any]]
    
    # Motiv-Integration (wie Motiv behandelt wird)
    motiv_treatment: Dict[str, Any]
    
    # Typography (angewendete Schriftgrößen)
    applied_typography: Dict[str, Any]
    
    # Adaptive Adjustments (Content-Anpassungen)
    adaptive_adjustments: List[Dict[str, Any]]
    
    # Layout-Metriken
    layout_metrics: Dict[str, Any]
    
    # Metadaten
    processing_stage: str = "layout_integrated"

@dataclass
class FinalizedPrompts:
    """Finalisierte Prompts nach Prompt-Finalisierung"""
    # Layout-integrierte Daten (inherited)
    layout_data: LayoutIntegratedData
    
    # Generierte Prompts
    midjourney_prompt: str
    dalle_prompt: str
    
    # Prompt-Metriken
    midjourney_metrics: Dict[str, Any]
    dalle_metrics: Dict[str, Any]
    
    # Qualitäts-Assessment
    quality_assessment: Dict[str, Any]
    
    # Output-Files
    output_files: List[str]
    
    # Metadaten (mit Default-Werten am Ende)
    processing_stage: str = "prompts_finalized"
    total_processing_time: float = 0.0
    
    # Cinematischer Prompt für OpenAI API (mit Default-Wert am Ende)
    cinematic_prompt: Optional[CinematicPromptData] = None

class MultiPromptStage(ABC):
    """Abstrakte Basis-Klasse für Multi-Prompt-Stufen"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.stage_name = self.__class__.__name__
        
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Verarbeitet Input-Daten und gibt Output zurück"""
        pass
    
    def _log_stage_start(self, input_type: str):
        logger.info(f"🔄 STARTE {self.stage_name} - Input: {input_type}")
    
    def _log_stage_complete(self, output_type: str, processing_time: float):
        logger.info(f"✅ {self.stage_name} ABGESCHLOSSEN - Output: {output_type} ({processing_time:.2f}s)")

class InputProcessor(MultiPromptStage):
    """
    🔧 STUFE 1: INPUT-PROCESSOR
    
    ZWECK: Strukturiert rohe Streamlit-Eingaben für Layout-Processing
    INPUT: Dict mit Streamlit-Daten
    OUTPUT: StructuredInput mit standardisierter Struktur
    """
    
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        
    def process(self, streamlit_input: Dict[str, Any]) -> StructuredInput:
        """Verarbeitet Streamlit-Eingaben zu strukturierten Daten"""
        start_time = datetime.now()
        self._log_stage_start("Streamlit-Dict")
        
        try:
            # Text-Daten extrahieren und normalisieren
            headline = self._normalize_text(streamlit_input.get('headline', ''), max_length=50)
            subline = self._normalize_text(streamlit_input.get('subline', ''), max_length=60)
            company = self._normalize_text(streamlit_input.get('company', ''), max_length=30)
            location = self._normalize_text(streamlit_input.get('location', ''), max_length=25)
            stellentitel = self._normalize_text(streamlit_input.get('stellentitel', ''), max_length=50)
            position_long = self._normalize_text(streamlit_input.get('position_long', ''), max_length=40)
            cta = self._normalize_text(streamlit_input.get('cta', 'Jetzt bewerben!'), max_length=25)
            # position_short removed - nicht mehr verwendet
            
            # Benefits verarbeiten (Liste normalisieren)
            raw_benefits = streamlit_input.get('benefits', [])
            benefits = self._normalize_benefits(raw_benefits, max_items=5, max_length_per_item=35)
            
            # Motiv-Daten extrahieren
            motiv_prompt = self._normalize_text(streamlit_input.get('motiv_prompt', ''), max_length=200)
            visual_style = streamlit_input.get('visual_style', 'professional, realistic photography')
            lighting_type = streamlit_input.get('lighting_type', 'natural, soft lighting')
            lighting_mood = streamlit_input.get('lighting_mood', 'warm, welcoming, professional')
            framing = streamlit_input.get('framing', 'medium shot, waist up')
            
            # Upload-Daten extrahieren (NEU)
            motiv_source = streamlit_input.get('motiv_source', '📝 Text-Beschreibung')
            uploaded_image = streamlit_input.get('uploaded_image', None)
            uploaded_image_name = None
            if uploaded_image is not None:
                uploaded_image_name = getattr(uploaded_image, 'name', 'uploaded_image.jpg')
                logger.info(f"📁 Bild hochgeladen: {uploaded_image_name}")
            
            # Layout & CI-Farben
            layout_id = streamlit_input.get('layout_id', 'skizze1_vertical_split')
            ci_colors = self._extract_ci_colors_from_streamlit(streamlit_input)
            
            # Style-Optionen (Design-Anpassungen) - NEU HINZUGEFÜGT
            style_options = streamlit_input.get('style_options', {})
            
            # Logo & Branding
            logo_file = streamlit_input.get('logo_file', None)
            logo_placeholder = self._normalize_text(streamlit_input.get('logo_placeholder', '[FIRMENLOGO]'), max_length=30)
            
            # Strukturierte Daten erstellen
            structured = StructuredInput(
                headline=headline,
                subline=subline,
                company=company,
                location=location,
                stellentitel=stellentitel,
                position_long=position_long,
                benefits=benefits,
                cta=cta,
                motiv_prompt=motiv_prompt,
                visual_style=visual_style,
                lighting_type=lighting_type,
                lighting_mood=lighting_mood,
                framing=framing,
                motiv_source=motiv_source,  # NEU
                uploaded_image=uploaded_image,  # NEU
                uploaded_image_name=uploaded_image_name,  # NEU
                layout_id=layout_id,
                ci_colors=ci_colors,
                logo_file=logo_file,
                logo_placeholder=logo_placeholder,
                timestamp=datetime.now().strftime('%Y%m%d_%H%M%S'),
                style_options=style_options
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self._log_stage_complete("StructuredInput", processing_time)
            
            logger.info(f"   📊 Headline: '{headline}' ({len(headline)} chars)")
            logger.info(f"   📊 Benefits: {len(benefits)} items")
            logger.info(f"   📊 Layout: {layout_id}")
            logger.info(f"   📊 CI-Farben: {len(ci_colors)} definiert")
            
            return structured
            
        except Exception as e:
            logger.error(f"❌ InputProcessor Fehler: {e}")
            raise
    
    def _normalize_text(self, text: str, max_length: int) -> str:
        """Normalisiert Text (Länge, Encoding, etc.)"""
        if not text or not isinstance(text, str):
            return ""
        
        # Basic cleanup
        text = text.strip()
        
        # Längen-Beschränkung
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
            logger.warning(f"⚠️ Text gekürzt auf {max_length} Zeichen")
        
        return text
    
    def _normalize_benefits(self, benefits: List[str], max_items: int, max_length_per_item: int) -> List[str]:
        """Normalisiert Benefits-Liste"""
        if not benefits or not isinstance(benefits, list):
            return []
        
        normalized = []
        for benefit in benefits[:max_items]:
            if benefit and isinstance(benefit, str):
                normalized_benefit = self._normalize_text(benefit.strip(), max_length_per_item)
                if normalized_benefit:
                    normalized.append(normalized_benefit)
        
        return normalized
    
    def _extract_ci_colors_from_streamlit(self, streamlit_input: Dict[str, Any]) -> Dict[str, str]:
        """Extrahiert CI-Farben aus Streamlit-Input (neue Methode)"""
        # Priorität 1: ci_colors_palette (strukturiert)
        if 'ci_colors_palette' in streamlit_input:
            palette = streamlit_input['ci_colors_palette']
            if isinstance(palette, dict):
                return self._extract_ci_colors(palette)
        
        # Priorität 2: Einzelne Farbfelder
        colors_mapping = {
            'primary': streamlit_input.get('primary_color'),
            'secondary': streamlit_input.get('secondary_color'),
            'accent': streamlit_input.get('accent_color'),
            'background': streamlit_input.get('background_color'),
            'text': streamlit_input.get('text_color')
        }
        
        # Entferne None-Werte
        colors_mapping = {k: v for k, v in colors_mapping.items() if v is not None}
        
        if colors_mapping:
            logger.info(f"   🎨 CI-Farben aus Einzelfeldern: {list(colors_mapping.keys())}")
            return self._extract_ci_colors(colors_mapping)
        
        # Priorität 3: Fallback zu corporate_colors (legacy)
        corporate_colors = streamlit_input.get('corporate_colors', {})
        if corporate_colors:
            return self._extract_ci_colors(corporate_colors)
        
        # Fallback: Default-Farben
        logger.warning("⚠️ Keine CI-Farben gefunden, verwende Default-Farben")
        return self._extract_ci_colors({})
    
    def _extract_ci_colors(self, colors: Dict[str, str]) -> Dict[str, str]:
        """Extrahiert und validiert CI-Farben (legacy Methode)"""
        default_colors = {
            'primary': '#005EA5',
            'secondary': '#B4D9F7', 
            'accent': '#FFC20E',
            'background': '#FFFFFF',
            'text': '#000000'
        }
        
        ci_colors = {}
        for key, default_value in default_colors.items():
            color = colors.get(key, default_value)
            # Basic Hex-Color validation
            if isinstance(color, str) and color.startswith('#') and len(color) in [4, 7]:
                ci_colors[key] = color
            else:
                ci_colors[key] = default_value
                logger.warning(f"⚠️ Ungültige Farbe für {key}, verwende Default: {default_value}")
        
        return ci_colors
    


class LayoutIntegrator(MultiPromptStage):
    """
    🎨 STUFE 2: LAYOUT-INTEGRATOR
    
    ZWECK: Wendet Layout-Rules auf strukturierte Daten an
    INPUT: StructuredInput
    OUTPUT: LayoutIntegratedData mit Layout-spezifischen Anpassungen
    """
    
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.enhanced_layouts = self._load_enhanced_layouts()
        
    def _load_enhanced_layouts(self) -> Dict[str, Any]:
        """Lädt erweiterte Layout-Definitionen"""
        layout_files = [
            'enhanced_layout_definitions.yaml',
            'complete_layout_definitions.yaml'  # Fallback
        ]
        
        for layout_file in layout_files:
            file_path = self.project_root / "input_config" / layout_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        layouts = yaml.safe_load(f)
                        logger.info(f"✅ Layout-Definitionen geladen: {layout_file} ({len(layouts)} Layouts)")
                        return layouts
                except Exception as e:
                    logger.error(f"❌ Fehler beim Laden von {layout_file}: {e}")
        
        logger.warning("⚠️ Keine Layout-Definitionen gefunden - verwende Minimal-Fallback")
        return self._get_minimal_layouts()
    
    def _get_minimal_layouts(self) -> Dict[str, Any]:
        """Minimal-Fallback für Layout-Definitionen"""
        return {
            'skizze1_vertical_split': {
                'name': 'Vertikale Teilung',
                'zones': {'left_zone': {}, 'right_zone': {}},
                'text_mapping': {},
                'motiv_integration': {},
                'typography': {},
                'adaptive_rules': {}
            }
        }
    
    def process(self, structured_input: StructuredInput) -> LayoutIntegratedData:
        """Integriert Layout-Rules in strukturierte Daten"""
        start_time = datetime.now()
        self._log_stage_start("StructuredInput")
        
        try:
            layout_id = structured_input.layout_id
            
            # Layout-Definition laden
            layout_def = self.enhanced_layouts.get(layout_id)
            if not layout_def:
                logger.warning(f"⚠️ Layout '{layout_id}' nicht gefunden - verwende skizze1_vertical_split")
                layout_def = self.enhanced_layouts.get('skizze1_vertical_split', {})
                layout_id = 'skizze1_vertical_split'
            
            # Banner-Farben zu generischen Beschreibungen konvertieren
            layout_def = self._convert_banner_colors_to_generic(layout_def)
            logger.info(f"   🎨 Banner-Farben zu generischen Beschreibungen konvertiert")
            
            # CI-Farben in Layout-Definition einsetzen (nur für Akzente)
            resolved_layout = self._resolve_layout_colors(layout_def, structured_input.ci_colors)
            
            # Text-Mappings berechnen
            text_placements = self._calculate_text_placements(resolved_layout, structured_input)
            
            # Motiv-Treatment bestimmen
            motiv_treatment = self._determine_motiv_treatment(resolved_layout, structured_input)
            
            # Typography anwenden
            applied_typography = self._apply_typography(resolved_layout, structured_input)
            
            # Adaptive Anpassungen
            adaptive_adjustments = self._apply_adaptive_rules(resolved_layout, structured_input)
            
            # Layout-Metriken berechnen
            layout_metrics = self._calculate_layout_metrics(resolved_layout, structured_input)
            
            # Layout-integrierte Daten erstellen
            integrated = LayoutIntegratedData(
                structured_input=structured_input,
                layout_definition=resolved_layout,
                text_placements=text_placements,
                motiv_treatment=motiv_treatment,
                applied_typography=applied_typography,
                adaptive_adjustments=adaptive_adjustments,
                layout_metrics=layout_metrics
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self._log_stage_complete("LayoutIntegratedData", processing_time)
            
            logger.info(f"   🎨 Layout: {resolved_layout.get('name', 'Unknown')}")
            logger.info(f"   📐 Zonen: {len(resolved_layout.get('zones', {}))}")
            logger.info(f"   📝 Text-Placements: {len(text_placements)}")
            logger.info(f"   🔧 Adaptive Adjustments: {len(adaptive_adjustments)}")
            
            return integrated
            
        except Exception as e:
            logger.error(f"❌ LayoutIntegrator Fehler: {e}")
            raise
    
    def _convert_banner_colors_to_generic(self, layout_def: Dict[str, Any]) -> Dict[str, Any]:
        """Konvertiert Banner-Hintergrundfarben zu generischen Beschreibungen"""
        import copy
        converted = copy.deepcopy(layout_def)
        
        def convert_colors(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'background_color' and isinstance(value, str):
                        # Banner-Farben zu generischen Beschreibungen
                        if '{secondary_color}' in value:
                            obj[key] = 'professional dark background'
                        elif '{primary_color}' in value:
                            obj[key] = 'professional light background'
                        elif '{accent_color}' in value:
                            obj[key] = 'highlighted accent area'
                        else:
                            obj[key] = convert_colors(value)
                    else:
                        obj[key] = convert_colors(value)
            elif isinstance(obj, list):
                return [convert_colors(item) for item in obj]
            elif isinstance(obj, str):
                # Banner-Hintergrundfarben in generische Beschreibungen umwandeln
                if 'background_color' in str(obj):
                    obj = obj.replace('{secondary_color}', 'professional dark background')
                    obj = obj.replace('{primary_color}', 'professional light background')
                    obj = obj.replace('{accent_color}', 'highlighted accent area')
                return obj
            return obj
        
        return convert_colors(converted)
    
    def _resolve_layout_colors(self, layout_def: Dict[str, Any], ci_colors: Dict[str, Any]) -> Dict[str, Any]:
        """Ersetzt CI-Farben-Platzhalter UND hardcodierte Standard-Farben in Layout-Definition"""
        import copy
        resolved = copy.deepcopy(layout_def)
        
        # CI-Farben extrahieren
        primary = ci_colors.get('primary', '#005EA5')
        secondary = ci_colors.get('secondary', '#B4D9F7')
        accent = ci_colors.get('accent', '#FFC20E')
        background = ci_colors.get('background', '#FFFFFF')
        
        # Standard-Farben Mapping zu CI-Farben
        color_mapping = {
            # Headline und wichtige Texte → Primary
            '#000000': primary,  # Schwarz → Primary
            '#333333': primary,  # Dunkelgrau → Primary
            
            # Subline und sekundäre Texte → Secondary  
            '#777777': secondary,  # Grau → Secondary
            '#666666': secondary,  # Mittelgrau → Secondary
            
            # Stellentitel → Primary (aber heller)
            '#00B5E2': primary,  # Blau → Primary
            '#0088CC': primary,  # Dunkelblau → Primary
            
            # CTA und Akzente → Accent
            '#FFC20E': accent,  # Gelb → Accent
            '#FFB300': accent,  # Orange → Accent
            
            # Logo und Hintergründe → Secondary
            '#EEEEEE': secondary,  # Hellgrau → Secondary
            '#F5F5F5': secondary,  # Sehr hellgrau → Secondary
        }
        
        # Rekursive Farben-Ersetzung
        def replace_colors(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'background_color' and isinstance(value, str):
                        # ALLE CI-Farben-Platzhalter auflösen
                        if '{primary_color}' in value:
                            obj[key] = value.replace('{primary_color}', primary)
                        elif '{secondary_color}' in value:
                            obj[key] = value.replace('{secondary_color}', secondary)
                        elif '{accent_color}' in value:
                            obj[key] = value.replace('{accent_color}', accent)
                        elif '{background_color}' in value:
                            obj[key] = value.replace('{background_color}', background)
                        else:
                            # Hardcodierte Farben durch CI-Farben ersetzen
                            for old_color, new_color in color_mapping.items():
                                if old_color in value:
                                    obj[key] = value.replace(old_color, new_color)
                                    logger.info(f"   🎨 Farbe ersetzt: {old_color} → {new_color} in {key}")
                        obj[key] = replace_colors(obj[key])
                    else:
                        obj[key] = replace_colors(value)
            elif isinstance(obj, list):
                return [replace_colors(item) for item in obj]
            elif isinstance(obj, str):
                # Ersetze Farben-Platzhalter UND hardcodierte Farben
                # 1. Platzhalter ersetzen
                if '{primary_color}' in obj:
                    obj = obj.replace('{primary_color}', primary)
                if '{secondary_color}' in obj:
                    obj = obj.replace('{secondary_color}', secondary)
                if '{accent_color}' in obj:
                    obj = obj.replace('{accent_color}', accent)
                if '{background_color}' in obj:
                    obj = obj.replace('{background_color}', background)
                
                # 2. Hardcodierte Standard-Farben durch CI-Farben ersetzen
                for old_color, new_color in color_mapping.items():
                    if old_color in obj:
                        obj = obj.replace(old_color, new_color)
                        logger.info(f"   🎨 Hardcodierte Farbe ersetzt: {old_color} → {new_color}")
                
                return obj
            return obj
        
        result = replace_colors(resolved)
        logger.info(f"   🎨 CI-Farben vollständig in Layout integriert: Primary={primary}, Secondary={secondary}, Accent={accent}")
        return result
    
    def _calculate_text_placements(self, layout_def: Dict[str, Any], structured_input: StructuredInput) -> Dict[str, Dict[str, Any]]:
        """Berechnet exakte Text-Platzierungen basierend auf Layout-Definition"""
        text_mapping = layout_def.get('text_mapping', {})
        placements = {}
        
        # Mapping für alle Text-Elemente
        text_elements = {
            'headline': structured_input.headline,
            'subline': structured_input.subline,
            'company': structured_input.company,
            'stellentitel': structured_input.stellentitel,
            'position': structured_input.position_long,
            'benefits': structured_input.benefits,
            'cta': structured_input.cta,
            'logo': structured_input.logo_placeholder if not structured_input.logo_file else f"[Logo: {structured_input.logo_file.name}]" if hasattr(structured_input.logo_file, 'name') else structured_input.logo_placeholder
        }
        
        # Standort mit Pin-Symbol hinzufügen
        if structured_input.location:
            text_elements['standort'] = f"📍 {structured_input.location}"
        
        for element_name, element_content in text_elements.items():
            if element_name in text_mapping and element_content:
                mapping = text_mapping[element_name]
                
                # Spezielle Behandlung für Standort mit Pin-Symbol
                if element_name == 'standort':
                    # Pin-Symbol bereits im Content enthalten
                    content = element_content
                else:
                    content = element_content
                
                placements[element_name] = {
                    'content': content,
                    'target_zone': mapping.get('target_zone', 'default'),
                    'position': mapping.get('position', 'center'),
                    'coordinates': mapping.get('coordinates', 'center'),
                    'font_size': self._select_font_size(mapping.get('font_size', {}), content),
                    'color': mapping.get('color', '#000000'),
                    'weight': mapping.get('weight', 'regular'),
                    'max_length': mapping.get('max_length', 50),
                    'priority': mapping.get('priority', 5)
                }
        
        return placements
    
    def _select_font_size(self, font_size_config: Dict[str, str], content: str) -> str:
        """Wählt passende Schriftgröße basierend auf Content-Länge"""
        if isinstance(font_size_config, str):
            return font_size_config
        
        # Intelligente Größen-Auswahl basierend auf Content-Länge
        content_length = len(str(content))
        
        if content_length <= 20:
            return font_size_config.get('primary', '42px')
        elif content_length <= 35:
            return font_size_config.get('secondary', '36px')
        else:
            return font_size_config.get('fallback', '30px')
    
    def _determine_motiv_treatment(self, layout_def: Dict[str, Any], structured_input: StructuredInput) -> Dict[str, Any]:
        """Bestimmt Motiv-Behandlung basierend auf Layout"""
        motiv_integration = layout_def.get('motiv_integration', {})
        
        return {
            'original_prompt': structured_input.motiv_prompt,
            'fill_mode': motiv_integration.get('fill_mode', 'cover'),
            'aspect_ratio': motiv_integration.get('aspect_ratio', '1:1'),
            'positioning': motiv_integration.get('positioning', 'center_crop'),
            'focal_point': motiv_integration.get('focal_point', 'center'),
            'overlay_compatibility': motiv_integration.get('overlay_compatibility', False),
            'text_safe_areas': motiv_integration.get('text_safe_areas', []),
            'contrast_requirements': motiv_integration.get('contrast_requirements', 'medium'),
            'enhanced_description': self._enhance_motiv_description(
                structured_input.motiv_prompt,
                motiv_integration.get('motiv_description_integration', {})
            )
        }
    
    def _enhance_motiv_description(self, original_prompt: str, integration_rules: Dict[str, Any]) -> str:
        """Erweitert Motiv-Beschreibung um Layout-spezifische Elemente"""
        if not integration_rules:
            return original_prompt
        
        enhancements = []
        
        # Scene Focus
        scene_focus = integration_rules.get('scene_focus')
        if scene_focus:
            enhancements.append(f"Komposition: {scene_focus}")
        
        # Subject Positioning
        subject_pos = integration_rules.get('subject_positioning')
        if subject_pos:
            enhancements.append(f"Positionierung: {subject_pos}")
        
        # Lighting Preference
        lighting_pref = integration_rules.get('lighting_preference')
        if lighting_pref:
            enhancements.append(f"Beleuchtung: {lighting_pref}")
        
        if enhancements:
            return f"{original_prompt}. {', '.join(enhancements)}"
        else:
            return original_prompt
    
    def _apply_typography(self, layout_def: Dict[str, Any], structured_input: StructuredInput) -> Dict[str, Any]:
        """Wendet Typography-Regeln an"""
        typography = layout_def.get('typography', {})
        
        return {
            'font_family': typography.get('font_family', 'Inter, system-ui, sans-serif'),
            'base_size': typography.get('base_size', '16px'),
            'scale_ratio': typography.get('scale_ratio', 1.25),
            'hierarchy': typography.get('hierarchy', {}),
            'applied_to_layout': layout_def.get('name', 'Unknown')
        }
    
    def _apply_adaptive_rules(self, layout_def: Dict[str, Any], structured_input: StructuredInput) -> List[Dict[str, Any]]:
        """Wendet adaptive Regeln an (Content-Overflow-Handling)"""
        adaptive_rules = layout_def.get('adaptive_rules', {})
        adjustments = []
        
        # Long Headline Check
        if 'long_headline' in adaptive_rules:
            rule = adaptive_rules['long_headline']
            trigger_length = int(rule.get('trigger', 'length > 50').split('> ')[1])
            
            if len(structured_input.headline) > trigger_length:
                adjustments.append({
                    'rule': 'long_headline',
                    'trigger': f"Headline zu lang ({len(structured_input.headline)} > {trigger_length})",
                    'action': rule.get('action', 'reduce_font_size'),
                    'applied': True
                })
        
        # Many Benefits Check
        if 'many_benefits' in adaptive_rules:
            rule = adaptive_rules['many_benefits']
            trigger_count = int(rule.get('trigger', 'count > 5').split('> ')[1])
            
            if len(structured_input.benefits) > trigger_count:
                adjustments.append({
                    'rule': 'many_benefits',
                    'trigger': f"Zu viele Benefits ({len(structured_input.benefits)} > {trigger_count})",
                    'action': rule.get('action', 'truncate_with_ellipsis'),
                    'applied': True
                })
        
        return adjustments
    
    def _calculate_layout_metrics(self, layout_def: Dict[str, Any], structured_input: StructuredInput) -> Dict[str, Any]:
        """Berechnet Layout-Metriken"""
        zones = layout_def.get('zones', {})
        
        return {
            'layout_complexity': layout_def.get('complexity', 'unknown'),
            'zones_count': len(zones),
            'text_elements_count': len([x for x in [structured_input.headline, structured_input.company, structured_input.position_long] if x]),
            'benefits_count': len(structured_input.benefits),
            'total_content_length': sum([
                len(structured_input.headline),
                len(structured_input.company), 
                len(structured_input.position_long),
                sum(len(b) for b in structured_input.benefits)
            ]),
            'ci_colors_count': len(structured_input.ci_colors),
            'layout_efficiency': 'high' if len(zones) <= 3 else 'medium' if len(zones) <= 6 else 'complex'
        }

class PromptFinalizer(MultiPromptStage):
    """
    🚀 STUFE 3: PROMPT-FINALIZER
    
    ZWECK: Generiert finale DALL-E und Midjourney-Prompts
    INPUT: LayoutIntegratedData 
    OUTPUT: FinalizedPrompts mit optimierten Prompts
    """
    
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.outputs_dir = project_root / "outputs"
        self.outputs_dir.mkdir(exist_ok=True)
        
        # OpenAI Setup für AI-Enhanced Prompt Generation
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("✅ OpenAI Client initialisiert für AI-Enhanced Prompts")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI Client Fehler: {e}")
    
    def process(self, layout_data: LayoutIntegratedData, enable_text_rendering: bool = False) -> FinalizedPrompts:
        """
        Generiert finale Prompts aus Layout-integrierten Daten
        
        Args:
            layout_data: Layout-integrierte Daten
            enable_text_rendering: Ob Text im DALL-E Bild gerendert werden soll
        """
        start_time = datetime.now()
        self._log_stage_start("LayoutIntegratedData")
        
        try:
            # Midjourney-Prompt generieren
            midjourney_prompt = self._generate_midjourney_prompt(layout_data, enable_text_rendering)
            midjourney_metrics = self._analyze_prompt_quality(midjourney_prompt, 'midjourney')
            
            # DALL-E-Prompt generieren
            dalle_prompt = self._generate_dalle_prompt(layout_data, enable_text_rendering)
            dalle_metrics = self._analyze_prompt_quality(dalle_prompt, 'dalle')
            
            # Cinematischen Prompt für OpenAI API generieren
            cinematic_prompt = self._generate_cinematic_prompt(layout_data, enable_text_rendering)
            
            # Quality Assessment
            quality_assessment = self._assess_overall_quality(layout_data, midjourney_prompt, dalle_prompt)
            
            # Output-Files erstellen
            output_files = self._save_output_files(layout_data, midjourney_prompt, dalle_prompt, cinematic_prompt)
            
            # Finalisierte Prompts erstellen
            processing_time = (datetime.now() - start_time).total_seconds()
            
            finalized = FinalizedPrompts(
                layout_data=layout_data,
                midjourney_prompt=midjourney_prompt,
                dalle_prompt=dalle_prompt,
                cinematic_prompt=cinematic_prompt,
                midjourney_metrics=midjourney_metrics,
                dalle_metrics=dalle_metrics,
                quality_assessment=quality_assessment,
                output_files=output_files,
                total_processing_time=processing_time
            )
            
            self._log_stage_complete("FinalizedPrompts", processing_time)
            
            logger.info(f"   🎬 Midjourney: {len(midjourney_prompt)} chars")
            logger.info(f"   🏗️ DALL-E: {len(dalle_prompt)} chars ({'✅ OK' if len(dalle_prompt) <= 4000 else '❌ ZU LANG'})")
            logger.info(f"   🎭 Cinematic: {len(cinematic_prompt.full_prompt) if cinematic_prompt else 0} chars")
            logger.info(f"   📊 Quality Score: {quality_assessment.get('overall_score', 0)}/100")
            logger.info(f"   📁 Files: {len(output_files)} erstellt")
            
            return finalized
            
        except Exception as e:
            logger.error(f"❌ PromptFinalizer Fehler: {e}")
            raise
    
    def _generate_midjourney_prompt(self, layout_data: LayoutIntegratedData, enable_text_rendering: bool = False) -> str:
        """
        🎬 Generiert professionellen Midjourney-Prompt nach optimierter 9-Punkte-Formel
        
        Struktur:
        1. Subjektbeschreibung (Beruf + Tätigkeit + Emotion)
        2. Szene & Umgebung (Ort + Interaktion + Stimmung)
        3. Körperhaltung + Perspektive + Komposition
        4. Kamera + Licht + Stilmittel
        5. Bildaufbau: Flächenaufteilung + visuelle Balance
        6. Corporate Design Hinweise
        7. Stilattribute & Rendering
        8. Midjourney Parameter
        9. Negative Prompts
        """
        # Extract data
        structured = layout_data.structured_input
        layout_def = layout_data.layout_definition
        motiv_treatment = layout_data.motiv_treatment
        
        prompt_parts = []
        
        # 1. 👤 SUBJEKTBESCHREIBUNG (Beruf + Tätigkeit + Emotion)
        subject_description = self._build_subject_description(structured)
        prompt_parts.append(subject_description)
        
        # 2. 🏢 SZENE & UMGEBUNG (Ort + Interaktion + Stimmung)
        scene_environment = self._build_scene_environment(structured, layout_def)
        prompt_parts.append(scene_environment)
        
        # 3. 🎭 KÖRPERHALTUNG + PERSPEKTIVE + KOMPOSITION
        posture_perspective = self._build_posture_perspective(structured, layout_def)
        prompt_parts.append(posture_perspective)
        
        # 4. 📸 KAMERA + LICHT + STILMITTEL
        camera_lighting = self._build_camera_lighting(structured)
        prompt_parts.append(camera_lighting)
        
        # 5. 🎨 BILDAUFBAU: FLÄCHENAUFTEILUNG + VISUELLE BALANCE
        composition_balance = self._build_composition_balance(layout_def)
        prompt_parts.append(composition_balance)
        
        # 6. 🏢 CORPORATE DESIGN HINWEISE
        corporate_design = self._build_corporate_design(structured)
        if corporate_design:
            prompt_parts.append(corporate_design)
        
        # 6.5. 📝 TEXT-LAYOUT-BEREICHE (Headlines, Benefits, CTA)
        text_layout = self._build_text_layout_areas(structured, layout_data, enable_text_rendering)
        if text_layout:
            prompt_parts.append(text_layout)
        
        # 7. ✨ STILATTRIBUTE & RENDERING
        style_rendering = self._build_style_rendering(structured, enable_text_rendering)
        prompt_parts.append(style_rendering)
        
        # 8. ⚙️ MIDJOURNEY PARAMETER
        mj_parameters = self._build_midjourney_parameters(motiv_treatment)
        
        # 9. 🚫 NEGATIVE PROMPTS  
        negative_prompts = self._build_negative_prompts(enable_text_rendering)
        
        # Combine all parts
        main_prompt = ", ".join([part for part in prompt_parts if part])
        full_prompt = f"{main_prompt} {mj_parameters} {negative_prompts}"
        
        logger.info("🎬 MIDJOURNEY 10-PUNKTE-FORMEL angewendet (mit Text-Layout-Integration):")
        logger.info(f"   👤 Subjekt: {len(prompt_parts[0]) if len(prompt_parts) > 0 else 0} chars")
        logger.info(f"   🏢 Umgebung: {len(prompt_parts[1]) if len(prompt_parts) > 1 else 0} chars")
        logger.info(f"   🎭 Körperhaltung: {len(prompt_parts[2]) if len(prompt_parts) > 2 else 0} chars")
        logger.info(f"   📸 Kamera/Licht: {len(prompt_parts[3]) if len(prompt_parts) > 3 else 0} chars")
        logger.info(f"   🎨 Komposition: {len(prompt_parts[4]) if len(prompt_parts) > 4 else 0} chars")
        logger.info(f"   🏢 Corporate: {len(prompt_parts[5]) if len(prompt_parts) > 5 else 0} chars")
        
        # Text-Layout-Bereiche berücksichtigen (kann optional sein)
        text_layout_idx = 6 if len(prompt_parts) > 6 else None
        if text_layout_idx and text_layout:
            logger.info(f"   📝 Text-Layout: {len(prompt_parts[text_layout_idx]) if len(prompt_parts) > text_layout_idx else 0} chars")
            style_idx = 7
        else:
            logger.info(f"   📝 Text-Layout: 0 chars (nicht enthalten)")
            style_idx = 6
            
        logger.info(f"   ✨ Stilattribute: {len(prompt_parts[style_idx]) if len(prompt_parts) > style_idx else 0} chars")
        logger.info(f"   ⚙️ Parameter: {len(mj_parameters)} chars")
        logger.info(f"   🚫 Negative: {len(negative_prompts)} chars")
        logger.info(f"   📊 Gesamt: {len(full_prompt)} chars")
        logger.info(f"   📝 Text-Rendering: {'AKTIVIERT' if enable_text_rendering else 'DEAKTIVIERT'}")
        
        return full_prompt.strip()
    
    def _generate_dalle_prompt(self, layout_data: LayoutIntegratedData, enable_text_rendering: bool = False) -> str:
        """
        Generiert strukturierten DALL-E-Prompt
        
        Args:
            layout_data: Layout und Struktur-Daten
            enable_text_rendering: Ob Text im Bild gerendert werden soll
                                 True = Mit Text (Risiko korrupter deutscher Zeichen)
                                 False = Ohne Text (sauberes Layout, Text später als Overlay)
        """
        # Extract data
        structured = layout_data.structured_input
        layout_def = layout_data.layout_definition
        text_placements = layout_data.text_placements
        motiv_treatment = layout_data.motiv_treatment
        
        prompt_sections = []
        
        # Canvas Structure - REIN BESCHREIBEND (keine Layout-Details)
        canvas_size = layout_def.get('canvas_size', '1080x1080')
        layout_name = layout_def.get('name', 'Layout')
        layout_description = layout_def.get('description', '')
        
        prompt_sections.append(f"— CANVAS STRUCTURE: {layout_name} —")
        prompt_sections.append(f"Canvas: {canvas_size}px, {layout_description}")
        prompt_sections.append("**LAYOUT-ORIENTIERUNG: Links Textstack, rechts Motiv mit Kreis - rein verbale Orientierung**")
        
        # VOLLSTÄNDIGE LAYOUT-KONTUREN INTEGRATION
        style_options = structured.style_options or {}
        
        # 1. Layout-Style (Container-Form)
        layout_style_config = style_options.get('layout_style', {})
        layout_style = layout_style_config.get('type', 'rounded_modern')
        layout_style_name = layout_style_config.get('name', 'Abgerundet & Modern')
        
        # Layout-Style Beschreibungen für DALL-E
        layout_style_descriptions = {
            "sharp_geometric": "scharfe, eckige Konturen für ein modernes, technisches Aussehen",
            "rounded_modern": "sanft abgerundete Ecken für ein freundliches, modernes Design", 
            "organic_flowing": "organische, fließende Formen für ein natürliches, dynamisches Layout",
            "wave_contours": "wellige, geschwungene Konturen für ein spielerisches, kreatives Design",
            "hexagonal": "sechseckige Formen für ein futuristisches, technisches Aussehen",
            "circular": "kreisförmige und ovale Bereiche für ein harmonisches, ausgewogenes Layout",
            "asymmetric": "asymmetrische, unregelmäßige Formen für ein dynamisches, künstlerisches Design",
            "minimal_clean": "minimalistische, saubere Linien für ein professionelles, klares Layout"
        }
        
        style_description = layout_style_descriptions.get(layout_style, "moderne, abgerundete Konturen")
        
        # 2. Container-Form (Text-Container)
        container_shape_config = style_options.get('container_shape', {})
        container_shape = container_shape_config.get('type', 'rounded_rectangle')
        container_shape_name = container_shape_config.get('name', '📱 Abgerundet')
        
        container_shape_descriptions = {
            "rectangle": "rechteckige, eckige Text-Container",
            "rounded_rectangle": "abgerundete, moderne Text-Container", 
            "circle": "kreisförmige, runde Text-Container",
            "hexagon": "sechseckige, geometrische Text-Container",
            "organic_blob": "organische, fließende Text-Container"
        }
        
        container_description = container_shape_descriptions.get(container_shape, "abgerundete, moderne Text-Container")
        
        # 3. Rahmen-Stil
        border_style_config = style_options.get('border_style', {})
        border_style = border_style_config.get('type', 'soft_shadow')
        border_style_name = border_style_config.get('name', '🌫️ Weicher Schatten')
        
        border_style_descriptions = {
            "solid": "durchgezogene, klare Rahmen",
            "dashed": "gestrichelte, moderne Rahmen", 
            "dotted": "gepunktete, dezente Rahmen",
            "soft_shadow": "weiche Schatten ohne sichtbare Rahmen",
            "glow": "leuchtende, glühende Effekte",
            "none": "keine sichtbaren Rahmen"
        }
        
        border_description = border_style_descriptions.get(border_style, "weiche Schatten ohne sichtbare Rahmen")
        
        # 4. Ecken-Rundung
        corner_radius_config = style_options.get('corner_radius', {})
        corner_radius = corner_radius_config.get('type', 'medium')
        corner_radius_name = corner_radius_config.get('name', '⌜ Mittel')
        
        corner_radius_descriptions = {
            "small": "kleine, subtile Rundung (8px)",
            "medium": "mittlere, ausgewogene Rundung (16px)", 
            "large": "große, freundliche Rundung (24px)",
            "xl": "sehr große, weiche Rundung (32px)"
        }
        
        corner_description = corner_radius_descriptions.get(corner_radius, "mittlere, ausgewogene Rundung (16px)")
        
        # 5. Akzent-Stil
        accent_elements_config = style_options.get('accent_elements', {})
        accent_elements = accent_elements_config.get('type', 'modern_minimal')
        accent_elements_name = accent_elements_config.get('name', '⚪ Modern Minimal')
        
        accent_elements_descriptions = {
            "classic": "klassische, traditionelle Akzente",
            "modern_minimal": "moderne, minimalistische Akzente", 
            "playful": "verspielte, kreative Akzente",
            "organic": "organische, natürliche Akzente",
            "bold": "auffällige, kraftvolle Akzente"
        }
        
        accent_description = accent_elements_descriptions.get(accent_elements, "moderne, minimalistische Akzente")
        
        # Alle Layout-Konturen Parameter integrieren
        prompt_sections.append(f"• Layout-Konturen: {style_description}")
        prompt_sections.append(f"• Container-Form: {container_description}")
        prompt_sections.append(f"• Rahmen-Stil: {border_description}")
        prompt_sections.append(f"• Ecken-Rundung: {corner_description}")
        prompt_sections.append(f"• Akzent-Stil: {accent_description}")
        prompt_sections.append(f"• Layout-Style: {layout_style_name} - {style_description}")
        prompt_sections.append(f"• Layout-Orientierung: Links Textstack, rechts Motiv mit Kreis")
        
        # 6. Textur-Stil
        texture_style_config = style_options.get('texture_style', {})
        texture_style = texture_style_config.get('type', 'gradient')
        texture_style_name = texture_style_config.get('name', '🌈 Farbverlauf')
        
        texture_style_descriptions = {
            "solid": "einfarbige, flache Oberflächen",
            "gradient": "sanfte Farbverläufe und Übergänge", 
            "pattern": "subtile Muster und Texturen",
            "glass_effect": "gläserne, transparente Effekte",
            "matte": "mattierte, weiche Oberflächen"
        }
        
        texture_description = texture_style_descriptions.get(texture_style, "sanfte Farbverläufe und Übergänge")
        
        # 7. Hintergrund-Behandlung
        background_treatment_config = style_options.get('background_treatment', {})
        background_treatment = background_treatment_config.get('type', 'subtle_pattern')
        background_treatment_name = background_treatment_config.get('name', '🌸 Subtiles Muster')
        
        background_treatment_descriptions = {
            "solid": "einfarbige, saubere Hintergründe",
            "subtle_pattern": "subtile, dezente Muster", 
            "geometric": "geometrische, strukturierte Hintergründe",
            "organic": "organische, natürliche Hintergründe",
            "none": "transparente, offene Hintergründe"
        }
        
        background_description = background_treatment_descriptions.get(background_treatment, "subtile, dezente Muster")
        
        # Zusätzliche Layout-Details
        prompt_sections.append(f"• Textur-Stil: {texture_description}")
        prompt_sections.append(f"• Hintergrund: {background_description}")
        
        # Zones Description - REIN BESCHREIBEND (keine Layout-Details)
        zones = layout_def.get('zones', {})
        if zones:
            for zone_name, zone_config in zones.items():
                position = zone_config.get('position', '')
                bg_color = zone_config.get('background_color', 'transparent')
                content_type = zone_config.get('content_type', '')
                description = zone_config.get('description', '')
                
                if bg_color != 'transparent':
                    prompt_sections.append(f"• {zone_name.upper()} ({position}): {content_type} in {bg_color}")
                else:
                    prompt_sections.append(f"• {zone_name.upper()} ({position}): {content_type}")
                
                if description:
                    prompt_sections.append(f"  → {description}")
        
        # Text Elements Description - DYNAMIC basierend auf Text-Rendering Option
        if text_placements:
            if enable_text_rendering:
                prompt_sections.append("\n— TEXT-CONTENT RENDERING —")
                prompt_sections.append("**TEXT-RENDERING AKTIVIERT: Alle Texte sollen als lesbare Schrift im Bild erscheinen**")
                prompt_sections.append("**WARNUNG: Deutsche Umlaute könnten als korrupte Zeichen erscheinen**")
                prompt_sections.append("**ANWEISUNG: Verwende klare, gut lesbare Schriftarten für alle Textelemente:**")
            else:
                prompt_sections.append("\n— TEXT-LAYOUT-BEREICHE —")
                prompt_sections.append("**LAYOUT-ANWEISUNG: Alle definierten Bereiche müssen als sichtbare Farbflächen im Bild erscheinen**")
                prompt_sections.append("**KRITISCH: Text-BEREICHE als deutlich abgegrenzte Layout-Zonen - KEINE Unterbrechungen, KEINE überlappenden Texte**")
                prompt_sections.append("**Die folgenden Bereiche sollen als kompakte, zusammenhängende Flächen in den definierten Layout-Bereichen erscheinen:**")
            
            # Hierarchische Reihenfolge für bessere Verständlichkeit
            element_order = ['headline', 'subline', 'company', 'stellentitel', 'logo', 'position', 'benefits', 'cta']
            
            for element_name in element_order:
                if element_name in text_placements:
                    placement = text_placements[element_name]
                    content = placement.get('content', '')
                    target_zone = placement.get('target_zone', '')
                    font_size = placement.get('font_size', {})
                    
                    if not content:  # Skip empty content
                        continue
                    
                    if enable_text_rendering:
                        # TEXT-RENDERING MODUS: Zeige echten Text
                        if isinstance(content, list):  # Benefits
                            prompt_sections.append(f"• {element_name.title()}-Text in {target_zone}: LESBARE SCHRIFT")
                            for i, item in enumerate(content, 1):
                                prompt_sections.append(f"  → \"{item}\" als gut lesbare Schrift")
                        else:
                            primary_size = font_size.get('primary', 'Standard') if isinstance(font_size, dict) else 'Standard'
                            prompt_sections.append(f"• {element_name.upper()}-Text in {target_zone}: \"{content}\" als lesbare Schrift ({primary_size})")
                    else:
                        # LAYOUT-MODUS: Zeige Bereiche mit detailliertem Inhalt und Stil
                        if isinstance(content, list):  # Benefits
                            prompt_sections.append(f"• {element_name.title()}-BEREICH in {target_zone}: TEXT-ZONE")
                            prompt_sections.append(f"  → Inhalt: {len(content)} Bullet-Points, Text: {', '.join(content[:3])}")
                            prompt_sections.append(f"  → Stil: professionelle, gut lesbare Schrift, weiß auf #005EA5, gleichmäßiger Abstand, gut lesbar")
                            prompt_sections.append(f"  → Text wird direkt im Bild gerendert")
                        else:
                            primary_size = font_size.get('primary', 'Standard') if isinstance(font_size, dict) else 'Standard'
                            prompt_sections.append(f"• {element_name.upper()}-BEREICH in {target_zone}: TEXT-ZONE")
                            prompt_sections.append(f"  → Inhalt: \"{content}\"")
                            prompt_sections.append(f"  → Stil: professionelle, gut lesbare Schrift, weiß auf #005EA5, zentriert")
                            prompt_sections.append(f"  → Text wird direkt im Bild gerendert")
            
            # Standort-Integration mit Akzentfarbe und Pin-Symbol
            if hasattr(layout_data.structured_input, 'location') and layout_data.structured_input.location:
                location = layout_data.structured_input.location
                accent_color = layout_data.structured_input.ci_colors.get('accent', '#FFC20E')
                
                if enable_text_rendering:
                    prompt_sections.append(f"• STANDORT-BEREICH: TEXT-ZONE mit Pin-Symbol und Akzentfarbe {accent_color}")
                    prompt_sections.append(f"  → Inhalt: \"📍 {location}\"")
                    prompt_sections.append(f"  → Stil: professionelle, gut lesbare Schrift, weiß auf {accent_color}")
                else:
                    prompt_sections.append(f"• STANDORT-BEREICH: TEXT-ZONE mit Pin-Symbol und Akzentfarbe {accent_color}")
                    prompt_sections.append(f"  → Standort-Pin-Symbol (📍) als visuelles Element")
                    prompt_sections.append(f"  → Akzentfarbe {accent_color} für Standort-Bereich verwenden")
                    prompt_sections.append(f"  → Text wird direkt im Bild gerendert")
            
            # CTA-Integration mit Akzentfarbe
            if hasattr(layout_data.structured_input, 'cta') and layout_data.structured_input.cta:
                cta_text = layout_data.structured_input.cta
                accent_color = layout_data.structured_input.ci_colors.get('accent', '#FFC20E')
                
                if enable_text_rendering:
                    prompt_sections.append(f"• CTA-BUTTON: TEXT-ZONE in Akzentfarbe {accent_color}")
                    prompt_sections.append(f"  → Inhalt: \"{cta_text}\"")
                    prompt_sections.append(f"  → Stil: professionelle, gut lesbare Schrift, weiß auf {accent_color}")
                else:
                    prompt_sections.append(f"• CTA-BUTTON: TEXT-ZONE in Akzentfarbe {accent_color}")
                    prompt_sections.append(f"  → Professioneller Button-Stil mit abgerundeten Ecken")
                    prompt_sections.append(f"  → Text wird direkt im Bild gerendert")
            
            # Umsetzungs-Anweisungen
            if enable_text_rendering:
                prompt_sections.append("\n**TEXT-UMSETZUNG: Alle Texte als lesbare Schrift in den entsprechenden Zonen rendern**")
            else:
                prompt_sections.append("\n**TEXT-UMSETZUNG: Alle Texte werden direkt im Bild gerendert**")
        
        # Motiv Description with Image Reference
        enhanced_motiv = motiv_treatment.get('enhanced_description', structured.motiv_prompt)
        prompt_sections.append(f"\n— MOTIV BESCHREIBUNG —")
        
        # Bild-Referenz hinzufügen (Anhang-Modus) - PLATZHALTER-MODUS
        if structured.motiv_source == "🖼️ Eigenes Bild hochladen":
            prompt_sections.append("**📎 ANHANG-REFERENZ: Verwende das angehängte Bild als Motiv-Vorlage**")
            prompt_sections.append("**ANWEISUNG**: Das im Anhang befindliche Bild soll als visuelle Basis für das Marketing-Creative dienen.")
            if enhanced_motiv.strip():  # Falls zusätzliche Beschreibung vorhanden
                prompt_sections.append(f"Ergänzende Beschreibung: {enhanced_motiv}")
            else:
                prompt_sections.append("Adaptiere das Referenzbild für professionelle Recruiting-Zwecke.")
        else:
            prompt_sections.append(enhanced_motiv)
        
        # Add character details
        if structured.position_long:
            prompt_sections.append(f"Beruf: {structured.position_long}")
        if structured.company and structured.location:
            prompt_sections.append(f"Arbeitsplatz: {structured.company} in {structured.location}")
        
        # Visual details
        prompt_sections.append(f"Darstellung: {structured.visual_style}")
        prompt_sections.append(f"Beleuchtung: {structured.lighting_type}")
        prompt_sections.append(f"Komposition: {structured.framing}")
        prompt_sections.append(f"Stimmung: {structured.lighting_mood}")
        
        # Quality requirements
        prompt_sections.append("\n— QUALITÄTS-ANFORDERUNGEN —")
        prompt_sections.append("• Bildqualität: Hochauflösend, professionelle Fotografie")
        prompt_sections.append("• Authentizität: Echte Arbeitsplatz-Szenarien, natürliche Gesichtsausdrücke")
        prompt_sections.append("• Corporate Standard: Professionelle Kampagne-Qualität")
        
        # CI Colors (Enhanced Integration)
        ci_colors = structured.ci_colors
        if ci_colors:
            primary = ci_colors.get('primary', '#005EA5')
            secondary = ci_colors.get('secondary', '#B4D9F7')
            accent = ci_colors.get('accent', '#FFC20E')
            background = ci_colors.get('background', '#FFFFFF')
            text_color = ci_colors.get('text', '#000000')
            
            # Konvertiere Hex zu beschreibenden Farbnamen für bessere AI-Verständlichkeit
            primary_desc = _hex_to_color_description(primary)
            secondary_desc = _hex_to_color_description(secondary)
            accent_desc = _hex_to_color_description(accent)
            
            prompt_sections.append(f"• Corporate Design: Hauptfarbe {primary_desc} ({primary}), Sekundärfarbe {secondary_desc} ({secondary})")
            prompt_sections.append(f"• Akzentfarbe: {accent_desc} ({accent}) für CTA-Buttons, Highlights und wichtige Elemente")
            prompt_sections.append(f"• Farbharmonie: Professionelle Unternehmensfarben durchgängig in Layout und Design integriert")
            
            logger.info(f"   🎨 CI-Farben integriert: Primary={primary_desc}, Secondary={secondary_desc}, Accent={accent_desc}")
        
        # Style Options Integration (NEU HINZUGEFÜGT)
        style_options = structured.style_options
        if style_options:
            prompt_sections.append("\n— DESIGN & STYLE-OPTIONEN —")
            
            text_containers = style_options.get('text_containers', {})
            if text_containers:
                shape = text_containers.get('shape', 'rounded_rectangle')
                border_style = text_containers.get('border_style', 'soft_shadow')
                texture = text_containers.get('texture', 'gradient')
                corner_radius = text_containers.get('corner_radius', 'medium')
                
                # Deutsche Übersetzung für bessere DALL-E Verständnis
                shape_mapping = {
                    'rectangle': 'rechteckige',
                    'rounded_rectangle': 'abgerundete rechteckige',
                    'circle': 'kreisrunde',
                    'hexagon': 'sechseckige',
                    'organic_blob': 'organische'
                }
                
                border_mapping = {
                    'solid': 'durchgezogene Umrandung',
                    'dashed': 'gestrichelte Umrandung', 
                    'dotted': 'gepunktete Umrandung',
                    'soft_shadow': 'weichen Schatten',
                    'glow': 'leuchtenden Schein',
                    'none': 'keine Umrandung'
                }
                
                texture_mapping = {
                    'solid': 'einfarbige Füllung',
                    'gradient': 'Verlaufsfüllung',
                    'pattern': 'Muster-Textur',
                    'glass_effect': 'Glas-Effekt',
                    'matte': 'matte Oberfläche'
                }
                
                corner_mapping = {
                    'small': 'leicht abgerundete Ecken (8px)',
                    'medium': 'mittel abgerundete Ecken (16px)', 
                    'large': 'stark abgerundete Ecken (24px)',
                    'xl': 'sehr stark abgerundete Ecken (32px)'
                }
                
                prompt_sections.append(f"• Text-Container-Form: {shape_mapping.get(shape, shape)} Container")
                prompt_sections.append(f"• Container-Rahmen: {border_mapping.get(border_style, border_style)}")
                prompt_sections.append(f"• Container-Textur: {texture_mapping.get(texture, texture)}")
                prompt_sections.append(f"• Ecken-Styling: {corner_mapping.get(corner_radius, corner_radius)}")
            
            visual_effects = style_options.get('visual_effects', {})
            if visual_effects:
                background_treatment = visual_effects.get('background_treatment', 'subtle_pattern')
                accent_elements = visual_effects.get('accent_elements', 'modern_minimal')
                
                background_mapping = {
                    'solid': 'einfarbiger Hintergrund',
                    'subtle_pattern': 'dezentes Hintergrundmuster',
                    'geometric': 'geometrisches Hintergrundmuster',
                    'organic': 'organisches Hintergrundmuster',
                    'none': 'ohne spezielle Hintergrund-Behandlung'
                }
                
                accent_mapping = {
                    'classic': 'klassische Akzent-Elemente',
                    'modern_minimal': 'moderne minimalistische Akzente',
                    'playful': 'verspielte Akzent-Elemente',
                    'organic': 'organische Akzent-Formen',
                    'bold': 'kräftige Akzent-Elemente'
                }
                
                prompt_sections.append(f"• Hintergrund-Behandlung: {background_mapping.get(background_treatment, background_treatment)}")
                prompt_sections.append(f"• Akzent-Stil: {accent_mapping.get(accent_elements, accent_elements)}")
                
            prompt_sections.append("• WICHTIG: Alle Style-Optionen müssen visuell erkennbar umgesetzt werden")
        
        # Negative prompts
        prompt_sections.append("\n— NEGATIVE PROMPTS (VERMEIDEN) —")
        prompt_sections.append("• KEINE unscharfen oder niedrigauflösenden Elemente")
        prompt_sections.append("• KEINE generischen Stock-Foto Erscheinung")
        prompt_sections.append("• KEINE verzerrten Gesichter oder unnatürliche Proportionen")
        
        # TEXT-RENDERING CONTROL
        if not enable_text_rendering:
            prompt_sections.append("• Alle Texte werden direkt im Bild gerendert")
            prompt_sections.append("• Professionelle, gut lesbare Schrift verwenden")
        else:
            prompt_sections.append("• Text soll klar und lesbar sein")
            prompt_sections.append("• Alle Texte werden mit professioneller, gut lesbarer Schrift gerendert")
        
        # Prompt sanitieren - verbotene Text-Phrasen entfernen
        dalle_prompt = self._sanitize_prompt('\n'.join(prompt_sections))
        
        # Prompt validieren und bereinigen - fehlerhafte Prompts verhindern
        dalle_prompt = self._validate_prompt(dalle_prompt)
        
        return dalle_prompt
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Entfernt verbotene Text-Phrasen und bereinigt den Prompt"""
        import re
        
        # Verbotene Text-Phrasen, die Text-Rendering verhindern
        FORBIDDEN_TEXT_PHRASES = [
            "KEIN Text oder Schrift",
            "ohne Text-Inhalt",
            "Buchstaben NICHT rendern",
            "Text wird später als Overlay hinzugefügt",
            "nur Layout-Bereiche",
            "ohne Text",
            "NICHT rendern"
        ]
        
        # Entferne alle Zeilen, die verbotene Phrasen enthalten
        for phrase in FORBIDDEN_TEXT_PHRASES:
            prompt = re.sub(rf".*{re.escape(phrase)}.*\n?", "", prompt, flags=re.IGNORECASE)
        
        # Entferne mehrfache Leerzeilen
        prompt = re.sub(r"\n{3,}", "\n\n", prompt)
        
        # Entferne führende/abschließende Leerzeichen
        prompt = prompt.strip()
        
        return prompt
    
    def _validate_prompt(self, prompt: str):
        """Validiert den generierten Prompt auf Vollständigkeit und Korrektheit - ROBUSTE VERSION"""
        missing_blocks = []
        required_blocks = ["HEADLINE", "SUBLINE", "BENEFITS", "STELLENTITEL", "CTA"]
        
        # ROBUSTE VALIDIERUNG: Prüfe ob alle erforderlichen Layout-Blöcke vorhanden sind
        # Aber erlaube fehlende Elemente, da nicht alle Layouts alle Elemente haben
        for block in required_blocks:
            if block not in prompt.upper():
                missing_blocks.append(block)
        
        # WARNUNG statt Fehler - fehlende Blöcke sind erlaubt
        if missing_blocks:
            logger.warning(f"⚠️ Fehlende Layout-Blöcke (erlaubt): {', '.join(missing_blocks)}")
            logger.info("ℹ️ Diese Elemente sind optional - Layout kann trotzdem verarbeitet werden")
        
        # ROBUSTE CI-FARBEN-VALIDIERUNG: Prüfe ob mindestens eine CI-Farbe vorhanden ist
        ci_colors = ["#005EA5", "#B4D9F7", "#FFC20E"]
        found_colors = [color for color in ci_colors if color in prompt]
        
        if not found_colors:
            logger.warning("⚠️ Keine Standard-CI-Farben gefunden - Layout-spezifische Farben werden verwendet")
        else:
            logger.info(f"✅ CI-Farben gefunden: {', '.join(found_colors)}")
        
        # ROBUSTE TEXT-RENDERING-VALIDIERUNG: Prüfe ob Text-Rendering-Anweisungen vorhanden sind
        text_rendering_indicators = ["TEXT-ZONE", "Text wird direkt im Bild gerendert", "lesbare Schrift", "TEXT-CONTENT RENDERING"]
        found_text_rendering = any(indicator in prompt for indicator in text_rendering_indicators)
        
        if not found_text_rendering:
            logger.warning("⚠️ Text-Rendering-Anweisungen nicht explizit gefunden - Layout wird trotzdem verarbeitet")
        else:
            logger.info("✅ Text-Rendering-Anweisungen gefunden")
        
        # ROBUSTE TEXT-VERBOT-VALIDIERUNG: Prüfe ob keine Text-Verbote vorhanden sind
        forbidden_indicators = ["ohne Text", "NICHT rendern", "KEIN Text", "Buchstaben NICHT rendern"]
        found_forbidden = [indicator for indicator in forbidden_indicators if indicator in prompt]
        
        if found_forbidden:
            logger.warning(f"⚠️ Text-Verbote gefunden (werden entfernt): {', '.join(found_forbidden)}")
            # Entferne Text-Verbote automatisch
            for forbidden in found_forbidden:
                prompt = prompt.replace(forbidden, "")
            logger.info("✅ Text-Verbote automatisch entfernt")
        else:
            logger.info("✅ Keine Text-Verbote gefunden")
        
        # VALIDIERUNG ERFOLGREICH - Layout kann verarbeitet werden
        logger.info("✅ Prompt-Validierung erfolgreich - Layout wird verarbeitet")
        return prompt
    
    def _generate_cinematic_prompt(self, layout_data: LayoutIntegratedData, enable_text_rendering: bool = False, quality_level: str = "high") -> CinematicPromptData:
        """
        🎭 Generiert cinematisch-natürlichsprachlichen Prompt für optimale OpenAI API Bildgenerierung
        
        Args:
            layout_data: Layout-integrierte Daten
            enable_text_rendering: Ob Text gerendert werden soll
            quality_level: Qualitätsstufe ("basic", "high", "premium")
            
        Returns:
            CinematicPromptData mit transformiertem Prompt
        """
        try:
            # Prompt Transformer initialisieren
            transformer = create_prompt_transformer()
            
            # Transformation durchführen
            cinematic_data = transformer.transform_to_cinematic_prompt(layout_data, enable_text_rendering, quality_level)
            
            # Statistiken loggen
            stats = transformer.get_transformation_stats(
                self._generate_dalle_prompt(layout_data, enable_text_rendering),
                cinematic_data.full_prompt
            )
            
            logger.info(f"🎭 Cinematic Prompt generiert: {stats['cinematic_length']} chars "
                       f"(Reduktion: {stats['reduction_percentage']}%)")
            
            return cinematic_data
            
        except Exception as e:
            logger.error(f"❌ Cinematic Prompt Generation Fehler: {e}")
            # Fallback: Leeres CinematicPromptData zurückgeben
            return CinematicPromptData(
                visual_description="",
                layout_description="",
                style_description="",
                quality_requirements="",
                negative_prompts="",
                full_prompt="",
                metadata={'error': str(e)}
            )
    
    # =====================================
    # 🎬 MIDJOURNEY 9-PUNKTE-FORMEL HELPER
    # =====================================
    
    def _build_subject_description(self, structured: 'StructuredInput') -> str:
        """1. 👤 SUBJEKTBESCHREIBUNG (Beruf + Tätigkeit + Emotion)"""
        parts = []
        
        # Bild-Referenz prüfen (Anhang-Modus) - PLATZHALTER-MODUS
        if structured.motiv_source == "🖼️ Eigenes Bild hochladen":
            parts.append("📎 use attached reference image as visual inspiration")
            parts.append("professional marketing style adaptation")
            # Zusätzliche Beschreibung falls vorhanden
            if structured.motiv_prompt.strip():
                additional_desc = self._translate_to_english(structured.motiv_prompt)
                parts.append(f"additional details: {additional_desc}")
        else:
            # Hauptmotiv (übersetzt)
            main_subject = self._translate_to_english(structured.motiv_prompt)
            parts.append(main_subject)
        
        # Beruf detailliert
        if structured.position_long:
            profession_en = self._translate_profession(structured.position_long)
            parts.append(f"working as {profession_en}")
        
        # Emotion/Ausdruck aus Lighting Mood ableiten
        emotion_mapping = {
            'Professionell': 'confident and professional expression',
            'Einladend': 'warm and welcoming smile',
            'Vertrauensvoll': 'trustworthy and reliable demeanor',
            'Energetisch': 'energetic and motivated attitude',
            'Beruhigend': 'calm and reassuring presence'
        }
        emotion = emotion_mapping.get(structured.lighting_mood, 'professional and approachable expression')
        parts.append(emotion)
        
        return ", ".join(parts)
    
    def _build_scene_environment(self, structured: 'StructuredInput', layout_def: dict) -> str:
        """2. 🏢 SZENE & UMGEBUNG (Ort + Interaktion + Stimmung)"""
        parts = []
        
        # Arbeitsplatz-Umgebung
        if structured.company and structured.location:
            # Branche-spezifische Umgebung
            company_lower = structured.company.lower()
            if any(word in company_lower for word in ['tech', 'software', 'digital']):
                environment = f"modern tech office in {structured.location}, open workspace with computers and monitors"
            elif any(word in company_lower for word in ['hospital', 'clinic', 'medical', 'health']):
                environment = f"contemporary medical facility in {structured.location}, clean healthcare environment"
            elif any(word in company_lower for word in ['bank', 'finance']):
                environment = f"sleek corporate office in {structured.location}, professional business setting"
            else:
                environment = f"modern {structured.company} workplace in {structured.location}, professional office environment"
            parts.append(environment)
        
        # Interaktion und Stimmung
        layout_name = layout_def.get('name', '').lower()
        if 'hero' in layout_name:
            parts.append("dynamic workplace interaction, collaborative atmosphere")
        elif 'team' in layout_name:
            parts.append("team collaboration, group dynamic, productive workspace")
        else:
            parts.append("authentic workplace scene, natural work environment")
        
        # Atmosphäre
        atmosphere_mapping = {
            'Professionell': 'corporate professional atmosphere',
            'Einladend': 'welcoming and inclusive workplace culture',
            'Vertrauensvoll': 'stable and trustworthy business environment',
            'Energetisch': 'dynamic and innovative workspace vibe',
            'Beruhigend': 'calm and organized office atmosphere'
        }
        atmosphere = atmosphere_mapping.get(structured.lighting_mood, 'professional business atmosphere')
        parts.append(atmosphere)
        
        return ", ".join(parts)
    
    def _build_posture_perspective(self, structured: 'StructuredInput', layout_def: dict) -> str:
        """3. 🎭 KÖRPERHALTUNG + PERSPEKTIVE + KOMPOSITION"""
        parts = []
        
        # Körperhaltung aus Framing ableiten
        posture_mapping = {
            'Medium Shot': 'confident upright posture, hands naturally positioned',
            'Close-Up': 'direct eye contact, shoulders relaxed, professional headshot pose',
            'Wide Shot': 'full body confident stance, natural workplace positioning',
            'Portrait': 'professional portrait pose, engaging body language',
            'Environmental': 'natural interaction with environment, authentic workplace posture'
        }
        posture = posture_mapping.get(structured.framing, 'confident professional posture')
        parts.append(posture)
        
        # Perspektive
        perspective_mapping = {
            'Medium Shot': 'shot from chest up, slightly angled perspective',
            'Close-Up': 'intimate close-up perspective, shallow depth of field',
            'Wide Shot': 'wide environmental perspective, context-rich composition',
            'Portrait': 'centered portrait perspective, professional framing',
            'Environmental': 'environmental storytelling perspective, workplace context'
        }
        perspective = perspective_mapping.get(structured.framing, 'professional perspective')
        parts.append(perspective)
        
        # Layout-spezifische Komposition
        layout_name = layout_def.get('name', '').lower()
        if 'hero' in layout_name:
            parts.append("heroic composition, dynamic rule of thirds, visual impact")
        elif 'grid' in layout_name:
            parts.append("structured grid composition, balanced layout, geometric harmony")
        elif 'card' in layout_name:
            parts.append("centered card composition, balanced framing, professional layout")
        else:
            parts.append("balanced composition, rule of thirds, visual hierarchy")
        
        return ", ".join(parts)
    
    def _build_camera_lighting(self, structured: 'StructuredInput') -> str:
        """4. 📸 KAMERA + LICHT + STILMITTEL"""
        parts = []
        
        # Kamera-Einstellungen
        camera_mapping = {
            'Medium Shot': 'shot with 85mm lens, medium focal length',
            'Close-Up': 'shot with 135mm lens, portrait focal length, shallow DoF',
            'Wide Shot': 'shot with 35mm lens, wide angle perspective',
            'Portrait': 'shot with 85mm portrait lens, professional headshot setup',
            'Environmental': 'shot with 50mm lens, natural field of view'
        }
        camera = camera_mapping.get(structured.framing, 'shot with professional DSLR camera')
        parts.append(camera)
        
        # Beleuchtung detailliert
        lighting_mapping = {
            'Natürliches Licht': 'natural window lighting, soft daylight, golden hour warmth',
            'Studioleuchten': 'professional studio lighting setup, three-point lighting, key and fill lights',
            'Warme Beleuchtung': 'warm tungsten lighting, cozy atmosphere, golden color temperature',
            'Kalte Beleuchtung': 'cool LED lighting, modern clinical feel, daylight color temperature',
            'Dramatische Beleuchtung': 'dramatic directional lighting, strong shadows, high contrast'
        }
        lighting = lighting_mapping.get(structured.lighting_type, 'professional corporate lighting')
        parts.append(lighting)
        
        # Stilmittel
        style_mapping = {
            'Fotorealistisch': 'photorealistic rendering, authentic photography style',
            'Künstlerisch': 'artistic interpretation, creative visual treatment',
            'Dokumentarisch': 'documentary photography style, candid authentic moments',
            'Werbung': 'commercial advertising photography, polished marketing aesthetic',
            'Editorial': 'editorial photography style, storytelling visual approach'
        }
        style_treatment = style_mapping.get(structured.visual_style, 'professional commercial photography')
        parts.append(style_treatment)
        
        return ", ".join(parts)
    
    def _build_composition_balance(self, layout_def: dict) -> str:
        """5. 🎨 BILDAUFBAU: FLÄCHENAUFTEILUNG + VISUELLE BALANCE"""
        parts = []
        
        layout_name = layout_def.get('name', '').lower()
        layout_description = layout_def.get('description', '')
        
        # Layout-spezifische Flächenaufteilung
        if 'hero' in layout_name:
            parts.append("heroic central composition, 60/40 visual weight distribution")
            parts.append("prominent subject placement, secondary elements balanced")
        elif 'grid' in layout_name:
            parts.append("structured grid layout, systematic visual organization")
            parts.append("balanced geometric composition, clean sectional arrangement")
        elif 'card' in layout_name:
            parts.append("centered card layout, symmetrical balance")
            parts.append("contained composition, focused visual hierarchy")
        elif 'split' in layout_name:
            parts.append("split composition, 50/50 visual balance")
            parts.append("dual-focus layout, harmonious division")
        else:
            parts.append("balanced composition, visual hierarchy, professional layout")
        
        # Raum für Text-Layout berücksichtigen
        zones = layout_def.get('zones', {})
        if zones:
            text_zones = [name for name, zone in zones.items() if 'text' in zone.get('content_type', '').lower()]
            if text_zones:
                parts.append(f"composition with designated text areas, {len(text_zones)} content zones")
        
        # Visuelle Balance
        parts.append("optimal negative space usage, professional visual weight distribution")
        
        return ", ".join(parts)
    
    def _build_corporate_design(self, structured: 'StructuredInput') -> str:
        """6. 🏢 CORPORATE DESIGN HINWEISE"""
        if not structured.ci_colors:
            return ""
        
        parts = []
        ci_colors = structured.ci_colors
        
        # Farbharmonie
        primary = ci_colors.get('primary', '#005EA5')
        secondary = ci_colors.get('secondary', '#B4D9F7')
        accent = ci_colors.get('accent', '#FFC20E')
        
        # Farbbeschreibungen für Midjourney
        primary_desc = _hex_to_color_description(primary)
        secondary_desc = _hex_to_color_description(secondary)
        accent_desc = _hex_to_color_description(accent)
        
        parts.append(f"corporate color scheme with {primary_desc} as primary brand color")
        parts.append(f"{secondary_desc} supporting elements, {accent_desc} accent highlights")
        
        # Standort-spezifische Akzentfarbe
        if structured.location:
            parts.append(f"{accent_desc} location highlighting, location pin with accent color")
            parts.append(f"location indicator using {accent_desc} for visual emphasis")
            parts.append(f"{accent_desc} call-to-action button with white text for maximum readability")
        
        parts.append("professional brand consistency, cohesive corporate visual identity")
        
        return ", ".join(parts)
    
    def _build_style_rendering(self, structured: 'StructuredInput', enable_text_rendering: bool = False) -> str:
        """7. ✨ STILATTRIBUTE & RENDERING"""
        parts = []
        
        # Basis-Qualität
        parts.append("ultra-high quality, professional photography")
        parts.append("sharp focus, detailed textures, realistic lighting")
        
        # TEXT-RENDERING CONTROL
        if not enable_text_rendering:
            parts.append("clean layout composition with designated content areas")
            parts.append("professional space allocation for text overlays")
            parts.append("marketing-ready background without text elements")
        else:
            parts.append("readable text integration, professional typography")
            parts.append("high-contrast text visibility, marketing campaign ready")
        
        # Visual Style Integration
        style_rendering = {
            'Fotorealistisch': 'photorealistic rendering, authentic workplace photography, natural colors',
            'Künstlerisch': 'artistic photography, creative composition, enhanced visual appeal',
            'Dokumentarisch': 'documentary style, candid moments, authentic workplace capture',
            'Werbung': 'commercial photography quality, polished marketing aesthetic, brand-ready visuals',
            'Editorial': 'editorial photography standard, storytelling composition, magazine quality'
        }
        rendering = style_rendering.get(structured.visual_style, 'commercial photography quality')
        parts.append(rendering)
        
        # Recruiting-spezifische Attribute
        parts.append("employer branding quality, talent acquisition appeal")
        parts.append("professional workplace representation, career opportunity visualization")
        
        return ", ".join(parts)
    
    def _build_midjourney_parameters(self, motiv_treatment: dict) -> str:
        """8. ⚙️ MIDJOURNEY PARAMETER"""
        params = []
        
        # Aspect Ratio
        aspect_ratio = motiv_treatment.get('aspect_ratio', '16:9')
        params.append(f"--ar {aspect_ratio}")
        
        # Style und Qualität (optimiert für V6)
        params.append("--style raw")  # Für mehr Fotorealismus
        params.append("--q 2")       # Höchste Qualität
        
        # Chaos für kontrollierte Variation
        params.append("--c 20")      # Niedrig für konsistente Ergebnisse
        
        return " ".join(params)
    
    def _build_text_layout_areas(self, structured: 'StructuredInput', layout_data: 'LayoutIntegratedData', enable_text_rendering: bool = False) -> str:
        """6.5. 📝 TEXT-LAYOUT-BEREICHE für Marketing-Content"""
        if not hasattr(layout_data, 'text_placements') or not layout_data.text_placements:
            return ""
            
        parts = []
        text_placements = layout_data.text_placements
        
        if enable_text_rendering:
            # TEXT-RENDERING MODUS: Beschreibe echten Text-Content
            parts.append("marketing layout with readable text elements:")
            
            # Headlines
            if 'headline' in text_placements:
                headline_content = text_placements['headline'].get('content', '')
                if headline_content:
                    parts.append(f"prominent headline text '{headline_content}' in professional typography")
            
            # Benefits
            if 'benefits' in text_placements:
                benefits_content = text_placements['benefits'].get('content', [])
                if benefits_content and isinstance(benefits_content, list):
                    parts.append(f"bullet point benefits section with {len(benefits_content)} key selling points")
            
            # CTA
            if 'cta' in text_placements:
                cta_content = text_placements['cta'].get('content', '')
                if cta_content:
                    parts.append(f"call-to-action button with '{cta_content}' text in accent color")
                    parts.append(f"white text on accent color background for maximum readability")
            
            # Company & Position
            if structured.company:
                parts.append(f"company branding for {structured.company}")
            if structured.position_long:
                parts.append(f"job position '{structured.position_long}' clearly displayed")
            
            # Standort mit Akzentfarbe und Pin-Symbol
            if structured.location:
                accent_color = structured.ci_colors.get('accent', '#FFC20E')
                parts.append(f"location pin with '📍 {structured.location}' in accent color {accent_color}")
                parts.append(f"location indicator with pin symbol and highlighted text")
                parts.append(f"white text on accent color background for maximum readability")
                
        else:
            # LAYOUT-MODUS: KEINE Text-Bereiche beschreiben - nur Layout-Struktur
            parts.append("clean professional marketing layout")
            parts.append("balanced composition with visual hierarchy")
            parts.append("modern design with clear visual zones")
            parts.append("professional spacing and layout structure")
            
            # Standort-Bereich mit Akzentfarbe (mit Text)
            if structured.location:
                accent_color = structured.ci_colors.get('accent', '#FFC20E')
                parts.append(f"location area with accent color {accent_color}")
                parts.append(f"location pin symbol as visual element")
                parts.append(f"cta button in accent color with professional styling")
            # KEINE Text-Bereiche mehr erwähnen!
        
        return ", ".join(parts) if parts else ""
    
    def _build_negative_prompts(self, enable_text_rendering: bool = False) -> str:
        """9. 🚫 NEGATIVE PROMPTS"""
        negative_elements = [
            "amateur photography",
            "low quality",
            "blurry",
            "distorted faces", 
            "unnatural proportions",
            "oversaturated colors",
            "generic stock photo",
            "artificial lighting",
            "unprofessional setting",
            "cluttered background",
            "poor composition"
        ]
        
        # TEXT-RENDERING CONTROL für Midjourney
        if not enable_text_rendering:
            negative_elements.extend([
                "blurry text", "unreadable text", "distorted letters",
                "corrupted characters", "illegible writing"
            ])
        else:
            negative_elements.extend([
                "blurry text", "unreadable text", "distorted letters",
                "corrupted characters", "illegible writing"
            ])
        
        return f"--no {', '.join(negative_elements)}"
    
    def _translate_to_english(self, german_text: str) -> str:
        """Einfache Übersetzung deutscher Begriffe ins Englische für Midjourney"""
        translations = {
            'Empathische Pflegekraft': 'empathetic healthcare professional',
            'Pflegekraft': 'healthcare worker',
            'mittleren Alters': 'middle-aged',
            'warmem Kasack': 'warm-colored medical uniform',
            'moderner Klinik': 'modern clinic',
            'lichtdurchfluteter': 'bright, well-lit',
            'steht in': 'standing in',
            'Krankenhaus': 'hospital',
            'medizinische': 'medical',
            'professionell': 'professional'
        }
        
        result = german_text
        for german, english in translations.items():
            result = result.replace(german, english)
        
        return result
    
    def _translate_profession(self, german_profession: str) -> str:
        """Übersetzt deutsche Berufsbezeichnungen"""
        profession_translations = {
            'Gesundheits- und Krankenpfleger/in': 'professional nurse',
            'Pflegekraft': 'healthcare professional',
            'Arzt': 'doctor',
            'Ärztin': 'doctor',
            'Therapeut': 'therapist',
            'Software-Entwickler': 'software developer'
        }
        
        for german, english in profession_translations.items():
            if german.lower() in german_profession.lower():
                return english
        
        return 'healthcare professional'  # Default fallback
    
    def _analyze_prompt_quality(self, prompt: str, prompt_type: str) -> Dict[str, Any]:
        """Analysiert Prompt-Qualität"""
        metrics = {
            'length': len(prompt),
            'word_count': len(prompt.split()),
            'prompt_type': prompt_type
        }
        
        if prompt_type == 'midjourney':
            metrics['optimal_length'] = 200 <= len(prompt) <= 800
            metrics['has_parameters'] = '--ar' in prompt and '--style' in prompt
            metrics['language'] = 'english'
            
        elif prompt_type == 'dalle':
            metrics['compatible'] = len(prompt) <= 4000
            metrics['structured'] = '—' in prompt
            metrics['language'] = 'german'
            metrics['has_negative_prompts'] = 'VERMEIDEN' in prompt
        
        return metrics
    
    def _assess_overall_quality(self, layout_data: LayoutIntegratedData, mj_prompt: str, dalle_prompt: str) -> Dict[str, Any]:
        """Bewertet Gesamt-Qualität der Prompt-Generierung"""
        scores = []
        
        # Layout Integration Score
        layout_score = 90 if layout_data.layout_definition else 50
        scores.append(layout_score)
        
        # Text Mapping Score
        text_score = min(100, len(layout_data.text_placements) * 20)
        scores.append(text_score)
        
        # Midjourney Quality Score
        mj_score = 90 if 200 <= len(mj_prompt) <= 800 else 70
        scores.append(mj_score)
        
        # DALL-E Quality Score
        dalle_score = 95 if len(dalle_prompt) <= 4000 else 50
        scores.append(dalle_score)
        
        # Adaptive Adjustments Score
        adaptive_score = 100 if layout_data.adaptive_adjustments else 80
        scores.append(adaptive_score)
        
        overall_score = sum(scores) // len(scores)
        
        return {
            'overall_score': overall_score,
            'layout_integration_score': layout_score,
            'text_mapping_score': text_score,
            'midjourney_score': mj_score,
            'dalle_score': dalle_score,
            'adaptive_score': adaptive_score,
            'recommendations': self._generate_recommendations(layout_data, overall_score)
        }
    
    def _generate_recommendations(self, layout_data: LayoutIntegratedData, score: int) -> List[str]:
        """Generiert Verbesserungs-Empfehlungen"""
        recommendations = []
        
        if score < 80:
            recommendations.append("Layout-Integration könnte verbessert werden")
        
        if len(layout_data.text_placements) < 3:
            recommendations.append("Mehr Text-Elemente könnten platziert werden")
        
        if not layout_data.adaptive_adjustments:
            recommendations.append("Adaptive Anpassungen implementieren")
        
        if score >= 90:
            recommendations.append("Exzellente Prompt-Qualität erreicht!")
        
        return recommendations
    
    def _save_output_files(self, layout_data: LayoutIntegratedData, mj_prompt: str, dalle_prompt: str, cinematic_prompt: CinematicPromptData = None) -> List[str]:
        """Speichert alle Output-Dateien"""
        timestamp = layout_data.structured_input.timestamp
        layout_id = layout_data.structured_input.layout_id
        output_files = []
        
        # Midjourney Prompt
        mj_file = self.outputs_dir / f"midjourney_multiprompt_{layout_id}_{timestamp}.txt"
        with open(mj_file, 'w', encoding='utf-8') as f:
            f.write(f"# MIDJOURNEY PROMPT - Multi-Prompt-System\n")
            f.write(f"# Layout: {layout_id}\n")
            f.write(f"# Timestamp: {timestamp}\n")
            f.write(f"# Length: {len(mj_prompt)} characters\n\n")
            f.write(mj_prompt)
        output_files.append(str(mj_file))
        
        # DALL-E Prompt
        dalle_file = self.outputs_dir / f"dalle_multiprompt_{layout_id}_{timestamp}.txt"
        with open(dalle_file, 'w', encoding='utf-8') as f:
            f.write(f"# DALL-E PROMPT - Multi-Prompt-System\n")
            f.write(f"# Layout: {layout_id}\n")
            f.write(f"# Timestamp: {timestamp}\n")
            f.write(f"# Length: {len(dalle_prompt)} characters\n")
            f.write(f"# Compatible: {'Yes' if len(dalle_prompt) <= 4000 else 'No'}\n\n")
            f.write(dalle_prompt)
        output_files.append(str(dalle_file))
        
        # Cinematic Prompt (NEU)
        if cinematic_prompt:
            cinematic_file = self.outputs_dir / f"cinematic_prompt_{layout_id}_{timestamp}.txt"
            with open(cinematic_file, 'w', encoding='utf-8') as f:
                f.write(f"# CINEMATIC PROMPT - OpenAI API Optimiert\n")
                f.write(f"# Layout: {layout_id}\n")
                f.write(f"# Timestamp: {timestamp}\n")
                f.write(f"# Length: {len(cinematic_prompt.full_prompt)} characters\n")
                f.write(f"# Transformation Type: {cinematic_prompt.metadata.get('transformation_type', 'unknown')}\n\n")
                f.write("## VISUELLES MOTIV\n")
                f.write(f"{cinematic_prompt.visual_description}\n\n")
                f.write("## LAYOUT\n")
                f.write(f"{cinematic_prompt.layout_description}\n\n")
                f.write("## STIL\n")
                f.write(f"{cinematic_prompt.style_description}\n\n")
                f.write("## QUALITÄT\n")
                f.write(f"{cinematic_prompt.quality_requirements}\n\n")
                f.write("## NICHT ERWÜNSCHT\n")
                f.write(f"{cinematic_prompt.negative_prompts}\n\n")
                f.write("## VOLLSTÄNDIGER PROMPT\n")
                f.write(f"{cinematic_prompt.full_prompt}")
            output_files.append(str(cinematic_file))
        
        # Processing Report
        report_file = self.outputs_dir / f"multiprompt_report_{layout_id}_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            report = {
                'timestamp': timestamp,
                'layout_id': layout_id,
                'layout_name': layout_data.layout_definition.get('name', 'Unknown'),
                'processing_stages': {
                    'input_processed': True,
                    'layout_integrated': True,
                    'prompts_finalized': True
                },
                'text_placements_count': len(layout_data.text_placements),
                'adaptive_adjustments_count': len(layout_data.adaptive_adjustments),
                'layout_metrics': layout_data.layout_metrics,
                'prompts': {
                    'midjourney': {
                        'length': len(mj_prompt),
                        'preview': mj_prompt[:100] + '...'
                    },
                    'dalle': {
                        'length': len(dalle_prompt),
                        'compatible': len(dalle_prompt) <= 4000,
                        'preview': dalle_prompt[:100] + '...'
                    },
                    'cinematic': {
                        'length': len(cinematic_prompt.full_prompt) if cinematic_prompt else 0,
                        'transformation_type': cinematic_prompt.metadata.get('transformation_type', 'unknown') if cinematic_prompt else 'none',
                        'preview': cinematic_prompt.full_prompt[:100] + '...' if cinematic_prompt else 'N/A'
                    }
                }
            }
            json.dump(report, f, indent=2, ensure_ascii=False)
        output_files.append(str(report_file))
        
        return output_files

class MultiPromptSystem:
    """
    🎯 HAUPT-KLASSE: 3-Stufen Multi-Prompt-System
    
    Orchestriert die komplette Pipeline:
    Input-Processor → Layout-Integrator → Prompt-Finalizer
    """
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        
        self.project_root = project_root
        
        # Initialisiere alle Stufen
        self.input_processor = InputProcessor(project_root)
        self.layout_integrator = LayoutIntegrator(project_root)
        self.prompt_finalizer = PromptFinalizer(project_root)
        
        logger.info("🚀 Multi-Prompt-System initialisiert")
        logger.info(f"   📂 Projekt-Root: {project_root}")
    
    def process_streamlit_input(self, streamlit_input: Dict[str, Any], enable_text_rendering: bool = False) -> FinalizedPrompts:
        """
        Verarbeitet Streamlit-Eingaben durch die komplette 3-Stufen-Pipeline
        
        Args:
            streamlit_input: Dict mit Streamlit-UI-Daten
            enable_text_rendering: Ob Text im DALL-E Bild gerendert werden soll
                                 True = Mit Text (Risiko korrupter deutscher Zeichen)
                                 False = Text-Rendering aktiviert
            
        Returns:
            FinalizedPrompts mit beiden optimierten Prompts
        """
        
        logger.info("🔄 STARTE 3-STUFEN MULTI-PROMPT-PIPELINE")
        logger.info(f"   📝 Text-Rendering: {'AKTIVIERT' if enable_text_rendering else 'DEAKTIVIERT'}")
        if enable_text_rendering:
            logger.warning("   ⚠️ Deutsche Umlaute können als korrupte Zeichen erscheinen")
        else:
            logger.info("   🎨 Layout-Modus: Layout-Bereiche mit Text-Rendering")
        total_start_time = datetime.now()
        
        try:
            # STUFE 1: Input Processing
            structured_input = self.input_processor.process(streamlit_input)
            
            # STUFE 2: Layout Integration
            layout_integrated = self.layout_integrator.process(structured_input)
            
            # STUFE 3: Prompt Finalization
            finalized_prompts = self.prompt_finalizer.process(layout_integrated, enable_text_rendering)
            
            # Gesamt-Processing-Zeit
            total_time = (datetime.now() - total_start_time).total_seconds()
            finalized_prompts.total_processing_time = total_time
            
            logger.info("✅ MULTI-PROMPT-PIPELINE ABGESCHLOSSEN")
            logger.info(f"   ⏱️ Gesamt-Zeit: {total_time:.2f}s")
            logger.info(f"   🎬 Midjourney: {len(finalized_prompts.midjourney_prompt)} chars")
            logger.info(f"   🏗️ DALL-E: {len(finalized_prompts.dalle_prompt)} chars")
            logger.info(f"   📊 Quality: {finalized_prompts.quality_assessment.get('overall_score', 0)}/100")
            
            return finalized_prompts
            
        except Exception as e:
            logger.error(f"❌ Multi-Prompt-Pipeline Fehler: {e}")
            raise
    
    def _generate_cinematic_prompt(self, layout_data: LayoutIntegratedData, enable_text_rendering: bool = False, quality_level: str = "high") -> CinematicPromptData:
        """
        🎭 Generiert cinematisch-natürlichsprachlichen Prompt für optimale OpenAI API Bildgenerierung
        
        Args:
            layout_data: Layout-integrierte Daten
            enable_text_rendering: Ob Text gerendert werden soll
            quality_level: Qualitätsstufe ("basic", "high", "premium")
            
        Returns:
            CinematicPromptData mit transformiertem Prompt
        """
        try:
            # Prompt Transformer initialisieren
            transformer = create_prompt_transformer()
            
            # Transformation durchführen
            cinematic_data = transformer.transform_to_cinematic_prompt(layout_data, enable_text_rendering, quality_level)
            
            # Statistiken loggen
            stats = transformer.get_transformation_stats(
                self.prompt_finalizer._generate_dalle_prompt(layout_data, enable_text_rendering),
                cinematic_data.full_prompt
            )
            
            logger.info(f"🎭 Cinematic Prompt generiert: {stats['cinematic_length']} chars "
                       f"(Reduktion: {stats['reduction_percentage']}%)")
            
            return cinematic_data
            
        except Exception as e:
            logger.error(f"❌ Cinematic Prompt Generation Fehler: {e}")
            # Fallback: Leeres CinematicPromptData zurückgeben
            return CinematicPromptData(
                visual_description="",
                layout_description="",
                style_description="",
                quality_requirements="",
                negative_prompts="",
                full_prompt="",
                metadata={'error': str(e)}
            )

# Factory Functions für einfache Nutzung
def create_multi_prompt_system() -> MultiPromptSystem:
    """Factory Function für Multi-Prompt-System"""
    return MultiPromptSystem()

def process_streamlit_to_prompts(streamlit_input: Dict[str, Any]) -> FinalizedPrompts:
    """Quick-Function: Streamlit-Input direkt zu finalen Prompts"""
    system = create_multi_prompt_system()
    return system.process_streamlit_input(streamlit_input)

if __name__ == "__main__":
    # Test des Multi-Prompt-Systems
    print("🧪 MULTI-PROMPT-SYSTEM TEST")
    print("=" * 60)
    
    # Test-Input (simuliert Streamlit-Eingaben)
    test_input = {
        'headline': 'Werden Sie Teil unseres Teams!',
        'company': 'TechMed Solutions',
        'location': 'Berlin',
        'position_long': 'Software-Entwickler/in im Gesundheitswesen',
        'position_short': 'Developer',
        'cta': 'Jetzt bewerben!',
        'benefits': [
            'Innovative Projekte',
            'Remote-Work möglich',
            'Überdurchschnittliche Vergütung',
            'Moderne Technologien'
        ],
        'motiv_prompt': 'Konzentrierter Software-Entwickler arbeitet an medizinischer App in modernem Tech-Büro',
        'visual_style': 'modern corporate style',
        'lighting_type': 'studio lighting',
        'lighting_mood': 'confident, modern',
        'framing': 'medium shot, waist up',
        'layout_id': 'skizze4_hero',
        'corporate_colors': {
            'primary': '#1e40af',
            'secondary': '#dbeafe',
            'accent': '#dc2626',
            'text': '#111827'
        },
        'style_options': {
            'font_family': 'Arial, sans-serif',
            'base_size': '18px',
            'scale_ratio': 1.3,
            'hierarchy': {
                'headline': 'h1',
                'subline': 'h2',
                'company': 'h3',
                'stellentitel': 'h4',
                'benefits': 'p',
                'cta': 'button'
            },
            'text_containers': {
                'shape': 'rounded_rectangle',
                'border_style': 'soft_shadow',
                'texture': 'gradient',
                'corner_radius': 'medium'
            },
            'visual_effects': {
                'background_treatment': 'subtle_pattern',
                'accent_elements': 'modern_minimal'
            },
            'layout_style': {
                'type': 'rounded_modern',
                'name': 'Abgerundet & Modern'
            }
        }
    }
    
    try:
        # Multi-Prompt-System ausführen
        result = process_streamlit_to_prompts(test_input)
        
        print(f"\n✅ TEST ERFOLGREICH!")
        print(f"   🎬 Midjourney: {len(result.midjourney_prompt)} chars")
        print(f"   🏗️ DALL-E: {len(result.dalle_prompt)} chars")
        print(f"   📊 Quality Score: {result.quality_assessment.get('overall_score', 0)}/100")
        print(f"   📁 Files: {len(result.output_files)} erstellt")
        print(f"   ⏱️ Processing Zeit: {result.total_processing_time:.2f}s")
        
    except Exception as e:
        print(f"❌ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc() 