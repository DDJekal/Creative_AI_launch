#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
text_to_motiv_converter.py

🎯 Einfacher Text-zu-Motiv-Converter
🚀 Wandelt Textelemente (Headline, Subline, Benefits) in Motiv-Beschreibungen um
✨ Keine API-Aufrufe - nur lokale Text-Transformation

FEATURES:
- Automatische Motiv-Generierung aus Textelementen
- Kontext-bewusste Transformation
- Integration mit Layout und CI-Farben
- Optimiert für Pflege-Recruiting Szenarien
"""

from typing import Dict, List, Any
import re

class TextToMotivConverter:
    """
    Einfacher Text-zu-Motiv-Converter
    
    Wandelt Textelemente (Headline, Subline, Benefits) automatisch in
    passende Motiv-Beschreibungen um, ohne externe API-Aufrufe.
    """
    
    def __init__(self):
        """Initialisiert den Text-zu-Motiv-Converter"""
        # Schlüsselwörter für verschiedene Branchen
        self.industry_keywords = {
            'pflege': ['pflege', 'krankenhaus', 'klinik', 'station', 'patient', 'medizin', 'gesundheit'],
            'technik': ['entwickler', 'programmierer', 'software', 'it', 'digital', 'technologie'],
            'beratung': ['berater', 'consulting', 'strategie', 'management', 'planung'],
            'bildung': ['lehrer', 'dozent', 'bildung', 'schule', 'universität', 'lernen'],
            'handel': ['verkäufer', 'kassierer', 'laden', 'shop', 'retail', 'kunde']
        }
        
        # Visuelle Stil-Vorlagen
        self.visual_templates = {
            'pflege': [
                "Professionelle Pflegekraft in moderner Krankenhausumgebung, freundlich lächelnd, Stethoskop um den Hals",
                "Engagierte Pflegekraft bei der Arbeit, konzentriert und einfühlsam, moderne medizinische Ausrüstung im Hintergrund",
                "Team von Pflegekräften in heller, sauberer Station, positive Atmosphäre, vertrauensvoll"
            ],
            'technik': [
                "Entwickler an modernem Arbeitsplatz, konzentriert vor mehreren Bildschirmen, professionelle Umgebung",
                "IT-Team in kollaborativer Arbeitsatmosphäre, moderne Büroausstattung, innovative Technologie",
                "Programmierer bei der Arbeit, fokussiert und kreativ, moderne Arbeitsumgebung"
            ],
            'beratung': [
                "Professioneller Berater in eleganter Büroumgebung, vertrauensvoll und kompetent",
                "Beratungsteam bei der Präsentation, moderne Konferenzräume, professionelle Atmosphäre",
                "Strategieberater bei der Arbeit, konzentriert und analytisch, hochwertige Büroausstattung"
            ],
            'bildung': [
                "Engagierter Lehrer in modernem Klassenzimmer, motivierend und inspirierend",
                "Dozent bei der Präsentation, moderne Hörsaalausstattung, professionelle Lernumgebung",
                "Bildungsexperte bei der Arbeit, konzentriert und leidenschaftlich, moderne Arbeitsumgebung"
            ],
            'handel': [
                "Freundlicher Verkäufer im modernen Laden, kundenorientiert und servicebereit",
                "Verkaufsteam in eleganter Geschäftsumgebung, professionell und einladend",
                "Kassierer bei der Arbeit, effizient und freundlich, moderne Verkaufsfläche"
            ]
        }
    
    def generate_motiv_from_textelements(
        self, 
        text_elements: Dict[str, Any],
        visual_style: str = "Professionell",
        lighting_type: str = "Natürlich", 
        lighting_mood: str = "Vertrauensvoll",
        framing: str = "Medium Shot",
        layout_id: str = "skizze1_vertical_split",
        ci_colors: Dict[str, str] = None
    ) -> str:
        """
        Generiert ein Motiv basierend auf den verfügbaren Textelementen
        
        Args:
            text_elements: Dictionary mit Textelementen (headline, subline, benefits, etc.)
            visual_style: Gewünschter visueller Stil
            lighting_type: Art der Beleuchtung
            lighting_mood: Gewünschte Stimmung
            framing: Bildausschnitt
            layout_id: Gewähltes Layout
            ci_colors: CI-Farben für Kontext
            
        Returns:
            Generierter Motiv-Text für DALL-E
        """
        try:
            # Branche identifizieren
            industry = self._identify_industry(text_elements)
            
            # Basis-Motiv aus Branche wählen
            base_motiv = self._get_base_motiv(industry)
            
            # Motiv mit Textelementen anreichern
            enriched_motiv = self._enrich_motiv_with_elements(base_motiv, text_elements)
            
            # Visuelle Parameter hinzufügen
            final_motiv = self._add_visual_parameters(
                enriched_motiv, 
                visual_style, 
                lighting_type, 
                lighting_mood, 
                framing
            )
            
            return final_motiv
            
        except Exception as e:
            # Fallback-Motiv
            return f"Professionelle Person in moderner Umgebung, {visual_style.lower()} Stil, {lighting_type.lower()} Beleuchtung, {framing.lower()}"
    
    def _identify_industry(self, text_elements: Dict[str, Any]) -> str:
        """Identifiziert die Branche basierend auf den Textelementen"""
        combined_text = " ".join([
            str(text_elements.get('headline', '')),
            str(text_elements.get('subline', '')),
            str(text_elements.get('stellentitel', '')),
            str(text_elements.get('position_long', '')),
            " ".join(text_elements.get('benefits', []))
        ]).lower()
        
        # Branche mit den meisten Übereinstimmungen finden
        best_match = 'pflege'  # Standard
        max_matches = 0
        
        for industry, keywords in self.industry_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            if matches > max_matches:
                max_matches = matches
                best_match = industry
        
        return best_match
    
    def _get_base_motiv(self, industry: str) -> str:
        """Holt das Basis-Motiv für die identifizierte Branche"""
        import random
        
        if industry in self.visual_templates:
            return random.choice(self.visual_templates[industry])
        else:
            return "Professionelle Person in moderner Arbeitsumgebung, konzentriert und engagiert"
    
    def _enrich_motiv_with_elements(self, base_motiv: str, text_elements: Dict[str, Any]) -> str:
        """Reichert das Basis-Motiv mit spezifischen Textelementen an"""
        enriched = base_motiv
        
        # Unternehmen hinzufügen (falls verfügbar)
        if 'unternehmen' in text_elements and text_elements['unternehmen']:
            company = text_elements['unternehmen']
            if 'klinikum' in company.lower() or 'krankenhaus' in company.lower():
                enriched = enriched.replace('Krankenhausumgebung', f'{company} Umgebung')
                enriched = enriched.replace('Station', f'{company} Station')
        
        # Standort hinzufügen (falls verfügbar)
        if 'location' in text_elements and text_elements['location']:
            location = text_elements['location']
            if location not in enriched:
                enriched += f", Standort {location}"
        
        # Stellentitel für Kontext
        if 'stellentitel' in text_elements and text_elements['stellentitel']:
            position = text_elements['stellentitel']
            if 'pflege' in position.lower():
                enriched = enriched.replace('Person', 'Pflegekraft')
            elif 'entwickler' in position.lower() or 'programmierer' in position.lower():
                enriched = enriched.replace('Person', 'Entwickler')
            elif 'berater' in position.lower():
                enriched = enriched.replace('Person', 'Berater')
        
        return enriched
    
    def _add_visual_parameters(
        self, 
        motiv: str, 
        visual_style: str, 
        lighting_type: str, 
        lighting_mood: str, 
        framing: str
    ) -> str:
        """Fügt visuelle Parameter zum Motiv hinzu"""
        visual_elements = []
        
        # Visueller Stil
        if visual_style and visual_style != "Professionell":
            visual_elements.append(f"{visual_style.lower()} Stil")
        
        # Beleuchtung
        if lighting_type and lighting_type != "Natürlich":
            visual_elements.append(f"{lighting_type.lower()} Beleuchtung")
        
        # Stimmung
        if lighting_mood and lighting_mood != "Vertrauensvoll":
            visual_elements.append(f"{lighting_mood.lower()} Stimmung")
        
        # Bildausschnitt
        if framing and framing != "Medium Shot":
            visual_elements.append(f"{framing.lower()} Bildausschnitt")
        
        # Visuelle Elemente hinzufügen
        if visual_elements:
            motiv += f", {', '.join(visual_elements)}"
        
        return motiv
    
    def create_contextual_motiv(self, text_elements: Dict[str, Any]) -> str:
        """
        Erstellt ein kontextuelles Motiv basierend auf den Textelementen
        
        Args:
            text_elements: Dictionary mit Textelementen
            
        Returns:
            Kontextuelles Motiv
        """
        # Headline für Kontext verwenden
        headline = text_elements.get('headline', '')
        subline = text_elements.get('subline', '')
        benefits = text_elements.get('benefits', [])
        
        # Motiv aus Headline und Subline ableiten
        if headline and subline:
            # Schlüsselwörter aus Headline extrahieren
            headline_keywords = self._extract_keywords(headline)
            subline_keywords = self._extract_keywords(subline)
            
            # Kombiniertes Motiv erstellen
            motiv_parts = []
            
            if headline_keywords:
                motiv_parts.append(f"Person mit {', '.join(headline_keywords)}")
            
            if subline_keywords:
                motiv_parts.append(f"in {', '.join(subline_keywords)} Umgebung")
            
            if benefits:
                benefit_keywords = self._extract_keywords(" ".join(benefits))
                if benefit_keywords:
                    motiv_parts.append(f"mit Fokus auf {', '.join(benefit_keywords)}")
            
            if motiv_parts:
                return ", ".join(motiv_parts) + ", professionell und vertrauensvoll"
        
        # Fallback
        return "Professionelle Person in moderner Arbeitsumgebung, engagiert und motiviert"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiert Schlüsselwörter aus einem Text"""
        # Einfache Schlüsselwort-Extraktion
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Wichtige Wörter filtern
        important_words = [
            'team', 'zukunft', 'gesundheit', 'pflege', 'medizin', 'technologie',
            'entwicklung', 'beratung', 'bildung', 'verkauf', 'service', 'qualität',
            'innovation', 'wachstum', 'erfolg', 'zusammenarbeit', 'kompetenz'
        ]
        
        keywords = [word for word in words if word in important_words and len(word) > 3]
        
        # Auf 3-5 Schlüsselwörter begrenzen
        return keywords[:5] if keywords else ['professionell', 'modern']

