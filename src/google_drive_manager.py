"""
Google Drive Manager für Dokumenten-Upload und -Organisation.
"""

import io
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from loguru import logger

# Google Drive API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveManager:
    """Manager für Google Drive Operationen."""

    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialisiert den Google Drive Manager.

        Args:
            credentials_path: Pfad zur credentials.json (OAuth)
            token_path: Pfad zur token.json (gespeicherte Credentials)
        """
        self.credentials_path = credentials_path or "credentials.json"
        self.token_path = token_path or "token.json"
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authentifiziert mit Google Drive API."""
        creds = None

        # Token.json speichert User-Credentials nach erstem Login
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # Falls keine gültigen Credentials vorhanden, neu anmelden
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Erneuere Google Drive Credentials...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials-Datei nicht gefunden: {self.credentials_path}\n"
                        "Bitte erstellen Sie ein Google Cloud Project und laden Sie die credentials.json herunter."
                    )

                logger.info("Starte OAuth-Flow für Google Drive...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Credentials für zukünftige Nutzung speichern
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        logger.info("Google Drive API erfolgreich authentifiziert")

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """
        Erstellt einen Ordner in Google Drive.

        Args:
            folder_name: Name des Ordners
            parent_id: ID des übergeordneten Ordners (None = Root)

        Returns:
            Ordner-ID
        """
        try:
            # Prüfe ob Ordner bereits existiert
            existing_folder = self.find_folder(folder_name, parent_id)
            if existing_folder:
                logger.info(f"Ordner '{folder_name}' existiert bereits: {existing_folder}")
                return existing_folder

            # Erstelle neuen Ordner
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"Ordner erstellt: {folder_name} (ID: {folder_id})")
            return folder_id

        except HttpError as error:
            logger.error(f"Fehler beim Erstellen des Ordners: {error}")
            raise

    def find_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Sucht einen Ordner nach Name.

        Args:
            folder_name: Name des Ordners
            parent_id: ID des übergeordneten Ordners

        Returns:
            Ordner-ID oder None
        """
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

            if parent_id:
                query += f" and '{parent_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()

            items = results.get('files', [])
            return items[0]['id'] if items else None

        except HttpError as error:
            logger.error(f"Fehler bei Ordnersuche: {error}")
            return None

    def upload_file(
        self,
        file_path: Path,
        folder_id: Optional[str] = None,
        new_name: Optional[str] = None
    ) -> Dict:
        """
        Lädt eine Datei zu Google Drive hoch.

        Args:
            file_path: Pfad zur lokalen Datei
            folder_id: Zielordner-ID (None = Root)
            new_name: Neuer Name für die Datei (optional)

        Returns:
            Dict mit file_id und webViewLink
        """
        try:
            file_name = new_name or file_path.name

            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # MIME-Type bestimmen
            mime_types = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
            }
            mime_type = mime_types.get(file_path.suffix.lower(), 'application/octet-stream')

            media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, name'
            ).execute()

            logger.info(f"Datei hochgeladen: {file_name} (ID: {file.get('id')})")

            return {
                'file_id': file.get('id'),
                'url': file.get('webViewLink'),
                'name': file.get('name')
            }

        except HttpError as error:
            logger.error(f"Fehler beim Datei-Upload: {error}")
            raise

    def move_file(self, file_id: str, new_folder_id: str) -> bool:
        """
        Verschiebt eine Datei in einen anderen Ordner.

        Args:
            file_id: ID der zu verschiebenden Datei
            new_folder_id: Zielordner-ID

        Returns:
            True bei Erfolg
        """
        try:
            # Hole aktuelle Parents
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()

            previous_parents = ",".join(file.get('parents', []))

            # Verschiebe Datei
            self.service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            logger.info(f"Datei {file_id} verschoben nach {new_folder_id}")
            return True

        except HttpError as error:
            logger.error(f"Fehler beim Verschieben der Datei: {error}")
            return False

    def rename_file(self, file_id: str, new_name: str) -> bool:
        """
        Benennt eine Datei um.

        Args:
            file_id: ID der Datei
            new_name: Neuer Name

        Returns:
            True bei Erfolg
        """
        try:
            self.service.files().update(
                fileId=file_id,
                body={'name': new_name}
            ).execute()

            logger.info(f"Datei {file_id} umbenannt zu: {new_name}")
            return True

        except HttpError as error:
            logger.error(f"Fehler beim Umbenennen: {error}")
            return False

    def list_files_in_folder(
        self,
        folder_id: Optional[str] = None,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Listet Dateien in einem Ordner auf.

        Args:
            folder_id: Ordner-ID (None = Root)
            page_size: Anzahl Ergebnisse pro Seite

        Returns:
            Liste von Datei-Metadaten
        """
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, modifiedTime, webViewLink)',
                pageSize=page_size,
                orderBy='createdTime desc'
            ).execute()

            files = results.get('files', [])
            logger.info(f"Gefunden: {len(files)} Dateien")
            return files

        except HttpError as error:
            logger.error(f"Fehler beim Auflisten der Dateien: {error}")
            return []

    def download_file(self, file_id: str, output_path: Path) -> bool:
        """
        Lädt eine Datei von Google Drive herunter.

        Args:
            file_id: ID der Datei
            output_path: Ziel-Pfad

        Returns:
            True bei Erfolg
        """
        try:
            request = self.service.files().get_media(fileId=file_id)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            fh = io.FileIO(str(output_path), 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"Download {int(status.progress() * 100)}%")

            logger.info(f"Datei heruntergeladen: {output_path}")
            return True

        except HttpError as error:
            logger.error(f"Fehler beim Download: {error}")
            return False

    def create_folder_structure(self, base_folder_name: str, categories: List[str]) -> Dict[str, str]:
        """
        Erstellt eine Ordnerstruktur für Dokumentenkategorien.

        Args:
            base_folder_name: Name des Hauptordners
            categories: Liste von Kategorien (Unterordner)

        Returns:
            Dict mit {kategorie: folder_id}
        """
        # Hauptordner erstellen
        base_folder_id = self.create_folder(base_folder_name)

        # Kategorieordner erstellen
        folder_map = {'base': base_folder_id}

        for category in categories:
            folder_id = self.create_folder(category, parent_id=base_folder_id)
            folder_map[category] = folder_id

        logger.info(f"Ordnerstruktur erstellt: {len(categories)} Kategorien")
        return folder_map

    def get_or_create_folder_path(self, path_parts: List[str]) -> str:
        """
        Erstellt eine Ordnerhierarchie (z.B. ['Dokumente', '2024', 'Rechnungen']).

        Args:
            path_parts: Liste von Ordnernamen (von oben nach unten)

        Returns:
            ID des untersten Ordners
        """
        parent_id = None

        for folder_name in path_parts:
            folder_id = self.find_folder(folder_name, parent_id)
            if not folder_id:
                folder_id = self.create_folder(folder_name, parent_id)
            parent_id = folder_id

        return parent_id
