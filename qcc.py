import streamlit as st
import pandas as pd
import math
import os

# Pastikan ini adalah perintah pertama
st.set_page_config(page_title='Database 2024 - EDII', layout='wide')

# CSS untuk mengatur skala halaman menjadi 80%
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

# Sisanya tetap sama
image_path = os.path.join("static", "LOGISTEED.PNG")
if os.path.exists(image_path):
    st.image(image_path, width=250)
    st.write("PT. BERDIRI MATAHARI LOGISTIK")
else:
    st.error("Gambar tidak ditemukan.")

st.write('')
st.divider()

# Kolom yang tidak ditampilkan dan tidak bisa dicari
columns_to_remove = ["KODE SATUAN", "JUMLAH SATUAN", "KODE KEMASAN", "JUMLAH KEMASAN", "Jumlah Nilai CIF"]
unsearchable_columns = ["BM", "PPN", "PPH", "MEREK"]  

def search_data(data, keyword, column=None):
    if column in ["Pilih Kolom", "TANGGAL PENGAJUAN"] or not keyword:
        return data
    keyword = keyword.lower()
    if column == "HS":
        return data[data["HS"].str.lower().str.startswith(keyword)]
    elif column:
        return data[data[column].str.lower().str.contains(keyword, na=False)]
    return data[data.apply(lambda row: any(keyword in str(val).lower() for val in row), axis=1)]

def convert_df_to_excel(df):
    output = pd.ExcelWriter("search_results.xlsx", engine='xlsxwriter')
    df.to_excel(output, index=False, sheet_name='Hasil Pencarian')
    output.close()
    return "search_results.xlsx"

def main():
    st.title("Database Import Shipment 2024 - EDII")
    data = load_data('database_2024.xlsx')

    if data is not None:
        searchable_columns = ["Pilih Kolom"] + [col for col in data.columns if col not in columns_to_remove + unsearchable_columns]

        selected_column = st.selectbox("Cari di kolom:", searchable_columns)

        if selected_column in ["Pilih Kolom", "TANGGAL PENGAJUAN"]:
            keyword = ""
        else:
            keyword = st.text_input("Masukkan kata kunci pencarian:")

        results = data.copy()

        if selected_column not in ["Pilih Kolom", "TANGGAL PENGAJUAN"] and keyword:
            results = search_data(data, keyword, selected_column)

        if selected_column == "TANGGAL PENGAJUAN" and "TANGGAL PENGAJUAN" in data.columns:
            results['TANGGAL PENGAJUAN'] = pd.to_datetime(results['TANGGAL PENGAJUAN'], errors='coerce')
            valid_dates = results['TANGGAL PENGAJUAN'].dropna()

            if not valid_dates.empty:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()

                start_date = st.date_input("Tanggal Mulai", min_value=min_date, max_value=max_date, value=min_date)
                end_date = st.date_input("Tanggal Akhir", min_value=min_date, max_value=max_date, value=max_date)

                if start_date > end_date:
                    st.warning("Tanggal Mulai tidak boleh lebih besar dari Tanggal Akhir!")
                else:
                    results = results[(results['TANGGAL PENGAJUAN'] >= pd.to_datetime(start_date)) & 
                                      (results['TANGGAL PENGAJUAN'] <= pd.to_datetime(end_date))]
            else:
                st.error("Data tanggal tidak valid atau kosong.")

        if 'TANGGAL PENGAJUAN' in results.columns:
            results['TANGGAL PENGAJUAN'] = pd.to_datetime(results['TANGGAL PENGAJUAN'], errors='coerce')
            results['TANGGAL PENGAJUAN'] = results['TANGGAL PENGAJUAN'].dt.strftime('%d %B %Y')

        results = results.drop(columns=columns_to_remove, errors='ignore')

        st.write("Hasil Pencarian:")

        # 🔹 **Menampilkan Tabel tanpa Toolbar (Find, Download, Fullscreen)**
        st.markdown("""
            <style>
            [data-testid="stElementToolbar"] {display: none;}
            </style>
        """, unsafe_allow_html=True)

        # Pagination
        page_size = 100
        num_pages = math.ceil(len(results) / page_size)
        page_num = st.session_state.get('page_num', 1)
        page_num = max(1, min(page_num, num_pages))

        start_index = (page_num - 1) * page_size
        end_index = start_index + page_size
        paged_results = results.iloc[start_index:end_index].copy()

        st.dataframe(paged_results, use_container_width=True, hide_index=True)

        if (selected_column not in ["Pilih Kolom"] and keyword) or selected_column == "TANGGAL PENGAJUAN":
            file_path = convert_df_to_excel(results)
            with open(file_path, "rb") as f:
                st.download_button("📥 Download Hasil Pencarian", f, file_name="Hasil_Pencarian.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

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

if __name__ == "__main__":
    main()