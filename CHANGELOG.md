# 📝 Changelog

Todos los cambios notables del proyecto se documentarán aquí.

## [0.1.0] - MVP - 2025-11-04

### ✨ Características iniciales

- ✅ Extracción de campos de formularios PDF
- ✅ Generación de plantillas CSV
- ✅ Archivo INFO.txt con detalles de campos
- ✅ Rellenado de PDFs con datos de CSV
- ✅ Interfaz web con Streamlit
- ✅ Soporte para campos de texto, checkboxes y dropdowns
- ✅ Opción de aplanar PDF (hacer campos no editables)
- ✅ Script de testing para análisis de PDFs

### 📋 Tipos de campo soportados

- Text fields
- Checkboxes
- Dropdown lists
- Radio buttons

### 🚧 Limitaciones conocidas

- No soporta tablas / campos repetitivos (próximamente)
- No soporta PDFs escaneados sin campos interactivos
- No recalcula campos con fórmulas
- No soporta firma digital

### 🔧 Stack tecnológico

- Python 3.8+
- Streamlit 1.32.0
- pypdf 4.1.0
- pandas 2.2.1

---

## [Próxima versión] - Fase 2: Tablas

### 🔮 Planeado

- [ ] Detección automática de campos de tabla
- [ ] Soporte para CSV multi-fila
- [ ] Checkbox "Tiene tablas" en UI
- [ ] Opción de generar 2 CSVs (general + tablas)
- [ ] Sistema de plantillas guardadas
- [ ] Validaciones mejoradas
- [ ] Preview del PDF antes de descargar

---

## Formato

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
