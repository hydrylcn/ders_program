import sqlite3
import pandas as pd
import os

# 0. ESKİ VERİTABANINI SİL
if os.path.exists("okul.db"):
    os.remove("okul.db")

conn = sqlite3.connect("okul.db")
cursor = conn.cursor()

# 2. TABLOLAR (YENİ YAPI)
cursor.execute("CREATE TABLE OgretimUyeleri (uye_id INTEGER PRIMARY KEY AUTOINCREMENT, isim TEXT NOT NULL)")

# Kontenjan buradan kaldırıldı
cursor.execute("CREATE TABLE Dersler (ders_id INTEGER PRIMARY KEY AUTOINCREMENT, ders_adi TEXT NOT NULL, sinif TEXT NOT NULL)")

cursor.execute("CREATE TABLE Derslikler (derslik_id INTEGER PRIMARY KEY AUTOINCREMENT, derslik_adi TEXT NOT NULL, kontenjan INTEGER)")

# Kontenjan buraya eklendi
cursor.execute("""
CREATE TABLE OgretimUyeleriDersler (
    uye_id INTEGER,
    ders_id INTEGER,
    sinif TEXT NOT NULL,
    kontenjan INTEGER, 
    FOREIGN KEY (uye_id) REFERENCES OgretimUyeleri(uye_id),
    FOREIGN KEY (ders_id) REFERENCES Dersler(ders_id)
)
""")
conn.commit()

def veri_ekle(excel_dosyasi="dersler.xlsx"):
    df_uyeler = pd.read_excel(excel_dosyasi, sheet_name="OgretimUyeleri")
    df_dersler = pd.read_excel(excel_dosyasi, sheet_name="Dersler")
    df_derslikler = pd.read_excel(excel_dosyasi, sheet_name="Derslikler")
    df_uyeler_dersler = pd.read_excel(excel_dosyasi, sheet_name="OgretimUyeleriDersler")

    for isim in df_uyeler["OgretimUyesi"]:
        cursor.execute("INSERT INTO OgretimUyeleri (isim) VALUES (?)", (isim.strip(),))

    for _, row in df_dersler.iterrows():
        cursor.execute("INSERT INTO Dersler (ders_adi, sinif) VALUES (?, ?)",
                       (row["Dersler"].strip(), row["Sinif"].strip()))

    for _, row in df_derslikler.iterrows():
        cursor.execute("INSERT INTO Derslikler (derslik_adi, kontenjan) VALUES (?, ?)",
                       (row["Derslikler"].strip(), int(row["Kontenjan"])))
    conn.commit()

    # Eşleştirme Sözlükleri
    cursor.execute("SELECT uye_id, isim FROM OgretimUyeleri")
    uye_adi_to_id = {isim.strip().upper(): uye_id for uye_id, isim in cursor.fetchall()}
    cursor.execute("SELECT ders_id, ders_adi FROM Dersler")
    ders_adi_to_id = {ders_adi.strip().upper(): ders_id for ders_id, ders_adi in cursor.fetchall()}

    # OgretimUyeleriDersler'i Kontenjan ile birlikte ekle
    for _, row in df_uyeler_dersler.iterrows():
        uye_id = uye_adi_to_id[row["OgretimUyesi"].strip().upper()]
        ders_id = ders_adi_to_id[row["Ders"].strip().upper()]
        cursor.execute(
            "INSERT INTO OgretimUyeleriDersler (uye_id, ders_id, sinif, kontenjan) VALUES (?, ?, ?, ?)",
            (uye_id, ders_id, str(row["Sinif"]).strip(), int(row["Kontenjan"]))
        )
    conn.commit()

veri_ekle()
conn.close()
print("✅ okul.db oluşturuldu! Veriler dersler.xlsx dosyasından alındı.")