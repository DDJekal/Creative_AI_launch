#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gpt_utils.py - Utility-Funktionen für GPT-Integration und Retry-Mechanik

Stellt Hilfsfunktionen bereit für:
- Prompt-Qualitäts-Validierung
- Automatische Retry-Mechanismen
- Score-basierte Optimierung
- ChatGPT-Level Qualitätskontrolle

Workflow-ID: gpt_utilities_for_quality_assurance_v1
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import yaml
import openai

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import eigener Module
try:
    from prompt.validate_prompt_quality import validate_prompt_quality
    from prompt.rewrite_suggestions_gpt import revise_prompt_with_feedback, analyze_prompt_quality_gaps
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    logger.warning("⚠️ Validation-Module nicht verfügbar")


def validate_prompt_score(prompt_path: str, 
                         template_path: str = None,
                         report_path: str = None) -> float:
    """
    Validiert Prompt-Qualität und gibt Score zurück
    
    Args:
        prompt_path: Pfad zum zu validierenden Prompt
        template_path: Optional Template-YAML für Layout-Validation
        report_path: Optional Pfad für Validation-Report
    
    Returns:
        float: Qualitäts-Score (0-100)
    """
    if not VALIDATION_AVAILABLE:
        logger.warning("⚠️ Validation nicht verfügbar, gebe Default-Score zurück")
        return 75.0
    
    try:
        # Standard Report-Pfad falls nicht angegeben
        if not report_path:
            report_path = prompt_path.replace('.txt', '_validation.yaml')
        
        # Validation ausführen
        result = validate_prompt_quality(
            prompt_path=prompt_path,
            template_path=template_path,
            report_path=report_path
        )
        
        score = result.get('score', 0)
        logger.info(f"📊 Prompt-Score: {score}/100")
        
        return score
        
    except Exception as e:
        logger.error(f"❌ Validation fehlgeschlagen: {e}")
        return 0.0


