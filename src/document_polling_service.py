"""
Polling Service für regelmäßige Überprüfung von Google Drive Inbox.
Läuft kontinuierlich und verarbeitet neue Dokumente alle X Minuten.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from src.document_sorter import DocumentSorter
from src.config import get_settings


class DocumentPollingService:
    """Service für kontinuierliche Dokumentenüberwachung."""

    def __init__(
        self,
        sorter: DocumentSorter,
        inbox_folder_id: Optional[str] = None,
        poll_interval_minutes: int = 15
    ):
        """
        Initialisiert den Polling Service.

        Args:
            sorter: DocumentSorter Instanz
            inbox_folder_id: Google Drive Inbox Folder-ID (None = Root)
            poll_interval_minutes: Intervall in Minuten (Standard: 15)
        """
        self.sorter = sorter
        self.inbox_folder_id = inbox_folder_id
        self.poll_interval = timedelta(minutes=poll_interval_minutes)
        self.is_running = False
        self.last_run: Optional[datetime] = None

        logger.info(f"Polling Service initialisiert: Intervall {poll_interval_minutes} Minuten")

    async def start(self):
        """Startet den Polling Service."""
        self.is_running = True
        logger.info("🚀 Polling Service gestartet")

        try:
            while self.is_running:
                await self._run_polling_cycle()

                # Warte bis zum nächsten Intervall
                await asyncio.sleep(self.poll_interval.total_seconds())

        except KeyboardInterrupt:
            logger.info("⏹️ Polling Service durch Benutzer gestoppt")
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler im Polling Service: {e}")
        finally:
            self.is_running = False
            logger.info("Polling Service beendet")

    async def _run_polling_cycle(self):
        """Führt einen Polling-Zyklus aus."""
        cycle_start = datetime.now()
        logger.info(f"⏰ Starte Polling-Zyklus: {cycle_start.strftime('%H:%M:%S')}")

        try:
            # Verarbeite Inbox
            stats = await self.sorter.process_inbox_folder(self.inbox_folder_id)

            # Log Statistiken
            duration = (datetime.now() - cycle_start).total_seconds()
            logger.info(
                f"✅ Zyklus abgeschlossen in {duration:.2f}s: "
                f"{stats['processed']} verarbeitet, "
                f"{stats['failed']} fehlgeschlagen, "
                f"{stats['skipped']} übersprungen"
            )

            self.last_run = cycle_start

        except Exception as e:
            logger.error(f"❌ Fehler im Polling-Zyklus: {e}")

    def stop(self):
        """Stoppt den Polling Service."""
        logger.info("Stoppe Polling Service...")
        self.is_running = False

    async def run_once(self) -> dict:
        """
        Führt einen einzelnen Polling-Zyklus aus (für manuelle Ausführung).

        Returns:
            Dict mit Verarbeitungsstatistik
        """
        logger.info("Manueller Polling-Zyklus...")
        await self._run_polling_cycle()
        return {'status': 'completed', 'last_run': self.last_run}


class ScheduledPoller:
    """Wrapper für geplante Ausführung (z.B. via Cron)."""

    def __init__(self, sorter: DocumentSorter, inbox_folder_id: Optional[str] = None):
        """
        Initialisiert den Scheduled Poller.

        Args:
            sorter: DocumentSorter Instanz
            inbox_folder_id: Google Drive Inbox Folder-ID
        """
        self.sorter = sorter
        self.inbox_folder_id = inbox_folder_id

    async def run(self) -> dict:
        """
        Führt einen einzelnen Durchlauf aus.

        Returns:
            Dict mit Statistiken
        """
        logger.info("📅 Starte geplanten Durchlauf...")

        start_time = datetime.now()

        stats = await self.sorter.process_inbox_folder(self.inbox_folder_id)

        duration = (datetime.now() - start_time).total_seconds()

        result = {
            'timestamp': start_time.isoformat(),
            'duration_seconds': duration,
            'statistics': stats
        }

        logger.info(f"✅ Geplanter Durchlauf abgeschlossen: {stats}")

        return result


async def start_polling_service(
    sorter: DocumentSorter,
    inbox_folder_id: Optional[str] = None,
    poll_interval_minutes: int = 15
):
    """
    Startet den Polling Service.

    Args:
        sorter: DocumentSorter Instanz
        inbox_folder_id: Inbox Folder-ID
        poll_interval_minutes: Polling-Intervall in Minuten
    """
    service = DocumentPollingService(
        sorter=sorter,
        inbox_folder_id=inbox_folder_id,
        poll_interval_minutes=poll_interval_minutes
    )

    await service.start()


async def run_scheduled_job(
    sorter: DocumentSorter,
    inbox_folder_id: Optional[str] = None
) -> dict:
    """
    Führt einen geplanten Job aus (z.B. via Cron).

    Args:
        sorter: DocumentSorter Instanz
        inbox_folder_id: Inbox Folder-ID

    Returns:
        Dict mit Statistiken
    """
    poller = ScheduledPoller(sorter, inbox_folder_id)
    return await poller.run()
