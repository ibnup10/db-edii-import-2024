import streamlit as st
import pandas as pd
import math
import os

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path).astype(str)
        return df.reset_index(drop=True)
    except FileNotFoundError:
        st.error(f"File {file_path} tidak ditemukan.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None

st.set_page_config(page_title='Database 2024 - EDII', layout='wide')

image_path = os.path.join("static", "LOGISTEED.PNG") # path relatif
if os.path.exists(image_path):
    st.image(image_path, width=250)
    st.write("PT. BERDIRI MATAHARI LOGISTIK")
else:
    st.error("Gambar tidak ditemukan.")
st.write('')

st.divider()

def search_data(data, keyword, column=None):
    keyword = keyword.lower()
    if column == "HS":
        return data[data["HS"].str.lower().str.startswith(keyword)]
    elif column and column != "Semua Kolom":
        return data[data[column].str.lower().str.contains(keyword)]
    else:
        return data[data.apply(lambda row: any(keyword in str(val).lower() for val in row), axis=1)]

def main():
    st.title("Database Import Shipment 2024 - EDII")
    data = load_data('database_2024.xlsx')

    if data is not None:
        columns = ["Semua Kolom"] + data.columns.tolist()
        selected_column = st.selectbox("Cari di kolom:", columns)
        keyword = st.text_input("Masukkan kata kunci pencarian:")
        results = search_data(data, keyword, selected_column) if keyword else data

        # Tampilkan pesan hanya saat ada kata kunci
        if keyword:
            st.markdown("<h3 style='font-weight: bold;'>NOTE</h3>", unsafe_allow_html=True)
            st.markdown("""
            <p style='color: white;'>- Please always check BM Tarif on <a href='https://insw.go.id/intr' style='color: blue; font-style: italic;'>INSW</a><br>
            <span>- Same HS Code but one of them have a 0 (zero) and different BM Tarif, Might be process with E-COO or Original CO<span><br>
            <span style='font-style: oblique;'>- Check the name of goods on the invoice and this database before copy-paste it with carefully!</span></p>""", unsafe_allow_html=True)

        page_size = 100
        num_pages = math.ceil(len(results) / page_size)
        page_num = st.session_state.get('page_num', 1)
        page_num = max(1, min(page_num, num_pages))

        start_index = (page_num - 1) * page_size
        end_index = start_index + page_size
        paged_results = results.iloc[start_index:end_index].copy()

        st.write("Hasil Pencarian:")
        st.dataframe(paged_results, use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            left, center, right = st.columns([1, 2, 1])
            with left:
                if st.button("Sebelumnya", disabled=page_num == 1):
                    st.session_state['page_num'] = page_num - 1
                    st.rerun()
            with center:
                st.write(f"<center>Halaman {page_num} dari {num_pages}</center>", unsafe_allow_html=True)
            with right:
                if st.button("Selanjutnya", disabled=page_num == num_pages):
                    st.session_state['page_num'] = page_num + 1
                    st.rerun()
        
        st.divider()

        st.markdown("""
        <p style='text-align: center; font-size: 14px; color: #888;'>
        Made with &hearts; By EDII Team Department<br>
        Deployed on Streamlit<br>
        BML-EDII ®​​ 2025 For QCC Kaizen 2025
        </p>""", unsafe_allow_html=True)

        st.markdown(f"""
            <style>
            [data-testid="stElementToolbar"], .stDataFrame tr th:first-child {{display: none;}}
            .pagination-container {{display: flex; justify-content: center; align-items: center; margin-top: 20px;}}
            .pagination-button {{margin: 0 10px; padding: 8px 16px; border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;}}
            .pagination-button[disabled] {{opacity: 0.5; cursor: not-allowed;}}
            .stTable table {{width: 100%; table-layout: auto; height: 400px; display: block; overflow-x: auto; overflow-y: auto;}}
            th, td {{padding: 10px; word-break: break-word; white-space: nowrap;}}
            .stTable {{overflow-x: auto;}}
            .stDataFrame {{width: 80% !important;margin: 0 auto;}}
            </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()