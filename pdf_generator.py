# app/integrations/pdf_generator.py
from pathlib import Path
import uuid


class PDFGenerator:
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_fake_pdf(self, prefix: str, content: str) -> str:
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.txt"
        filepath = self.storage_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)