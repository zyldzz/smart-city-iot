"""
IoT Sensör Simülatörü
Hava kalitesi ve çevre verilerini simüle eder,
MQTT protokolü üzerinden yayınlar.
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import math
from datetime import datetime

# MQTT Ayarları (ücretsiz public broker)
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_BASE = "smartcity/hava"

# Simüle edilecek sensör istasyonları
ISTASYONLAR = [
    {"id": "IST-001", "konum": "Ankara Merkez",    "lat": 39.9208, "lon": 32.8541},
    {"id": "IST-002", "konum": "Ankara Keçiören",  "lat": 39.9891, "lon": 32.8543},
    {"id": "IST-003", "konum": "Çanakkale Merkez", "lat": 40.1553, "lon": 26.4142},
    {"id": "IST-004", "konum": "Çanakkale Gelibolu","lat": 40.4083, "lon": 26.6714},
    {"id": "IST-005", "konum": "Balıkesir Merkez", "lat": 39.6484, "lon": 27.8826},
]

# Saat bazlı kirlilik çarpanı (sabah/akşam trafiğinde yükselir)
def saat_carpani():
    saat = datetime.now().hour
    # Sabah trafiği: 7-9, Akşam trafiği: 17-19
    if 7 <= saat <= 9 or 17 <= saat <= 19:
        return random.uniform(1.3, 1.7)
    elif 0 <= saat <= 5:
        return random.uniform(0.5, 0.8)
    else:
        return random.uniform(0.9, 1.2)

def veri_uret(istasyon):
    """Gerçekçi hava kalitesi verisi üretir"""
    carpan = saat_carpani()

    # PM2.5 (µg/m³) - İyi: 0-12, Orta: 12-35, Kötü: 35+
    pm25 = round(random.uniform(5, 25) * carpan, 2)

    # PM10 (µg/m³) - İyi: 0-54, Orta: 54-154
    pm10 = round(random.uniform(10, 50) * carpan, 2)

    # CO2 (ppm) - Normal dış ortam: ~400-450
    co2 = round(random.uniform(380, 500) * carpan, 1)

    # NO2 (µg/m³) - Trafik kaynaklı
    no2 = round(random.uniform(10, 80) * carpan, 2)

    # Sıcaklık (°C)
    ay = datetime.now().month
    temel_sicaklik = 10 + 10 * math.sin((ay - 3) * math.pi / 6)
    sicaklik = round(temel_sicaklik + random.uniform(-3, 3), 1)

    # Nem (%)
    nem = round(random.uniform(40, 80), 1)

    # Hava Kalitesi İndeksi (AQI) hesaplama (basitleştirilmiş)
    aqi = round((pm25 * 2 + pm10 * 0.5 + no2 * 0.3) / 3, 1)
    
    # AQI kategorisi
    if aqi < 50:
        kategori = "İyi"
    elif aqi < 100:
        kategori = "Orta"
    elif aqi < 150:
        kategori = "Hassas Gruplar İçin Sağlıksız"
    else:
        kategori = "Sağlıksız"

    return {
        "istasyon_id": istasyon["id"],
        "konum": istasyon["konum"],
        "lat": istasyon["lat"],
        "lon": istasyon["lon"],
        "timestamp": datetime.now().isoformat(),
        "pm25": pm25,
        "pm10": pm10,
        "co2": co2,
        "no2": no2,
        "sicaklik": sicaklik,
        "nem": nem,
        "aqi": aqi,
        "kategori": kategori
    }

# MQTT bağlantı callback'leri
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ MQTT Broker'a bağlandı: {BROKER}")
    else:
        print(f"❌ Bağlantı hatası, kod: {rc}")

def on_publish(client, userdata, mid):
    pass  # Sessiz yayın

def main():
    print("=" * 55)
    print("  🌆 Akıllı Şehir - Hava Kalitesi Sensör Simülatörü")
    print("=" * 55)
    print(f"  Broker : {BROKER}:{PORT}")
    print(f"  Topic  : {TOPIC_BASE}/<istasyon_id>")
    print(f"  Aktif istasyon sayısı: {len(ISTASYONLAR)}")
    print("=" * 55)

    # MQTT istemci oluştur
    client = mqtt.Client(client_id="smartcity-simulator")
    client.on_connect = on_connect
    client.on_publish = on_publish

    print("\n📡 Broker'a bağlanılıyor...")
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()
    time.sleep(2)

    print("\n🚀 Veri yayını başladı! (Durdurmak için Ctrl+C)\n")

    try:
        while True:
            for istasyon in ISTASYONLAR:
                veri = veri_uret(istasyon)
                topic = f"{TOPIC_BASE}/{istasyon['id']}"
                payload = json.dumps(veri, ensure_ascii=False)

                result = client.publish(topic, payload, qos=1)

                # Konsola renkli özet yazdır
                renk = "\033[92m" if veri["aqi"] < 50 else "\033[93m" if veri["aqi"] < 100 else "\033[91m"
                sifirla = "\033[0m"
                print(
                    f"📤 [{veri['timestamp'][11:19]}] "
                    f"{istasyon['konum']:<12} | "
                    f"PM2.5: {veri['pm25']:5.1f} | "
                    f"CO2: {veri['co2']:5.1f} | "
                    f"AQI: {renk}{veri['aqi']:5.1f} ({veri['kategori']}){sifirla}"
                )

            print(f"  {'─'*50}")
            time.sleep(5)  # Her 5 saniyede bir veri gönder

    except KeyboardInterrupt:
        print("\n\n🛑 Simülatör durduruldu.")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
