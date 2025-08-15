#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_creative_generator.py

🎨 VERBESSERTER CREATIVE GENERATOR
Basiert auf creative_core Prinzipien aber nutzt Multi-Prompt-System Output

PHILOSOPHIE:
- Einfach & zuverlässig wie creative_core
- Direkte OpenAI API-Calls
- Fokus auf Ergebnisse statt Komplexität
- Ein Bild, maximale Qualität

WORKFLOW:
1. Nimmt Multi-Prompt DALL-E Prompt
2. Direkter DALL-E 3 API-Call (wie creative_core)
3. Bild downloaden & speichern
4. Fertig!
"""

import os
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import base64
from io import BytesIO
from PIL import Image
import json
import uuid

# OpenAI
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utils
from utils.gpt_utils import optimize_prompt_with_gpt4

class EnhancedCreativeGenerator:
    """
    🎨 VERBESSERTER CREATIVE GENERATOR
    
    Inspiriert von creative_core, aber für Multi-Prompt-System optimiert.
    Fokus auf Einfachheit, Zuverlässigkeit und Qualität.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.output_dir = self.project_root / "outputs" / "generated_creatives"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenAI Setup (wie creative_core)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY nicht gefunden in Umgebungsvariablen")
        
        # DALL-E 3 Settings (optimiert wie creative_core)
        self.dalle_settings = {
            'model': 'dall-e-3',
            'size': '1792x1024',  # Landscape format für Creative-Ads
            'quality': 'hd',      # Höchste Qualität
            'style': 'natural',   # Fotorealistisch
            'n': 1                # Ein Bild
        }
        
        # API Endpoint (wie creative_core)
        self.openai_img_endpoint = "https://api.openai.com/v1/images/generations"
        
        logger.info("🎨 Enhanced Creative Generator initialisiert")
        logger.info(f"   📂 Output: {self.output_dir}")
        logger.info(f"   🖼️ Format: {self.dalle_settings['size']}")
        logger.info(f"   ⚡ Qualität: {self.dalle_settings['quality']}")
        logger.info("   🚀 Basiert auf creative_core Prinzipien")
    
    def generate_creative_from_prompt(
        self, 
        dalle_prompt: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        🎯 HAUPT-FUNKTION: Generiert Creative aus DALL-E Prompt
        
        Args:
            dalle_prompt: DALL-E Prompt aus Multi-Prompt-System
            metadata: Zusätzliche Metadaten für Dateibenennung
            
        Returns:
            Dict mit Bild-Info und Status
        """
        start_time = datetime.now()
        timestamp = start_time.strftime('%Y%m%d_%H%M%S')
        
        logger.info("🎨 STARTE ENHANCED CREATIVE GENERATION")
        logger.info(f"   📝 Prompt-Länge: {len(dalle_prompt)} Zeichen")
        logger.info(f"   ⏰ Timestamp: {timestamp}")
        
        try:
            # 1. PROMPT OPTIMIERUNG (minimal, nur Längen-Check)
            optimized_prompt = self._optimize_prompt(dalle_prompt)
            
            # 2. DALL-E 3 API CALL (direkt wie creative_core)
            logger.info("🚀 Direkte DALL-E 3 API-Anfrage...")
            response_data = self._call_dalle_api(optimized_prompt)
            
            # 3. BILD DOWNLOADEN & SPEICHERN
            logger.info("💾 Bild herunterladen und speichern...")
            image_path = self._download_and_save_image(response_data, timestamp, metadata)
            
            # 4. METADATEN ERSTELLEN
            result = {
                'success': True,
                'image_path': str(image_path),
                'image_url': response_data.get('url'),
                'revised_prompt': response_data.get('revised_prompt'),
                'timestamp': timestamp,
                'prompt_used': optimized_prompt,
                'dalle_settings': self.dalle_settings.copy(),
                'generation_time': (datetime.now() - start_time).total_seconds(),
                'metadata': metadata or {},
                'method': 'enhanced_creative_generator'
            }
            
            # 5. METADATEN SPEICHERN
            self._save_generation_metadata(result, timestamp)
            
            logger.info("🎉 CREATIVE ERFOLGREICH GENERIERT")
            logger.info(f"   📁 Gespeichert: {image_path.name}")
            logger.info(f"   ⏱️ Zeit: {result['generation_time']:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced Creative Generation fehlgeschlagen: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': timestamp,
                'prompt_used': dalle_prompt,
                'generation_time': (datetime.now() - start_time).total_seconds(),
                'method': 'enhanced_creative_generator'
            }
    
    def _optimize_prompt(self, prompt: str) -> str:
        """
        Optimiert den Prompt zuerst mit GPT-4 (DALL-E-Optimierung), dann ggf. Längenkürzung.
        """
        logger.info(f"🔧 Starte Prompt-Optimierung: {len(prompt)} Zeichen")
        
        # 1. GPT-4 Optimierung (IMMER anwenden)
        try:
            logger.info("🤖 Wende GPT-4 Optimierung an...")
            optimized = optimize_prompt_with_gpt4(prompt)
            if optimized != prompt:
                logger.info(f"🤖 Prompt wurde mit GPT-4 optimiert: {len(prompt)} → {len(optimized)} Zeichen")
            else:
                logger.info("ℹ️ GPT-4 Optimierung brachte keine Änderung oder war nicht möglich.")
        except Exception as e:
            logger.error(f"❌ Fehler bei GPT-4 Optimierung: {e}")
            optimized = prompt

        # 2. Längenkontrolle (nach GPT-4 Optimierung)
        max_length = 4000
        if len(optimized) <= max_length:
            logger.info(f"✅ Prompt-Länge optimal nach GPT-4: {len(optimized)} Zeichen")
            return optimized
            
        logger.warning(f"⚠️ Prompt nach GPT-4 immer noch zu lang ({len(optimized)} > {max_length}), kürze intelligent...")
        
        # Intelligentes Kürzen nach GPT-4 Optimierung
        sections = optimized.split('\n')
        kept_sections = []
        current_length = 0
        
        # Priorisierte Keywords für wichtige Abschnitte
        priority_keywords = [
            'CANVAS STRUCTURE', 'MOTIV BESCHREIBUNG', 'TEXT-LAYOUT',
            'QUALITÄTS-ANFORDERUNGEN', 'Corporate Design'
        ]
        
        # 1. Wichtige Abschnitte zuerst
        for section in sections:
            if any(keyword in section for keyword in priority_keywords):
                if current_length + len(section) + 1 < max_length - 200:  # Puffer
                    kept_sections.append(section)
                    current_length += len(section) + 1
        
        # 2. Fülle mit restlichen Abschnitten auf
        for section in sections:
            if section not in kept_sections and section.strip():
                if current_length + len(section) + 1 < max_length - 50:
                    kept_sections.append(section)
                    current_length += len(section) + 1
                else:
                    break
        
        optimized_final = '\n'.join(kept_sections)
        logger.info(f"✂️ Prompt nach GPT-4 gekürzt: {len(optimized)} → {len(optimized_final)} chars")
        
        return optimized_final
    
    def _call_dalle_api(self, prompt: str) -> Dict[str, Any]:
        """
        Direkter DALL-E 3 API-Call (wie creative_core)
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.dalle_settings['model'],
            "prompt": prompt,
            "size": self.dalle_settings['size'],
            "quality": self.dalle_settings['quality'],
            "style": self.dalle_settings['style'],
            "n": self.dalle_settings['n']
        }
        
        logger.info(f"🌐 API-Call an {self.openai_img_endpoint}")
        logger.info(f"   📦 Payload: {payload['model']}, {payload['size']}, {payload['quality']}")
        
        try:
            response = requests.post(
                self.openai_img_endpoint, 
                json=payload, 
                headers=headers, 
                timeout=180  # 3 Minuten Timeout
            )
            
            # Status prüfen
            response.raise_for_status()
            
            # JSON parsen
            data = response.json()
            
            # OpenAI-spezifische Fehler prüfen
            if "error" in data:
                raise RuntimeError(f"OpenAI API Fehler: {data['error']['message']}")
            
            # Bild-Daten extrahieren
            if not data.get("data") or len(data["data"]) == 0:
                raise RuntimeError("Keine Bild-Daten in API-Antwort")
            
            image_data = data["data"][0]
            
            # URL oder Base64 extrahieren
            if "url" in image_data:
                result = {
                    'url': image_data["url"],
                    'revised_prompt': image_data.get('revised_prompt', prompt)
                }
                logger.info("✅ Bild-URL erfolgreich erhalten")
                return result
            elif "b64_json" in image_data:
                result = {
                    'b64_json': image_data["b64_json"],
                    'revised_prompt': image_data.get('revised_prompt', prompt)
                }
                logger.info("✅ Base64-Bild erfolgreich erhalten")
                return result
            else:
                raise RuntimeError("Weder URL noch Base64-Daten in API-Antwort")
                
        except requests.HTTPError as e:
            # Detaillierte HTTP-Fehler
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"❌ HTTP-Fehler: {error_msg}")
            raise RuntimeError(f"API-Anfrage fehlgeschlagen: {error_msg}")
        
        except requests.RequestException as e:
            # Netzwerk-Fehler
            logger.error(f"❌ Netzwerk-Fehler: {e}")
            raise RuntimeError(f"Netzwerk-Problem: {str(e)}")
        
        except Exception as e:
            # Sonstige Fehler
            logger.error(f"❌ API-Call Fehler: {e}")
            raise
    
    def _download_and_save_image(
        self, 
        response_data: Dict[str, Any], 
        timestamp: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Lädt Bild herunter und speichert es (wie creative_core)
        """
        
        # Dateiname generieren
        if metadata and 'company' in metadata:
            company_safe = "".join(c for c in metadata['company'] if c.isalnum() or c in (' ', '_', '-')).strip()
            company_safe = company_safe.replace(' ', '_')[:20]
            filename = f"enhanced_creative_{company_safe}_{timestamp}.png"
        else:
            filename = f"enhanced_creative_{timestamp}.png"
        
        image_path = self.output_dir / filename
        
        try:
            # Bild-Daten erhalten
            if 'url' in response_data:
                # Von URL herunterladen
                logger.info("🌐 Lade Bild von URL herunter...")
                img_response = requests.get(response_data['url'], timeout=60)
                img_response.raise_for_status()
                image_data = img_response.content
                
            elif 'b64_json' in response_data:
                # Base64 dekodieren
                logger.info("🔓 Dekodiere Base64-Bild...")
                image_data = base64.b64decode(response_data['b64_json'])
                
            else:
                raise ValueError("Keine Bild-Daten verfügbar")
            
            # Als PIL Image verarbeiten
            image = Image.open(BytesIO(image_data))
            
            # In hoher Qualität speichern (wie creative_core)
            image.save(
                image_path, 
                'PNG', 
                optimize=True, 
                compress_level=1  # Minimale Kompression
            )
            
            # Statistiken
            file_size_kb = image_path.stat().st_size / 1024
            
            logger.info(f"✅ Bild gespeichert: {filename}")
            logger.info(f"   📐 Größe: {image.size[0]}x{image.size[1]} px")
            logger.info(f"   📦 Dateigröße: {file_size_kb:.1f} KB")
            
            return image_path
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern: {e}")
            raise RuntimeError(f"Bild-Download fehlgeschlagen: {str(e)}")
    
    def _save_generation_metadata(self, result: Dict[str, Any], timestamp: str):
        """
        Speichert Metadaten (wie creative_core aber vereinfacht)
        """
        metadata_file = self.output_dir / f"enhanced_creative_log_{timestamp}.json"
        
        try:
            # Vereinfachte Metadaten (nur das Wichtigste)
            metadata = {
                'timestamp': timestamp,
                'method': 'enhanced_creative_generator',
                'success': result['success'],
                'image_path': result.get('image_path'),
                'prompt_length': len(result.get('prompt_used', '')),
                'generation_time': result.get('generation_time'),
                'dalle_settings': result.get('dalle_settings'),
                'metadata': result.get('metadata', {})
            }
            
            # Nur bei Erfolg zusätzliche Daten
            if result['success']:
                metadata.update({
                    'image_url': result.get('image_url'),
                    'revised_prompt': result.get('revised_prompt'),
                    'file_exists': Path(result['image_path']).exists() if result.get('image_path') else False
                })
            else:
                metadata['error'] = result.get('error')
            
            # JSON speichern
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Metadaten gespeichert: {metadata_file.name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Metadaten-Speicherung fehlgeschlagen: {e}")
            # Nicht kritisch - Generation war erfolgreich
    
    def get_recent_creatives(self, limit: int = 10) -> list:
        """
        Gibt die letzten generierten Creatives zurück
        """
        try:
            # Alle Enhanced Creative Dateien
            image_files = list(self.output_dir.glob("enhanced_creative_*.png"))
            
            # Nach Erstellungszeit sortieren
            image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return [str(f) for f in image_files[:limit]]
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der Creatives: {e}")
            return []

# =====================================
# FACTORY FUNCTION & INTEGRATION
# =====================================

def create_enhanced_creative_generator(project_root: Optional[Path] = None) -> EnhancedCreativeGenerator:
    """Factory-Funktion für Enhanced Creative Generator"""
    return EnhancedCreativeGenerator(project_root)

def generate_creative_from_multiprompt_result(
    multiprompt_result, 
    project_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Quick-Function: Generiert Creative aus Multi-Prompt-System Ergebnis
    
    Args:
        multiprompt_result: Ergebnis vom Multi-Prompt-System (FinalizedPrompts)
        project_root: Projekt-Root-Pfad
        
    Returns:
        Generation-Ergebnis
    """
    generator = create_enhanced_creative_generator(project_root)
    
    # Metadaten aus Multi-Prompt-Ergebnis extrahieren
    metadata = {
        'layout_id': multiprompt_result.layout_data.structured_input.layout_id,
        'company': multiprompt_result.layout_data.structured_input.company,
        'headline': multiprompt_result.layout_data.structured_input.headline,
        'timestamp': multiprompt_result.layout_data.structured_input.timestamp,
        'quality_score': multiprompt_result.quality_assessment.get('overall_score', 0),
        'source': 'multi_prompt_system'
    }
    
    # Verwende das cinematische Prompt falls verfügbar, sonst den ursprünglichen DALL-E Prompt
    if hasattr(multiprompt_result, 'cinematic_prompt') and multiprompt_result.cinematic_prompt:
        prompt_to_use = multiprompt_result.cinematic_prompt.full_prompt
        prompt_type = "cinematic"
        logger.info(f"🎭 Verwende Cinematic Prompt: {len(prompt_to_use)} Zeichen")
    else:
        prompt_to_use = multiprompt_result.dalle_prompt
        prompt_type = "dalle"
        logger.info(f"🏗️ Verwende DALL-E Prompt: {len(prompt_to_use)} Zeichen")
    
    # Metadaten erweitern
    metadata['prompt_type'] = prompt_type
    metadata['cinematic_reduction'] = None
    if prompt_type == "cinematic":
        reduction = round((1 - len(prompt_to_use) / len(multiprompt_result.dalle_prompt)) * 100, 1)
        metadata['cinematic_reduction'] = reduction
    
    return generator.generate_creative_from_prompt(
        prompt_to_use, 
        metadata
    )

# =====================================
# TEST & DEBUG
# =====================================

if __name__ == "__main__":
    # Test des Enhanced Creative Generators
    print("🧪 ENHANCED CREATIVE GENERATOR TEST")
    print("=" * 50)
    
    test_prompt = """
    — CANVAS STRUCTURE: Professional Split Layout —
    Canvas: 1792x1024px, modern corporate design
    
    — TEXT-LAYOUT-BEREICHE —
    • HEADLINE-BEREICH: "Werden Sie Teil unseres Teams!" als sichtbare Farbfläche
    • COMPANY-BEREICH: "TechMed Solutions" als Layout-Zone
    • CTA-BEREICH: "Jetzt bewerben!" als Akzent-Element
    
    — MOTIV BESCHREIBUNG —
    Professional healthcare worker in modern clinic environment, 
    confident expression, natural lighting, medium shot composition
    
    — QUALITÄTS-ANFORDERUNGEN —
    • Bildqualität: Hochauflösend, professionelle Fotografie
    • Corporate Standard: Recruiting-Kampagne Qualität
    • Farbharmonie: Blau-basierte Corporate Identity
    """
    
    test_metadata = {
        'company': 'TechMed Solutions',
        'layout': 'test_layout',
        'source': 'test'
    }
    
    try:
        generator = create_enhanced_creative_generator()
        result = generator.generate_creative_from_prompt(test_prompt, test_metadata)
        
        if result['success']:
            print(f"✅ TEST ERFOLGREICH!")
            print(f"   📁 Bild: {result['image_path']}")
            print(f"   ⏱️ Zeit: {result['generation_time']:.2f}s")
            print(f"   📝 Prompt: {len(result['prompt_used'])} chars")
        else:
            print(f"❌ TEST FEHLGESCHLAGEN: {result['error']}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()