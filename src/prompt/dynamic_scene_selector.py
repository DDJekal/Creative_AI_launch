"""
Dynamic Scene Selector - Multi-Scene-Builder für Premium Healthcare Creatives
Version: 1.0

Modulares System zur automatischen Szenenauswahl und strukturierten Prompt-Generierung
basierend auf 3-Layer-Architecture (Scene → Visual → Style)

Author: CreativeAI Pipeline Team
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicSceneSelector:
    """
    Klasse für dynamische Szenenauswahl und strukturierte Prompt-Generierung
    """
    
    def __init__(self, scene_library_path: str = "input_config/scene_library.yaml"):
        """
        Initialisiert den Scene Selector
        
        Args:
            scene_library_path: Pfad zur Scene Library YAML-Datei
        """
        self.scene_library_path = scene_library_path
        self.scene_library = self._load_scene_library()
        
    def _load_scene_library(self) -> Dict:
        """Lädt die Scene Library aus YAML-Datei"""
        try:
            if not os.path.exists(self.scene_library_path):
                logger.error(f"❌ Scene Library nicht gefunden: {self.scene_library_path}")
                return {}
                
            with open(self.scene_library_path, 'r', encoding='utf-8') as f:
                library = yaml.safe_load(f)
                
            logger.info(f"✅ Scene Library geladen: {len(library)} Szenarien verfügbar")
            return library
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Scene Library: {e}")
            return {}
    
    def get_available_scenes(self) -> List[str]:
        """Gibt Liste aller verfügbaren Scene-Types zurück"""
        return list(self.scene_library.keys())
    
    def get_scene_info(self, scene_type: str) -> Optional[Dict]:
        """
        Gibt Scene-Informationen für gegebenen Scene-Type zurück
        
        Args:
            scene_type: Scene-Type (z.B. 'pflege_interaktion')
            
        Returns:
            Dict mit Scene-Informationen oder None
        """
        return self.scene_library.get(scene_type)
    
    def load_scene_by_type(self, scene_type: str) -> Dict:
        """
        Lädt Scene-Konfiguration basierend auf Scene-Type
        
        Args:
            scene_type: Scene-Type (z.B. 'pflege_interaktion')
            
        Returns:
            Dict mit scene_layer, visual_layer, style_layer
        """
        try:
            # Scene-Info aus Library abrufen
            scene_info = self.scene_library.get(scene_type)
            if not scene_info:
                logger.warning(f"⚠️ Scene-Type nicht gefunden: {scene_type}")
                return self._get_fallback_scene()
            
            # YAML-Datei laden
            yaml_file = scene_info.get('yaml_file')
            if not yaml_file or not os.path.exists(yaml_file):
                logger.warning(f"⚠️ Scene YAML nicht gefunden: {yaml_file}")
                return self._get_fallback_scene()
            
            with open(yaml_file, 'r', encoding='utf-8') as f:
                scene_config = yaml.safe_load(f)
            
            logger.info(f"✅ Scene-Konfiguration geladen: {scene_type}")
            logger.info(f"   📄 YAML-Datei: {yaml_file}")
            
            return scene_config
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Scene: {e}")
            return self._get_fallback_scene()
    
    def _get_fallback_scene(self) -> Dict:
        """Fallback Scene-Konfiguration wenn normale Ladung fehlschlägt"""
        return {
            'scene_layer': {
                'primary_interaction': 'Professional healthcare worker in modern medical environment',
                'emotional_connection': 'Competent, caring, professional demeanor',
                'atmosphere': 'Professional healthcare workplace'
            },
            'visual_layer': {
                'lighting': 'Natural professional lighting',
                'environment': 'Modern healthcare facility',
                'depth': 'Professional background',
                'mood': 'Professional, competent atmosphere'
            },
            'style_layer': {
                'photography_type': 'Professional healthcare photography',
                'quality': 'High resolution, professional quality',
                'technical': 'Professional composition',
                'authenticity': 'Authentic workplace scene'
            }
        }
    
    def build_structured_prompt_from_scene(self, scene_dict: Dict, enable_gpt_quality: bool = False, user_context: str = "") -> str:
        """
        Generiert strukturierten 3-Layer-Prompt aus Scene-Konfiguration
        
        Args:
            scene_dict: Dictionary mit scene_layer, visual_layer, style_layer
            enable_gpt_quality: Aktiviert GPT-Qualitätsverbesserung als 4. Layer
            user_context: Zusätzlicher Kontext für GPT-Qualitätsverbesserung
            
        Returns:
            Strukturierter English Prompt im Format SCENE: ... VISUAL: ... STYLE: ... [QUALITY: ...]
        """
        try:
            # Layer-Daten extrahieren
            scene_data = scene_dict.get('scene_layer', {})
            visual_data = scene_dict.get('visual_layer', {})
            style_data = scene_dict.get('style_layer', {})
            
            # Scene Layer zusammenstellen
            scene_elements = [
                scene_data.get('primary_interaction', ''),
                scene_data.get('emotional_connection', ''),
                scene_data.get('atmosphere', '')
            ]
            scene_layer = ', '.join([elem for elem in scene_elements if elem])
            
            # Visual Layer zusammenstellen
            visual_elements = [
                visual_data.get('lighting', ''),
                visual_data.get('environment', ''),
                visual_data.get('depth', ''),
                visual_data.get('mood', '')
            ]
            visual_layer = ', '.join([elem for elem in visual_elements if elem])
            
            # Style Layer zusammenstellen
            style_elements = [
                style_data.get('photography_type', ''),
                style_data.get('quality', ''),
                style_data.get('technical', ''),
                style_data.get('authenticity', '')
            ]
            style_layer = ', '.join([elem for elem in style_elements if elem])
            
            # QUALITY Layer (4. Layer) - GPT-Qualitätsverbesserung
            quality_layer = ""
            if enable_gpt_quality:
                quality_layer = self._generate_gpt_quality_layer(
                    scene_layer, visual_layer, style_layer, user_context
                )
            
            # Strukturierten Prompt zusammenbauen
            if quality_layer:
                structured_prompt = f"""SCENE: {scene_layer}

