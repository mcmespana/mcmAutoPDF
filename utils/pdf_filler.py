"""
Módulo para rellenar formularios PDF con datos.
"""

from pypdf import PdfReader, PdfWriter
from typing import Dict, Any, List


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

            # Obtener los campos disponibles en el PDF
            pdf_fields = writer.get_fields()
            if not pdf_fields:
                print("[ERROR] El PDF no tiene campos de formulario")
                return False

            print(f"[INFO] PDF tiene {len(pdf_fields)} campos disponibles")
            print(f"[INFO] CSV tiene {len(data)} valores para rellenar")

            # Procesar datos
            processed_data = self._process_data(data)

            # Filtrar solo los datos que corresponden a campos existentes
            valid_data = {}
            invalid_fields = []

            for field_name, value in processed_data.items():
                if field_name in pdf_fields:
                    valid_data[field_name] = value
                else:
                    invalid_fields.append(field_name)

            if invalid_fields:
                print(f"[WARNING] Campos no encontrados en PDF: {', '.join(invalid_fields[:5])}")
                if len(invalid_fields) > 5:
                    print(f"[WARNING] ... y {len(invalid_fields) - 5} más")

            if not valid_data:
                print("[ERROR] Ningún campo del CSV coincide con los campos del PDF")
                return False

            print(f"[INFO] Rellenando {len(valid_data)} campos válidos")

            # Rellenar campos
            try:
                writer.update_form_field_values(valid_data)
                print("[SUCCESS] Campos actualizados correctamente")
            except Exception as e:
                print(f"[ERROR] Error al actualizar campos: {e}")
                # Intentar método alternativo página por página
                print("[INFO] Intentando método alternativo...")
                success = self._fill_page_by_page(writer, valid_data)
                if not success:
                    return False

            # Aplanar si se solicita
            if flatten:
                try:
                    # Flatten anotaciones pero mantener el contenido visible
                    for page in writer.pages:
                        if '/Annots' in page:
                            page.flatten_annotations()
                    print("[INFO] PDF aplanado exitosamente")
                except Exception as e:
                    print(f"[WARNING] Error al aplanar PDF: {e}")

            # Guardar el PDF rellenado
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            print(f"[SUCCESS] PDF guardado en: {output_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Error al rellenar PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _fill_page_by_page(self, writer: PdfWriter, data: Dict[str, Any]) -> bool:
        """
        Intenta rellenar campos página por página como fallback.

        Args:
            writer: PdfWriter con las páginas
            data: Datos procesados para rellenar

        Returns:
            True si tuvo éxito
        """
        try:
            filled_count = 0
            for page_num, page in enumerate(writer.pages):
                try:
                    writer.update_page_form_field_values(
                        page,
                        data,
                        auto_regenerate=True
                    )
                    filled_count += 1
                except Exception as e:
                    print(f"[WARNING] Error en página {page_num}: {e}")
                    continue

            if filled_count > 0:
                print(f"[SUCCESS] Rellenadas {filled_count} páginas")
                return True
            else:
                print("[ERROR] No se pudo rellenar ninguna página")
                return False

        except Exception as e:
            print(f"[ERROR] Error en método alternativo: {e}")
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
            value_upper = str(value).upper()
            if value_upper in ['__YES__', 'YES', 'SÍ', 'SI', 'TRUE', '1', 'X']:
                processed[field_name] = '/Yes'
            elif value_upper in ['__NO__', 'NO', 'FALSE', '0', '']:
                processed[field_name] = '/Off'
            else:
                # Valor normal de texto
                processed[field_name] = str(value)

        return processed

    def get_fillable_fields(self) -> List[str]:
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
