#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gpt5_image_generator.py

🤖 GPT-5 Bildgenerierung für CreativeAI
📊 Optimiert für Pflege-Recruiting mit automatischer Prompt-Optimierung
🎨 Unterstützt verschiedene Stile und Qualitätsstufen
"""

import os
import base64
from typing import Dict, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class GPT5ImageGenerator:
    """GPT-5 basierter Bildgenerator für CreativeAI"""
    
    def __init__(self):
        self.client = OpenAI()
        
        # GPT-5 Stil-Templates
        self.style_templates = {
            "realistisch": {
                "name": "Realistisch",
                "description": "Fotorealistische Darstellung",
                "prompt_addition": "realistic, photorealistic, high detail",
                "negative_prompt": "cartoon, illustration, painting, drawing"
            },
            "künstlerisch": {
                "name": "Künstlerisch",
                "description": "Kreative, künstlerische Darstellung",
                "prompt_addition": "artistic, creative, stylized, artistic composition",
                "negative_prompt": "photographic, realistic, documentary"
            },
            "fotografisch": {
                "name": "Fotografisch",
                "description": "Professionelle Fotografie",
                "prompt_addition": "professional photography, high quality photo, sharp focus",
                "negative_prompt": "painting, drawing, illustration, blurry"
            },
            "illustrativ": {
                "name": "Illustrativ",
                "description": "Moderne Illustration",
                "prompt_addition": "modern illustration, clean design, vector style",
                "negative_prompt": "photography, realistic, 3d render"
            },
            "cinematisch": {
                "name": "Cinematisch",
                "description": "Filmische Darstellung",
                "prompt_addition": "cinematic, movie still, dramatic lighting, film grain",
                "negative_prompt": "photography, illustration, flat design"
            }
        }
        
        # Qualitätsstufen
        self.quality_levels = {
            "standard": {"detail": "standard detail", "resolution": "standard"},
            "hoch": {"detail": "high detail", "resolution": "high resolution"},
            "sehr_hoch": {"detail": "ultra high detail", "resolution": "ultra high resolution"}
        }
        
        # Seitenverhältnisse
        self.aspect_ratios = {
            "1:1": {"width": 1024, "height": 1024},
            "16:9": {"width": 1792, "height": 1024},
            "9:16": {"width": 1024, "height": 1792},
            "4:3": {"width": 1365, "height": 1024},
            "3:4": {"width": 1024, "height": 1365}
        }
    
    def generate_image(self, 
                      prompt: str,
                      style: str = "realistisch",
                      quality: str = "standard",
                      aspect_ratio: str = "1:1",
                      size: str = "1024x1024") -> Tuple[bytes, Dict[str, Any]]:
        """
        Generiert ein Bild mit GPT-5
        
        Args:
            prompt: Basis-Prompt für die Bildgenerierung
            style: Stil der Bildgenerierung
            quality: Qualitätsstufe
            aspect_ratio: Seitenverhältnis
            size: Bildgröße
            
        Returns:
            Tuple aus Bilddaten (bytes) und Metadaten (Dict)
        """
        
        try:
            # Stil-Template extrahieren
            style_template = self.style_templates.get(style, self.style_templates["realistisch"])
            quality_config = self.quality_levels.get(quality, self.quality_levels["standard"])
            
            # Prompt optimieren
            optimized_prompt = self._optimize_prompt(prompt, style_template, quality_config)
            
            # GPT-5 Bildgenerierung
            response = self.client.images.generate(
                model="gpt-5",
                prompt=optimized_prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            # Bilddaten extrahieren
            image_url = response.data[0].url
            image_data = self._download_image(image_url)
            
            # Metadaten sammeln
            metadata = {
                "prompt": optimized_prompt,
                "style": style,
                "quality": quality,
                "aspect_ratio": aspect_ratio,
                "size": size,
                "model": "gpt-5",
                "generation_time": "real-time"
            }
            
            return image_data, metadata
            
        except Exception as e:
            st.error(f"❌ GPT-5 Bildgenerierung fehlgeschlagen: {str(e)}")
            return None, {"error": str(e)}
    
    def _optimize_prompt(self, base_prompt: str, style_template: Dict, quality_config: Dict) -> str:
        """Optimiert den Prompt für GPT-5 Bildgenerierung"""
        
        # Basis-Prompt bereinigen
        clean_prompt = base_prompt.replace("--ar", "").replace("--q", "").replace("--style", "").replace("--no", "")
        
        # Stil-spezifische Ergänzungen
        style_addition = style_template["prompt_addition"]
        quality_addition = quality_config["detail"]
        
        # Finalen Prompt zusammenbauen
        optimized_prompt = f"{clean_prompt}, {style_addition}, {quality_addition}"
        
        # Prompt auf maximale Länge beschränken
        if len(optimized_prompt) > 1000:
            optimized_prompt = optimized_prompt[:1000] + "..."
        
        return optimized_prompt
    
    def _download_image(self, image_url: str) -> bytes:
        """Lädt ein Bild von einer URL herunter"""
        import requests
        
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"❌ Fehler beim Herunterladen des Bildes: {str(e)}")
            return None

# Hilfsfunktion für einfache Verwendung
def generate_gpt5_image(prompt: str, style: str = "realistisch", quality: str = "standard", 
                       aspect_ratio: str = "1:1", size: str = "1024x1024") -> Tuple[bytes, Dict[str, Any]]:
    """Einfache Hilfsfunktion für GPT-5 Bildgenerierung"""
    generator = GPT5ImageGenerator()
    return generator.generate_image(prompt, style, quality, aspect_ratio, size)