VISUAL: {visual_layer}

STYLE: {style_layer}

QUALITY: {quality_layer}"""
            else:
                structured_prompt = f"""SCENE: {scene_layer}

VISUAL: {visual_layer}

STYLE: {style_layer}"""
            
            logger.info(f"✅ Strukturierter Prompt generiert: {len(structured_prompt)} Zeichen")
            if quality_layer:
                logger.info(f"🎯 GPT-Qualitätsverbesserung aktiviert: {len(quality_layer)} Zeichen")
            
            return structured_prompt
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Prompt-Generierung: {e}")
            return "SCENE: Professional healthcare scene\n\nVISUAL: Modern medical environment\n\nSTYLE: Professional photography"
    
    def _generate_gpt_quality_layer(self, scene_layer: str, visual_layer: str, style_layer: str, user_context: str = "") -> str:
        """
        Generiert GPT-Qualitätsverbesserung als 4. Layer
        
        Args:
            scene_layer: Scene Layer Inhalt
            visual_layer: Visual Layer Inhalt  
            style_layer: Style Layer Inhalt
            user_context: Zusätzlicher Benutzer-Kontext
            
        Returns:
            GPT-optimierter Quality Layer String
        """
        try:
            # Basis-Prompt für GPT-Qualitätsverbesserung
            base_prompt = f"""
            Du bist ein Experte für professionelle Bildgenerierung. Analysiere diese 3-Layer-Prompt-Struktur und verbessere sie:

            SCENE: {scene_layer}
            VISUAL: {visual_layer} 
            STYLE: {style_layer}

            Benutzer-Kontext: {user_context if user_context else 'Standard Healthcare Recruiting'}

            Aufgabe: Erstelle einen QUALITY Layer mit spezifischen Verbesserungsvorschlägen für:
            1. Komposition & Perspektive
            2. Beleuchtung & Atmosphäre  
            3. Technische Qualität
            4. Authentizität & Glaubwürdigkeit
            5. Markenintegration

            Format: Gib nur den QUALITY Layer Inhalt zurück, ohne "QUALITY:" Prefix.
            Maximale Länge: 200 Zeichen
            Sprache: Englisch
            Stil: Professionell, spezifisch, umsetzbar
            """
            
            # Hier würde der GPT-API-Call erfolgen
            # Für jetzt verwende ich eine intelligente Fallback-Logik
            quality_suggestions = self._generate_fallback_quality_suggestions(
                scene_layer, visual_layer, style_layer, user_context
            )
            
            return quality_suggestions
            
        except Exception as e:
            logger.error(f"❌ Fehler bei GPT-Qualitätsverbesserung: {e}")
            return self._generate_fallback_quality_suggestions(scene_layer, visual_layer, style_layer, user_context)
    
    def _generate_fallback_quality_suggestions(self, scene_layer: str, visual_layer: str, style_layer: str, user_context: str = "") -> str:
        """
        Fallback-Qualitätsverbesserung ohne GPT-API
        
        Args:
            scene_layer: Scene Layer Inhalt
            visual_layer: Visual Layer Inhalt
            style_layer: Style Layer Inhalt  
            user_context: Benutzer-Kontext
            
        Returns:
            Intelligente Fallback-Qualitätsvorschläge
        """
        quality_elements = []
        
        # Komposition & Perspektive
        if 'team' in scene_layer.lower() or 'group' in scene_layer.lower():
            quality_elements.append("rule of thirds composition")
        elif 'portrait' in style_layer.lower():
            quality_elements.append("close-up framing")
        else:
            quality_elements.append("balanced composition")
        
        # Beleuchtung & Atmosphäre
        if 'warm' in visual_layer.lower():
            quality_elements.append("soft natural lighting")
        elif 'dramatic' in visual_layer.lower():
            quality_elements.append("dramatic side lighting")
        else:
            quality_elements.append("professional studio lighting")
        
        # Technische Qualität
        if 'professional' in style_layer.lower():
            quality_elements.append("ultra-high resolution")
        else:
            quality_elements.append("high-quality photography")
        
        # Authentizität
        if 'healthcare' in user_context.lower() or 'medical' in scene_layer.lower():
            quality_elements.append("authentic medical environment")
        
        # Markenintegration
        if 'corporate' in style_layer.lower() or 'brand' in user_context.lower():
            quality_elements.append("subtle brand integration")
        
        return ', '.join(quality_elements[:4])  # Maximal 4 Elemente
    
    def search_scene_by_tag(self, tag: str) -> List[Tuple[str, Dict]]:
        """
        Sucht Szenen basierend auf Tags
        
        Args:
            tag: Tag zum Suchen (z.B. 'team', 'emotion')
            
        Returns:
            Liste von (scene_type, scene_info) Tupeln
        """
        matching_scenes = []
        
        for scene_type, scene_info in self.scene_library.items():
            scene_tags = scene_info.get('tags', [])
            if tag.lower() in [t.lower() for t in scene_tags]:
                matching_scenes.append((scene_type, scene_info))
        
        logger.info(f"🔍 Tag-Suche '{tag}': {len(matching_scenes)} Treffer gefunden")
        
        return matching_scenes
    
    def get_scene_suggestions(self, user_input: str) -> List[str]:
        """
        Schlägt passende Scene-Types basierend auf User-Input vor
        
        Args:
            user_input: User-Input String
            
        Returns:
            Liste von empfohlenen Scene-Types
        """
        suggestions = []
        user_words = user_input.lower().split()
        
        for scene_type, scene_info in self.scene_library.items():
            # Prüfe Tags
            scene_tags = [tag.lower() for tag in scene_info.get('tags', [])]
            # Prüfe Description
            description = scene_info.get('description', '').lower()
            
            # Score berechnen
            score = 0
            for word in user_words:
                if word in scene_tags:
                    score += 2  # Tags haben höhere Gewichtung
                if word in description:
                    score += 1
            
            if score > 0:
                suggestions.append((scene_type, score))
        
        # Nach Score sortieren
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return [scene_type for scene_type, score in suggestions]


# Convenience-Funktionen
def load_scene_by_type(scene_type: str) -> Dict:
    """
    Convenience-Funktion: Lädt Scene-Konfiguration basierend auf Scene-Type
    
    Args:
        scene_type: Scene-Type (z.B. 'pflege_interaktion')
        
    Returns:
        Dict mit scene_layer, visual_layer, style_layer
    """
    selector = DynamicSceneSelector()
    return selector.load_scene_by_type(scene_type)


def build_structured_prompt_from_scene(scene_dict: Dict, enable_gpt_quality: bool = False, user_context: str = "") -> str:
    """
    Convenience-Funktion: Generiert strukturierten Prompt aus Scene-Dict
    
    Args:
        scene_dict: Dictionary mit scene_layer, visual_layer, style_layer
        enable_gpt_quality: Aktiviert GPT-Qualitätsverbesserung als 4. Layer
        user_context: Zusätzlicher Kontext für GPT-Qualitätsverbesserung
        
    Returns:
        Strukturierter English Prompt
    """
    selector = DynamicSceneSelector()
    return selector.build_structured_prompt_from_scene(scene_dict, enable_gpt_quality, user_context)


def test_scene_selection():
    """
    Test-Funktion für Scene Selection und Prompt-Generierung
    """
    print("🧪 DYNAMIC SCENE SELECTOR - TESTING")
    print("=" * 60)
    
    # Scene Selector initialisieren
    selector = DynamicSceneSelector()
    
    # Verfügbare Szenen anzeigen
    available_scenes = selector.get_available_scenes()
    print(f"📋 Verfügbare Szenen: {len(available_scenes)}")
    for scene in available_scenes:
        info = selector.get_scene_info(scene)
        print(f"   • {scene}: {info.get('description', 'Keine Beschreibung')}")
    
    print("\n" + "=" * 60)
    
    # Test Scene: pflege_interaktion
    test_scene = 'pflege_interaktion'
    print(f"🎯 Test Scene: {test_scene}")
    
    # Scene laden
    scene_config = selector.load_scene_by_type(test_scene)
    
    # Scene-Info anzeigen
    scene_info = selector.get_scene_info(test_scene)
    if scene_info:
        print(f"   📄 YAML-Datei: {scene_info.get('yaml_file')}")
        print(f"   🏷️ Tags: {scene_info.get('tags')}")
        print(f"   📝 Beschreibung: {scene_info.get('description')}")
    
    # Strukturierten Prompt generieren
    structured_prompt = selector.build_structured_prompt_from_scene(scene_config)
    
    print(f"\n📋 GENERIERTER 3-LAYER-PROMPT:")
    print("-" * 60)
    print(structured_prompt)
    print("-" * 60)
    
    # Tag-Suche testen
    print(f"\n🔍 TAG-SUCHE TEST: 'team'")
    team_scenes = selector.search_scene_by_tag('team')
    for scene_type, scene_info in team_scenes:
        print(f"   • {scene_type}: {scene_info.get('description')}")
    
    print(f"\n✅ SCENE SELECTOR TEST ABGESCHLOSSEN")
    
    return structured_prompt


if __name__ == "__main__":
    # Testing ausführen
    test_scene_selection() 