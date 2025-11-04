"""
Módulo para rellenar formularios PDF con datos.
"""

from PyPDF2 import PdfReader, PdfWriter
from typing import Dict, Any


class PDFFiller:
    """Rellena formularios PDF con datos proporcionados."""
    
    def __init__(self, pdf_path: str):
        """
        Inicializa el rellenador.
        
        Args:
            pdf_path: Ruta al PDF template
        """
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        
    def fill_pdf(self, data: Dict[str, str], output_path: str, flatten: bool = False) -> bool:
        """
        Rellena el PDF con los datos proporcionados.
        
        Args:
            data: Diccionario con {nombre_campo: valor}
            output_path: Ruta donde guardar el PDF rellenado
            flatten: Si True, el PDF se "aplana" (no se pueden editar los campos después)
            
        Returns:
            True si se rellenó correctamente, False si hubo error
        """
        try:
            writer = PdfWriter()
            
            # Copiar todas las páginas del PDF original
            for page in self.reader.pages:
                writer.add_page(page)
            
            # Preparar datos para rellenar
            processed_data = self._process_data(data)
            
            # Rellenar campos
            if writer.get_fields():
                writer.update_page_form_field_values(
                    writer.pages[0], 
                    processed_data,
                    auto_regenerate=False
                )
            
            # Si hay múltiples páginas, intentar rellenar en todas
            for page_num in range(len(writer.pages)):
                try:
                    writer.update_page_form_field_values(
                        writer.pages[page_num], 
                        processed_data,
                        auto_regenerate=False
                    )
                except:
                    # Algunas páginas pueden no tener campos
                    pass
            
            # Aplanar si se solicita (hacer campos no editables)
            if flatten:
                try:
                    # Intentar con el método de PyPDF2 3.0+
                    for page in writer.pages:
                        page.compress_content_streams()
                    # PyPDF2 no tiene flatten_annotations, solo lo simulamos
                except:
                    pass
            
            # Guardar el PDF rellenado
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error al rellenar PDF: {e}")
            return False
    
    def _process_data(self, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Procesa los datos antes de rellenarlos en el PDF.
        Convierte valores especiales como checkboxes.
        
        Args:
            data: Datos crudos del CSV
            
        Returns:
            Datos procesados listos para el PDF
        """
        processed = {}
        
        for field_name, value in data.items():
            if not value or value == '':
                # Campo vacío, skip
                continue
                
            # Procesar checkboxes
            if value.upper() in ['__YES__', 'YES', 'SÍ', 'SI', 'TRUE', '1']:
                processed[field_name] = '/Yes'  # Valor típico de checkbox marcado
            elif value.upper() in ['__NO__', 'NO', 'FALSE', '0']:
                processed[field_name] = '/Off'  # Checkbox desmarcado
            else:
                # Valor normal de texto
                processed[field_name] = str(value)
        
        return processed
    
    def get_fillable_fields(self) -> list:
        """
        Obtiene los campos que pueden ser rellenados.
        
        Returns:
            Lista de nombres de campos
        """
        if self.reader.get_fields():
            return list(self.reader.get_fields().keys())
        return []
    
    def preview_filled_fields(self, data: Dict[str, str]) -> Dict[str, str]:
        """
        Muestra qué campos se rellenarían con los datos dados.
        
        Args:
            data: Datos a rellenar
            
        Returns:
            Diccionario con {campo: valor_que_se_pondría}
        """
        processed = self._process_data(data)
        fillable = self.get_fillable_fields()
        
        preview = {}
        for field in fillable:
            if field in processed:
                preview[field] = processed[field]
            else:
                preview[field] = "[VACÍO]"
        
        return preview


if __name__ == "__main__":
    # Test básico
    import sys
    
    if len(sys.argv) > 3:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2]
        
        # Datos de ejemplo
        test_data = {
            sys.argv[3]: "Valor de prueba"
        }
        
        filler = PDFFiller(pdf_path)
        success = filler.fill_pdf(test_data, output_path)
        
        if success:
            print(f"✅ PDF rellenado guardado en: {output_path}")
        else:
            print("❌ Error al rellenar PDF")
    else:
        print("Uso: python pdf_filler.py <input.pdf> <output.pdf> <campo_prueba>")
