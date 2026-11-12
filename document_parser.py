from pathlib import Path
import re
import fitz

def _clean(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def _is_heading(line: str) -> bool:
    s = line.strip()
    if len(s) < 3 or len(s) > 140:
        return False
    patterns = [
        r"^(?:\d+(?:\.\d+)*\.?\s+)[A-Z]",
        r"^(?:[A-Z]\.\s+)[A-Z]",
        r"^(ABSTRACT|INTRODUCTION|CONCLUSION|REFERENCES|ACKNOWLEDGMENTS?)$",
    ]
    return any(re.match(p, s, re.I) for p in patterns)

def parse_pdf(title: str, path: Path) -> list[dict]:
    pdf = fitz.open(path)
    records, current_section, current_heading = [], "Front matter", "Front matter"
    for page_index, page in enumerate(pdf):
        blocks = page.get_text("blocks")
        for block in blocks:
            raw = block[4] if len(block) > 4 else ""
            lines = [x.strip() for x in raw.splitlines() if x.strip()]
            for line in lines:
                if _is_heading(line):
                    current_heading = line
                    current_section = line
                else:
                    text = _clean(line)
                    if len(text) >= 35:
                        records.append({
                            "paper": title,
                            "section": current_section,
                            "heading": current_heading,
                            "page": page_index + 1,
                            "text": text,
                        })
    pdf.close()
    return records

def parse_papers(paths: dict[str, Path]) -> list[dict]:
    all_records = []
    for title, path in paths.items():
        all_records.extend(parse_pdf(title, path))
    if not all_records:
        raise RuntimeError("No text was extracted from the PDFs.")
    return all_records
