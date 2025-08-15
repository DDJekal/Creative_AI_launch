#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ki_creative_text_generator.py

🤖 KI-gestützte Generierung von Headlines und Sublines
🎯 Generiert kreative Texte aus minimalen Eingaben mit GPT-5
😊 Gefühls-basierte Stil-Steuerung für konsistente Kreativität
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CreativeTextInput:
    """Eingabedaten für die KI-gestützte Textgenerierung"""
    company: str
    job_title: str
    cta: str
    benefits: List[str]
    feeling: str
    location: Optional[str] = None

@dataclass
class GeneratedTexts:
    """Generierte Texte von der KI"""
    headline: str
    subline: str
    success: bool
    error_message: Optional[str] = None

class KICreativeTextGenerator:
    """KI-gestützte Generierung von kreativen Headlines und Sublines"""
    
    def __init__(self):
        self.feeling_styles = {
            "heroisch": {
                "description": "Kraftvoll, selbstbewusst, inspirierend",
                "examples": ["Wir, weil wer sonst", "Die Zukunft wartet auf uns", "Exzellenz ist unser Standard"],
                "tone": "selbstbewusst und motivierend"
            },
            "motivierend": {
                "description": "Energisch, aufbauend, zielgerichtet",
                "examples": ["Dein Potential. Unsere Mission.", "Gemeinsam schaffen wir das Unmögliche", "Jeder Tag ist eine neue Chance"],
                "tone": "energisch und aufbauend"
            },
            "einladend": {
                "description": "Warm, offen, einladend",
                "examples": ["Komm zu uns", "Wir freuen uns auf dich", "Werde Teil unserer Geschichte"],
                "tone": "warm und einladend"
            },
            "inspirierend": {
                "description": "Visionär, bewegend, transformativ",
                "examples": ["Verändere Leben. Beginne mit deinem.", "Neue Wege, neue Lösungen", "Die Zukunft gestalten"],
                "tone": "visionär und bewegend"
            },
            "stolz": {
                "description": "Stolz, professionell, exklusiv",
                "examples": ["Exzellenz ist unser Standard", "Wir sind stolz auf unser Team", "Qualität hat einen Namen"],
                "tone": "stolz und professionell"
            },
            "innovativ": {
                "description": "Modern, fortschrittlich, zukunftsweisend",
                "examples": ["Die Zukunft gestalten", "Neue Wege, neue Lösungen", "Innovation lebt hier"],
                "tone": "modern und fortschrittlich"
            },
            "empathisch": {
                "description": "Menschlich, fürsorglich, verständnisvoll",
                "examples": ["Menschlichkeit im Mittelpunkt", "Wir kümmern uns um dich", "Jeder Mensch zählt"],
                "tone": "menschlich und fürsorglich"
            },
            "dynamisch": {
                "description": "Bewegt, lebendig, aktiv",
                "examples": ["Bewegung schafft Wandel", "Gemeinsam vorwärts", "Leben ist Bewegung"],
                "tone": "dynamisch und lebendig"
            }
        }
    
    def generate_creative_texts(self, input_data: CreativeTextInput) -> GeneratedTexts:
        """
        Generiert Headline und Subline basierend auf minimalen Eingaben
        
        Args:
            input_data: CreativeTextInput mit allen notwendigen Daten
            
        Returns:
            GeneratedTexts mit generierten Texten oder Fehlermeldung
        """
        try:
            logger.info(f"🤖 Starte KI-gestützte Textgenerierung für {input_data.company}")
            
            # Gefühls-Stil extrahieren
            feeling_style = self.feeling_styles.get(input_data.feeling.lower(), self.feeling_styles["motivierend"])
            
            # 1. HEADLINE generieren (einfach, direkt)
            if self._is_gpt5_available():
                headline = self._generate_headline_with_gpt(input_data, feeling_style)
            else:
                headline = self._generate_headline_fallback(input_data, feeling_style)
            
            # 2. SUBLINE mit Benefit-Emotion Workflow generieren
            subline = self._generate_subline_with_workflow(input_data, feeling_style)
            
            if headline and subline:
                logger.info(f"✅ KI-Textgenerierung erfolgreich: Headline='{headline}', Subline='{subline}'")
                return GeneratedTexts(
                    headline=headline,
                    subline=subline,
                    success=True
                )
            else:
                raise ValueError("KI konnte keine vollständigen Texte generieren")
                
        except Exception as e:
            logger.error(f"❌ Fehler bei der KI-Textgenerierung: {str(e)}")
            return GeneratedTexts(
                headline="",
                subline="",
                success=False,
                error_message=f"Fehler bei der Textgenerierung: {str(e)}"
            )
    
    def _is_gpt5_available(self) -> bool:
        """Prüft ob GPT-5 verfügbar ist"""
        try:
            from openai import OpenAI
            client = OpenAI()
            # Einfacher Test-Call
            response = client.chat.completions.create(
                model="gpt-4",  # Verwende GPT-4 als Fallback
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.warning(f"⚠️ GPT-5 nicht verfügbar: {str(e)}")
            return False
    
    def _generate_headline_with_gpt(self, input_data: CreativeTextInput, feeling_style: Dict) -> str:
        """Generiert Headline mit GPT"""
        try:
            from openai import OpenAI
            client = OpenAI()
            
            system_prompt = f"""Du bist ein kreativer Copywriter für Stellenausschreibungen und Employer Branding.

Deine Aufgabe: Erstelle eine HEADLINE basierend auf den gegebenen Informationen.

STIL: {feeling_style['description']}
TON: {feeling_style['tone']}
BEISPIELE: {', '.join(feeling_style['examples'])}

REGELN:
- HEADLINE: Kurz, prägnant, einprägsam (max. 8 Wörter)
- Verwende den gewählten Gefühls-Stil durchgängig
- Integriere das Unternehmen und den Stellentitel
- Mache es persönlich und ansprechend
- Verwende deutsche Sprache

Gib deine Antwort direkt zurück, ohne Formatierung."""

            user_prompt = f"""Unternehmen: {input_data.company}
Stellentitel: {input_data.job_title}
Call-to-Action: {input_data.cta}
Benefits: {', '.join(input_data.benefits)}
Standort: {input_data.location or 'Nicht angegeben'}
Gefühl: {input_data.feeling}

Erstelle eine {feeling_style['tone']} HEADLINE für diese Stellenausschreibung."""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,
                max_tokens=100
            )
            
            headline = response.choices[0].message.content.strip()
            return headline
            
        except Exception as e:
            logger.error(f"❌ GPT-Headline-Generierung fehlgeschlagen: {str(e)}")
            return self._generate_headline_fallback(input_data, feeling_style)
    
    def _generate_headline_fallback(self, input_data: CreativeTextInput, feeling_style: Dict) -> str:
        """Fallback: Regelbasierte Headline-Generierung"""
        import random
        
        # Gefühls-spezifische Headline-Templates
        templates = {
            "heroisch": [
                "Wir, weil wer sonst",
                "Die Zukunft wartet auf uns",
                "Exzellenz ist unser Standard",
                "Wir sind die Besten",
                "Dein Potential, unsere Mission"
            ],
            "motivierend": [
                "Dein Potential. Unsere Mission.",
                "Gemeinsam schaffen wir das Unmögliche",
                "Jeder Tag ist eine neue Chance",
                "Wir glauben an dich",
                "Deine Zukunft beginnt hier"
            ],
            "einladend": [
                "Komm zu uns",
                "Wir freuen uns auf dich",
                "Werde Teil unserer Geschichte",
                "Du fehlst uns noch",
                "Willkommen im Team"
            ]
        }
        
        # Standard-Templates falls Gefühl nicht gefunden
        default_templates = templates.get(input_data.feeling.lower(), templates["motivierend"])
        
        # Headline generieren
        headline_template = random.choice(default_templates)
        return headline_template
    
    def _generate_subline_with_workflow(self, input_data: CreativeTextInput, feeling_style: Dict) -> str:
        """Generiert Subline mit Benefit-Emotion Workflow"""
        try:
            # Benefit-Emotion Workflow importieren und ausführen
            try:
                from src.workflow.benefit_emotion_workflow import create_benefit_emotion_workflow
                
                workflow = create_benefit_emotion_workflow()
                result = workflow.run_workflow(
                    benefits=input_data.benefits,
                    feeling_style=input_data.feeling,
                    company=input_data.company,
                    job_title=input_data.job_title
                )
                
                if result.get('success') and result.get('final_subline'):
                    logger.info(f"✅ Benefit-Emotion Workflow erfolgreich: {result['final_subline']}")
                    return result['final_subline']
                else:
                    logger.warning(f"⚠️ Benefit-Emotion Workflow fehlgeschlagen: {result.get('error_message', 'Unbekannter Fehler')}")
                    # Fallback zur einfachen Subline-Generierung
                    return self._generate_subline_fallback(input_data, feeling_style)
                    
            except ImportError:
                logger.warning("⚠️ Benefit-Emotion Workflow nicht verfügbar - verwende Fallback")
                return self._generate_subline_fallback(input_data, feeling_style)
                
        except Exception as e:
            logger.error(f"❌ Fehler bei Subline-Workflow: {str(e)}")
            return self._generate_subline_fallback(input_data, feeling_style)
    
    def _generate_subline_fallback(self, input_data: CreativeTextInput, feeling_style: Dict) -> str:
        """Fallback: Regelbasierte Subline-Generierung"""
        import random
        
        # Gefühls-spezifische Subline-Templates
        templates = {
            "heroisch": [
                "Gestalte mit uns die Zukunft des {company}",
                "Bei uns wird jeder Tag zu einer Erfolgsgeschichte",
                "Wir suchen Menschen, die mehr als nur arbeiten wollen",
                "Gemeinsam erreichen wir das Unmögliche"
            ],
            "motivierend": [
                "Bei {company} wirst du Teil eines dynamischen Teams",
                "Wir bieten dir alle Möglichkeiten zur Entwicklung",
                "Deine Karriere verdient den besten Start",
                "Lass uns gemeinsam wachsen"
            ],
            "einladend": [
                "Bei {company} findest du deinen Platz",
                "Wir öffnen dir die Türen zu neuen Möglichkeiten",
                "Deine Talente sind bei uns willkommen",
                "Lass uns gemeinsam Großes schaffen"
            ]
        }
        
        # Standard-Templates falls Gefühl nicht gefunden
        default_templates = templates.get(input_data.feeling.lower(), templates["motivierend"])
        
        # Subline generieren
        subline_template = random.choice(default_templates)
        return subline_template.format(company=input_data.company)
    
    def get_available_feelings(self) -> Dict[str, Dict]:
        """Gibt alle verfügbaren Gefühls-Stile zurück"""
        return self.feeling_styles

# Factory-Funktion für einfache Verwendung
def create_ki_creative_text_generator() -> KICreativeTextGenerator:
    """Erstellt eine neue Instanz des KI Creative Text Generators"""
    return KICreativeTextGenerator()
