#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
langgraph_integration.py

🔗 Integration für LangGraph Quality Workflow
Verbindet Streamlit mit dem LangGraph Workflow für automatische Qualitätsverbesserung

FEATURES:
- Streamlit Integration
- Workflow Configuration
- Result Processing
- Error Handling
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json

# Local Imports
from src.workflow.langgraph_quality_workflow import run_quality_workflow
from src.image.enhanced_creative_generator import create_enhanced_creative_generator

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangGraphIntegration:
    """Integration für LangGraph Quality Workflow"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.output_dir = self.project_root / "outputs" / "langgraph_workflows"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔗 LangGraph Integration initialisiert")
        logger.info(f"   📂 Output: {self.output_dir}")
    
    def run_enhanced_workflow(
        self,
        streamlit_input: Dict[str, Any],
        enable_text_rendering: bool = False,
        target_quality_score: int = 85,
        max_attempts: int = 3,
        generate_image: bool = True
    ) -> Dict[str, Any]:
        """
        Führe erweiterten Workflow mit LangGraph aus
        
        Args:
            streamlit_input: Streamlit Input Data
            enable_text_rendering: Text-Rendering aktivieren
            target_quality_score: Ziel-Qualitäts-Score (0-100)
            max_attempts: Maximale Optimierungs-Versuche
            generate_image: Bild nach Workflow generieren
        
        Returns:
            Dict mit vollständigem Workflow-Ergebnis
        """
        logger.info("🚀 STARTE ERWEITERTEN LANGGRAPH WORKFLOW")
        logger.info(f"   🎯 Ziel-Score: {target_quality_score}/100")
        logger.info(f"   🔄 Max Attempts: {max_attempts}")
        logger.info(f"   🖼️ Bild-Generierung: {'AKTIVIERT' if generate_image else 'DEAKTIVIERT'}")
        
        workflow_start = datetime.now()
        
        try:
            # 1. LangGraph Quality Workflow ausführen
            logger.info("🧠 Schritt 1: LangGraph Quality Workflow")
            workflow_result = run_quality_workflow(
                streamlit_input=streamlit_input,
                enable_text_rendering=enable_text_rendering,
                target_quality_score=target_quality_score,
                max_attempts=max_attempts
            )
            
            # 2. Ergebnis verarbeiten
            if not workflow_result.get('success', False):
                logger.error(f"❌ LangGraph Workflow fehlgeschlagen: {workflow_result.get('error_message', 'Unknown error')}")
                return {
                    'success': False,
                    'error_message': workflow_result.get('error_message', 'LangGraph workflow failed'),
                    'workflow_result': workflow_result
                }
            
            # 3. Bild generieren (falls aktiviert)
            image_result = None
            if generate_image and workflow_result.get('final_prompt'):
                logger.info("🎨 Schritt 2: Bild-Generierung mit optimiertem Prompt")
                
                try:
                    # Enhanced Creative Generator initialisieren
                    enhanced_generator = create_enhanced_creative_generator(self.project_root)
                    
                    # Metadaten für Workflow-Integration
                    metadata = {
                        'workflow_type': 'langgraph_quality_workflow',
                        'workflow_id': workflow_result.get('workflow_id'),
                        'target_quality_score': target_quality_score,
                        'final_quality_score': workflow_result.get('final_quality_score'),
                        'attempts_used': workflow_result.get('attempts_used'),
                        'optimization_strategy': workflow_result.get('quality_history', [{}])[-1].get('strategy', 'unknown'),
                        'company': streamlit_input.get('unternehmen', 'Unknown'),
                        'headline': streamlit_input.get('headline', ''),
                        'layout': streamlit_input.get('layout_id', ''),
                        'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
                    }
                    
                    # Bild generieren
                    image_result = enhanced_generator.generate_creative_from_prompt(
                        workflow_result['final_prompt'],
                        metadata
                    )
                    
                    logger.info(f"✅ Bild erfolgreich generiert: {image_result.get('image_path', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"❌ Bild-Generierung fehlgeschlagen: {e}")
                    image_result = {
                        'success': False,
                        'error_message': str(e)
                    }
            
            # 4. Finales Ergebnis zusammenstellen
            final_result = {
                'success': True,
                'workflow_success': workflow_result.get('success', False),
                'image_success': image_result.get('success', False) if image_result else None,
                
                # Workflow-Daten
                'workflow_result': workflow_result,
                'final_quality_score': workflow_result.get('final_quality_score'),
                'target_quality_score': target_quality_score,
                'attempts_used': workflow_result.get('attempts_used'),
                'optimization_strategy': workflow_result.get('quality_history', [{}])[-1].get('strategy', 'unknown'),
                
                # Prompt-Daten
                'original_prompt': workflow_result.get('original_prompt'),
                'final_prompt': workflow_result.get('final_prompt'),
                'prompt_improvement': self._calculate_prompt_improvement(workflow_result),
                
                # Bild-Daten (falls generiert)
                'image_result': image_result,
                'image_path': image_result.get('image_path') if image_result else None,
                
                # Metadaten
                'workflow_id': workflow_result.get('workflow_id'),
                'processing_time': (datetime.now() - workflow_start).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
            # 5. Ergebnis speichern
            self._save_workflow_result(final_result)
            
            # 6. Erfolgs-Status loggen
            if final_result['workflow_success']:
                logger.info(f"🎉 ERWEITERTER WORKFLOW ERFOLGREICH")
                logger.info(f"   📊 Qualität: {final_result['final_quality_score']}/100 (Ziel: {target_quality_score})")
                logger.info(f"   🔄 Versuche: {final_result['attempts_used']}")
                logger.info(f"   ⏱️ Zeit: {final_result['processing_time']:.2f}s")
                if image_result and image_result.get('success'):
                    logger.info(f"   🖼️ Bild: {final_result['image_path']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ ERWEITERTER WORKFLOW FEHLGESCHLAGEN: {e}")
            return {
                'success': False,
                'error_message': str(e),
                'processing_time': (datetime.now() - workflow_start).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_prompt_improvement(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Berechne Prompt-Verbesserung"""
        original_prompt = workflow_result.get('original_prompt', '')
        final_prompt = workflow_result.get('final_prompt', '')
        quality_history = workflow_result.get('quality_history', [])
        
        if not original_prompt or not final_prompt:
            return {'improvement_percentage': 0, 'length_change': 0}
        
        # Längen-Verbesserung
        original_length = len(original_prompt)
        final_length = len(final_prompt)
        length_change = final_length - original_length
        
        # Qualitäts-Verbesserung
        if len(quality_history) >= 2:
            initial_score = quality_history[0].get('score', 0)
            final_score = quality_history[-1].get('score', 0)
            score_improvement = final_score - initial_score
        else:
            score_improvement = 0
        
        return {
            'length_change': length_change,
            'length_change_percentage': (length_change / original_length * 100) if original_length > 0 else 0,
            'score_improvement': score_improvement,
            'original_length': original_length,
            'final_length': final_length
        }
    
    def _save_workflow_result(self, result: Dict[str, Any]) -> None:
        """Speichere Workflow-Ergebnis"""
        try:
            workflow_id = result.get('workflow_id', f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # JSON-Datei speichern
            json_path = self.output_dir / f"{workflow_id}_result.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            # YAML-Summary speichern
            yaml_path = self.output_dir / f"{workflow_id}_summary.yaml"
            summary = {
                'workflow_id': result.get('workflow_id'),
                'success': result.get('success'),
                'workflow_success': result.get('workflow_success'),
                'image_success': result.get('image_success'),
                'final_quality_score': result.get('final_quality_score'),
                'target_quality_score': result.get('target_quality_score'),
                'attempts_used': result.get('attempts_used'),
                'optimization_strategy': result.get('optimization_strategy'),
                'processing_time': result.get('processing_time'),
                'timestamp': result.get('timestamp'),
                'prompt_improvement': result.get('prompt_improvement'),
                'image_path': result.get('image_path')
            }
            
            import yaml
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(summary, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"📋 Workflow-Ergebnis gespeichert: {json_path}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern des Workflow-Ergebnisses: {e}")

def create_langgraph_integration(project_root: Optional[Path] = None) -> LangGraphIntegration:
    """Factory-Funktion für LangGraph Integration"""
    return LangGraphIntegration(project_root)

def run_enhanced_workflow_from_streamlit(
    streamlit_input: Dict[str, Any],
    enable_text_rendering: bool = False,
    target_quality_score: int = 85,
    max_attempts: int = 3,
    generate_image: bool = True,
    project_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Bequeme Funktion für Streamlit-Integration
    
    Args:
        streamlit_input: Streamlit Input Data
        enable_text_rendering: Text-Rendering aktivieren
        target_quality_score: Ziel-Qualitäts-Score (0-100)
        max_attempts: Maximale Optimierungs-Versuche
        generate_image: Bild nach Workflow generieren
        project_root: Projekt-Root-Verzeichnis
    
    Returns:
        Dict mit vollständigem Workflow-Ergebnis
    """
    integration = create_langgraph_integration(project_root)
    
    return integration.run_enhanced_workflow(
        streamlit_input=streamlit_input,
        enable_text_rendering=enable_text_rendering,
        target_quality_score=target_quality_score,
        max_attempts=max_attempts,
        generate_image=generate_image
    )

if __name__ == "__main__":
    # Test Integration
    test_input = {
        'headline': 'Test Headline',
        'subline': 'Test Subline',
        'company': 'Test Company',
        'layout_id': 'skizze1_vertical_split',
        'unternehmen': 'Test Company',
        'benefits': ['Benefit 1', 'Benefit 2'],
        'cta': 'Jetzt bewerben!'
    }
    
    result = run_enhanced_workflow_from_streamlit(
        streamlit_input=test_input,
        target_quality_score=85,
        max_attempts=3,
        generate_image=False  # Kein Bild für Test
    )
    
    print("🔗 LANGGRAPH INTEGRATION TEST")
    print("=" * 50)
    print(f"Success: {result['success']}")
    print(f"Workflow Success: {result['workflow_success']}")
    print(f"Final Score: {result['final_quality_score']}/100")
    print(f"Attempts: {result['attempts_used']}")
    print(f"Strategy: {result['optimization_strategy']}")
    print(f"Processing Time: {result['processing_time']:.2f}s") 