import streamlit as st
import pandas as pd
import math
import os

st.set_page_config(page_title='Database 2024 - EDII', layout='wide')

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 10px;
    }
        [data-testid="stElementToolbar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path, dtype=str).drop_duplicates()
        for col in ['SERI BARANG', 'KODE FASILITAS']:
            if col in df.columns:
                df[col] = df[col].str.rstrip('.0')

        # Tambahkan kolom "DOKUMEN" di posisi setelah "KODE DOKUMEN"
        if "KODE DOKUMEN" in df.columns:
            df.insert(df.columns.get_loc("KODE DOKUMEN") + 1, 'DOKUMEN',
                      df["KODE DOKUMEN"].map(lambda x: "E-COO" if x == "860" else "COO" if x == "861" else x))

        return df.reset_index(drop=True)
    except FileNotFoundError:
        st.error(f"File {file_path} tidak ditemukan.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None

image_path = os.path.join("static", "LOGISTEED.PNG")
if os.path.exists(image_path):
    st.image(image_path, width=250)
    st.write("PT. BERDIRI MATAHARI LOGISTIK")
else:
    st.error("Gambar tidak ditemukan.")

st.write('')
st.divider()

columns_to_remove = ["KODE SATUAN", "JUMLAH SATUAN", "KODE KEMASAN", "JUMLAH KEMASAN", "Jumlah Nilai CIF", "SERI BARANG"]
unsearchable_columns = ["BM", "PPN", "PPH", "MEREK", "KODE NEGARA ASAL"]

def search_data(data, keyword, column=None):
    if column in ["Pilih Kolom", "TANGGAL PENGAJUAN"] or not keyword:
        return data.drop_duplicates()

    keyword = keyword.lower()
    
    if column == "HS":
        return data[data["HS"].str.lower().str.startswith(keyword)].drop_duplicates()
    elif column == "DOKUMEN":
        kode_dokumen = "860" if keyword == "e-coo" else "861" if keyword == "coo" else None
        return data[data["KODE DOKUMEN"] == kode_dokumen].drop_duplicates() if kode_dokumen else data
    elif column:
        return data[data[column].str.lower().str.contains(keyword, na=False)].drop_duplicates()
    
    return data[data.apply(lambda row: any(keyword in str(val).lower() for val in row), axis=1)].drop_duplicates()

def convert_df_to_excel(df):
    output = pd.ExcelWriter("search_results.xlsx", engine='xlsxwriter')
    df.drop_duplicates().to_excel(output, index=False, sheet_name='Hasil Pencarian')
    output.close()
    return "search_results.xlsx"

def main():
    st.title("Database Import Shipment 2024 - EDII")
    data = load_data('database_2024.xlsx')

    if data is not None:
        # Tambahkan kolom "DOKUMEN" ke daftar pencarian, tetapi "KODE DOKUMEN" tidak dimunculkan
        searchable_columns = ["Pilih Kolom"] + [col for col in data.columns if col not in columns_to_remove + unsearchable_columns and col != "KODE DOKUMEN"]

        selected_column = st.selectbox("Cari di kolom:", searchable_columns)

        # Jika kolom pencarian adalah "DOKUMEN", gunakan dropdown
        if selected_column == "DOKUMEN":
            keyword = st.selectbox("Pilih Jenis Dokumen:", ["E-COO", "COO"])
        else:
            keyword = "" if selected_column in ["Pilih Kolom", "TANGGAL PENGAJUAN"] else st.text_input("Masukkan kata kunci pencarian:")

        results = search_data(data, keyword, selected_column)

        # Filter berdasarkan tanggal jika kolom "TANGGAL PENGAJUAN" dipilih
        if selected_column == "TANGGAL PENGAJUAN" and "TANGGAL PENGAJUAN" in data.columns:
            results['TANGGAL PENGAJUAN'] = pd.to_datetime(results['TANGGAL PENGAJUAN'], errors='coerce')
            valid_dates = results['TANGGAL PENGAJUAN'].dropna()

            if not valid_dates.empty:
                min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
                start_date = st.date_input("Tanggal Mulai", min_value=min_date, max_value=max_date, value=min_date)
                end_date = st.date_input("Tanggal Akhir", min_value=min_date, max_value=max_date, value=max_date)

                if start_date > end_date:
                    st.warning("Tanggal Mulai tidak boleh lebih besar dari Tanggal Akhir!")
                else:
                    results = results[(results['TANGGAL PENGAJUAN'] >= pd.to_datetime(start_date)) & 
                                      (results['TANGGAL PENGAJUAN'] <= pd.to_datetime(end_date))].drop_duplicates()
            else:
                st.error("Data tanggal tidak valid atau kosong.")

        if 'TANGGAL PENGAJUAN' in results.columns:
            results['TANGGAL PENGAJUAN'] = pd.to_datetime(results['TANGGAL PENGAJUAN'], errors='coerce')
            results['TANGGAL PENGAJUAN'] = results['TANGGAL PENGAJUAN'].dt.strftime('%d %B %Y')

        results = results.drop(columns=columns_to_remove, errors='ignore').drop_duplicates()

        # Pagination
        items_per_page = 100
        total_items = len(results)
        total_pages = max(1, math.ceil(total_items / items_per_page))

        if "page_number" not in st.session_state:
            st.session_state.page_number = 1

        sorted_results = results.sort_values(by=results.columns[0], ascending=True)

        start_idx = (st.session_state.page_number - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_results = sorted_results.iloc[start_idx:end_idx]

        st.write(f"Menampilkan data **{start_idx + 1} - {min(end_idx, total_items)}** dari total **{total_items}**")

        st.dataframe(paginated_results.style.set_table_attributes('style="overflow-x: auto;"'), use_container_width=True, hide_index=True)

        # Navigasi Halaman
        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            if st.session_state.page_number > 1:
                if st.button("⬅️ Sebelumnya", key="prev_page"):
                    st.session_state.page_number -= 1
                    st.rerun()

        with col3:
            if st.session_state.page_number < total_pages:
                if st.button("Selanjutnya ➡️", key="next_page"):
                    st.session_state.page_number += 1
                    st.rerun()

        st.write(f"**Halaman {st.session_state.page_number} dari {total_pages}**")

        if (selected_column not in ["Pilih Kolom"] and keyword) or selected_column == "TANGGAL PENGAJUAN":
            file_path = convert_df_to_excel(results)
            with open(file_path, "rb") as f:
                st.download_button(" Download Hasil Pencarian", f, file_name="Hasil_Pencarian.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.divider()

if __name__ == "__main__":
    main()
