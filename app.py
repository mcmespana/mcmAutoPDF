"""
PDF Form Filler - Aplicación Streamlit
"""

import streamlit as st
import os
import tempfile
from pathlib import Path

from utils import PDFExtractor, CSVHandler, PDFFiller


# Configuración de la página
st.set_page_config(
    page_title="PDF Form Filler",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Función principal de la aplicación."""
    
    st.title("📄 PDF Form Filler")
    st.markdown("*Extrae campos de PDFs, genera plantillas CSV y rellena formularios automáticamente*")
    
    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Cómo usar")
        st.markdown("""
        ### Paso 1: Extraer campos
        1. Sube tu PDF
        2. Descarga la plantilla CSV
        
        ### Paso 2: Rellenar PDF
        1. Edita el CSV con tus datos
        2. Sube PDF + CSV
        3. Descarga el PDF rellenado
        
        ---
        
        **Versión:** MVP 0.1  
        **Soporte para tablas:** Próximamente 🔜
        """)
        
        st.info("💡 Para checkboxes usa: **__YES__** o **__NO__**")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["🔍 Extraer Campos", "✍️ Rellenar PDF", "⚡ Editor Rápido"])
    
    # TAB 1: EXTRAER CAMPOS
    with tab1:
        st.header("Paso 1: Extraer campos del PDF")
        st.markdown("Sube un PDF con formulario para extraer sus campos y generar una plantilla CSV.")
        
        pdf_file = st.file_uploader(
            "Sube tu PDF",
            type=['pdf'],
            key='extract_pdf',
            help="Solo PDFs con campos de formulario interactivos"
        )
        
        if pdf_file:
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                tmp_pdf.write(pdf_file.read())
                tmp_pdf_path = tmp_pdf.name
            
            try:
                # Extraer información
                extractor = PDFExtractor(tmp_pdf_path)
                pdf_info = extractor.get_pdf_info()
                fields = extractor.get_fields_with_descriptions()
                
                # Mostrar información
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📄 Páginas", pdf_info['num_pages'])
                with col2:
                    st.metric("📝 Campos", pdf_info['num_fields'])
                with col3:
                    if pdf_info['has_form']:
                        st.success("✅ Tiene formulario")
                    else:
                        st.error("❌ Sin formulario")
                
                if pdf_info['num_fields'] > 0:
                    st.success(f"Se detectaron **{pdf_info['num_fields']} campos**")
                    
                    # Mostrar campos en expander
                    with st.expander("🔎 Ver campos detectados", expanded=True):
                        for field_name, field_data in fields.items():
                            col_a, col_b, col_c = st.columns([2, 2, 1])
                            with col_a:
                                # Mostrar descripción sugerida
                                suggested = field_data.get('suggested_description', field_name)
                                st.markdown(f"**{suggested}**")
                            with col_b:
                                st.caption(f"📋 {field_name}")
                            with col_c:
                                badge = {
                                    'text': '📝',
                                    'checkbox': '☑️',
                                    'dropdown': '📋',
                                    'radio': '🔘',
                                    'unknown': '❓'
                                }.get(field_data['type'], '❓')
                                st.caption(badge)

                            # Mostrar opciones si las hay
                            if field_data['options']:
                                st.caption(f"  Opciones: {', '.join(field_data['options'][:3])}{'...' if len(field_data['options']) > 3 else ''}")
                    
                    # Opciones de generación
                    st.markdown("---")
                    st.subheader("Generar plantilla CSV")

                    col_opt1, col_opt2 = st.columns(2)
                    with col_opt1:
                        use_descriptive = st.checkbox(
                            "🌟 Usar nombres descriptivos en CSV",
                            value=True,
                            help="Usa descripciones legibles en lugar de nombres técnicos (Ej: 'Nombre' en vez de 'txt_field_1')"
                        )
                    with col_opt2:
                        include_info = st.checkbox(
                            "📋 Incluir archivo INFO",
                            value=True,
                            help="Genera un archivo adicional con información sobre cada campo"
                        )
                    
                    if st.button("📥 Generar y descargar CSV", type="primary", use_container_width=True):
                        # Generar CSV
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_csv:
                            tmp_csv_path = tmp_csv.name

                        if use_descriptive:
                            CSVHandler.generate_descriptive_template(fields, tmp_csv_path)
                            if include_info:
                                CSVHandler.generate_template_with_info(fields, tmp_csv_path)
                        else:
                            if include_info:
                                CSVHandler.generate_template_with_info(fields, tmp_csv_path)
                            else:
                                CSVHandler.generate_template(fields, tmp_csv_path)

                        # Leer CSV para descarga
                        with open(tmp_csv_path, 'rb') as f:
                            csv_data = f.read()

                        st.download_button(
                            label="💾 Descargar plantilla.csv",
                            data=csv_data,
                            file_name=f"{Path(pdf_file.name).stem}_plantilla.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                        # Descargar archivos adicionales
                        files_to_download = []
                        if include_info:
                            info_path = tmp_csv_path.replace('.csv', '_INFO.txt')
                            if os.path.exists(info_path):
                                files_to_download.append(('INFO.txt', info_path, 'text/plain'))

                        if use_descriptive:
                            mapping_path = tmp_csv_path.replace('.csv', '_MAPEO.txt')
                            if os.path.exists(mapping_path):
                                files_to_download.append(('MAPEO.txt', mapping_path, 'text/plain'))

                        # Botones de descarga para archivos adicionales
                        if files_to_download:
                            cols = st.columns(len(files_to_download))
                            for idx, (name, path, mime) in enumerate(files_to_download):
                                with cols[idx]:
                                    with open(path, 'rb') as f:
                                        file_data = f.read()
                                    st.download_button(
                                        label=f"📋 {name}",
                                        data=file_data,
                                        file_name=f"{Path(pdf_file.name).stem}_{name}",
                                        mime=mime,
                                        use_container_width=True
                                    )

                        st.success("✅ Plantilla generada. Ahora edita el CSV y pasa al **Paso 2**.")

                        if use_descriptive:
                            st.info("💡 Recuerda subir también el archivo MAPEO.txt junto con tu CSV al rellenar el PDF")

                        # Limpiar archivos temporales
                        os.unlink(tmp_csv_path)
                        for name, path, _ in files_to_download:
                            if os.path.exists(path):
                                os.unlink(path)
                else:
                    st.warning("⚠️ Este PDF no tiene campos de formulario detectables.")
                    st.info("💡 Asegúrate de que el PDF tenga campos interactivos (no es un PDF escaneado).")
                
            except Exception as e:
                st.error(f"❌ Error al procesar el PDF: {str(e)}")
            
            finally:
                # Limpiar archivo temporal
                if os.path.exists(tmp_pdf_path):
                    os.unlink(tmp_pdf_path)
    
    # TAB 2: RELLENAR PDF
    with tab2:
        st.header("Paso 2: Rellenar el PDF")
        st.markdown("Sube el PDF original y el CSV con los datos para generar el PDF rellenado.")

        col_pdf, col_csv, col_map = st.columns([2, 2, 1])

        with col_pdf:
            pdf_to_fill = st.file_uploader(
                "📄 PDF a rellenar",
                type=['pdf'],
                key='fill_pdf',
                help="El PDF original con formulario"
            )

        with col_csv:
            csv_data_file = st.file_uploader(
                "📊 CSV con datos",
                type=['csv'],
                key='fill_csv',
                help="El CSV que editaste con tus datos"
            )

        with col_map:
            mapping_file = st.file_uploader(
                "🗺️ Archivo MAPEO",
                type=['txt'],
                key='mapping_file',
                help="Opcional: archivo MAPEO.txt si usaste nombres descriptivos"
            )
        
        if pdf_to_fill and csv_data_file:
            # Guardar archivos temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                tmp_pdf.write(pdf_to_fill.read())
                tmp_pdf_path = tmp_pdf.name

            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp_csv:
                tmp_csv.write(csv_data_file.read())
                tmp_csv_path = tmp_csv.name

            # Guardar archivo de mapeo si existe
            tmp_mapping_path = None
            if mapping_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='wb') as tmp_map:
                    tmp_map.write(mapping_file.read())
                    tmp_mapping_path = tmp_map.name

            try:
                # Leer datos del CSV (con o sin mapeo)
                if tmp_mapping_path:
                    csv_data = CSVHandler.read_descriptive_csv(tmp_csv_path, tmp_mapping_path)
                    st.info("🗺️ Usando archivo de mapeo para convertir nombres descriptivos")
                else:
                    csv_data = CSVHandler.get_first_row_data(tmp_csv_path)
                
                st.success(f"✅ CSV leído: {len(csv_data)} campos detectados")
                
                # Preview de datos
                with st.expander("👀 Preview de datos a rellenar"):
                    for field, value in csv_data.items():
                        if value and value != '':
                            st.text(f"• {field}: {value}")
                
                # Opciones de relleno
                st.markdown("---")
                
                flatten = st.checkbox(
                    "🔒 Aplanar PDF (campos no editables después)",
                    value=False,
                    help="Si marcas esto, el PDF final no podrá ser editado"
                )
                
                if st.button("✨ Rellenar PDF", type="primary", use_container_width=True):
                    with st.spinner("Rellenando PDF..."):
                        # Rellenar PDF
                        filler = PDFFiller(tmp_pdf_path)
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                            tmp_output_path = tmp_output.name
                        
                        success = filler.fill_pdf(csv_data, tmp_output_path, flatten=flatten)
                        
                        if success:
                            st.success("🎉 ¡PDF rellenado exitosamente!")
                            
                            # Leer PDF rellenado para descarga
                            with open(tmp_output_path, 'rb') as f:
                                pdf_bytes = f.read()
                            
                            st.download_button(
                                label="💾 Descargar PDF rellenado",
                                data=pdf_bytes,
                                file_name=f"{Path(pdf_to_fill.name).stem}_rellenado.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            # Limpiar
                            os.unlink(tmp_output_path)
                        else:
                            st.error("❌ Error al rellenar el PDF. Verifica que los campos coincidan.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            
            finally:
                # Limpiar archivos temporales
                if os.path.exists(tmp_pdf_path):
                    os.unlink(tmp_pdf_path)
                if os.path.exists(tmp_csv_path):
                    os.unlink(tmp_csv_path)
                if tmp_mapping_path and os.path.exists(tmp_mapping_path):
                    os.unlink(tmp_mapping_path)
        
        elif not pdf_to_fill:
            st.info("👆 Sube el PDF original")
        elif not csv_data_file:
            st.info("👆 Sube el CSV con tus datos")

    # TAB 3: EDITOR RÁPIDO
    with tab3:
        st.header("⚡ Editor Rápido - Todo en Uno")
        st.markdown("Sube tu PDF, edita los campos directamente en la web y descarga el PDF rellenado.")

        pdf_quick = st.file_uploader(
            "📄 Sube tu PDF",
            type=['pdf'],
            key='quick_pdf',
            help="PDF con formulario interactivo"
        )

        if pdf_quick:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                tmp_pdf.write(pdf_quick.read())
                tmp_pdf_path = tmp_pdf.name

            try:
                extractor = PDFExtractor(tmp_pdf_path)
                fields = extractor.get_fields_with_descriptions()

                if fields:
                    st.success(f"✅ {len(fields)} campos detectados")

                    st.markdown("### Edita los valores de los campos:")

                    # Crear formulario interactivo
                    with st.form("quick_edit_form"):
                        form_data = {}

                        # Organizar en dos columnas
                        for i, (field_name, field_data) in enumerate(fields.items()):
                            desc = field_data.get('suggested_description', field_name)
                            field_type = field_data['type']

                            # Crear input según el tipo de campo
                            if field_type == 'checkbox':
                                form_data[field_name] = st.checkbox(
                                    f"{desc}",
                                    key=f"quick_{field_name}",
                                    help=f"Campo: {field_name}"
                                )
                            elif field_type == 'dropdown' and field_data['options']:
                                form_data[field_name] = st.selectbox(
                                    f"{desc}",
                                    options=[''] + field_data['options'],
                                    key=f"quick_{field_name}",
                                    help=f"Campo: {field_name}"
                                )
                            else:
                                form_data[field_name] = st.text_input(
                                    f"{desc}",
                                    key=f"quick_{field_name}",
                                    help=f"Campo: {field_name}"
                                )

                        col_submit, col_flatten = st.columns([3, 1])
                        with col_flatten:
                            flatten_quick = st.checkbox("🔒 Aplanar", value=False)
                        with col_submit:
                            submitted = st.form_submit_button("✨ Generar PDF", type="primary", use_container_width=True)

                        if submitted:
                            with st.spinner("Generando PDF..."):
                                # Convertir datos del formulario
                                data_to_fill = {}
                                for field_name, value in form_data.items():
                                    if isinstance(value, bool):
                                        data_to_fill[field_name] = '__YES__' if value else '__NO__'
                                    elif value:
                                        data_to_fill[field_name] = str(value)

                                # Rellenar PDF
                                filler = PDFFiller(tmp_pdf_path)

                                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                                    tmp_output_path = tmp_output.name

                                success = filler.fill_pdf(data_to_fill, tmp_output_path, flatten=flatten_quick)

                                if success:
                                    st.success("🎉 ¡PDF generado!")

                                    with open(tmp_output_path, 'rb') as f:
                                        pdf_bytes = f.read()

                                    st.download_button(
                                        label="💾 Descargar PDF rellenado",
                                        data=pdf_bytes,
                                        file_name=f"{Path(pdf_quick.name).stem}_rellenado.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )

                                    os.unlink(tmp_output_path)
                                else:
                                    st.error("❌ Error al generar el PDF")
                else:
                    st.warning("⚠️ Este PDF no tiene campos de formulario")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                if os.path.exists(tmp_pdf_path):
                    os.unlink(tmp_pdf_path)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>PDF Form Filler v0.1 | MVP sin soporte de tablas</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
