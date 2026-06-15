"""
Flask Web Sunucusu
Gerçek zamanlı hava kalitesi dashboard'u sunar.
"""

from flask import Flask, render_template, jsonify
from database import son_olcumler, istasyon_gecmisi, istatistikler, uyarilar

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/son-olcumler")
def api_son_olcumler():
    return jsonify(son_olcumler())

@app.route("/api/gecmis/<istasyon_id>")
def api_gecmis(istasyon_id):
    return jsonify(istasyon_gecmisi(istasyon_id, saat=1))

@app.route("/api/istatistikler")
def api_istatistikler():
    return jsonify(istatistikler())

@app.route("/api/uyarilar")
def api_uyarilar():
    return jsonify(uyarilar())

if __name__ == "__main__":
    print("🌐 Dashboard başlatılıyor → http://localhost:5000")
    app.run(debug=True, port=5000)
