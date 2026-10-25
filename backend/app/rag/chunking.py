import re
import hashlib
from typing import List, Dict, Any


def generate_stable_chunk_id(doc_title: str, section_title: str, chunk_index: int) -> str:
    seed_str = f"{doc_title}::{section_title}::{chunk_index}"
    return hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:16]


def chunk_markdown_document(
    doc_id: str,
    title: str,
    asset_type: str,
    markdown_content: str,
    source_label: str = "Standard Operating Procedure",
) -> List[Dict[str, Any]]:
    """
    Splits markdown documentation by section headers (##) while preserving
    metadata, title, section, and stable chunk identifiers.
    """
    sections = re.split(r"\n(?=##\s+)", markdown_content)
    chunks = []
    chunk_index = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract section header
        header_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
        section_name = header_match.group(1).strip() if header_match else "General"

        # Generate stable chunk ID
        chunk_id = f"chk_{generate_stable_chunk_id(title, section_name, chunk_index)}"
        chunk_index += 1

        chunks.append({
            "chunk_id": chunk_id,
            "document_id": doc_id,
            "title": title,
            "section": section_name,
            "asset_type": asset_type,
            "source_label": source_label,
            "content": section,
            "metadata": {
                "doc_id": doc_id,
                "asset_type": asset_type,
                "section": section_name,
                "length_chars": len(section),
            },
        })

    return chunks
