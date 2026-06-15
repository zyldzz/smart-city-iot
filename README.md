# 🌆 Akıllı Şehir – Hava Kalitesi İzleme Sistemi

IoT cihazlarından hava kalitesi verisi toplayıp analiz eden bir akıllı şehir uygulaması.

## Teknolojiler
- **Dil:** Python 3
- **Protokol:** MQTT (paho-mqtt)
- **Veritabanı:** SQLite
- **Web:** Flask + Chart.js
- **Broker:** HiveMQ (ücretsiz public)

## Kurulum

```bash
# 1. Kütüphaneleri yükle
pip install -r requirements.txt

# 2. Terminal 1 — Veri alıcıyı başlat
python subscriber.py

# 3. Terminal 2 — Sensör simülatörünü başlat
python simulator.py

# 4. Terminal 3 — Web dashboard'u başlat
python app.py

# 5. Tarayıcıda aç
http://localhost:5000
```

## Dosya Yapısı
```
smart_city_iot/
├── simulator.py       # IoT sensör simülatörü (MQTT yayıncı)
├── subscriber.py      # MQTT abone + veritabanına kayıt
├── app.py             # Flask web sunucusu
├── database.py        # SQLite veritabanı işlemleri
├── requirements.txt   # Python bağımlılıkları
└── templates/
    └── dashboard.html # Gerçek zamanlı web arayüzü
```

## Veri Akışı
```
Sensör Simülatörü
      │  MQTT Publish
      ▼
MQTT Broker (HiveMQ)
      │  MQTT Subscribe
      ▼
Subscriber → SQLite DB
                │
                ▼
         Flask API → Dashboard (Chart.js)
```

## Sensörler & Veriler
| Parametre | Birim | Açıklama |
|-----------|-------|----------|
| PM2.5 | µg/m³ | İnce parçacık maddesi |
| PM10  | µg/m³ | Kaba parçacık maddesi |
| CO₂   | ppm   | Karbondioksit |
| NO₂   | µg/m³ | Nitrojen dioksit (trafik) |
| Sıcaklık | °C | Ortam sıcaklığı |
| Nem | % | Bağıl nem |
| AQI | — | Hava Kalitesi İndeksi |

## AQI Kategorileri
| AQI | Kategori |
|-----|---------|
| 0–50 | ✅ İyi |
| 51–100 | 🟡 Orta |
| 101–150 | 🟠 Hassas Gruplar İçin Sağlıksız |
| 150+ | 🔴 Sağlıksız |
