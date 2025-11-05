# PDF Form Filler 📄

Utilidad para extraer campos de PDFs, generar plantillas CSV y rellenarlos automáticamente.

## 🚀 Características

### MVP (v0.2) - Mejorado
- ✅ Extraer campos de formularios PDF
- ✅ **NUEVO**: Mapeo inteligente de campos con descripciones automáticas
- ✅ **NUEVO**: CSV con nombres descriptivos en lugar de técnicos
- ✅ **NUEVO**: Editor rápido web - rellena PDFs sin CSV
- ✅ **MEJORADO**: Sistema de llenado de PDFs más robusto
- ✅ Interfaz web con Streamlit

### Próximamente
- 🔜 Soporte para tablas (múltiples filas)
- 🔜 Sistema de plantillas guardadas
- 🔜 Validaciones de campos

## 📦 Instalación

```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Opción 1: Streamlit (Recomendado)
```bash
streamlit run app.py
```

La aplicación tiene 3 modos de uso:

#### 🔍 Extraer Campos
1. Sube tu PDF con formulario
2. Visualiza los campos detectados con descripciones automáticas
3. Descarga plantilla CSV (con nombres descriptivos o técnicos)
4. Edita el CSV con tus datos

#### ✍️ Rellenar PDF
1. Sube el PDF original
2. Sube el CSV editado (y archivo MAPEO.txt si usaste nombres descriptivos)
3. Descarga el PDF rellenado

#### ⚡ Editor Rápido
¡Todo en uno! Sube tu PDF y edita los campos directamente en la web. Sin CSV necesario.

### Opción 2: CLI (WIP)
```bash
# Extraer campos
python cli.py extract input.pdf --output campos.csv

# Rellenar PDF
python cli.py fill input.pdf datos.csv --output resultado.pdf
```

## 📁 Estructura

```
pdf-filler/
├── app.py                 # Aplicación Streamlit
├── requirements.txt       
├── utils/
│   ├── pdf_extractor.py  # Extracción de campos
│   ├── csv_handler.py    # Manejo de CSV
│   └── pdf_filler.py     # Relleno de PDFs
└── temp/                 # Archivos temporales
```

## 🔧 Stack tecnológico

- **pypdf**: Lectura y escritura de PDFs con campos
- **streamlit**: Interfaz web
- **pandas**: Manipulación de CSV

## 📝 Formato CSV

### CSV con nombres técnicos (clásico)
```csv
txt_field_1,txt_field_2,checkbox_1
Juan,Pérez,__YES__
```

### CSV con nombres descriptivos (nuevo)
```csv
Nombre,Apellido,Acepto términos (Sí/No)
Juan,Pérez,__YES__
```

Cuando usas nombres descriptivos, también se genera un archivo `_MAPEO.txt` que traduce los nombres descriptivos a los nombres técnicos del PDF. Asegúrate de subir ambos archivos al rellenar.

### Valores especiales
- Checkboxes: `__YES__` o `__NO__`
- Campos vacíos: déjalos en blanco

Para campos de tabla (próximamente):
```csv
nombre_entidad,campo_tabla_1,campo_tabla_2
Mi Entidad,Valor fila 1,Otro valor fila 1
Mi Entidad,Valor fila 2,Otro valor fila 2
```

## 🌐 Deploy en Streamlit Cloud

1. Sube el repo a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo
4. ¡Listo!

## 📄 Licencia

MIT
