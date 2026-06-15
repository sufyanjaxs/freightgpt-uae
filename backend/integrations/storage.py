import logging
import os
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO
from core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self.upload_dir = Path(settings.UPLOAD_DIR)
        if self.backend == "local":
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Local storage at: {self.upload_dir}")

    async def save(self, path: str, content: bytes) -> str:
        """Save file to storage. Returns the file path/URL."""
        if self.backend == "local":
            full_path = self.upload_dir / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(str(full_path), "wb") as f:
                await f.write(content)
            logger.info(f"File saved: {full_path}")
            return str(full_path)
        else:
            logger.info(f"[STORAGE MOCK] Would save: {path} ({len(content)} bytes)")
            return path

    async def read(self, path: str) -> Optional[bytes]:
        """Read file from storage."""
        if self.backend == "local":
            full_path = self.upload_dir / path
            if full_path.exists():
                async with aiofiles.open(str(full_path), "rb") as f:
                    return await f.read()
        return None

    async def delete(self, path: str) -> bool:
        """Delete file from storage."""
        if self.backend == "local":
            full_path = self.upload_dir / path
            if full_path.exists():
                full_path.unlink()
                return True
        return False

    def get_url(self, path: str) -> str:
        """Get public URL for file."""
        if self.backend == "local":
            return f"/api/v1/files/{path}"
        return path


storage_service = StorageService()
