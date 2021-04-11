import sqlite3
import requests
from bs4 import BeautifulSoup

# Bilgisayar verilerini saklamak için yerel veritabanımı bağlıyorum
con = sqlite3.connect("COMPUTERS.db")
cursor = con.cursor()
print("Bağlantı gerçekleştirildi")

def tabloolustur():
    # Tablo daha önceden varsa hata vermemesi için IF NOT EXISTS kullandım
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Urunler (
            isim TEXT, fiyat TEXT, puan TEXT, site TEXT, Marka TEXT,
            islemcimodeli TEXT, EkranBoyutu TEXT, İşletimSistemi TEXT,
            İşlemciHızı TEXT, RAM TEXT, DiskTürü TEXT, DiskKapasitesi TEXT, ÜrünLinki TEXT
        )
    """)
    con.commit()

def degerekle(urunun_adi, urunun_fiyati, urunun_puani, urunun_sitesi, markasinin_adi, a, b, d, c, e, f, g, urunun_linki):
    # Çektiğim verileri sırasıyla tabloya gömmek için bu fonksiyonu kullanıyorum
    cursor.execute("""
        INSERT INTO Urunler (isim, fiyat, puan, site, Marka, islemcimodeli, EkranBoyutu, 
                             İşletimSistemi, İşlemciHızı, RAM, DiskTürü, DiskKapasitesi, ÜrünLinki) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (urunun_adi, urunun_fiyati, urunun_puani, urunun_sitesi, markasinin_adi, a, b, d, c, e, f, g, urunun_linki))
    con.commit()

# İlk iş olarak tablomu hazır hale getiriyorum
tabloolustur()

vatanToplamUrun = 0
# Bot olduğumu anlayıp engellemesinler diye araya bir User-Agent attım
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

# Şimdilik ilk 9 sayfayı dönüyorum, gerekirse sayfa sayısını artırırım
for page in range(1, 10):
    vatan_url = f"https://www.vatanbilgisayar.com/lenovo-huawei-hp-dell-casper-asus-apple-acer-msi/notebook/?page={page}"
    vatan_r = requests.get(vatan_url, headers=headers)
    vatan_soup = BeautifulSoup(vatan_r.content, "lxml")
    
    # Sayfadaki tüm ürün kartlarını yakaladığım yer
    urunler = vatan_soup.find_all("div", attrs={"class": "product-list product-list--list-page"})
    
    for urun in urunler:
        # Burası önemli: Bir önceki üründen kalan teknik özellikler yeni ürüne taşmasın diye
        # her döngü başında değişkenleri sıfırlamam gerekti.
        a = b = c = d = e = f = g = None
        
        # Sitedeki linkler /notebook... diye başlıyor, başını ana domaine bağlıyorum
        urun_link_basi = "https://www.vatanbilgisayar.com"
        urun_link_devam = urun.a.get("href") if urun.a else ""
        urunun_linki = urun_link_basi + urun_link_devam
        print(f"Ürünün Linki: {urunun_linki}")

        # Ana sayfadaki listeden ürünün ismini ve fiyatını ayıklıyorum
        isim_etiket = urun.find("div", attrs={"class": "product-list__product-name"})
        urunun_adi = isim_etiket.text.strip() if isim_etiket else "Bilinmiyor"
        print(f"Ürünün Adı: {urunun_adi}")

        fiyat_etiket = urun.find("span", attrs={"class": "product-list__price"})
        urunun_fiyati = fiyat_etiket.text.strip() if fiyat_etiket else "0"
        print(f"Ürünün Fiyatı: {urunun_fiyati} TL")

        # Esas detayları çekmek için ürünün kendi sayfasına gitmem lazım.
        # Sayfa yüklenmezse veya internet koparsa tüm kod patlamasın diye try-except'e aldım.
        try:
            urun_r = requests.get(urunun_linki, headers=headers, timeout=10)
            urun_soup = BeautifulSoup(urun_r.content, "lxml")
            vatanToplamUrun += 1
        except Exception as err:
            # Bağlantı patlarsa log basıp bu ürünü pas geçiyorum, sıradakine devam.
            print(f"Ürün detayı alınamadı (Pas geçiliyor): {err}")
            continue

        # Ürünün detay sayfasından marka logosunu bulup 'title' özniteliğinden marka adını çekiyorum
        brand_div = urun_soup.find("div", attrs={"class": "wrapper-product-brand"})
        if brand_div:
            markasinin_adi = brand_div.find("img").get("title", "").strip() if brand_div.find("img") else "Bilinmiyor"
            markasinin_linki = brand_div.find("a").get("href", "") if brand_div.find("a") else ""
            marka_linki = urun_link_basi + markasinin_linki
        else:
            markasinin_adi = "Bilinmiyor"
            marka_linki = ""

        print(f"Ürünün Markasının Adı: {markasinin_adi}")

        # Yıldız puanını ve site bilgisini çekiyorum
        puan_etiket