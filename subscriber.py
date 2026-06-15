"""
MQTT Abone (Subscriber)
Sensörlerden gelen verileri dinler ve veritabanına kaydeder.
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime
from database import tablo_olustur, veri_ekle, istatistikler

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smartcity/hava/#"  # Tüm istasyonları dinle

mesaj_sayisi = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Broker'a bağlandı: {BROKER}")
        client.subscribe(TOPIC, qos=1)
        print(f"📥 Dinleniyor: {TOPIC}\n")
    else:
        print(f"❌ Bağlantı hatası: {rc}")

def on_message(client, userdata, msg):
    global mesaj_sayisi
    try:
        veri = json.loads(msg.payload.decode("utf-8"))
        veri_ekle(veri)
        mesaj_sayisi += 1

        renk = "\033[92m" if veri["aqi"] < 50 else "\033[93m" if veri["aqi"] < 100 else "\033[91m"
        sifirla = "\033[0m"

        print(
            f"💾 #{mesaj_sayisi:04d} [{veri['timestamp'][11:19]}] "
            f"{veri['konum']:<12} | "
            f"AQI: {renk}{veri['aqi']:5.1f}{sifirla} | "
            f"PM2.5: {veri['pm25']:5.1f} | "
            f"CO2: {veri['co2']:5.1f} | "
            f"Sıcaklık: {veri['sicaklik']:4.1f}°C"
        )

        # Her 25 mesajda istatistik göster
        if mesaj_sayisi % 25 == 0:
            stats = istatistikler()
            print(f"\n  📊 İSTATİSTİK | Toplam: {stats['toplam_olcum']} ölçüm | "
                  f"Ort. AQI: {stats['ortalama_aqi']} | "
                  f"Ort. PM2.5: {stats['ort_pm25']} µg/m³\n")

    except Exception as e:
        print(f"⚠️  Veri işleme hatası: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"⚠️  Bağlantı koptu (kod: {rc}), yeniden bağlanılıyor...")

def main():
    print("=" * 55)
    print("  📥 Akıllı Şehir - MQTT Veri Alıcısı")
    print("=" * 55)

    # Veritabanını hazırla
    tablo_olustur()

    # MQTT istemcisi
    client = mqtt.Client(client_id="smartcity-subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print(f"\n📡 {BROKER}:{PORT} adresine bağlanılıyor...")
    client.connect(BROKER, PORT, keepalive=60)

    print("🔄 Mesajlar bekleniyor... (Durdurmak için Ctrl+C)\n")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        stats = istatistikler()
        print(f"\n\n📊 OTURUM ÖZETİ")
        print(f"  Toplam ölçüm : {stats.get('toplam_olcum', 0)}")
        print(f"  Aktif istasyon: {stats.get('aktif_istasyon', 0)}")
        print(f"  Ortalama AQI : {stats.get('ortalama_aqi', '-')}")
        print(f"  Ortalama PM2.5: {stats.get('ort_pm25', '-')} µg/m³")
        print("\n🛑 Abone durduruldu.")
        client.disconnect()

if __name__ == "__main__":
    main()
