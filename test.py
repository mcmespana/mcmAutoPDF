#!/usr/bin/env python3
"""
Script de prueba rápida para testar el sistema con los PDFs de ejemplo.
"""

import sys
from pathlib import Path

# Añadir el directorio actual al path para importar utils
sys.path.insert(0, str(Path(__file__).parent))

from utils import PDFExtractor, CSVHandler, PDFFiller


def test_extract(pdf_path: str):
    """Prueba la extracción de campos."""
    print(f"\n{'='*60}")
    print(f"TESTEANDO: {Path(pdf_path).name}")
    print(f"{'='*60}\n")
    
    try:
        extractor = PDFExtractor(pdf_path)
        info = extractor.get_pdf_info()
        fields = extractor.get_fields()
        
        print(f"📄 Páginas: {info['num_pages']}")
        print(f"📝 Campos: {info['num_fields']}")
        print(f"✅ Tiene formulario: {info['has_form']}")
        
        if info['num_fields'] > 0:
            print(f"\n📋 CAMPOS DETECTADOS:\n")
            for i, (name, data) in enumerate(fields.items(), 1):
                print(f"{i}. {name}")
                print(f"   Tipo: {data['type']}")
                if data['options']:
                    print(f"   Opciones: {', '.join(data['options'][:3])}...")
                if data['required']:
                    print(f"   ⚠️  REQUERIDO")
                print()
        else:
            print("\n⚠️  No se detectaron campos de formulario")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Función principal."""
    
    if len(sys.argv) < 2:
        print("Uso: python test.py <archivo.pdf>")
        print("\nO para testar todos los PDFs en una carpeta:")
        print("python test.py /ruta/a/carpeta/")
        sys.exit(1)
    
    path = sys.argv[1]
    path_obj = Path(path)
    
    if path_obj.is_file():
        # Testar un solo PDF
        test_extract(str(path_obj))
    elif path_obj.is_dir():
        # Testar todos los PDFs en la carpeta
        pdfs = list(path_obj.glob("*.pdf"))
        if not pdfs:
            print(f"No se encontraron PDFs en {path}")
            sys.exit(1)
        
        print(f"\n🔍 Encontrados {len(pdfs)} PDFs\n")
        
        for pdf in pdfs:
            test_extract(str(pdf))
            input("\nPresiona ENTER para continuar...")
    else:
        print(f"❌ No se encontró: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
