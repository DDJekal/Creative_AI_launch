# CreativeAI 6.0 - Start-Skript
# ================================

Write-Host "🚀 Starte CreativeAI 6.0..." -ForegroundColor Green

# PYTHONPATH korrekt setzen
$env:PYTHONPATH = "C:\Users\David Jekal\Desktop\Projekte\CreativeKI\CreativeAI_launch;C:\Users\David Jekal\Desktop\Projekte\CreativeKI\CreativeAI_launch\src;C:\Users\David Jekal\Desktop\Projekte\CreativeKI\CreativeAI_launch\utils"

Write-Host "✅ PYTHONPATH gesetzt:" -ForegroundColor Green
Write-Host "   $env:PYTHONPATH" -ForegroundColor Yellow

# Virtuelle Umgebung aktivieren (falls vorhanden)
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Aktiviere virtuelle Umgebung..." -ForegroundColor Blue
    & .\venv\Scripts\Activate.ps1
    Write-Host "✅ Virtuelle Umgebung aktiviert" -ForegroundColor Green
}

# Module testen
Write-Host "🧪 Teste Module-Imports..." -ForegroundColor Blue
try {
    python -c "from src.workflow.multi_prompt_system import MultiPromptSystem; print('✅ Multi-Prompt-System OK')"
    python -c "from src.image.enhanced_creative_generator import create_enhanced_creative_generator; print('✅ Enhanced Creative Generator OK')"
    python -c "from src.workflow.langgraph_integration import run_enhanced_workflow_from_streamlit; print('✅ LangGraph Integration OK')"
    python -c "from utils.gpt_utils import optimize_prompt_with_gpt4; print('✅ Utils-Modul OK')"
    Write-Host "✅ Alle Module erfolgreich geladen!" -ForegroundColor Green
} catch {
    Write-Host "❌ Fehler beim Laden der Module: $_" -ForegroundColor Red
    exit 1
}

# Streamlit-App starten
Write-Host "🌐 Starte Streamlit-App..." -ForegroundColor Blue
Write-Host "📱 App wird verfügbar unter: http://localhost:8501" -ForegroundColor Cyan
Write-Host "🔄 Drücke Ctrl+C zum Beenden" -ForegroundColor Yellow

streamlit run streamlit_app_multi_prompt_enhanced_restructured.py --server.headless true --server.port 8501
