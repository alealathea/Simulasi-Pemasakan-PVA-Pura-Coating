# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 09:02:25 2026

@author: aleal
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. KONSTANTA HASIL OPTIMASI & PARAMETER PABRIK
# ==========================================
bukaan1 = 0.5155
bukaan2 = 0.2103
Tslip1 = 74.3585
Tevap1 = 58.4496
Tslip2 = 78.6107
Tevap2 = 56.0674
UA = 3560.1756
mCPalat = 1242161.5549
T_awal = 30
Cpair = 4180 # J/kgC
Cppva = 1600 # J/kgC
Lamda = 2257000 # J/kg
mseasoning = 1.3497 # kg/mnt
Tambience = 30 # C
Limbuk1 = 68.25 # C
Limbuk2 = 75 # C
Tseasoning = 82 # C

# ==========================================
# 2. MASUKKAN FUNGSI ENGINE (calapp) DI SINI
# ==========================================
def calapp (mtota,mpvaa,Tinit,bukaan1,bukaan2,deltasteam,Tslip,Tevap,xsteam,UA,mCPalat, max_time):

  mtot=[]
  mpva=[]
  mair=[]
  cptot=[]
  T=[]
  etacond=[]
  etaevap=[]
  Qin=[]
  Qout=[]
  H=[]
  Putaransteam=[]
  SSEmair=[]
  SSEtemp=[]
  Solid = []
  mtot.append(mtota)
  mpva.append(mpvaa)
  mair.append(mtot[0]-mpva[0])
  cptot.append((mpva[-1]/mtot[-1])*Cppva+(mair[-1]/mtot[-1])*Cpair)
  T.append(Tinit)
  etacond.append(1)
  etaevap.append(0)
  Putaransteam.append(1)
  Qin.append(deltasteam*etacond[-1]*Putaransteam[-1]*(xsteam*Lamda+Cpair*100))
  Qout.append(mseasoning*etaevap[-1]*Lamda+UA*(T[-1]-Tambience))
  H.append(mtot[-1]*cptot[-1]*T[-1])
  Solid.append(mpva[-1]/mtot[-1])

  for t in range(1,max_time + 1):
    #mpva
    mpva.append(mpva[-1])

    #bukaansteam
    if T[-1]<=Limbuk1:
      Putsteam = 1
    elif T[-1]<=Limbuk2:
      Putsteam = bukaan1
    else:
      Putsteam = bukaan2
    Putaransteam.append(Putsteam)

    #etacond
    if T[-1]<=Tslip:
      etacon = 1
    else:
      etacon = (100-T[-1])/(100-Tslip)
    etacond.append(etacon)

    #etaevap
    if T[-1]<=Tevap:
      etaeva = 0
    else:
      etaeva = (T[-1]-Tevap)/(Tseasoning-Tevap)
    etaevap.append(etaeva)

    #massatotal
    mtot.append(mtot[-1]+deltasteam*etacond[-1]*Putaransteam[-1]-mseasoning*etaevap[-1])

    #mair
    mair.append(mtot[-1]-mpva[-1])

    #Cptot
    cptot.append((mpva[-1]/mtot[-1])*Cppva+(mair[-1]/mtot[-1])*Cpair)

    #suhu
    T.append((H[-1]+Qin[-1]-Qout[-1]+mCPalat*T[-1])/(mtot[-1]*cptot[-1]+mCPalat))

    #Qin
    Qin.append((deltasteam*Putaransteam[-1]*etacond[-1])*(xsteam*Lamda+Cpair*100))

    #Qout
    Qout.append(mseasoning*etaevap[-1]*Lamda+UA*(T[-1]-Tambience))

    #H
    H.append(mtot[-1]*cptot[-1]*T[-1])

    #Solid content
    Solid.append(mpva[-1]/mtot[-1])


  mair_new = np.array(mair)-44.66
  mtot_new = mpvaa + mair_new
  solid_new = mpvaa / mtot_new


  return mair,T,Solid,mair_new,solid_new


