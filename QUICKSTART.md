# 🚀 Guía de Inicio Rápido

## ⚡ Instalación Express

```bash
# 1. Clonar o descargar el proyecto
cd pdf-filler

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Lanzar la aplicación
streamlit run app.py
```

La app se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 📖 Cómo usar (MVP)

### ✅ Paso 1: Extraer campos

1. Abre la app (tab "🔍 Extraer Campos")
2. Sube tu PDF con formulario
3. Verás los campos detectados
4. Click en "📥 Generar y descargar CSV"
5. Descarga `plantilla.csv` (y opcionalmente `INFO.txt`)

### ✅ Paso 2: Editar CSV

1. Abre `plantilla.csv` en Excel / LibreOffice / cualquier editor
2. Rellena la **primera fila** con tus datos
3. Para checkboxes usa: `__YES__` o `__NO__`
4. Guarda el archivo

### ✅ Paso 3: Rellenar PDF

1. Ve al tab "✍️ Rellenar PDF"
2. Sube:
   - PDF original
   - CSV editado
3. (Opcional) Marca "Aplanar PDF" si quieres hacerlo no-editable
4. Click "✨ Rellenar PDF"
5. Descarga tu PDF rellenado

---

## 🧪 Testing rápido

Probar extracción con tus PDFs:

```bash
# Un PDF específico
python test.py /ruta/a/tu/archivo.pdf

# Todos los PDFs de una carpeta
python test.py /ruta/a/carpeta/
```

---

## ⚠️ Limitaciones MVP

- ❌ **No soporta tablas todavía** (campos repetitivos)
- ❌ No hay OCR para PDFs escaneados
- ❌ No puede firmar digitalmente
- ❌ Campos calculados no se actualizan

**Próximamente en Fase 2:**
- ✅ Soporte para tablas/campos repetitivos
- ✅ CSV multi-fila
- ✅ Sistema de plantillas guardadas

---

## 🐛 Solución de problemas

**"No se detectan campos"**
→ Tu PDF no tiene campos interactivos. Necesita ser un formulario PDF, no un PDF escaneado.

**"Error al rellenar PDF"**
→ Verifica que los nombres de columnas del CSV coincidan exactamente con los del template.

**"Faltan campos en el CSV"**
→ Regenera el template desde el PDF más reciente.

---

## 📦 Deploy a Streamlit Cloud

### Preparar repo

```bash
# 1. Inicializar git (si no lo tienes)
git init
git add .
git commit -m "MVP PDF Filler"

# 2. Crear repo en GitHub
# (hazlo desde github.com)

# 3. Subir código
git remote add origin https://github.com/TU_USUARIO/pdf-filler.git
git push -u origin main
```

### Deploy

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu GitHub
3. Selecciona el repo `pdf-filler`
4. Branch: `main`
5. Main file: `app.py`
6. ¡Deploy! 🚀

En 2-3 minutos tendrás tu app online en:
`https://TU_USUARIO-pdf-filler.streamlit.app`

---

## 💡 Tips

**Para campos de texto largo:**
En el CSV, puedes usar saltos de línea escribiendo literalmente `\n` donde quieras el salto.

**Para dropdowns:**
Asegúrate de usar exactamente una de las opciones que aparece en el INFO.txt

**Checkboxes:**
Usa `__YES__` para marcar, `__NO__` o déjalo vacío para desmarcar.

---

## 📞 Soporte

- 📖 Lee `README.md` para más detalles
- 🔮 Consulta `FASE2_TABLAS.md` para el roadmap
- 🐛 Si hay bugs, documéntalos con el PDF que falla

---

**¡Listo para usar!** 🎉
