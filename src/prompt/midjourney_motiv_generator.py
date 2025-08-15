#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
midjourney_motiv_generator.py

🎯 ChatGPT-Modul für Midjourney Motiv-Prompt-Generierung
📊 Optimiert für Pflege-Recruiting mit Eye-Catcher-Elementen
�� Basiert auf 6 Szenarien + 5 Eye-Catcher-Stilen
"""

import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class MidjourneyMotivGenerator:
    """ChatGPT-basierter Generator für Midjourney Motiv-Prompts"""
    
    def __init__(self):
        self.client = OpenAI()
        
        # Szenario-Templates
        self.scenario_templates = {
            "workplace": {
                "name": "Arbeitsumgebung im Pflegealltag",
                "description": "Pflegekräfte bei der Arbeit in moderner Station/Pflegeheim",
                "elements": [
                    "Pflegekraft im Gespräch mit Patient*in",
                    "Team-Interaktion am Stationsstützpunkt", 
                    "Natürliche Beleuchtung, freundliche Stimmung"
                ],
                "effect": "Authentizität, Vertrauen, Nähe",
                "meta_advantage": "Funktioniert sehr gut im Feed, da es realistisch wirkt"
            },
            "team": {
                "name": "Team- und Gemeinschaftsbilder",
                "description": "Gruppenaufnahme von Kolleg*innen, lächelnd, in Uniform",
                "elements": [
                    "3-6 Personen",
                    "Positive Körpersprache",
                    "CI-Farben als Akzent in Kleidung oder Hintergrund"
                ],
                "effect": "Hier will ich dazugehören-Gefühl",
                "meta_advantage": "Starke soziale Bindung, hoher Engagement-Faktor"
            },
            "empathy": {
                "name": "Menschliche Nähe & Empathie",
                "description": "Emotionale Momente - Handhalten, Gespräch auf Augenhöhe",
                "elements": [
                    "Patient und Pflegekraft in Interaktion",
                    "Weiche Lichtstimmung, geringe Tiefenschärfe"
                ],
                "effect": "Wärme, Sinnhaftigkeit des Berufs",
                "meta_advantage": "Hohe Klickrate durch emotionale Ansprache"
            },
            "technology": {
                "name": "Moderne Technik & Innovation",
                "description": "Pflegekräfte nutzen moderne Geräte oder digitale Dokumentation",
                "elements": [
                    "Tablet, EKG, Monitor",
                    "Saubere, helle Umgebung"
                ],
                "effect": "Fortschrittlich, professionell",
                "meta_advantage": "Spricht technikaffine Bewerber*innen an"
            },
            "employer": {
                "name": "Arbeitgeber-Marke & Standort",
                "description": "Kombination aus Klinik-/Pflegeheim-Fassade + Logo",
                "elements": [
                    "Erkennbares Gebäude",
                    "Standort im Textfeld hervorgehoben"
                ],
                "effect": "Lokale Bindung",
                "meta_advantage": "Hohe Relevanz in regionalem Targeting"
            },
            "hero": {
                "name": "Hero-Portrait",
                "description": "Einzelportrait einer Pflegekraft als Held/in des Alltags",
                "elements": [
                    "Blick in Kamera",
                    "Dienstkleidung, ggf. Stethoskop",
                    "Unscharfer Arbeitsumgebungs-Hintergrund"
                ],
                "effect": "Personalisierte Ansprache",
                "meta_advantage": "Gut geeignet für Carousel oder Story-Format"
            }
        }
        
        # Eye-Catcher-Templates
        self.eyecatcher_templates = {
            "direct_gaze": {
                "name": "Nahaufnahme mit direktem Blickkontakt",
                "description": "Blick in die Kamera erzeugt sofort persönliche Verbindung",
                "setup": [
                    "Pflegekraft im Vordergrund, klar ausgeleuchtet",
                    "Unscharfer Hintergrund (Bokeh)",
                    "Leichtes Lächeln oder stolzer Gesichtsausdruck",
                    "CI-Farbe als Akzent (Stethoskop oder Kittel)"
                ],
                "eyecatcher_factor": "Sehr hoch - menschliche Gesichter stoppen den Scroll"
            },
            "emotional": {
                "name": "Emotionale Interaktion",
                "description": "Positive Emotionen wirken ansteckend und transportieren Sinnhaftigkeit",
                "setup": [
                    "Pflegekraft + Patient*in in authentischem Moment",
                    "Warmes, natürliches Licht",
                    "Hände sichtbar (Handhalten, Stützen)"
                ],
                "eyecatcher_factor": "Hoch - Emotion springt sofort ins Auge"
            },
            "color_contrast": {
                "name": "Starke Farbkontraste + klare Formen",
                "description": "Farbintensive Bilder stechen in der Social Media Flut hervor",
                "setup": [
                    "Hintergrund in CI-Farbe",
                    "Motiv klar freigestellt",
                    "CTA-Farbe als sichtbares grafisches Element"
                ],
                "eyecatcher_factor": "Hoch - besonders in Storys oder Carousels"
            },
            "hero_pose": {
                "name": "Hero-Pose Alltagsheld/in",
                "description": "Positioniert Pflegekraft als respektierte Fachperson",
                "setup": [
                    "Leicht von unten fotografiert (Hero-Angle)",
                    "Weite, helle Kulisse (Klinik, Station)",
                    "Selbstbewusste Körperhaltung"
                ],
                "eyecatcher_factor": "Mittel-Hoch - strahlt Stärke und Professionalität aus"
            },
            "pov": {
                "name": "Unerwartete Perspektive / POV",
                "description": "Ungewöhnliche Blickwinkel bleiben im Kopf",
                "setup": [
                    "Kamera aus Bettperspektive oder Stationsdurchgang",
                    "Hände der Pflegekraft im Vordergrund",
                    "Gesicht leicht unscharf"
                ],
                "eyecatcher_factor": "Hoch - bricht mit Standard-Stock-Optik"
            }
        }
    
    def generate_motiv_prompt(self, 
                             scenario_type: str,
                             custom_prompt: str = "",
                             company_name: str = "",
                             location_name: str = "") -> str:
        """
        Generiert einen Midjourney Prompt basierend auf Szenario-Template
        
        Args:
            scenario_type: Art des Szenarios (employer, workplace, team, empathy, technology, hero)
            custom_prompt: Benutzerdefinierte Zusätze
            company_name: Name des Unternehmens
            location_name: Name des Standorts
            
        Returns:
            Generierter Midjourney Prompt
        """
        
        try:
            # ERWEITERTE Szenario-spezifische Prompts mit mehr Variation und Adjektiven
            scenario_prompts = {
                "employer": [
                    f"stunning modern hospital building of {company_name} in {location_name}, architectural photography, clean geometric lines, professional corporate appearance, distinctive corporate identity, iconic landmark building, vibrant urban setting, golden hour natural lighting, award-winning photography style, ultra high quality, intricate details, contemporary design, glass facade, sustainable architecture",
                    f"magnificent contemporary hospital complex of {company_name} located in {location_name}, architectural masterpiece, sleek modern design, corporate branding excellence, recognizable landmark structure, dynamic urban environment, dramatic natural lighting, professional architectural photography, exceptional quality, fine details, innovative design, premium materials, urban sophistication",
                    f"impressive state-of-the-art hospital facility of {company_name} in {location_name}, cutting-edge architecture, sophisticated corporate aesthetic, prominent landmark presence, bustling urban landscape, natural daylight streaming, professional photography excellence, outstanding quality, meticulous details, avant-garde design, luxury finishes, metropolitan elegance"
                ],
                
                "workplace": [
                    f"dedicated healthcare professionals working passionately in modern hospital ward, bustling nursing station, advanced medical equipment, warm natural lighting, professional healthcare environment, authentic workplace atmosphere, realistic healthcare setting, exceptional detail, award-winning photography, compassionate care, medical excellence, healing environment",
                    f"skilled medical professionals delivering exceptional care in contemporary hospital ward, modern nursing station, cutting-edge medical technology, natural daylight illumination, professional medical environment, genuine workplace authenticity, realistic medical setting, outstanding detail, professional photography mastery, patient-centered care, clinical excellence, therapeutic atmosphere",
                    f"experienced healthcare team providing outstanding service in state-of-the-art hospital ward, innovative nursing station, sophisticated medical equipment, natural lighting design, professional healthcare setting, authentic workplace realism, true-to-life medical environment, superior detail, professional photography excellence, compassionate healthcare, medical professionalism, healing atmosphere"
                ],
                
                "team": [
                    f"dynamic group of 3-6 dedicated healthcare professionals in crisp uniforms, radiant smiles, engaging team interaction, modern hospital setting, positive body language, professional appearance, natural lighting, authentic team camaraderie, exceptional quality, collaborative spirit, medical excellence, team synergy",
                    f"inspiring team of healthcare professionals in professional uniforms, warm smiles, collaborative interaction, contemporary hospital environment, confident body language, polished appearance, natural lighting, genuine team atmosphere, outstanding quality, teamwork excellence, healthcare dedication, group harmony",
                    f"motivated healthcare team in immaculate uniforms, genuine smiles, interactive collaboration, state-of-the-art hospital setting, positive body language, professional demeanor, natural lighting, authentic team spirit, superior quality, collaborative excellence, medical dedication, team unity"
                ],
                
                "empathy": [
                    f"touching moment between compassionate healthcare professional and grateful patient, emotional hand holding, intimate conversation at eye level, warm golden lighting, artistic shallow depth of field, deeply emotional healthcare moment, authentic human connection, professional photography artistry, heartfelt care, emotional depth, healing touch",
                    f"heartwarming interaction between dedicated healthcare professional and appreciative patient, gentle hand holding, meaningful conversation, warm lighting atmosphere, creative shallow depth of field, emotionally rich healthcare scene, genuine human connection, professional photography excellence, compassionate care, emotional resonance, therapeutic connection",
                    f"moving encounter between caring healthcare professional and thankful patient, tender hand holding, heartfelt conversation, warm lighting design, artistic shallow depth of field, emotionally powerful healthcare moment, authentic human bond, professional photography mastery, empathetic care, emotional intensity, healing presence"
                ],
                
                "technology": [
                    f"innovative healthcare professionals utilizing cutting-edge medical devices, advanced tablet technology, sophisticated EKG monitoring, digital documentation systems, pristine bright environment, modern medical technology, professional healthcare setting, exceptional detail, professional photography excellence, technological advancement, medical innovation, digital healthcare",
                    f"tech-savvy healthcare professionals operating state-of-the-art medical equipment, modern tablet interfaces, advanced cardiac monitoring, digital healthcare systems, immaculate bright environment, contemporary medical technology, professional medical setting, outstanding detail, professional photography mastery, technological excellence, medical advancement, digital transformation",
                    f"forward-thinking healthcare professionals leveraging innovative medical technology, cutting-edge tablet solutions, advanced monitoring systems, digital healthcare platforms, spotless bright environment, modern medical technology, professional healthcare setting, superior detail, professional photography excellence, technological leadership, medical innovation, digital excellence"
                ],
                
                "hero": [
                    f"inspiring single healthcare professional portrait as everyday hero, confident gaze into camera, immaculate medical uniform, professional stethoscope, artistically blurred hospital background, dramatic professional lighting, powerful personal connection, exceptional quality portrait, heroic presence, medical dedication, professional pride",
                    f"remarkable healthcare professional portrait as daily hero, determined look at camera, pristine medical uniform, quality stethoscope, beautifully blurred hospital setting, professional lighting design, strong personal connection, outstanding quality portrait, heroic character, medical commitment, professional excellence",
                    f"exceptional healthcare professional portrait as workplace hero, focused gaze toward camera, perfect medical uniform, professional stethoscope, artistically blurred hospital environment, sophisticated professional lighting, compelling personal connection, superior quality portrait, heroic stature, medical devotion, professional distinction"
                ],
                
                "standort": [
                    f"breathtaking famous landmark of {location_name}, iconic architectural masterpiece, regional landmark significance, stunning architectural photography, vibrant urban setting, natural lighting perfection, professional photography excellence, exceptional detail, landmark recognition, architectural beauty, urban charm, regional pride",
                    f"magnificent famous landmark of {location_name}, iconic building excellence, regional landmark prominence, outstanding architectural photography, dynamic urban environment, natural lighting artistry, professional photography mastery, outstanding detail, landmark distinction, architectural grandeur, urban sophistication, regional significance",
                    f"spectacular famous landmark of {location_name}, iconic architectural wonder, regional landmark importance, exceptional architectural photography, bustling urban setting, natural lighting brilliance, professional photography excellence, superior detail, landmark excellence, architectural magnificence, urban elegance, regional heritage"
                ]
            }
            
            # Zufällige Auswahl aus den verschiedenen Varianten für mehr Variation
            import random
            base_prompt = random.choice(scenario_prompts.get(scenario_type, scenario_prompts["workplace"]))
            
            # Zusätzliche kreative Adjektive und Variationen hinzufügen
            creative_enhancements = [
                "cinematic composition, professional color grading, premium quality",
                "artistic framing, sophisticated lighting, exceptional clarity",
                "dynamic perspective, creative composition, outstanding resolution",
                "masterful photography, elegant styling, superior craftsmanship",
                "innovative approach, contemporary aesthetic, premium execution"
            ]
            
            # Zufällige kreative Verbesserung auswählen
            creative_enhancement = random.choice(creative_enhancements)
            
            # Benutzerdefinierte Eingabe hinzufügen
            if custom_prompt.strip():
                final_prompt = f"{base_prompt}, {custom_prompt}, {creative_enhancement}"
            else:
                final_prompt = f"{base_prompt}, {creative_enhancement}"
            
            # Prompt validieren und korrigieren
            final_prompt = self._validate_and_correct_prompt(final_prompt)
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Prompt-Generierung: {str(e)}")
            # Fallback-Prompt
            return self._generate_fallback_prompt(scenario_type, company_name, location_name)
    
    def _generate_fallback_prompt(self, scenario_type: str, company_name: str, location_name: str) -> str:
        """Generiert einen Fallback-Prompt falls die Hauptgenerierung fehlschlägt"""
        
        fallback_prompts = {
            "employer": f"stunning modern hospital building, {company_name}, {location_name}, architectural photography, professional corporate appearance, vibrant urban setting, natural lighting excellence, exceptional quality, architectural beauty, urban sophistication",
            "workplace": "dedicated healthcare professionals working in modern hospital, bustling nursing station, advanced medical equipment, natural lighting design, professional healthcare environment, exceptional detail, compassionate care, medical excellence",
            "team": "dynamic group of healthcare professionals in professional uniforms, radiant smiles, engaging team interaction, modern hospital setting, positive atmosphere, outstanding quality, collaborative spirit, medical dedication",
            "empathy": "touching moment between healthcare professional and patient, emotional interaction, warm lighting atmosphere, artistic composition, authentic healthcare scene, professional photography excellence, compassionate care, emotional depth",
            "technology": "innovative healthcare professionals using cutting-edge medical devices, modern technology integration, pristine bright environment, contemporary medical setting, exceptional detail, technological advancement, medical innovation",
            "hero": "inspiring healthcare professional portrait, confident gaze into camera, immaculate medical uniform, dramatic professional lighting, powerful personal connection, exceptional quality, heroic presence, medical dedication",
            "standort": f"breathtaking famous landmark of {location_name}, iconic architectural masterpiece, regional significance, stunning architectural photography, vibrant urban setting, natural lighting perfection, exceptional detail, architectural beauty"
        }
        
        return fallback_prompts.get(scenario_type, fallback_prompts["workplace"])
    
    def _validate_and_correct_prompt(self, prompt: str) -> str:
        """Validiert und korrigiert Midjourney Parameter im Prompt"""
        
        import re
        
        # KRITISCH: Alle Quality- und Aspect Ratio-Parameter entfernen
        prompt = re.sub(r'--q\s+[0-9]*[.]?[0-9]+', '', prompt)  # Entferne alle Quality-Parameter
        prompt = re.sub(r'--ar\s+[0-9]*[.]?[0-9]+:[0-9]*[.]?[0-9]+', '', prompt)  # Entferne alle AR-Parameter
        
        # KEINE Parameter hinzufügen - Midjourney soll Standard-Einstellungen verwenden
        
        # Zusätzliche Bereinigung: Doppelte Leerzeichen entfernen
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        return prompt

    def generate_motiv_prompt_with_job_analysis(self, scenario_type: str, custom_prompt: str = "", company_name: str = "", location_name: str = "", job_title: str = "") -> str:
        """Generiert einen Midjourney Prompt mit intelligenter Stellentitel-Analyse für bessere Personen-Generierung"""
        
        try:
            # Stellentitel analysieren und passende Personen-Beschreibung generieren
            job_specific_description = self._analyze_job_title(job_title)
            
            # Basis-Prompt aus dem Szenario holen
            scenario_prompts = self._get_scenario_prompts(company_name, location_name)
            base_prompt = random.choice(scenario_prompts.get(scenario_type, scenario_prompts["workplace"]))
            
            # Stellentitel-spezifische Beschreibung integrieren
            if job_specific_description:
                # Ersetze generische "healthcare professionals" mit spezifischer Beschreibung
                base_prompt = base_prompt.replace("healthcare professionals", job_specific_description)
                base_prompt = base_prompt.replace("healthcare professional", job_specific_description)
            
            # Zusätzliche kreative Adjektive und Variationen hinzufügen
            creative_enhancements = [
                "cinematic composition, professional color grading, premium quality",
                "artistic framing, sophisticated lighting, exceptional clarity",
                "dynamic perspective, creative composition, outstanding resolution",
                "masterful photography, elegant styling, superior craftsmanship",
                "innovative approach, contemporary aesthetic, premium execution"
            ]
            
            # Zufällige kreative Verbesserung auswählen
            creative_enhancement = random.choice(creative_enhancements)
            
            # Benutzerdefinierte Eingabe hinzufügen
            if custom_prompt.strip():
                final_prompt = f"{base_prompt}, {custom_prompt}, {creative_enhancement}"
            else:
                final_prompt = f"{base_prompt}, {creative_enhancement}"
            
            # Prompt validieren und korrigieren
            final_prompt = self._validate_and_correct_prompt(final_prompt)
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Job-spezifischen Prompt-Generierung: {str(e)}")
            # Fallback zur normalen Generierung
            return self.generate_motiv_prompt(scenario_type, custom_prompt, company_name, location_name)

    def _analyze_job_title(self, job_title: str) -> str:
        """Analysiert den Stellentitel und generiert passende Personen-Beschreibungen"""
        
        if not job_title or not job_title.strip():
            return "healthcare professionals"
        
        job_title_lower = job_title.lower().strip()
        
        # Pflege-Bereich
        if any(word in job_title_lower for word in ["pflege", "nurse", "krankenschwester", "krankenpfleger"]):
            if "intensiv" in job_title_lower or "icu" in job_title_lower:
                return "dedicated intensive care nurses in professional scrubs"
            elif "ambulant" in job_title_lower or "ambulatory" in job_title_lower:
                return "compassionate ambulatory care nurses in modern uniforms"
            elif "stationär" in job_title_lower or "stationary" in job_title_lower:
                return "dedicated ward nurses in professional healthcare attire"
            else:
                return "skilled registered nurses in crisp medical uniforms"
        
        # Ärzte-Bereich
        elif any(word in job_title_lower for word in ["arzt", "doctor", "mediziner", "physician"]):
            if "chirurg" in job_title_lower or "surgeon" in job_title_lower:
                return "experienced surgeons in professional medical attire"
            elif "internist" in job_title_lower or "internist" in job_title_lower:
                return "knowledgeable internists in professional medical clothing"
            elif "anästhesist" in job_title_lower or "anesthesiologist" in job_title_lower:
                return "skilled anesthesiologists in professional medical wear"
            else:
                return "dedicated physicians in professional medical attire"
        
        # Therapeuten-Bereich
        elif any(word in job_title_lower for word in ["therapeut", "therapist", "physio", "ergo"]):
            if "physio" in job_title_lower:
                return "skilled physical therapists in professional athletic wear"
            elif "ergo" in job_title_lower or "occupational" in job_title_lower:
                return "dedicated occupational therapists in professional attire"
            elif "psycho" in job_title_lower:
                return "compassionate psychotherapists in professional clothing"
            else:
                return "dedicated therapists in professional healthcare attire"
        
        # Verwaltung/Management
        elif any(word in job_title_lower for word in ["verwaltung", "administration", "management", "leitung", "leitungskraft"]):
            return "professional healthcare administrators in business attire"
        
        # Technische Berufe
        elif any(word in job_title_lower for word in ["techniker", "technician", "labor", "radiologie", "radiology"]):
            if "labor" in job_title_lower:
                return "skilled laboratory technicians in professional lab coats"
            elif "radiologie" in job_title_lower or "radiology" in job_title_lower:
                return "experienced radiology technicians in professional medical attire"
            else:
                return "skilled medical technicians in professional uniforms"
        
        # Sozialarbeiter
        elif any(word in job_title_lower for word in ["sozial", "social", "berater", "counselor"]):
            return "compassionate social workers in professional business attire"
        
        # Fallback für unbekannte Berufe
        else:
            # Versuche, aus dem Stellentitel eine Beschreibung abzuleiten
            if "kraft" in job_title_lower or "assistent" in job_title_lower:
                return "dedicated healthcare professionals in professional uniforms"
            elif "fach" in job_title_lower:
                return "skilled healthcare specialists in professional attire"
            else:
                return "dedicated healthcare professionals in professional uniforms"

# Hilfsfunktion für einfache Verwendung
def generate_midjourney_motiv_prompt(scenario_type: str, custom_prompt: str = "", company_name: str = "", location_name: str = "") -> str:
    """Einfache Hilfsfunktion für Midjourney Motiv-Prompt-Generierung mit intelligenter Stellentitel-Analyse"""
    generator = MidjourneyMotivGenerator()
    return generator.generate_motiv_prompt(scenario_type, custom_prompt, company_name, location_name)

def generate_midjourney_motiv_prompt_with_job_analysis(scenario_type: str, custom_prompt: str = "", company_name: str = "", location_name: str = "", job_title: str = "") -> str:
    """Erweiterte Hilfsfunktion mit intelligenter Stellentitel-Analyse für bessere Personen-Generierung"""
    generator = MidjourneyMotivGenerator()
    return generator.generate_motiv_prompt_with_job_analysis(scenario_type, custom_prompt, company_name, location_name, job_title)
