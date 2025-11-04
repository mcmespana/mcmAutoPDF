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
                f.write(f"Campo: {field_name}\n")
                f.write(f"  Tipo: {field_data['type']}\n")
                
                if field_data.get('required'):
                    f.write(f"  ⚠️  CAMPO REQUERIDO\n")
                
                if field_data['type'] == 'checkbox':
                    f.write(f"  Valores: __YES__ o __NO__\n")
                elif field_data['type'] == 'dropdown' and field_data['options']:
                    f.write(f"  Opciones: {', '.join(field_data['options'])}\n")
                
                f.write("\n")
    
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
