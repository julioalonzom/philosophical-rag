import re
from typing import List, Dict, Tuple

def detect_text_structure(text: str) -> Tuple[str, List[Dict[str, any]]]:
    lines = text.split('\n')
    structure = []
    text_type = "unknown"

    # Patterns for different structural elements
    patterns = {
        "book": r'^BOOK\s+([IVX]+|[0-9]+)',
        "chapter": r'^CHAPTER\s+([IVX]+|[0-9]+)',
        "question": r'^QUESTION\s+([IVX]+|[0-9]+)',
        "article": r'^ARTICLE\s+([IVX]+|[0-9]+)',
        "part": r'^PART\s+([IVX]+|[0-9]+)',
        "section": r'^SECTION\s+([IVX]+|[0-9]+)',
    }

    current_elements = {key: None for key in patterns.keys()}

    for i, line in enumerate(lines):
        for element_type, pattern in patterns.items():
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                number = match.group(1)
                current_elements[element_type] = {
                    "type": element_type,
                    "number": number,
                    "start_line": i + 1
                }
                
                # Close previous element of the same type
                for elem in reversed(structure):
                    if elem["type"] == element_type:
                        elem["end_line"] = i
                        break
                
                structure.append(current_elements[element_type])
                break

    # Close any open elements
    for elem in structure:
        if "end_line" not in elem:
            elem["end_line"] = len(lines)

    # Determine text_type based on the most common high-level element
    if any(elem["type"] == "book" for elem in structure):
        text_type = "book_based"
    elif any(elem["type"] == "question" for elem in structure):
        text_type = "question_based"
    elif any(elem["type"] == "part" for elem in structure):
        text_type = "part_based"
    elif any(elem["type"] == "chapter" for elem in structure):
        text_type = "chapter_based"

    return text_type, structure
