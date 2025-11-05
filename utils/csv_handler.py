"""
Módulo para generar y leer plantillas CSV.
"""

import pandas as pd
import os
from typing import Dict, List, Any


class CSVHandler:
    """Maneja la generación y lectura de plantillas CSV."""
    
    @staticmethod
    def generate_template(fields: Dict[str, Any], output_path: str) -> None:
        """
        Genera un CSV template con los nombres de los campos.
        
        Args:
            fields: Diccionario de campos {nombre: {tipo, valor, opciones, ...}}
            output_path: Ruta donde guardar el CSV
        """
        # Crear DataFrame con los nombres de campos como columnas
        field_names = list(fields.keys())
        
        # Fila de ejemplo vacía
        df = pd.DataFrame(columns=field_names)
        
        # Añadir una fila de ejemplo con valores por defecto según tipo
        example_row = {}
        for field_name, field_data in fields.items():
            field_type = field_data['type']
            
            if field_type == 'checkbox':
                example_row[field_name] = '__YES__'  # o '__NO__'
            elif field_type == 'dropdown' and field_data['options']:
                example_row[field_name] = field_data['options'][0]
            else:
                example_row[field_name] = ''
        
        df = pd.DataFrame([example_row])
        
        # Guardar CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    @staticmethod
    def generate_template_with_info(fields: Dict[str, Any], output_path: str) -> None:
        """
        Genera un CSV template con información adicional sobre cada campo.
        Incluye comentarios sobre tipo de campo y opciones.

        Args:
            fields: Diccionario de campos
            output_path: Ruta donde guardar el CSV
        """
        # Crear el CSV normal
        CSVHandler.generate_template(fields, output_path)

        # Añadir archivo de información adicional
        info_path = output_path.replace('.csv', '_INFO.txt')
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write("=== INFORMACIÓN DE CAMPOS ===\n\n")

            for field_name, field_data in fields.items():
                # Mostrar descripción sugerida si existe
                if 'suggested_description' in field_data:
                    f.write(f"📝 {field_data['suggested_description']}\n")
                    f.write(f"   Nombre técnico: {field_name}\n")
                else:
                    f.write(f"Campo: {field_name}\n")

                f.write(f"   Tipo: {field_data['type']}\n")

                if field_data.get('required'):
                    f.write(f"   ⚠️  CAMPO REQUERIDO\n")

                if field_data['type'] == 'checkbox':
                    f.write(f"   Valores: __YES__ o __NO__\n")
                elif field_data['type'] == 'dropdown' and field_data['options']:
                    f.write(f"   Opciones: {', '.join(field_data['options'])}\n")

                f.write("\n")

    @staticmethod
    def generate_descriptive_template(fields: Dict[str, Any], output_path: str) -> None:
        """
        Genera un CSV con nombres de columnas descriptivos en lugar de técnicos.

        Args:
            fields: Diccionario de campos con suggested_description
            output_path: Ruta donde guardar el CSV
        """
        # Crear mapeo de descripción -> nombre técnico
        mapping = {}
        descriptive_names = []

        for field_name, field_data in fields.items():
            desc = field_data.get('suggested_description', field_name)
            # Si hay duplicados, agregar el nombre técnico entre paréntesis
            if desc in descriptive_names:
                desc = f"{desc} ({field_name})"
            descriptive_names.append(desc)
            mapping[desc] = field_name

        # Crear DataFrame con nombres descriptivos
        example_row = {}
        for field_name, field_data in fields.items():
            field_type = field_data['type']
            desc = field_data.get('suggested_description', field_name)

            # Ajustar si hay duplicado
            if desc in example_row and desc != field_name:
                desc = f"{desc} ({field_name})"

            if field_type == 'checkbox':
                example_row[desc] = '__YES__'
            elif field_type == 'dropdown' and field_data['options']:
                example_row[desc] = field_data['options'][0]
            else:
                example_row[desc] = ''

        df = pd.DataFrame([example_row])
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        # Guardar archivo de mapeo
        mapping_path = output_path.replace('.csv', '_MAPEO.txt')
        with open(mapping_path, 'w', encoding='utf-8') as f:
            f.write("=== MAPEO DE CAMPOS ===\n\n")
            f.write("Descripción → Nombre técnico en PDF\n")
            f.write("-" * 60 + "\n\n")

            for desc, tech_name in mapping.items():
                f.write(f"{desc}\n  → {tech_name}\n\n")
    
    @staticmethod
    def read_data(csv_path: str) -> List[Dict[str, str]]:
        """
        Lee datos de un CSV.
        
        Para el MVP, solo usamos la primera fila.
        En el futuro, múltiples filas servirán para tablas.
        
        Args:
            csv_path: Ruta al CSV con datos
            
        Returns:
            Lista de diccionarios (una entrada por fila)
        """
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # Convertir a lista de diccionarios
        data = df.to_dict('records')
        
        # Limpiar valores NaN
        for row in data:
            for key in row:
                if pd.isna(row[key]):
                    row[key] = ''
                else:
                    row[key] = str(row[key])
        
        return data
    
    @staticmethod
    def get_first_row_data(csv_path: str) -> Dict[str, str]:
        """
        Lee solo la primera fila del CSV (para campos normales).

        Args:
            csv_path: Ruta al CSV

        Returns:
            Diccionario con datos de la primera fila
        """
        data = CSVHandler.read_data(csv_path)
        return data[0] if data else {}

    @staticmethod
    def read_descriptive_csv(csv_path: str, mapping_path: str = None) -> Dict[str, str]:
        """
        Lee un CSV con nombres descriptivos y lo convierte a nombres técnicos.

        Args:
            csv_path: Ruta al CSV con nombres descriptivos
            mapping_path: Ruta al archivo de mapeo (opcional, se busca automáticamente)

        Returns:
            Diccionario con nombres técnicos -> valores
        """
        # Si no se proporciona mapeo, buscar archivo _MAPEO.txt
        if mapping_path is None:
            mapping_path = csv_path.replace('.csv', '_MAPEO.txt')

        # Si no existe el archivo de mapeo, asumir que es CSV normal
        if not os.path.exists(mapping_path):
            return CSVHandler.get_first_row_data(csv_path)

        # Leer mapeo
        mapping = {}
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                current_desc = None
                for line in lines:
                    line = line.strip()
                    if line.startswith('→'):
                        # Línea con nombre técnico
                        tech_name = line.replace('→', '').strip()
                        if current_desc:
                            mapping[current_desc] = tech_name
                    elif line and not line.startswith('=') and not line.startswith('-') and 'Descripción' not in line:
                        # Línea con descripción
                        current_desc = line
        except Exception as e:
            print(f"[WARNING] No se pudo leer archivo de mapeo: {e}")
            return CSVHandler.get_first_row_data(csv_path)

        # Leer CSV con nombres descriptivos
        descriptive_data = CSVHandler.get_first_row_data(csv_path)

        # Convertir a nombres técnicos
        technical_data = {}
        for desc, value in descriptive_data.items():
            tech_name = mapping.get(desc, desc)  # Si no hay mapeo, usar el nombre original
            technical_data[tech_name] = value

        return technical_data
    
    @staticmethod
    def validate_csv(csv_path: str, expected_fields: List[str]) -> Dict[str, Any]:
        """
        Valida que el CSV contenga los campos esperados.
        
        Args:
            csv_path: Ruta al CSV
            expected_fields: Lista de campos que debe contener
            
        Returns:
            Diccionario con resultado de validación
        """
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            csv_fields = list(df.columns)
            
            missing = set(expected_fields) - set(csv_fields)
            extra = set(csv_fields) - set(expected_fields)
            
            return {
                'valid': len(missing) == 0,
                'missing_fields': list(missing),
                'extra_fields': list(extra),
                'num_rows': len(df)
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }


if __name__ == "__main__":
    # Test básico
    print("Módulo CSV Handler")
    print("Uso en app.py")
