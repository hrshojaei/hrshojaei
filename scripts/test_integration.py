#!/usr/bin/env python3
"""
Quick Start Beispiel für n8n und Notion Integration

Dieses Script zeigt, wie die Integration funktioniert.
"""
import asyncio
from src.candidate_manager import CandidateManager, CandidateStatus
from src.config import settings

async def main():
    print("=" * 60)
    print("n8n und Notion Integration - Quick Start Demo")
    print("=" * 60)
    print()
    
    # Zeige aktuelle Konfiguration
    print("📋 Konfiguration:")
    print(f"  Notion: {'✓ Aktiviert' if settings.notion_enabled else '✗ Deaktiviert'}")
    if settings.notion_enabled:
        print(f"    Database ID: {settings.notion_database_id[:20]}...")
    print(f"  n8n: {'✓ Aktiviert' if settings.n8n_enabled else '✗ Deaktiviert'}")
    if settings.n8n_enabled:
        print(f"    Webhook URL: {settings.n8n_webhook_url}")
    print()
    
    if not settings.notion_enabled and not settings.n8n_enabled:
        print("⚠️  Keine Integration aktiviert!")
        print()
        print("So aktivierst du die Integrationen:")
        print("1. Bearbeite .env und setze:")
        print("   NOTION_ENABLED=true")
        print("   NOTION_API_KEY=secret_...")
        print("   NOTION_DATABASE_ID=...")
        print()
        print("   N8N_ENABLED=true")
        print("   N8N_WEBHOOK_URL=https://your-n8n.app/webhook/recruiting-events")
        print()
        print("2. Siehe N8N_NOTION_GUIDE.md für Details")
        return
    
    # Initialisiere Manager
    manager = CandidateManager()
    print("✓ CandidateManager initialisiert")
    print()
    
    # Beispiel 1: Kandidat erstellen
    print("📝 Beispiel 1: Kandidat erstellen")
    print("-" * 60)
    
    candidate_id = manager.add_candidate(
        name="Max Mustermann (Demo)",
        phone="+4915199999999",
        email="max.demo@example.com",
        current_company="Hörakustik Demo GmbH",
        current_position="Hörakustiker",
        experience_years=5,
        notes="Demo-Kandidat für n8n/Notion Test"
    )
    
    print(f"✓ Kandidat erstellt (ID: {candidate_id})")
    
    if settings.notion_enabled:
        print("  → Wird zu Notion synchronisiert...")
    if settings.n8n_enabled:
        print("  → Event 'candidate.created' wird an n8n gesendet...")
    
    # Kurze Pause für async operations
    await asyncio.sleep(2)
    print()
    
    # Beispiel 2: Status aktualisieren
    print("📝 Beispiel 2: Kandidat-Status aktualisieren")
    print("-" * 60)
    
    manager.update_candidate_status(candidate_id, CandidateStatus.INTERESTED)
    print(f"✓ Status zu 'interested' aktualisiert")
    
    if settings.notion_enabled:
        print("  → Notion-Datenbank wird aktualisiert...")
    if settings.n8n_enabled:
        print("  → Events 'candidate.updated' + 'candidate.interested' an n8n...")
    
    await asyncio.sleep(2)
    print()
    
    # Beispiel 3: Call Log erstellen
    print("📝 Beispiel 3: Call Log erstellen")
    print("-" * 60)
    
    call_log_id = manager.create_call_log(
        candidate_id=candidate_id,
        call_sid="CA_DEMO_123456"
    )
    print(f"✓ Call Log erstellt (ID: {call_log_id})")
    
    if settings.n8n_enabled:
        print("  → Event 'call.started' an n8n...")
    
    await asyncio.sleep(1)
    
    # Call beenden
    manager.update_call_log(
        call_log_id=call_log_id,
        ended_at="2024-11-13T21:35:00",
        duration_seconds=180,
        outcome="interested",
        summary="Kandidat zeigt großes Interesse. Möchte mehr Details zur Position erfahren.",
        next_action="Follow-up Termin vereinbaren für nächste Woche"
    )
    print(f"✓ Call Log aktualisiert (Dauer: 3 Min)")
    
    if settings.notion_enabled:
        print("  → Call Log zu Notion hinzugefügt...")
    if settings.n8n_enabled:
        print("  → Event 'call.completed' an n8n...")
    
    await asyncio.sleep(2)
    print()
    
    # Zusammenfassung
    print("=" * 60)
    print("✓ Demo abgeschlossen!")
    print()
    
    if settings.notion_enabled:
        print("📊 Prüfe deine Notion-Datenbank:")
        print(f"   {settings.notion_database_id}")
        print("   Du solltest den neuen Kandidaten 'Max Mustermann (Demo)' sehen")
        print("   mit Call Log als Kommentar.")
        print()
    
    if settings.n8n_enabled:
        print("🔄 Prüfe deine n8n Workflow Executions:")
        print("   - 1x candidate.created")
        print("   - 1x candidate.updated")
        print("   - 1x candidate.interested (Slack/Email?)")
        print("   - 1x call.started")
        print("   - 1x call.completed")
        print()
    
    print("📚 Weitere Infos:")
    print("   - N8N_NOTION_GUIDE.md: Vollständige Setup-Anleitung")
    print("   - n8n-workflows/: Vorgefertigte Workflow-Templates")
    print()

if __name__ == "__main__":
    asyncio.run(main())
