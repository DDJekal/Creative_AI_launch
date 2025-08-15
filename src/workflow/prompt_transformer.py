"""
Prompt Transformer Module
=========================

Dieses Modul transformiert strukturierte Layout-Daten in cinematisch-natürlichsprachliche 
Prompts für die OpenAI API, um die Bildqualität zu verbessern.

Das Modul ist flexibel gestaltet, um zukünftige Anpassungen am Layout-System 
nicht zu beeinträchtigen.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CinematicPromptData:
    """Daten für einen cinematisch-natürlichsprachlichen Prompt"""
    visual_description: str
    layout_description: str
    style_description: str
    quality_requirements: str
    negative_prompts: str
    full_prompt: str
    metadata: Dict[str, Any]

class PromptTransformer:
    """
    Transformiert strukturierte Layout-Daten in cinematisch-natürlichsprachliche Prompts
    für optimale OpenAI API Bildgenerierung.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Flexibles Mapping für Layout-Typen zu visuellen Beschreibungen
        self.layout_visual_mapping = {
            'skizze11_dynamic_layout': {
                'description': 'dynamisches Layout mit diagonaler Komposition',
                'visual_style': 'modern und energetisch',
                'composition': 'diagonale Aufteilung mit dynamischen Elementen'
            },
            'skizze13_text_motiv_split_cta': {
                'description': 'klassisches Split-Layout mit Text und Motiv',
                'visual_style': 'professionell und ausgewogen',
                'composition': 'vertikale Aufteilung mit klaren Bereichen'
            },
            'skizze14_hero_layout': {
                'description': 'Hero-Layout mit großem Motiv und Text-Overlay',
                'visual_style': 'dramatisch und eindrucksvoll',
                'composition': 'zentrales Motiv mit überlagertem Text'
            }
        }
        
        # Farb-zu-Beschreibung Mapping für natürlichere Sprache
        self.color_description_mapping = {
            'primary': {
                '#005EA5': 'tiefes Unternehmensblau',
                '#1E3A8A': 'dunkles Marineblau',
                '#DC2626': 'kräftiges Rot',
                '#059669': 'dunkles Grün',
                '#7C3AED': 'tiefes Violett'
            },
            'secondary': {
                '#B4D9F7': 'helles Akzentblau',
                '#E5E7EB': 'helles Grau',
                '#FECACA': 'helles Rosa',
                '#A7F3D0': 'helles Grün',
                '#DDD6FE': 'helles Violett'
            },
            'accent': {
                '#FFC20E': 'lebendiges Akzentgelb',
                '#F59E0B': 'warmes Orange',
                '#EF4444': 'kräftiges Rot',
                '#10B981': 'frisches Grün',
                '#8B5CF6': 'lebendiges Violett'
            }
        }
    
    def transform_to_cinematic_prompt(self, layout_data: Any, enable_text_rendering: bool = False, quality_level: str = "high") -> CinematicPromptData:
        """
        Transformiert Layout-Daten in einen cinematisch-natürlichsprachlichen Prompt.
        
        Args:
            layout_data: LayoutIntegratedData Objekt
            enable_text_rendering: Ob Text gerendert werden soll
            quality_level: Qualitätsstufe ("basic", "high", "premium")
            
        Returns:
            CinematicPromptData mit transformiertem Prompt
        """
        self.logger.info("🎬 Starte Prompt-Transformation zu cinematischem Stil")
        
        # Extrahiere Daten
        structured = layout_data.structured_input
        layout_def = layout_data.layout_definition
        text_placements = layout_data.text_placements
        motiv_treatment = layout_data.motiv_treatment
        
        # 1. Visuelle Beschreibung (Hauptmotiv)
        visual_description = self._build_visual_description(structured, motiv_treatment)
        
        # 2. Layout-Beschreibung (natürlichsprachlich)
        layout_description = self._build_layout_description(layout_def, text_placements, structured, enable_text_rendering)
        
        # 3. Stil-Beschreibung
        style_description = self._build_style_description(structured, layout_def)
        
        # 4. Qualitäts-Anforderungen (basierend auf Level)
        quality_requirements = self._build_quality_requirements(quality_level)
        
        # 5. Negative Prompts
        negative_prompts = self._build_negative_prompts(enable_text_rendering)
        
        # 6. Vollständigen Prompt zusammenbauen
        full_prompt = self._assemble_full_prompt(
            visual_description, layout_description, style_description, 
            quality_requirements, negative_prompts
        )
        
        # 7. Metadaten für Tracking
        metadata = {
            'transformation_type': 'cinematic',
            'original_layout': layout_def.get('name', 'unknown'),
            'text_rendering': enable_text_rendering,
            'quality_level': quality_level,
            'prompt_length': len(full_prompt),
            'sections': {
                'visual': len(visual_description),
                'layout': len(layout_description),
                'style': len(style_description),
                'quality': len(quality_requirements),
                'negative': len(negative_prompts)
            }
        }
        
        self.logger.info(f"✅ Prompt-Transformation abgeschlossen: {len(full_prompt)} chars")
        
        return CinematicPromptData(
            visual_description=visual_description,
            layout_description=layout_description,
            style_description=style_description,
            quality_requirements=quality_requirements,
            negative_prompts=negative_prompts,
            full_prompt=full_prompt,
            metadata=metadata
        )
    
    def _build_visual_description(self, structured: Any, motiv_treatment: Dict[str, Any]) -> str:
        """Baut eine natürliche visuelle Beschreibung des Hauptmotivs mit Fokus auf echte Menschen"""
        
        # Basis-Motiv-Beschreibung (deutsch)
        enhanced_motiv = motiv_treatment.get('enhanced_description', structured.motiv_prompt)
        
        # ECHTE MENSCHEN - Qualitätsverbesserung
        human_quality_parts = [
            "Ein echter, authentischer Mensch mit natürlichen Gesichtszügen",
            "realistische Hauttextur und natürliche Gesichtsausdrücke",
            "professionelle, aber warme Ausstrahlung",
            "authentische Arbeitskleidung und natürliche Körperhaltung",
            "KEIN Stock-Foto oder generische Darstellung",
            "echte, ungeschönte Gesichtszüge wie von einem echten Foto",
            "natürliche Falten und Hautdetails",
            "🚨 WICHTIG: Echte, authentische Person, kein generisches Stock-Foto",
            "🚨 WICHTIG: Natürliche, ungeschönte Darstellung wie ein echtes Foto",
            "🚨 WICHTIG: Verwende echte, ungeschönte Gesichtszüge mit natürlichen Details",
            "🚨 WICHTIG: Keine perfekten, glatten Gesichter wie aus der Werbung"
        ]
        
        # Professionelle Kontext-Informationen hinzufügen
        context_parts = []
        
        if structured.position_long:
            context_parts.append(f"Die Person arbeitet als {structured.position_long}")
        
        if structured.company and structured.location:
            context_parts.append(f"bei {structured.company} in {structured.location}")
        
        # Visuelle Details (deutsch)
        visual_details = []
        if structured.visual_style:
            visual_details.append(f"Darstellung: {structured.visual_style}")
        if structured.lighting_type:
            visual_details.append(f"Beleuchtung: {structured.lighting_type}")
        if structured.framing:
            visual_details.append(f"Komposition: {structured.framing}")
        if structured.lighting_mood:
            visual_details.append(f"Stimmung: {structured.lighting_mood}")
        
        # Zusammenbauen mit Fokus auf Qualität
        description_parts = [
            enhanced_motiv,
            ", ".join(human_quality_parts),
            "WICHTIG: Alle Texte und Beschreibungen müssen auf Deutsch sein!"
        ]
        
        if context_parts:
            description_parts.append(f"Kontext: {' '.join(context_parts)}")
        
        if visual_details:
            description_parts.append(f"Technische Details: {', '.join(visual_details)}")
        
        return ' '.join(description_parts)
    
    def _build_layout_description(self, layout_def: Dict[str, Any], text_placements: Dict[str, Any], 
                                 structured: Any, enable_text_rendering: bool) -> str:
        """Baut eine natürliche Layout-Beschreibung ohne technische Koordinaten"""
        
        layout_name = layout_def.get('name', 'Layout')
        layout_mapping = self.layout_visual_mapping.get(layout_name, {
            'description': 'professionelles Layout',
            'visual_style': 'moderne Gestaltung',
            'composition': 'ausgewogene Komposition'
        })
        
        # Layout-Typ beschreiben
        layout_parts = [
            f"Das Creative verwendet ein {layout_mapping['description']}",
            f"mit {layout_mapping['composition']}",
            f"in {layout_mapping['visual_style']} Gestaltung",
            "🚨 WICHTIG: Das Layout muss exakt wie beschrieben umgesetzt werden!"
        ]
        
        # Text-Bereiche beschreiben (ohne Koordinaten)
        if text_placements:
            text_areas = []
            
            # Headline
            if 'headline' in text_placements and text_placements['headline'].get('content'):
                headline = text_placements['headline']['content']
                if enable_text_rendering:
                    text_areas.append(f"einer prominenten Headline \"{headline}\"")
                else:
                    text_areas.append("einem prominenten Headline-Bereich")
            
            # Subline
            if 'subline' in text_placements and text_placements['subline'].get('content'):
                subline = text_placements['subline']['content']
                if enable_text_rendering:
                    text_areas.append(f"einer unterstützenden Subline \"{subline}\"")
                else:
                    text_areas.append("einem unterstützenden Subline-Bereich")
            
            # Company
            if 'company' in text_placements and text_placements['company'].get('content'):
                company = text_placements['company']['content']
                if enable_text_rendering:
                    text_areas.append(f"dem Unternehmensnamen \"{company}\"")
                else:
                    text_areas.append("dem Unternehmensbereich")
            
            # Stellentitel
            if 'stellentitel' in text_placements and text_placements['stellentitel'].get('content'):
                stellentitel = text_placements['stellentitel']['content']
                if enable_text_rendering:
                    text_areas.append(f"dem Stellentitel \"{stellentitel}\"")
                else:
                    text_areas.append("dem Stellentitel-Bereich")
            
            # Benefits
            if 'benefits' in text_placements and text_placements['benefits'].get('content'):
                benefits = text_placements['benefits']['content']
                if isinstance(benefits, list) and benefits:
                    if enable_text_rendering:
                        benefit_texts = [f"\"{benefit}\"" for benefit in benefits[:3]]  # Max 3
                        text_areas.append(f"den Benefits {', '.join(benefit_texts)}")
                    else:
                        text_areas.append("den Benefits-Bereichen")
            
            # CTA
            if 'cta' in text_placements and text_placements['cta'].get('content'):
                cta = text_placements['cta']['content']
                accent_color = structured.ci_colors.get('accent', '#FFC20E')
                accent_desc = self._get_color_description(accent_color)
                
                if enable_text_rendering:
                    text_areas.append(f"einem Call-to-Action Button \"{cta}\" in {accent_desc}")
                else:
                    text_areas.append(f"einem Call-to-Action Button in {accent_desc}")
            
            # Location
            if structured.location:
                accent_color = structured.ci_colors.get('accent', '#FFC20E')
                accent_desc = self._get_color_description(accent_color)
                
                if enable_text_rendering:
                    text_areas.append(f"einem prominenten Standort-Banner \"📍 {structured.location}\" in {accent_desc} mit Pin-Symbol")
                else:
                    text_areas.append(f"einem prominenten Standort-Banner mit Pin-Symbol in {accent_desc}")
            
            if text_areas:
                layout_parts.append(f"mit {', '.join(text_areas)}")
        
        return ' '.join(layout_parts) + "."
    
    def _build_style_description(self, structured: Any, layout_def: Dict[str, Any]) -> str:
        """Baut eine natürliche Stil-Beschreibung"""
        
        style_parts = []
        
        # Corporate Design
        ci_colors = structured.ci_colors
        if ci_colors:
            primary = ci_colors.get('primary', '#005EA5')
            secondary = ci_colors.get('secondary', '#B4D9F7')
            accent = ci_colors.get('accent', '#FFC20E')
            
            primary_desc = self._get_color_description(primary)
            secondary_desc = self._get_color_description(secondary)
            accent_desc = self._get_color_description(accent)
            
            style_parts.append(f"Das Corporate Design verwendet {primary_desc} als Hauptfarbe")
            style_parts.append(f"mit {secondary_desc} als unterstützende Farbe")
            style_parts.append(f"und {accent_desc} für Akzente und Call-to-Actions")
        
        # Style Options
        style_options = structured.style_options
        if style_options:
            text_containers = style_options.get('text_containers', {})
            if text_containers:
                shape = text_containers.get('shape', 'rounded_rectangle')
                if shape == 'rounded_rectangle':
                    style_parts.append("mit abgerundeten Text-Containern")
                elif shape == 'rectangle':
                    style_parts.append("mit rechteckigen Text-Containern")
                elif shape == 'circle':
                    style_parts.append("mit kreisrunden Text-Containern")
        
        # Professionelle Qualität
        style_parts.append("Das Design ist professionell und modern gestaltet")
        style_parts.append("mit klaren visuellen Hierarchien und guter Lesbarkeit")
        
        return ' '.join(style_parts) + "."
    
    def _build_quality_requirements(self, quality_level: str = "high") -> str:
        """Baut Qualitäts-Anforderungen mit Midjourney-Style Integration"""
        
        if quality_level == "premium":
            return (
                "Das Bild soll in höchster Fotografie-Qualität sein mit 8K-Auflösung und professioneller Beleuchtung. "
                "Es soll echte, authentische Menschen mit natürlichen Gesichtsausdrücken und realistischer Hauttextur zeigen. "
                "Die Darstellung soll fotorealistisch sein mit natürlichen Schatten, realistischen Materialien und professioneller Komposition. "
                "Verwende natürliche Beleuchtung, realistische Farben und authentische Arbeitsumgebungen. "
                "Das Creative soll Corporate-Standard-Qualität haben und für professionelle Recruiting-Kampagnen geeignet sein. "
                "Hochwertige Texturen, detaillierte Gesichtszüge und professionelle Fotografie-Qualität."
            )
        elif quality_level == "high":
            return (
                "Das Bild soll in höchster Fotografie-Qualität sein mit 8K-Auflösung und professioneller Beleuchtung. "
                "Es soll echte, authentische Menschen mit natürlichen Gesichtsausdrücken und realistischer Hauttextur zeigen. "
                "Die Darstellung soll fotorealistisch sein mit natürlichen Schatten, realistischen Materialien und professioneller Komposition. "
                "Das Creative soll Corporate-Standard-Qualität haben und für professionelle Recruiting-Kampagnen geeignet sein. "
                "Verwende natürliche Beleuchtung, realistische Farben und authentische Arbeitsumgebungen. "
                "Alle Texte müssen auf Deutsch sein und korrekt geschrieben werden. "
                "Verwende echte, ungeschönte Gesichtszüge statt perfekter Stock-Foto Darstellungen."
            )
        else:  # basic
            return (
                "Das Bild soll in professioneller Fotografie-Qualität sein. "
                "Es soll authentische Arbeitsplatz-Szenarien zeigen mit natürlichen Gesichtsausdrücken. "
                "Das Creative soll Corporate-Standard-Qualität haben und für professionelle Recruiting-Kampagnen geeignet sein."
            )
    
    def _build_negative_prompts(self, enable_text_rendering: bool) -> str:
        """Baut negative Prompts mit Fokus auf echte Menschen"""
        negative_parts = [
            "Vermeide unscharfe oder niedrigauflösende Elemente",
            "keine generischen Stock-Foto Erscheinung",
            "keine verzerrten Gesichter oder unnatürliche Proportionen",
            "keine künstlich wirkenden oder generischen Gesichter",
            "keine übermäßig bearbeiteten oder unnatürlichen Hauttexturen",
            "keine cartoonartigen oder stilisierten Darstellungen",
            "keine übermäßig gestellten oder unnatürlichen Posen",
            "keine englischen Texte oder Begriffe",
            "keine perfekten, glatten Gesichter wie aus der Werbung",
            "keine generischen Business-Porträts",
            "keine übermäßig gestylten oder bearbeiteten Darstellungen"
        ]
        
        if not enable_text_rendering:
            negative_parts.append("alle Layout-Bereiche müssen als sichtbare Farbflächen erscheinen")
        else:
            negative_parts.append("Text soll klar und lesbar sein")
        
        return ' '.join(negative_parts) + "."
    
    def _assemble_full_prompt(self, visual_description: str, layout_description: str, 
                             style_description: str, quality_requirements: str, 
                             negative_prompts: str) -> str:
        """Baut den vollständigen cinematischen Prompt mit Midjourney-Style Integration"""
        
        prompt_parts = [
            "Ein professionelles Recruiting-Creative für Social Media in höchster Fotografie-Qualität mit folgender Gestaltung:",
            "",
            "🚨 WICHTIG: Alle Texte und Beschreibungen MÜSSEN auf Deutsch sein!",
            "🚨 WICHTIG: Keine englischen Begriffe verwenden!",
            "🚨 WICHTIG: Alle Headlines, Benefits und CTAs müssen auf Deutsch sein!",
            "🚨 WICHTIG: Verwende NUR deutsche Sprache, keine englischen Texte!",
            "🚨 WICHTIG: Alle Schriftzüge und Beschriftungen müssen auf Deutsch sein!",
            "🚨 WICHTIG: DALL-E soll deutsche Texte korrekt rendern, keine englischen Wörter!",
            "",
            f"VISUELLES MOTIV: {visual_description}",
            "",
            f"LAYOUT: {layout_description}",
            "",
            f"STIL: {style_description}",
            "",
            f"QUALITÄT: {quality_requirements}",
            "",
            f"NICHT ERWÜNSCHT: {negative_prompts}",
            "",
            "STYLE: fotorealistisch, professionelle Fotografie, natürliche Beleuchtung, authentische Darstellung",
            "",
            "SPRACHE: Alle Texte und Beschreibungen MÜSSEN auf Deutsch sein, keine englischen Begriffe verwenden!",
            "SPRACHE: Headlines, Benefits und Call-to-Actions MÜSSEN auf Deutsch sein!",
            "SPRACHE: Verwende ausschließlich deutsche Sprache für alle Textelemente!",
            "SPRACHE: DALL-E soll deutsche Wörter korrekt schreiben, keine englischen Texte rendern!",
            "SPRACHE: Verwende deutsche Umlaute (ä, ö, ü) und korrekte deutsche Rechtschreibung!"
        ]
        
        return '\n'.join(prompt_parts)
    
    def _get_color_description(self, hex_color: str) -> str:
        """Konvertiert Hex-Farben in natürliche Beschreibungen"""
        
        # Vereinfachte Farb-Erkennung
        hex_color = hex_color.upper()
        
        if hex_color.startswith('#FF'):
            return "lebendigem Gelb"
        elif hex_color.startswith('#00'):
            return "tiefem Blau"
        elif hex_color.startswith('#DC') or hex_color.startswith('#EF'):
            return "kräftigem Rot"
        elif hex_color.startswith('#10') or hex_color.startswith('#05'):
            return "frischem Grün"
        elif hex_color.startswith('#7C') or hex_color.startswith('#8B'):
            return "lebendigem Violett"
        elif hex_color.startswith('#F5'):
            return "warmem Orange"
        else:
            return "professioneller Farbe"
    
    def get_transformation_stats(self, original_prompt: str, cinematic_prompt: str) -> Dict[str, Any]:
        """Gibt Statistiken über die Transformation zurück"""
        return {
            'original_length': len(original_prompt),
            'cinematic_length': len(cinematic_prompt),
            'reduction_percentage': round((1 - len(cinematic_prompt) / len(original_prompt)) * 100, 1),
            'transformation_type': 'structured_to_cinematic'
        }

def create_prompt_transformer() -> PromptTransformer:
    """Factory-Funktion für PromptTransformer"""
    return PromptTransformer() 