# Einfache Funktion für die Verwendung
def generate_motiv_from_textelements_simple(
    headline: str,
    subline: str,
    benefits: List[str],
    **kwargs
) -> str:
    """
    Einfache Funktion für die Motiv-Generierung
    
    Args:
        headline: Hauptüberschrift
        subline: Untertitel
        benefits: Liste der Benefits
        **kwargs: Weitere Parameter
        
    Returns:
        Generierter Motiv-Text
    """
    converter = TextToMotivConverter()
    
    text_elements = {
        'headline': headline,
        'subline': subline,
        'benefits': benefits
    }
    text_elements.update(kwargs)
    
    return converter.generate_motiv_from_textelements(text_elements)

# Hauptfunktion für die Verwendung in der Streamlit-App
def create_text_to_motiv_converter() -> TextToMotivConverter:
    """Erstellt eine Instanz des Text-zu-Motiv-Converters"""
    return TextToMotivConverter()

if __name__ == "__main__":
    # Test der Funktionalität
    print("🧪 Teste Text-zu-Motiv-Converter...")
    
    # Test-Instanz erstellen
    converter = TextToMotivConverter()
    
    # Test-Textelemente
    test_elements = {
        'headline': 'Werden Sie Teil unseres Teams!',
        'subline': 'Gestalten Sie mit uns die Zukunft des Gesundheitswesens',
        'benefits': ['Flexible Arbeitszeiten', 'Attraktive Vergütung', 'Fortbildungsmöglichkeiten'],
        'unternehmen': 'Klinikum München',
        'stellentitel': 'Pflegekraft (m/w/d)',
        'location': 'München'
    }
    
    # Test-Motiv generieren
    test_motiv = converter.generate_motiv_from_textelements(test_elements)
    print(f"🎯 Generiertes Motiv: {test_motiv}")
    
    # Kontextuelles Motiv testen
    contextual_motiv = converter.create_contextual_motiv(test_elements)
    print(f"🎯 Kontextuelles Motiv: {contextual_motiv}")
