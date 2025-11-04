# PDF Form Filler 📄

Utilidad para extraer campos de PDFs, generar plantillas CSV y rellenarlos automáticamente.

## 🚀 Características

### MVP (v0.1)
- ✅ Extraer campos de formularios PDF
- ✅ Generar plantilla CSV con los campos detectados
- ✅ Rellenar PDF con datos desde CSV
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

```csv
nombre_campo_1,nombre_campo_2,nombre_campo_3
valor1,valor2,valor3
```

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