# ==========================================
# 3. DESAIN ANTARMUKA UI STREAMLIT
# ==========================================
st.set_page_config(page_title="Simulator PVA", page_icon="⚙️", layout="wide")

st.title("⚙️ Simulator Pemasakan PVA")
st.markdown("Aplikasi Prediksi Waktu, Total Air Akhir, dan Kadar Solid PVA.")
st.sidebar.image("logo_pura.png", width=200)
st.sidebar.markdown("---")
st.sidebar.write("Divisi Process Engineering")
st.sidebar.write("PT Pura Coating and Adhesive")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    pilihan_pva = st.selectbox('Tipe Bahan PVA:', ['PVA 1788', 'PVA BP17a'])
    pva_input_raw = st.number_input('Jumlah PVA (kg):', min_value=1.0, value=100.0, step=10.0)
    air_input_raw = st.number_input('Jumlah Air Awal (kg) [Flowmeter]:', min_value=1.0, value=500.0, step=10.0)

with col2:
    pilihan_boiler = st.selectbox('Kondisi Boiler:', [
        '1. Loyo (Low Pressure)',
        '2. Normal (Rata-rata)',
        '3. Ngebut (High Pressure)',
        '4. GABUNGAN (Bandingkan Semua)'
    ], index=3)
    input_max_time = st.number_input('Waktu Maksimum (Menit):', min_value=10, value=60, step=5)

with col3:
    pilihan_output_data_type = st.selectbox('Tipe Data Output Grafik:', ['Massa Air', 'Solid'])
    pilihan_data_source = st.selectbox('Kondisi Data (Fase):', ['Pemasakan', 'Setelah Pendinginan'])

st.markdown("---")

