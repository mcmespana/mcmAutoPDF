# PDF Form Filler 📄

Aplicación para **extraer campos de PDFs** con **detección automática de etiquetas** y **rellenarlos con datos de CSV**.

## 🎯 ¿Qué hace esta aplicación?

### ✅ Funcionalidades actuales (v0.3)

1. **Extracción inteligente de campos PDF**
   - Detecta todos los campos de formulario en un PDF
   - **NUEVO:** Extrae automáticamente el texto cercano a cada campo para usarlo como etiqueta
   - Identifica el tipo de cada campo (texto, checkbox, dropdown, radio)
   - Genera plantilla CSV con nombres legibles basados en las etiquetas detectadas

2. **Generación automática de CSV**
   - Crea CSV con etiquetas detectadas automáticamente
   - Genera archivo de mapeo (etiqueta → nombre técnico)
   - Opcionalmente incluye archivo INFO con detalles de cada campo
   - Incluye valores de ejemplo para cada tipo de campo

3. **Relleno robusto de PDFs**
   - Lee CSV y mapeo para traducir etiquetas a nombres técnicos
   - Rellena campos de forma inteligente con manejo de errores mejorado
   - Soporte para checkboxes, dropdowns, campos de texto
   - Método de fallback página por página
   - Opción de aplanar PDF (hacer campos no editables)

4. **Editor web interactivo**
   - Modo rápido: sube PDF y edita campos directamente en el navegador
   - Sin necesidad de CSV para ediciones simples

### ❌ Lo que NO hace (aún)

- ❌ **No soporta tablas** (campos repetitivos/múltiples filas) - Próximamente en Fase 2
- ❌ No valida tipos de datos (puedes poner texto en un campo numérico)
- ❌ No maneja PDFs escaneados (solo PDFs con campos interactivos)
- ❌ No soporta XFA forms completamente (Adobe LiveCycle con XFA dinámico limitado)

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## 📖 Uso

### Streamlit (Interfaz web)

```bash
streamlit run app.py
```

### Flujo de trabajo

#### 1. Extraer campos del PDF
- Sube tu PDF con formulario
- La app detecta automáticamente las etiquetas leyendo el texto cercano a cada campo
- Descarga: `plantilla.csv`, `mapeo.txt`, y opcionalmente `info.txt`

#### 2. Editar el CSV
- Abre `plantilla.csv` con Excel, Google Sheets, etc.
- Las columnas tienen nombres legibles (etiquetas detectadas)
- Rellena la primera fila con tus datos
- Guarda el archivo

#### 3. Rellenar el PDF
- Sube el PDF original
- Sube el CSV editado
- **IMPORTANTE:** Sube también el archivo `mapeo.txt`
- Descarga el PDF rellenado

## 📁 Estructura del proyecto

```
mcmAutoPDF/
├── app.py                      # Aplicación Streamlit
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── pdf_extractor.py       # Extracción de campos + detección de etiquetas
│   ├── csv_handler.py         # Generación y lectura de CSV
│   └── pdf_filler.py          # Relleno de PDFs
└── README.md
```

## 🔧 Stack tecnológico

- **pypdf** (>= 6.1.0): Manipulación de PDFs, extracción de texto posicional
- **streamlit** (>= 1.28.0): Interfaz web
- **pandas** (>= 2.0.0): Manejo de CSV

## 📝 Formatos

### CSV generado
```csv
Nombre,Apellido,Correo electrónico,Acepto términos
Juan,Pérez,juan@example.com,__YES__
```

### Archivo de mapeo (mapeo.txt)
```
=== MAPEO DE CAMPOS ===
Nombre → txt_field_1
Apellido → txt_field_2
Correo electrónico → email_field
Acepto términos → checkbox_terms
```

### Valores especiales
- **Checkboxes:** `__YES__` (marcado) o `__NO__` (desmarcado)
- **Campos vacíos:** déjalos en blanco
- **Dropdowns:** usa exactamente uno de los valores disponibles

## 🔍 Detección de etiquetas

La aplicación usa un algoritmo de detección posicional:

1. Extrae las coordenadas de cada campo del PDF
2. Extrae todo el texto de la página con sus coordenadas
3. Busca el texto más cercano a cada campo (prioriza izquierda y arriba)
4. Limpia el texto (elimina `:`, `*`, etc.)
5. Usa ese texto como etiqueta del campo

**Si no encuentra texto cercano:** usa el nombre técnico del campo limpio (ej: `txt_field_1` → `Field 1`)

## 🐛 Solución de problemas

### El PDF no se rellena correctamente
- **Causa:** El archivo de mapeo no coincide con el CSV
- **Solución:** Asegúrate de usar el archivo `mapeo.txt` generado junto con el CSV

### No se detectan campos
- **Causa:** El PDF no tiene campos interactivos (puede ser un PDF escaneado)
- **Solución:** Usa un PDF con formulario interactivo (AcroForm)

### Las etiquetas detectadas no son correctas
- **Causa:** El texto en el PDF no está bien posicionado o no existe
- **Solución:** Edita el CSV manualmente - las columnas son las etiquetas

### Error al rellenar algunos campos
- **Causa:** El tipo de dato no coincide o el formato es incorrecto
- **Solución:** Revisa los logs en la interfaz web para ver qué campos fallaron

## 📚 Tipos de PDF soportados

### ✅ Soportados
- **AcroForms:** PDFs con campos de formulario estándar
- **Adobe LiveCycle (AcroForm-based):** Formularios de LiveCycle que usan AcroForms

### ⚠️ Soporte limitado
- **XFA estático:** Funciona parcialmente, depende de cómo esté implementado
- **XFA dinámico:** No soportado (pypdf tiene limitaciones con XFA)

### ❌ No soportados
- PDFs escaneados sin campos interactivos
- PDFs con solo campos de firma digital
- Formularios web embebidos en PDF

## 🗺️ Roadmap

### Fase 2 (Próximamente)
- [ ] Soporte para tablas (campos repetitivos)
- [ ] Múltiples filas en CSV para rellenar tablas
- [ ] Detección automática de campos de tabla

### Fase 3 (Futuro)
- [ ] Validación de tipos de datos
- [ ] Plantillas guardadas
- [ ] Procesamiento por lotes (múltiples PDFs)
- [ ] API REST

## 📄 Licencia

MIT

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor abre un issue primero para discutir los cambios que te gustaría hacer.

---

**Versión actual:** v0.3 - Refactorizado con detección automática de etiquetas
