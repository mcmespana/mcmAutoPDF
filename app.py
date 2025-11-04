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
    tab1, tab2 = st.tabs(["🔍 Extraer Campos", "✍️ Rellenar PDF"])
    
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
                fields = extractor.get_fields()
                
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
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.text(f"📌 {field_name}")
                            with col_b:
                                badge = {
                                    'text': '📝 Texto',
                                    'checkbox': '☑️ Checkbox',
                                    'dropdown': '📋 Lista',
                                    'radio': '🔘 Radio',
                                    'unknown': '❓ Desconocido'
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
                        include_info = st.checkbox(
                            "Incluir archivo INFO con detalles de campos",
                            value=True,
                            help="Genera un archivo adicional con información sobre cada campo"
                        )
                    
                    if st.button("📥 Generar y descargar CSV", type="primary", use_container_width=True):
                        # Generar CSV
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_csv:
                            tmp_csv_path = tmp_csv.name
                        
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
                        
                        # Descargar INFO si existe
                        if include_info:
                            info_path = tmp_csv_path.replace('.csv', '_INFO.txt')
                            if os.path.exists(info_path):
                                with open(info_path, 'rb') as f:
                                    info_data = f.read()
                                
                                st.download_button(
                                    label="📋 Descargar INFO.txt",
                                    data=info_data,
                                    file_name=f"{Path(pdf_file.name).stem}_INFO.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                        
                        st.success("✅ Plantilla generada. Ahora edita el CSV y pasa al **Paso 2**.")
                        
                        # Limpiar archivos temporales
                        os.unlink(tmp_csv_path)
                        if include_info and os.path.exists(info_path):
                            os.unlink(info_path)
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
        
        col_pdf, col_csv = st.columns(2)
        
        with col_pdf:
            pdf_to_fill = st.file_uploader(
                "PDF a rellenar",
                type=['pdf'],
                key='fill_pdf',
                help="El PDF original con formulario"
            )
        
        with col_csv:
            csv_data_file = st.file_uploader(
                "CSV con datos",
                type=['csv'],
                key='fill_csv',
                help="El CSV que editaste con tus datos"
            )
        
        if pdf_to_fill and csv_data_file:
            # Guardar archivos temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                tmp_pdf.write(pdf_to_fill.read())
                tmp_pdf_path = tmp_pdf.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp_csv:
                tmp_csv.write(csv_data_file.read())
                tmp_csv_path = tmp_csv.name
            
            try:
                # Leer datos del CSV
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
        
        elif not pdf_to_fill:
            st.info("👆 Sube el PDF original")
        elif not csv_data_file:
            st.info("👆 Sube el CSV con tus datos")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>PDF Form Filler v0.1 | MVP sin soporte de tablas</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
