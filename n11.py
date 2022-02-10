import sqlite3
import requests
from bs4 import BeautifulSoup

# Veritabanı Bağlantısı
con = sqlite3.connect("COMPUTERS.db")
cursor = con.cursor()
print("Bağlantı gerçekleştirildi")

def tabloolustur():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Urunler (
            isim TEXT, fiyat TEXT, puan TEXT, site TEXT, Marka TEXT, 
            islemcimodeli TEXT, EkranBoyutu TEXT, İşletimSistemi TEXT, 
            İşlemciHızı TEXT, RAM TEXT, DiskTürü TEXT, DiskKapasitesi TEXT, ÜrünLinki TEXT
        )
    """)
    con.commit()

def degerekle():
    cursor.execute("""
        INSERT INTO Urunler (isim, fiyat, puan, site, Marka, islemcimodeli, EkranBoyutu, 
        İşletimSistemi, İşlemciHızı, RAM, DiskTürü, DiskKapasitesi, ÜrünLinki) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (urunAdi, urunFiyati, urun_puani, site, h, a, b, d, c, e, f, g, urunLinki))
    con.commit()

# Tabloyu başta bir kez oluşturuyoruz
tabloolustur()

n11_toplamUrun = 0
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}

for page in range(1, 10):
    n11_url = f"https://www.n11.com/arama?q=laptop&m=Asus-Lenovo-HP-Dell-Msi-Monster-Acer-Huawei-Casper&ipg={page}"
    
    # İsteklere headers eklemek n11'in engellemesini önler
    html = requests.get(n11_url, headers=headers).content
    n11_soup = BeautifulSoup(html, "html.parser")
    urunler = n11_soup.find_all("li", attrs={"class": "column"})

    for urun in urunler:
        # Her yeni üründe özellikleri sıfırlıyoruz (Python'da NULL yerine None)
        a = b = c = d = e = f = g = h = None
        urunFiyati = "Fiyat Alınamadı"
        urun_puani = "Puan Yok"
        site = "n11"  # Varsayılan değer

        try:
            urunAdi = urun.a.get("title")
            urunLinki = urun.a.get("href")
            print(f"Ürün Adı: {urunAdi}")
            print(urunLinki)
        except Exception:
            continue

        try:
            urunFiyati = urun.find("span", {"class": "newPrice cPoint priceEventClick"}).text.strip()
        except Exception:
            pass
        print(f"Sepette Ürün Fiyatı: {urunFiyati}")
    
        try:
            urun_r = requests.get(urunLinki, headers=headers)
            n11_toplamUrun += 1
        except Exception:
            print("Ürün detayına bağlanılamadı.")
            continue

        urun_soup = BeautifulSoup(urun_r.content, "html.parser")

        try:
            urun_puani = urun_soup.find("strong", attrs={"class": "ratingScore"}).text.strip()
        except Exception:
            pass
        print(f"Ürünün Puanı: {urun_puani}")

        try:
            site1 = urun_soup.find("div", attrs={"class": "columnContent"})
            if site1 and site1.h4:
                site = site1.h4.text.strip()
        except Exception:
            pass
        print(f"Ürün Sitesi: {site}")

        ozellikler = urun_soup.find_all("li", attrs={"class": "unf-prop-list-item"})
        for ozellik in ozellikler:
            try:
                urun_title = ozellik.find("p", attrs={"class": "unf-prop-list-title"}).text.strip()
                urun_prop = ozellik.find("p", attrs={"class": "unf-prop-list-prop"}).text.strip()
                print(f"{urun_title} : {urun_prop}")

                if "Model" in urun_title:
                    a = urun_prop
                if "Ekran Boyutu" in urun_title:
                    b = urun_prop
                if "İşletim Sistemi" in urun_title:
                    d = urun_prop
                if "İşlemci Hızı" in urun_title:
                    c = urun_prop
                if "Bellek Kapasitesi" in urun_title:
                    e = urun_prop
                if "Disk Türü" in urun_title:
                    f = urun_prop
                if "Disk Kapasitesi" in urun_title:
                    g = urun_prop  
                if "Marka" in urun_title:
                    h = urun_prop    
            except Exception:
                pass
            
        # Değer ekleme fonksiyonunu 'ozellikler' döngüsünün DIŞINA aldık.
        # Böylece her ürün için sadece 1 kez satır eklenir.
        degerekle()       
        print("-" * 150)

print(f"n11 toplam ürün sayısı: {n11_toplamUrun}")
con.close()