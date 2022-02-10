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
            isim TEXT, fiyat INT, puan INT, site TEXT, Marka TEXT, 
            islemcimodeli TEXT, EkranBoyutu TEXT, İşletimSistemi TEXT, 
            İşlemciHızı TEXT, RAM TEXT, DiskTürü TEXT, DiskKapasitesi INT, ÜrünLinki TEXT
        )
    """)
    con.commit()

def degerekle():
    cursor.execute("""
        INSERT INTO Urunler (isim, fiyat, puan, site, Marka, islemcimodeli, EkranBoyutu, 
        İşletimSistemi, İşlemciHızı, RAM, DiskTürü, DiskKapasitesi, ÜrünLinki) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (urunAd, urunFiyat, urun_puani, site, urun_marka_linki, a, b, d, c, e, f, g, link_tamami))
    con.commit()

# Tabloyu başlangıçta bir kez oluşturuyoruz
tabloolustur()

trendyolToplamUrun = 0
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}

for pi in range(1, 10):
    trendyol_url = f"https://www.trendyol.com/sr?wb=102323%2C101606%2C101849%2C104964%2C103505%2C105536%2C101470%2C102324%2C103502%2C107655&wc=103108&qt=laptop+&st=laptop+&os=1&pi={pi}"
    
    # Trendyol isteklerine bot engeline takılmamak için headers eklendi
    r = requests.get(trendyol_url, headers=headers)
    soup = BeautifulSoup(r.content, "lxml")
    urunler = soup.find_all("div", attrs={"class": "p-card-wrppr with-campaign-view"})

    for urun in urunler:
        # Her yeni üründe özellikleri sıfırlıyoruz
        a = b = c = d = e = f = g = h = None
        urunFiyat = "Fiyat Alınamadı"
        urun_puani = "Puan Yok"
        site = "Trendyol"
        urun_marka_linki = "Bilinmiyor"

        try:
            link_basi = "https://www.trendyol.com"
            link_devam = urun.a.get("href")
            link_tamami = link_basi + link_devam

            urunAd = urun.find("div", attrs={"class": "prdct-desc-cntnr"}).text.strip()
            urunFiyat = urun.find("div", attrs={"class": "prc-box-dscntd"}).text.strip()

            print(f"Ürünün Adı: {urunAd}")
            print(f"Ürünün Linki: {link_tamami}")
            print(f"Ürünün Fiyatı: {urunFiyat}")
        except Exception:
            continue

        try:
            urun_r = requests.get(link_tamami, headers=headers)
            trendyolToplamUrun += 1
        except Exception:
            print("Ürün detayı alınamadı.")
            continue

        urun_soup = BeautifulSoup(urun_r.content, "lxml")

        try:
            site1 = urun_soup.find("div", attrs={"class": "header"})
            if site1 and site1.a:
                site = site1.a.get("title")
            print(f"Ürün Sitesi: {site}")
        except Exception:
            pass

        try:
            urun_markasi = urun_soup.find("h1", attrs={"class": "pr-new-br"})
            if urun_markasi and urun_markasi.a:
                urun_marka_linki = link_basi + urun_markasi.a.get("href")
            print(f"Ürünün Markası: {urun_marka_linki}")
        except Exception:
            pass

        try:
            urun_puani_el = urun_soup.find("div", attrs={"class": "pr-rnr-sm-p"})
            if urun_puani_el:
                urun_puani = urun_puani_el.text.strip()
            print(f"Ürünün Puanı: {urun_puani}")
        except Exception:
            pass

        # Özellikleri toplama döngüsü
        ozellikler = urun_soup.find_all("li", attrs={"class": "detail-attr-item"})
        for ozellik in ozellikler:
            try:
                urun_ozellik = ozellik.span.text.strip()
                urun_ozellik_devam = ozellik.b.text.strip()
                print(f"{urun_ozellik} : {urun_ozellik_devam}")

                if "Model" in urun_ozellik:
                    a = urun_ozellik_devam
                if "Ekran Boyutu" in urun_ozellik:
                    b = urun_ozellik_devam
                if "İşletim Sistemi" in urun_ozellik:
                    d = urun_ozellik_devam
                if "Maksimum İşlemci Hızı" in urun_ozellik:
                    c = urun_ozellik_devam
                if "Ram" in urun_ozellik or "Bellek Kapasitesi" in urun_ozellik:
                    e = urun_ozellik_devam
                if "Disk Türü" in urun_ozellik:
                    f = urun_ozellik_devam
                if "SSD Kapasitesi" in urun_ozellik:
                    g = urun_ozellik_devam
            except Exception:
                pass
                
        # Değer ekleme fonksiyonu 'ozellikler' döngüsünün dışına alındı.
        # Böylece her ürün için sadece tek bir satır veri kaydedilir.
        degerekle() 
        print("#" * 200)

print(f"Trendyol toplam ürün sayısı: {trendyolToplamUrun}")
con.close()