import sqlite3
import requests
from bs4 import BeautifulSoup

# Veritabanı bağlantısı
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

def degerekle(urunun_adi, urunun_fiyati, urunun_puani, urunun_sitesi, markasinin_adi, a, b, d, c, e, f, g, urunun_linki):
    cursor.execute("""
        INSERT INTO Urunler (isim, fiyat, puan, site, Marka, islemcimodeli, EkranBoyutu, 
                             İşletimSistemi, İşlemciHızı, RAM, DiskTürü, DiskKapasitesi, ÜrünLinki) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (urunun_adi, urunun_fiyati, urunun_puani, urunun_sitesi, markasinin_adi, a, b, d, c, e, f, g, urunun_linki))
    con.commit()

# Tabloyu oluşturuyoruz
tabloolustur()

vatanToplamUrun = 0
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

for page in range(1, 10):
    vatan_url = f"https://www.vatanbilgisayar.com/lenovo-huawei-hp-dell-casper-asus-apple-acer-msi/notebook/?page={page}"
    vatan_r = requests.get(vatan_url, headers=headers)
    vatan_soup = BeautifulSoup(vatan_r.content, "lxml")
    
    urunler = vatan_soup.find_all("div", attrs={"class": "product-list product-list--list-page"})
    
    for urun in urunler:
        # Her yeni üründe özellikleri sıfırlıyoruz ki bir önceki ürünün verileri buna taşmasın
        a = b = c = d = e = f = g = None
        
        urun_link_basi = "https://www.vatanbilgisayar.com"
        urun_link_devam = urun.a.get("href") if urun.a else ""
        urunun_linki = urun_link_basi + urun_link_devam
        print(f"Ürünün Linki: {urunun_linki}")

        # İsim ve fiyat alanlarını kontrol ederek çekiyoruz
        isim_etiket = urun.find("div", attrs={"class": "product-list__product-name"})
        urunun_adi = isim_etiket.text.strip() if isim_etiket else "Bilinmiyor"
        print(f"Ürünün Adı: {urunun_adi}")

        fiyat_etiket = urun.find("span", attrs={"class": "product-list__price"})
        urunun_fiyati = fiyat_etiket.text.strip() if fiyat_etiket else "0"
        print(f"Ürünün Fiyatı: {urunun_fiyati} TL")

        # Ürün detay sayfasına istek atma ve hata yönetimi
        try:
            urun_r = requests.get(urunun_linki, headers=headers, timeout=10)
            urun_soup = BeautifulSoup(urun_r.content, "lxml")
            vatanToplamUrun += 1
        except Exception as err:
            print(f"Ürün detayı alınamadı (Pas geçiliyor): {err}")
            continue  # Hata varsa bu ürünü atla, sonraki ürüne geç

        # Marka Bilgileri
        brand_div = urun_soup.find("div", attrs={"class": "wrapper-product-brand"})
        if brand_div:
            markasinin_adi = brand_div.find("img").get("title", "").strip() if brand_div.find("img") else "Bilinmiyor"
            markasinin_linki = brand_div.find("a").get("href", "") if brand_div.find("a") else ""
            marka_linki = urun_link_basi + markasinin_linki
        else:
            markasinin_adi = "Bilinmiyor"
            marka_linki = ""

        print(f"Ürünün Markasının Adı: {markasinin_adi}")

        # Puan Bilgisi
        puan_etiket = urun_soup.find("strong", attrs={"id": "averageRankNum"})
        urunun_puani = puan_etiket.text.strip() if puan_etiket else "0"
        print(f"Ürünün Puanı: {urunun_puani}")

        # Site Bilgisi (Vatan Bilgisayar Footer alanından çekiyor)
        site_etiket = urun_soup.find("h4", attrs={"class": "footer-title"})
        urunun_sitesi = site_etiket.text.strip() if site_etiket else "Vatan Bilgisayar"

        # Teknik Özellikleri Döngüyle Bulma
        ozellikler = urun_soup.find_all("li", attrs={"data-count": "0"})
        for ozellik in ozellikler:
            head_etiket = ozellik.find("span", attrs={"class": "property-head"})
            if head_etiket:
                urun_ozelligi = head_etiket.text.strip()
                spans = ozellik.find_all("span")
                urun_ozelligi_devam = spans[1].text.strip() if len(spans) > 1 else ""
                
                # Eşleştirmeler
                if "İşlemci Numarası" in urun_ozelligi:
                    a = urun_ozelligi_devam
                elif "Ekran Boyutu" in urun_ozelligi:
                    b = urun_ozelligi_devam
                elif "İşlemci Nesli" in urun_ozelligi:
                    d = urun_ozelligi_devam
                elif "İşlemci Hızı" in urun_ozelligi:
                    c = urun_ozelligi_devam
                elif "Bellek Kapasitesi" in urun_ozelligi:
                    e = urun_ozelligi_devam
                elif "Disk Türü" in urun_ozelligi:
                    f = urun_ozelligi_devam
                elif "Disk Kapasitesi" in urun_ozelligi:
                    g = urun_ozelligi_devam

        # Veritabanına kaydet (Parametreleri fonksiyona paslıyoruz)
        degerekle(urunun_adi, urunun_fiyati, urunun_puani, urunun_sitesi, markasinin_adi, a, b, d, c, e, f, g, urunun_linki)
        print("-" * 100)

print(f"Vatan toplam ürün sayısı: {vatanToplamUrun}")

# Bağlantıyı güvenli kapatma
con.close()