def auto_optimize_prompt_quality(prompt_path: str,
                                min_score: float = 85,
                                max_retries: int = 2,
                                template_path: str = None) -> Tuple[str, float, bool]:
    """
    Automatische Prompt-Qualitäts-Optimierung mit Retry-Mechanik
    
    Args:
        prompt_path: Pfad zum zu optimierenden Prompt
        min_score: Minimum Score für Akzeptanz
        max_retries: Maximale Anzahl Optimierungs-Versuche
        template_path: Optional Template für Layout-Validation
    
    Returns:
        Tuple[str, float, bool]: (final_prompt_path, final_score, optimization_successful)
    """
    logger.info(f"🚀 Starte automatische Prompt-Optimierung (Ziel: {min_score}+ Punkte)")
    
    current_path = prompt_path
    current_score = validate_prompt_score(current_path, template_path)
    retries_used = 0
    
    # Optimization-Log initialisieren
    optimization_log = {
        'workflow_id': 'auto_prompt_optimization_v1',
        'original_path': prompt_path,
        'target_score': min_score,
        'max_retries': max_retries,
        'optimization_history': []
    }
    
    while current_score < min_score and retries_used < max_retries:
        logger.info(f"📈 Score {current_score} < {min_score} - Optimierung {retries_used + 1}/{max_retries}")
        
        # Quality-Gaps analysieren
        report_path = current_path.replace('.txt', '_validation.yaml')
        specific_issues = analyze_prompt_quality_gaps(report_path) if Path(report_path).exists() else []
        
        # Prompt-Revision durchführen
        revised_path = revise_prompt_with_feedback(
            prompt_path=current_path,
            validation_score=current_score,
            specific_issues=specific_issues
        )
        
        # Neuen Score validieren
        new_score = validate_prompt_score(revised_path, template_path)
        
        # Optimization-Step loggen
        optimization_log['optimization_history'].append({
            'retry_number': retries_used + 1,
            'input_path': current_path,
            'output_path': revised_path,
            'score_before': current_score,
            'score_after': new_score,
            'improvement': new_score - current_score,
            'issues_addressed': specific_issues
        })
        
        # Update für nächste Iteration
        current_path = revised_path
        current_score = new_score
        retries_used += 1
        
        logger.info(f"✨ Optimierung {retries_used}: {current_score:.1f} Punkte (+{new_score - validate_prompt_score(prompt_path):.1f})")
    
    # Finales Ergebnis
    optimization_successful = current_score >= min_score
    
    optimization_log.update({
        'final_path': current_path,
        'final_score': current_score,
        'retries_used': retries_used,
        'optimization_successful': optimization_successful,
        'total_improvement': current_score - validate_prompt_score(prompt_path, template_path)
    })
    
    # Log speichern
    log_path = current_path.replace('.txt', '_optimization_log.yaml')
    with open(log_path, 'w', encoding='utf-8') as f:
        yaml.dump(optimization_log, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    # Ergebnis-Summary
    if optimization_successful:
        logger.info(f"🎉 Optimierung erfolgreich! Final-Score: {current_score:.1f}/100")
    else:
        logger.warning(f"⚠️ Ziel-Score nicht erreicht. Final-Score: {current_score:.1f}/100 (Ziel: {min_score})")
    
    logger.info(f"📋 Optimization-Log: {log_path}")
    
    return current_path, current_score, optimization_successful


def estimate_quality_improvement_potential(prompt_path: str, template_path: str = None) -> Dict[str, Any]:
    """
    Schätzt Verbesserungs-Potenzial eines Prompts ein
    
    Returns:
        Dict mit Verbesserungs-Empfehlungen und geschätztem Score-Potenzial
    """
    try:
        # Aktuellen Score ermitteln
        current_score = validate_prompt_score(prompt_path, template_path)
        
        # Validation-Report analysieren
        report_path = prompt_path.replace('.txt', '_validation.yaml')
        
        improvement_potential = {
            'current_score': current_score,
            'improvement_areas': [],
            'estimated_max_score': 0,
            'priority_actions': []
        }
        
        if Path(report_path).exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                report = yaml.safe_load(f)
            
            scoring = report.get('scoring_breakdown', {})
            
            # Verbesserungs-Potenzial pro Bereich analysieren
            potential_gains = 0
            
            # Layout-Zonen Check
            if 'layout_zones_complete' in scoring:
                zone_info = scoring['layout_zones_complete']
                if isinstance(zone_info, str) and '/' in zone_info:
                    current_zones, total_zones = map(int, zone_info.split('/'))
                    if current_zones < total_zones:
                        missing_zones = total_zones - current_zones
                        potential_gain = (missing_zones / total_zones) * 20  # Max 20 Punkte für Zonen
                        potential_gains += potential_gain
                        improvement_potential['improvement_areas'].append({
                            'area': 'Layout-Zonen',
                            'current': f"{current_zones}/{total_zones}",
                            'potential_gain': potential_gain,
                            'action': f"Ergänze {missing_zones} fehlende Zonen"
                        })
            
            # Semantic Flow Check
            if 'semantic_flow' in scoring:
                flow_info = scoring['semantic_flow']
                if isinstance(flow_info, str) and '/' in flow_info:
                    current_flow, max_flow = map(int, flow_info.split('/'))
                    if current_flow < max_flow:
                        potential_gain = ((max_flow - current_flow) / max_flow) * 10
                        potential_gains += potential_gain
                        improvement_potential['improvement_areas'].append({
                            'area': 'Semantischer Flow',
                            'current': f"{current_flow}/{max_flow}",
                            'potential_gain': potential_gain,
                            'action': "Verbessere Sprachfluss und Struktur"
                        })
        
        # Geschätzter Max-Score
        improvement_potential['estimated_max_score'] = min(100, current_score + potential_gains + 5)  # +5 für allgemeine Optimierungen
        
        # Priority Actions basierend auf Score
        if current_score < 70:
            improvement_potential['priority_actions'] = [
                "Kritische Struktur-Probleme beheben",
                "Alle Layout-Zonen implementieren",
                "CI-Farben korrekt integrieren"
            ]
        elif current_score < 85:
            improvement_potential['priority_actions'] = [
                "Emotionale Tonalität verstärken",
                "Sprachliche Aktivität erhöhen",
                "CTA-Formulierung optimieren"
            ]
        else:
            improvement_potential['priority_actions'] = [
                "Premium-Sprachqualität erreichen",
                "Conversion-Optimierung maximieren",
                "Feintuning für Perfektion"
            ]
        
        return improvement_potential
        
    except Exception as e:
        logger.error(f"❌ Potenzial-Analyse fehlgeschlagen: {e}")
        return {
            'current_score': 0,
            'improvement_areas': [],
            'estimated_max_score': 0,
            'priority_actions': ["Error: Analyse nicht möglich"]
        }


def create_quality_dashboard(prompts_directory: str = "outputs") -> Dict[str, Any]:
    """
    Erstellt Quality-Dashboard für alle Prompts im Verzeichnis
    """
    dashboard = {
        'workflow_id': 'quality_dashboard_v1',
        'analysis_timestamp': str(Path(prompts_directory).resolve()),
        'prompts_analyzed': [],
        'quality_summary': {
            'total_prompts': 0,
            'average_score': 0,
            'highest_score': 0,
            'lowest_score': 100,
            'prompts_above_85': 0,
            'prompts_above_90': 0
        },
        'recommendations': []
    }
    
    try:
        prompt_files = list(Path(prompts_directory).glob("*final_prompt*.txt"))
        scores = []
        
        for prompt_file in prompt_files:
            score = validate_prompt_score(str(prompt_file))
            scores.append(score)
            
            dashboard['prompts_analyzed'].append({
                'file': prompt_file.name,
                'score': score,
                'status': 'excellent' if score >= 90 else 'good' if score >= 85 else 'needs_improvement'
            })
        
        if scores:
            dashboard['quality_summary'].update({
                'total_prompts': len(scores),
                'average_score': sum(scores) / len(scores),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'prompts_above_85': sum(1 for s in scores if s >= 85),
                'prompts_above_90': sum(1 for s in scores if s >= 90)
            })
        
        # Dashboard speichern
        dashboard_path = Path(prompts_directory) / "quality_dashboard.yaml"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            yaml.dump(dashboard, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"📊 Quality-Dashboard erstellt: {dashboard_path}")
        
    except Exception as e:
        logger.error(f"❌ Dashboard-Erstellung fehlgeschlagen: {e}")
    
    return dashboard


def optimize_prompt_with_gpt4(prompt: str, system_message: str = None) -> str:
    """
    Optimiert einen Bildprompt mit GPT-4 für DALL-E 3, ohne Details zu verlieren.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY nicht gesetzt!")
        return prompt

    openai.api_key = api_key

    if not system_message:
        system_message = (
            "Du bist ein Experte für DALL-E 3 Prompt-Optimierung. "
            "Optimiere den folgenden Prompt für maximale Bildqualität, "
            "aber entferne keine Details und kürze nichts. Ergänze nur, was für DALL-E hilfreich ist "
            "(z.B. Fotografie-Begriffe, Licht, Stil, Komposition, Auflösung, Kamera, professionelle Begriffe)."
        )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logger.error(f"❌ GPT-4 Optimierung fehlgeschlagen: {e}")
        return prompt


if __name__ == "__main__":
    print("🛠️ GPT UTILS Test")
    print("=" * 40)
    
    # Test Quality-Validation
    test_prompt = "outputs/final_prompt_optimized.txt"
    
    if Path(test_prompt).exists():
        print(f"📊 Score-Test: {test_prompt}")
        score = validate_prompt_score(test_prompt)
        print(f"   Score: {score}/100")
        
        # Test Auto-Optimization
        if score < 90:
            print(f"\n🚀 Auto-Optimization Test...")
            final_path, final_score, success = auto_optimize_prompt_quality(
                test_prompt, min_score=90, max_retries=1
            )
            print(f"   Final Score: {final_score}/100")
            print(f"   Success: {success}")
        
    else:
        print(f"❌ Test-Datei nicht gefunden: {test_prompt}")
    
    print("\n✅ GPT-Utils Tests abgeschlossen!") 