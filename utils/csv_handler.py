"""
Módulo para generar y leer plantillas CSV.
"""

import pandas as pd
from typing import Dict, List, Any


class CSVHandler:
    """Maneja la generación y lectura de plantillas CSV."""

    @staticmethod
    def generate_template(fields: Dict[str, Any], output_path: str) -> None:
        """
        Genera un CSV template usando las etiquetas detectadas de los campos.

        Args:
            fields: Diccionario de campos {nombre: {tipo, valor, opciones, label, ...}}
            output_path: Ruta donde guardar el CSV
        """
        # Crear mapeo de etiquetas a nombres técnicos
        label_to_technical = {}
        labels = []

        for field_name, field_data in fields.items():
            label = field_data.get('label', field_name)

            # Si hay duplicados, agregar número
            original_label = label
            counter = 2
            while label in labels:
                label = f"{original_label} {counter}"
                counter += 1

            labels.append(label)
            label_to_technical[label] = field_name

        # Crear fila de ejemplo
        example_row = {}
        for label, field_name in label_to_technical.items():
            field_data = fields[field_name]
            field_type = field_data['type']

            if field_type == 'checkbox':
                example_row[label] = '__YES__'
            elif field_type == 'dropdown' and field_data['options']:
                example_row[label] = field_data['options'][0]
            else:
                example_row[label] = ''

        # Crear DataFrame y guardar
        df = pd.DataFrame([example_row])
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        # Guardar mapeo en archivo adicional para referencia
        mapping_path = output_path.replace('.csv', '_mapeo.txt')
        with open(mapping_path, 'w', encoding='utf-8') as f:
            f.write("=== MAPEO DE CAMPOS ===\n")
            f.write("Mapeo automático de etiquetas a nombres técnicos del PDF\n\n")
            for label, tech_name in label_to_technical.items():
                f.write(f"{label} → {tech_name}\n")

    @staticmethod
    def generate_template_with_info(fields: Dict[str, Any], output_path: str) -> None:
        """
        Genera un CSV template con información adicional sobre cada campo.

        Args:
            fields: Diccionario de campos
            output_path: Ruta donde guardar el CSV
        """
        # Generar el CSV normal
        CSVHandler.generate_template(fields, output_path)

        # Añadir archivo de información adicional
        info_path = output_path.replace('.csv', '_info.txt')
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write("=== INFORMACIÓN DE CAMPOS ===\n\n")

            for field_name, field_data in fields.items():
                label = field_data.get('label', field_name)

                f.write(f"📝 {label}\n")
                f.write(f"   Nombre técnico: {field_name}\n")
                f.write(f"   Tipo: {field_data['type']}\n")

                if field_data.get('required'):
                    f.write(f"   ⚠️  CAMPO REQUERIDO\n")

                if field_data['type'] == 'checkbox':
                    f.write(f"   Valores: __YES__ o __NO__\n")
                elif field_data['type'] == 'dropdown' and field_data['options']:
                    f.write(f"   Opciones: {', '.join(field_data['options'])}\n")

                f.write("\n")

    @staticmethod
    def read_csv_with_mapping(csv_path: str, mapping_path: str) -> Dict[str, str]:
        """
        Lee un CSV y lo convierte usando el archivo de mapeo.

        Args:
            csv_path: Ruta al CSV con datos
            mapping_path: Ruta al archivo de mapeo

        Returns:
            Diccionario con nombres técnicos -> valores
        """
        # Leer mapeo
        label_to_technical = {}
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '→' in line:
                        parts = line.split('→')
                        if len(parts) == 2:
                            label = parts[0].strip()
                            tech_name = parts[1].strip()
                            label_to_technical[label] = tech_name
        except Exception as e:
            raise ValueError(f"Error al leer archivo de mapeo: {e}")

        # Leer CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        if len(df) == 0:
            return {}

        # Obtener primera fila
        row_data = df.iloc[0].to_dict()

        # Convertir a nombres técnicos
        technical_data = {}
        for label, value in row_data.items():
            tech_name = label_to_technical.get(label, label)

            # Limpiar valores NaN
            if pd.isna(value):
                value = ''
            else:
                value = str(value)

            if value and value != '':
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
