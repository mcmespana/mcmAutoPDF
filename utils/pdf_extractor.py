"""
Módulo para extraer campos de formularios PDF y detectar sus etiquetas.
"""

from pypdf import PdfReader
from typing import Dict, List, Any, Tuple
import re


class PDFExtractor:
    """Extrae campos de formularios PDF y detecta etiquetas cercanas automáticamente."""

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
            Diccionario con nombre_campo: {tipo, valor, opciones, rect, page}
        """
        fields = {}

        if self.reader.get_fields() is None:
            return fields

        for field_name, field_data in self.reader.get_fields().items():
            field_info = {
                'type': self._get_field_type(field_data),
                'value': field_data.get('/V', ''),
                'options': self._get_field_options(field_data),
                'required': field_data.get('/Ff', 0) & 2 == 2,
                'rect': self._get_field_rect(field_data),
                'page': self._get_field_page(field_data)
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

    def _get_field_rect(self, field_data: Dict) -> Tuple[float, float, float, float]:
        """
        Obtiene el rectángulo (bounding box) del campo.

        Args:
            field_data: Datos del campo del PDF

        Returns:
            Tupla (left, bottom, right, top) o None si no existe
        """
        try:
            # Buscar /Rect en diferentes ubicaciones posibles
            if '/Rect' in field_data:
                rect = field_data['/Rect']
                return (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))

            # Buscar en anotaciones
            if '/Kids' in field_data and len(field_data['/Kids']) > 0:
                kid = field_data['/Kids'][0].get_object()
                if '/Rect' in kid:
                    rect = kid['/Rect']
                    return (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))
        except:
            pass

        return None

    def _get_field_page(self, field_data: Dict) -> int:
        """
        Obtiene el número de página del campo.

        Args:
            field_data: Datos del campo del PDF

        Returns:
            Número de página (0-indexed) o 0 si no se puede determinar
        """
        try:
            # Buscar en anotaciones
            if '/Kids' in field_data and len(field_data['/Kids']) > 0:
                kid = field_data['/Kids'][0].get_object()
                if '/P' in kid:
                    page_obj = kid['/P']
                    # Buscar el índice de la página
                    for i, page in enumerate(self.reader.pages):
                        if page.indirect_reference == page_obj:
                            return i
        except:
            pass

        return 0

    def _extract_text_with_positions(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Extrae texto de una página con sus coordenadas.

        Args:
            page_num: Número de página (0-indexed)

        Returns:
            Lista de diccionarios con {text, x, y}
        """
        page = self.reader.pages[page_num]
        text_elements = []

        def visitor_body(text, cm, tm, font_dict, font_size):
            """Función visitor para extraer texto con posición."""
            # cm es la matriz de transformación actual
            # tm es la matriz de texto
            # Posición aproximada del texto
            x = tm[4]  # Coordenada X
            y = tm[5]  # Coordenada Y

            # Limpiar el texto
            text = text.strip()
            if text and len(text) > 0:
                text_elements.append({
                    'text': text,
                    'x': float(x),
                    'y': float(y),
                    'font_size': float(font_size) if font_size else 12
                })

        try:
            page.extract_text(visitor_text=visitor_body)
        except Exception as e:
            print(f"[WARNING] Error al extraer texto de página {page_num}: {e}")

        return text_elements

    def _find_nearest_text(self, field_rect: Tuple[float, float, float, float],
                          text_elements: List[Dict[str, Any]]) -> str:
        """
        Encuentra el texto más cercano a un campo.

        Prioriza texto a la izquierda o arriba del campo.

        Args:
            field_rect: Rectángulo del campo (left, bottom, right, top)
            text_elements: Lista de elementos de texto con posiciones

        Returns:
            Texto más cercano o None
        """
        if not field_rect or not text_elements:
            return None

        field_left, field_bottom, field_right, field_top = field_rect
        field_center_x = (field_left + field_right) / 2
        field_center_y = (field_bottom + field_top) / 2

        # Buscar texto cercano
        candidates = []

        for elem in text_elements:
            text = elem['text']
            x = elem['x']
            y = elem['y']

            # Ignorar texto muy corto o que parece ser un valor de campo
            if len(text) < 2 or text.isdigit():
                continue

            # Calcular distancia al campo
            # Priorizar texto a la izquierda o arriba
            distance = abs(x - field_left) + abs(y - field_center_y)

            # Si el texto está a la izquierda del campo, darle prioridad
            if x < field_left and abs(y - field_center_y) < 50:
                distance *= 0.5  # Reducir distancia para dar prioridad

            # Si el texto está arriba del campo, también es bueno
            elif y > field_top and abs(x - field_center_x) < 100:
                distance *= 0.7

            candidates.append({
                'text': text,
                'distance': distance,
                'x': x,
                'y': y
            })

        # Ordenar por distancia y tomar el más cercano
        if candidates:
            candidates.sort(key=lambda c: c['distance'])
            nearest = candidates[0]

            # Limpiar el texto
            text = nearest['text'].strip()
            # Eliminar dos puntos al final
            text = re.sub(r':$', '', text)
            # Limpiar caracteres especiales innecesarios
            text = re.sub(r'[*_]', '', text)

            return text.strip()

        return None

    def get_fields_with_labels(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene campos con etiquetas detectadas automáticamente.

        Returns:
            Diccionario con campos y sus etiquetas detectadas
        """
        fields = self.get_fields()

        # Extraer texto por página
        page_texts = {}
        for page_num in range(len(self.reader.pages)):
            page_texts[page_num] = self._extract_text_with_positions(page_num)

        # Detectar etiquetas para cada campo
        for field_name, field_data in fields.items():
            page_num = field_data.get('page', 0)
            field_rect = field_data.get('rect')

            label = None
            if field_rect and page_num in page_texts:
                label = self._find_nearest_text(field_rect, page_texts[page_num])

            # Si no encontramos etiqueta, usar el nombre del campo limpio
            if not label or len(label) < 2:
                label = self._clean_field_name(field_name)

            fields[field_name]['label'] = label

        return fields

    def _clean_field_name(self, field_name: str) -> str:
        """
        Limpia el nombre técnico de un campo para hacerlo más legible.

        Args:
            field_name: Nombre técnico del campo

        Returns:
            Nombre limpio y legible
        """
        # Eliminar prefijos comunes
        name = re.sub(r'^(txt|text|field|input|form)_?', '', field_name, flags=re.IGNORECASE)

        # Convertir snake_case y camelCase a espacios
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        name = re.sub(r'[_\-]', ' ', name)

        # Capitalizar
        name = name.strip().title()

        return name if name else field_name

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

        print("\n=== CAMPOS CON ETIQUETAS ===")
        fields = extractor.get_fields_with_labels()
        for name, data in fields.items():
            print(f"\n{data.get('label', name)}:")
            print(f"  Nombre técnico: {name}")
            print(f"  Tipo: {data['type']}")
            if data['options']:
                print(f"  Opciones: {data['options']}")
            if data['required']:
                print(f"  ⚠️  REQUERIDO")
    else:
        print("Uso: python pdf_extractor.py <archivo.pdf>")