# ==========================================
# 4. LOGIKA PERHITUNGAN & GRAFIK
# ==========================================
if st.button('🚀 Jalankan Simulasi', use_container_width=True):
    
    # Perhitungan Awal
    air_ril = air_input_raw * 1.128326652

    if pilihan_pva == 'PVA 1788':
        Tslip_aktif, Tevap_aktif = Tslip1, Tevap1
        SolidPVA = 0.953068592
    else: # PVA BP17a
        Tslip_aktif, Tevap_aktif = Tslip2, Tevap2
        SolidPVA = 0.955908289

    pva_solid_mass = pva_input_raw * SolidPVA
    mtota_in = pva_solid_mass + air_ril
    targetwater = (pva_solid_mass / 0.15) - pva_solid_mass

    data_skenario = {
        '1. Loyo (Low Pressure)': {'ds': 3.27, 'xs': 0.61, 'warna_air': '#85C1E9', 'warna_suhu': '#F1948A', 'label': 'Loyo'},
        '2. Normal (Rata-rata)': {'ds': 5.92, 'xs': 0.62, 'warna_air': '#2874A6', 'warna_suhu': '#CB4335', 'label': 'Normal'},
        '3. Ngebut (High Pressure)': {'ds': 12.08, 'xs': 0.48, 'warna_air': '#154360', 'warna_suhu': '#641E16', 'label': 'Ngebut'}
    }

    # Tampilan Laporan Header
    st.info(f"⏳ **MENGAWAL SIMULASI...**\n\n"
            f"📦 **INPUT:** {pva_input_raw} kg {pilihan_pva} | {air_input_raw} kg Air Awal (Flowmeter)\n\n"
            f"🔬 **Material Aktif:** Tslip={Tslip_aktif}°C, Tevap={Tevap_aktif}°C\n\n"
            f"📊 **Data Output:** {pilihan_output_data_type} ({pilihan_data_source})")
    
    # Siapkan Figure Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    ax1.set_xlabel('Waktu Pemasakan (Menit)', fontweight='bold')
    ax2.set_ylabel('Suhu (°C)', color='#CB4335', fontweight='bold')

    try:
        if pilihan_boiler == '4. GABUNGAN (Bandingkan Semua)':
            daftar_run = list(data_skenario.keys())
            st.subheader("🔥 SKENARIO: PERBANDINGAN 3 KONDISI BOILER SEKALIGUS")
        else:
            daftar_run = [pilihan_boiler]
            st.subheader(f"🔥 SKENARIO: {pilihan_boiler}")
        
        # Kolom untuk menampilkan teks hasil agar sejajar dan rapi
        hasil_cols = st.columns(len(daftar_run))

        for idx, nama in enumerate(daftar_run):
            ds = data_skenario[nama]['ds']
            xs = data_skenario[nama]['xs']
            lbl = data_skenario[nama]['label']
            w_data = data_skenario[nama]['warna_air']
            w_suhu = data_skenario[nama]['warna_suhu']

            # PANGGIL FUNGSI ENGINE
            hasil = calapp(mtota_in, pva_solid_mass, T_awal, bukaan1, bukaan2, ds, Tslip_aktif, Tevap_aktif, xs, UA, mCPalat, input_max_time)
            
            mair_sim = np.array(hasil[0])
            T_sim = hasil[1]
            Solid_sim = hasil[2]
            mair_new = hasil[3]
            Solid_new = hasil[4]

            # Seleksi Data
            if pilihan_data_source == 'Pemasakan':
                current_mair_data = mair_sim
                current_solid_data = Solid_sim
            else:
                current_mair_data = mair_new
                current_solid_data = Solid_new

            waktu_total = len(current_mair_data) - 1
            air_akhir = current_mair_data[-1]
            suhu_akhir = T_sim[-1] 
            solid_akhir_persen = current_solid_data[-1] * 100

            # Tulis Hasil ke Layar Streamlit
            with hasil_cols[idx]:
                st.markdown(f"**🔹 {lbl.upper()}** (Steam: {ds}, x: {xs})")
                if pilihan_output_data_type == 'Solid':
                    st.write(f"➜ Kadar Solid: **{solid_akhir_persen:.2f} %**")
                else:
                    st.write(f"➜ Air Akhir: **{air_akhir:.2f} kg**")
                st.write(f"➜ Suhu Akhir: **{suhu_akhir:.2f} °C**")
                st.write(f"➜ Waktu Masak: **{waktu_total} Menit**")
                st.write(f"➜ Air Target: **{targetwater:.2f} kg**")

            # Plotting Grafik
            if pilihan_output_data_type == 'Massa Air':
                ax1.plot(range(len(current_mair_data)), current_mair_data, color=w_data, linewidth=2.5, label=f"Massa Air ({lbl})")
                ax1.set_ylabel('Massa Air (kg)', color='#2874A6', fontweight='bold')
            else:
                ax1.plot(range(len(current_solid_data)), np.array(current_solid_data) * 100, color=w_data, linewidth=2.5, label=f"Solid ({lbl})")
                ax1.set_ylabel('Kadar Solid (%)', color='#2874A6', fontweight='bold')

            ax2.plot(range(len(T_sim)), T_sim, color=w_suhu, linewidth=2.5, linestyle='--', label=f"Suhu ({lbl})")

        # Plot Garis Target Water (Jika Massa Air dipilih)
        if pilihan_output_data_type == 'Massa Air':
            ax1.plot(np.linspace(0, input_max_time, 100), np.full(100, targetwater), color='blue', linestyle='--', linewidth=2.5, label="Target Water")

        plt.title(f"Kurva Prediksi Pemasakan ({pilihan_pva})", fontweight='bold')
        plt.grid(True, alpha=0.3, linestyle='--')

        # Merapikan Legend
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        all_lines = lines_1 + lines_2
        all_labels = labels_1 + labels_2
        sorted_labels_lines = sorted(zip(all_labels, all_lines), key=lambda x: x[0])
        sorted_labels = [label for label, line in sorted_labels_lines]
        sorted_lines = [line for label, line in sorted_labels_lines]
        ax1.legend(sorted_lines, sorted_labels, loc='upper left', bbox_to_anchor=(1.10, 1))

        fig.tight_layout()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan perhitungan: {e}")

        st.warning("Pastikan Anda sudah mem-paste fungsi 'calapp' dengan benar di bagian atas kode.")

