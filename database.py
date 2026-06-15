"""
Veritabanı Modülü
SQLite ile hava kalitesi verilerini saklar ve sorgular.
"""

import sqlite3
from datetime import datetime, timedelta
import json

DB_DOSYASI = "hava_kalitesi.db"

def baglanti_al():
    """Veritabanı bağlantısı döndürür"""
    conn = sqlite3.connect(DB_DOSYASI)
    conn.row_factory = sqlite3.Row  # Sonuçları dict olarak al
    return conn

def tablo_olustur():
    """Gerekli tabloları oluşturur"""
    conn = baglanti_al()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS olcumler (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            istasyon_id TEXT NOT NULL,
            konum       TEXT NOT NULL,
            lat         REAL,
            lon         REAL,
            timestamp   TEXT NOT NULL,
            pm25        REAL,
            pm10        REAL,
            co2         REAL,
            no2         REAL,
            sicaklik    REAL,
            nem         REAL,
            aqi         REAL,
            kategori    TEXT,
            olusturulma DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_istasyon_zaman 
        ON olcumler(istasyon_id, timestamp)
    """)

    conn.commit()
    conn.close()
    print("✅ Veritabanı hazır: hava_kalitesi.db")

def veri_ekle(veri: dict):
    """Yeni ölçüm kaydeder"""
    conn = baglanti_al()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO olcumler 
        (istasyon_id, konum, lat, lon, timestamp, pm25, pm10, co2, no2, sicaklik, nem, aqi, kategori)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        veri["istasyon_id"], veri["konum"], veri["lat"], veri["lon"],
        veri["timestamp"], veri["pm25"], veri["pm10"], veri["co2"],
        veri["no2"], veri["sicaklik"], veri["nem"], veri["aqi"], veri["kategori"]
    ))

    conn.commit()
    conn.close()

def son_olcumler():
    """Her istasyonun en son ölçümünü döndürür"""
    conn = baglanti_al()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM olcumler
        WHERE id IN (
            SELECT MAX(id) FROM olcumler GROUP BY istasyon_id
        )
        ORDER BY aqi DESC
    """)

    sonuc = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sonuc

def istasyon_gecmisi(istasyon_id: str, saat: int = 1):
    """Belirli bir istasyonun son N saatlik verisini döndürür"""
    conn = baglanti_al()
    cursor = conn.cursor()

    baslangic = (datetime.now() - timedelta(hours=saat)).isoformat()

    cursor.execute("""
        SELECT timestamp, pm25, pm10, co2, no2, sicaklik, nem, aqi
        FROM olcumler
        WHERE istasyon_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (istasyon_id, baslangic))

    sonuc = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sonuc

def istatistikler():
    """Genel istatistikleri döndürür"""
    conn = baglanti_al()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*)            AS toplam_olcum,
            COUNT(DISTINCT istasyon_id) AS aktif_istasyon,
            ROUND(AVG(aqi), 1)  AS ortalama_aqi,
            ROUND(MAX(aqi), 1)  AS max_aqi,
            ROUND(MIN(aqi), 1)  AS min_aqi,
            ROUND(AVG(pm25), 1) AS ort_pm25,
            ROUND(AVG(co2), 1)  AS ort_co2,
            ROUND(AVG(sicaklik), 1) AS ort_sicaklik
        FROM olcumler
    """)

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def uyarilar():
    """AQI > 100 olan son ölçümleri döndürür"""
    conn = baglanti_al()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT istasyon_id, konum, aqi, kategori, timestamp
        FROM olcumler
        WHERE aqi > 100
        ORDER BY timestamp DESC
        LIMIT 20
    """)

    sonuc = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sonuc
