"""
Módulo para extraer campos de formularios PDF.
"""

from pypdf import PdfReader
from typing import Dict, List, Any


class PDFExtractor:
    """Extrae campos de formularios PDF interactivos."""
    
    def __init__(self, pdf_path: str):
        """
        Inicializa el extractor.
        
        Args:
            pdf_path: Ruta al archivo PDF
        """
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        
    def get_fields(self) -> Dict[str, Any]:
        """
        Extrae todos los campos del PDF.
        
        Returns:
            Diccionario con nombre_campo: {tipo, valor, opciones}
        """
        fields = {}
        
        if self.reader.get_fields() is None:
            return fields
            
        for field_name, field_data in self.reader.get_fields().items():
            field_info = {
                'type': self._get_field_type(field_data),
                'value': field_data.get('/V', ''),
                'options': self._get_field_options(field_data),
                'required': field_data.get('/Ff', 0) & 2 == 2  # Flag de requerido
            }
            fields[field_name] = field_info
            
        return fields
    
    def get_field_names(self) -> List[str]:
        """
        Obtiene solo los nombres de los campos.
        
        Returns:
            Lista con nombres de campos
        """
        fields = self.get_fields()
        return list(fields.keys())
    
    def _get_field_type(self, field_data: Dict) -> str:
        """
        Determina el tipo de campo.
        
        Args:
            field_data: Datos del campo del PDF
            
        Returns:
            Tipo de campo: 'text', 'checkbox', 'radio', 'dropdown', 'unknown'
        """
        field_type = field_data.get('/FT', '')
        
        if field_type == '/Tx':
            return 'text'
        elif field_type == '/Btn':
            # Puede ser checkbox o radio button
            if field_data.get('/Ff', 0) & 32768:  # Flag de radio
                return 'radio'
            else:
                return 'checkbox'
        elif field_type == '/Ch':
            return 'dropdown'
        else:
            return 'unknown'
    
    def _get_field_options(self, field_data: Dict) -> List[str]:
        """
        Obtiene las opciones de un campo (para dropdowns, radios).
        
        Args:
            field_data: Datos del campo del PDF
            
        Returns:
            Lista de opciones disponibles
        """
        options = field_data.get('/Opt', [])
        if isinstance(options, list):
            # Puede ser lista de strings o lista de arrays [value, display]
            return [opt if isinstance(opt, str) else opt[1] for opt in options]
        return []
    
    def get_pdf_info(self) -> Dict[str, Any]:
        """
        Obtiene información general del PDF.
        
        Returns:
            Diccionario con información del PDF
        """
        info = {
            'num_pages': len(self.reader.pages),
            'num_fields': len(self.get_fields()),
            'has_form': self.reader.get_fields() is not None,
            'field_names': self.get_field_names()
        }
        
        return info
    
    def detect_table_fields(self, fields: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Detecta campos que parecen ser parte de una tabla (para futuro).
        
        Busca patrones como:
        - campo_1, campo_2, campo_3
        - row1_col1, row1_col2, row2_col1
        
        Args:
            fields: Diccionario de campos
            
        Returns:
            Diccionario con grupos de campos que parecen tablas
        """
        # TODO: Implementar en fase 2
        # Buscar patrones numéricos al final del nombre
        # Agrupar campos similares
        return {}


if __name__ == "__main__":
    # Test básico
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFExtractor(pdf_path)
        
        print("=== PDF INFO ===")
        info = extractor.get_pdf_info()
        for key, value in info.items():
            if key != 'field_names':
                print(f"{key}: {value}")
        
        print("\n=== CAMPOS ===")
        fields = extractor.get_fields()
        for name, data in fields.items():
            print(f"\n{name}:")
            print(f"  Tipo: {data['type']}")
            if data['options']:
                print(f"  Opciones: {data['options']}")
            if data['required']:
                print(f"  ⚠️  REQUERIDO")
    else:
        print("Uso: python pdf_extractor.py <archivo.pdf>")
