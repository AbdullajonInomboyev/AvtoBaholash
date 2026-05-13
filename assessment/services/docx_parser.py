"""
docx_parser.py — Eskirgan versiya, docx_importer.py ishlatiladi.
Bu fayl faqat backward compatibility uchun saqlanadi.
"""
# Barcha import va logika docx_importer.py ga ko'chirilgan
from assessment.services.docx_importer import (
    AvtoBaholashDocxParser,
    import_docx_to_assignment,
)

__all__ = ['AvtoBaholashDocxParser', 'import_docx_to_assignment']
