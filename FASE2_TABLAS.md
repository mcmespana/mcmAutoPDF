# 📋 NOTAS PARA FASE 2: Soporte de Tablas

## 🎯 Objetivo
Implementar soporte para campos que se repiten (tablas) en los PDFs.

## 📝 Casos de uso típicos

### Ejemplo 1: Tabla de gastos
```
Núm. factura | Concepto | Importe
-------------|----------|--------
F001         | Material | 500€
F002         | Viaje    | 300€
```

### Ejemplo 2: Tabla de actividades
```
Actividad | Fecha | Participantes
----------|-------|---------------
Campamento| 15/06 | 50
Formación | 20/07 | 30
```

## 🔧 Implementación propuesta

### 1. Detección de campos de tabla

**En `pdf_extractor.py`:**
```python
def detect_table_fields(self, fields: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Detecta patrones como:
    - actividad_1, actividad_2, actividad_3
    - row_1_col_1, row_1_col_2, row_2_col_1
    - factura_numero_1, factura_numero_2
    """
    # Agrupar campos por patrón
    # Usar regex para detectar números al final
    # Retornar: {'actividad': ['actividad_1', 'actividad_2', ...]}
```

### 2. CSV con múltiples filas

**Formato propuesto:**
```csv
# Campos generales (se copian de fila 1)
nombre_entidad,NIF,

# Campos de tabla (cada fila = una entrada)
factura_numero,factura_concepto,factura_importe

Mi Asociación,B12345,F001,Material,500
Mi Asociación,B12345,F002,Viaje,300
Mi Asociación,B12345,F003,Comida,200
```

**Lógica:**
- Fila 1 → Campos generales
- Fila 2+ → Entradas de tabla

### 3. Checkbox en UI

**En `app.py` - Tab 1:**
```python
has_tables = st.checkbox(
    "📊 Este PDF tiene tablas/campos repetitivos",
    value=False,
    help="Activa esto si el PDF tiene campos que se repiten (ej: facturas, actividades)"
)

if has_tables:
    st.info("Se generará un CSV que permite múltiples filas para las tablas")
    
    # Permitir al usuario marcar qué campos son de tabla
    table_fields = st.multiselect(
        "Selecciona los campos que forman parte de tablas",
        options=list(fields.keys())
    )
```

### 4. Generación CSV para tablas

**En `csv_handler.py`:**
```python
@staticmethod
def generate_table_template(
    general_fields: List[str],
    table_fields: List[str],
    output_path: str
) -> None:
    """
    Genera CSV con:
    - Columnas generales (se llenan una vez)
    - Columnas de tabla (se llenan en cada fila)
    """
```

### 5. Rellenado de PDFs con tablas

**En `pdf_filler.py`:**
```python
def fill_pdf_with_tables(
    self, 
    general_data: Dict[str, str],
    table_data: List[Dict[str, str]],
    output_path: str
) -> bool:
    """
    Rellena:
    1. Campos generales (de general_data)
    2. Campos de tabla fila por fila (de table_data)
    
    Si hay 3 filas de tabla_data, rellena:
    - factura_numero_1, factura_numero_2, factura_numero_3
    """
```

## 🎨 Opción alternativa: 2 CSVs

En vez de un CSV con formato especial, generar:

1. **general.csv** - Una fila con campos generales
2. **tablas.csv** - Múltiples filas para tablas

Ventajas:
- ✅ Más claro para el usuario
- ✅ Más fácil de editar en Excel

Desventajas:
- ❌ Dos archivos en vez de uno
- ❌ Hay que coordinar ambos

## 📌 Decisiones pendientes

- [ ] ¿Un CSV o dos CSVs?
- [ ] ¿Auto-detectar tablas o manual siempre?
- [ ] ¿Límite máximo de filas de tabla?
- [ ] ¿Validar que todas las filas tengan los mismos campos de tabla?

## 🚀 Próximos pasos

1. Implementar `detect_table_fields()` con detección básica
2. Añadir checkbox en UI
3. Probar con PDFs reales (Anexo III, Anexo II)
4. Iterar según feedback

---

**Notas del usuario:**
- Opción A de CSV (una fila por entrada de tabla)
- Campos generales se leen solo de fila 1
- Considerar checkbox para activar modo tabla
- Posible opción de 2 CSVs (uno general, uno para tablas)
