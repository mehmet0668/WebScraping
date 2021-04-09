import sqlite3
import requests
from bs4 import BeautifulSoup


# VERİTABANI BAĞLANTISI VE YAPILANDIRMASI

# 'COMPUTERS.db' adında bir SQLite veritabanı dosyası oluşturur veya var olana bağlanır.
con = sqlite3.connect("COMPUTERS.db")
# Veritabanı üzerinde SQL sorguları çalıştırabilmek için bir imleç (cursor) nesnesi oluşturur.
cursor = con.cursor()
print("Bağlantı gerçekleştirildi")

def tabloolustur():
    """
    Veritabanında eğer 'Urunler' tablosu yoksa belirtilen sütun yapısıyla 
    yeni bir tablo oluşturur. 'IF NOT EXISTS' eski verilerin silinmesini önler.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Urunler (
            isim TEXT, fiyat TEXT, puan TEXT, site TEXT, Marka TEXT, 
            islemcimodeli TEXT, EkranBoyutu TEXT, İşletimSistemi TEXT, 
            İşlemciHızı TEXT, RAM TEXT, DiskTürü TEXT, DiskKapasitesi TEXT, ÜrünLinki TEXT
        )
    """)
    con.commit() # Değişiklikleri veritabanına kalıcı olarak kaydeder.

def degerekle(veri_demeti):
    """
    Dışarıdan parametre olarak aldığı ürün bilgilerini güvenli bir şekilde 
    (SQL Injection engellenecek biçimde '?' kullanarak) Urunler tablosuna ekler.
    """
    cursor.execute("""
        INSERT INTO Urunler (isim, fiyat, puan, site, Marka, islemcimodeli, EkranBoyutu, 
        İşletimSistemi, İşlemciHızı, RAM, DiskTürü, DiskKapasitesi, ÜrünLinki) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, veri_demeti)
    con.commit() # Ekleme işlemini veritabanına kaydeder.

# Program başladığında tablonun hazır olduğundan emin olmak için fonksiyon çağrılır.
tabloolustur()


# WEB SCRAPING (VERİ KAZIMA) BAĞLANTI AYARLARI

# Başarılı şekilde kazınan toplam ürün sayısını tutacak sayaç.
trendyolToplamUrun = 0

# Trendyol'un bizi bir yazılım/bot olarak algılayıp engellememesi için tarayıcı taklidi yapan başlık bilgisi.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}


# ANA DÖNGÜ: SAYFA SAYFA GEZİNME

# 1. sayfadan 9. sayfaya kadar (9 dahil değil) Trendyol laptop arama sonuçlarını gezer.
for pi in range(1, 10):
    # Her sayfa için dinamik URL adresi oluşturulur.
    trendyol_url = f"https://www.trendyol.com/sr?wb=102323%2C101606%2C101849%2C104964%2C103505%2C105536%2C101470%2C102324%2C103502%2C107655&wc=103108&qt=laptop+&st=laptop+&os=1&pi={pi}"
    
    try:
        # Sayfa içeriğini indirir. timeout=10 ile sitenin yanıt vermemesi durumunda kodun kilitlenmesi önlenir.
        r = requests.get(trendyol_url, headers=headers, timeout=10)
        # HTML kodlarını ayrıştırmak (parse etmek) için BeautifulSoup kütüphanesine gönderir.
        soup = BeautifulSoup(r.content, "lxml")
        # Sayfadaki tüm ürün kartlarını içeren div elementlerini bir liste halinde yakalar.
        urunler = soup.find_all("div", attrs={"class": "p-card-wrppr with-campaign-view"})
    except Exception as e:
        print(f"Sayfa {pi} yüklenirken hata oluştu: {e}")
        continue

    # İÇ DÖNGÜ: SAYFA İÇİNDEKİ ÜRÜNLERİ TEK TEK İNCELEME

    for urun in urunler:
        # Her yeni ürüne geçildiğinde teknik özellik değişkenleri sıfırlanır (None yapılır).
        islemci_modeli = ekran_boyutu = isletim_sistemi = islemci_hizi = ram = disk_turu = disk_kapasitesi = None
        
        # Varsayılan temel değerler atanır.
        urunFiyat = "Fiyat Alınamadı"
        urun_puani = "Puan Yok"
        site = "Trendyol"
        urun_marka_linki = "Bilinmiyor"

        # --- 1. AŞAMA: Ana Listeleme Sayfasından Temel Bilgileri Çekme ---
        try:
            link_basi = "https://www.trendyol.com"
            link_devam = urun.a.get("href") # Ürünün detay sayfasına giden yarı bağıl link.
            link_tamami = link_basi + link_devam # Tam URL adresi oluşturulur.

            # Ürün başlığı ve fiyat metinleri çekilir, sağındaki solundaki boşluklar temizlenir (.strip()).
            urunAd = urun.find("div", attrs={"class": "prdct-desc-cntnr"}).text.strip()
            raw_fiyat = urun.find("div", attrs={"class": "prc-box-dscntd"}).text.strip()
            
            # Fiyattaki "TL" ibaresini kaldırıp daha temiz bir metin elde ediyoruz.
            urunFiyat = raw_fiyat.replace("TL", "").strip()

            print(f"Ürünün Adı: {urunAd}")
            print(f"Ürünün Linki: {link_tamami}")
            print(f"Ürünün Fiyatı: {urunFiyat} TL")
        except Exception:
            # Eğer ürün adı veya linki alınamazsa bu ürünü atlayıp bir sonraki ürüne geçer.
            continue

        # --- 2. AŞAMA: Ürünün Detay Sayfasına Gitme ---
        try:
            # Ürünün kendi detay sayfasına istek atılır.
            urun_r = requests.get(link_tamami, headers=headers, timeout=10)
            trendyolToplamUrun += 1 # Başarılı her bağlantıda toplam ürün sayacı artar.
        except Exception:
            print("Ürün detay sayfasına bağlanılamadı. Atlanıyor...")
            continue

        # Ürün detay sayfasının HTML kodları ayrıştırılır.
        urun_soup = BeautifulSoup(urun_r.content, "lxml")

        # --- 3. AŞAMA: Detay Sayfasından Mağaza, Marka ve Puan Çekme ---
        try:
            # Ürünü satan mağazanın bilgisini çeker.
            site1 = urun_soup.find("div", attrs={"class": "header"})
            if site1 and site1.a:
                site = site1.a.get("title")
            print(f"Ürün Sitesi (Satıcı): {site}")
        except Exception:
            pass

        try:
            # Ürünün markasını ve markanın Trendyol linkini çeker.
            urun_markasi = urun_soup.find("h1", attrs={"class": "pr-new-br"})
            if urun_markasi and urun_markasi.a:
                urun_marka_linki = link_basi + urun_markasi.a.get("href")
            print(f"Ürünün Marka Linki: {urun_marka_linki}")
        except Exception:
            pass

        try:
            # Ürünün değerlendirme puanını çeker (Örn: 4.5).
            urun_puani_el = urun_soup.find("div", attrs={"class": "pr-rnr-sm-p"})
            if urun_puani_el:
                urun_puani = urun_puani_el.text.strip()
            print(f"Ürünün Puanı: {urun_puani}")
        except Exception:
            pass

        # --- 4. AŞAMA: Ürün Özellikleri Tablosunu (Özellikler Listesini) Tarama ---
        # Detay sayfasındaki alt alta listelenen tüm teknik özellikleri bulur.
        ozellikler = urun_soup.find_all("li", attrs={"class": "detail-attr-item"})
        for ozellik in ozellikler:
            try:
                # Örn: 'Ekran Boyutu' kısmını sol taraftan (span) alır.
                urun_ozellik = ozellik.span.text.strip()
                # Örn: '15.6 inç' kısmını sağ taraftan (b) alır.
                urun_ozellik_devam = ozellik.b.text.strip()
                print(f" -> {urun_ozellik} : {urun_ozellik_devam}")

                # İlgili anahtar kelimeler eşleştiğinde yukarıda tanımladığımız düzenli değişkenlere atar.
                if "Model" in urun_ozellik:
                    islemci_modeli = urun_ozellik_devam
                if "Ekran Boyutu" in urun_ozellik:
                    ekran_boyutu = urun_ozellik_devam
                if "İşletim Sistemi" in urun_ozellik:
                    isletim_sistemi = urun_ozellik_devam
                if "Maksimum İşlemci Hızı" in urun_ozellik:
                    islemci_hizi = urun_ozellik_devam
                if "Ram" in urun_ozellik or "Bellek Kapasitesi" in urun_ozellik:
                    ram = urun_ozellik_devam
                if "Disk Türü" in urun_ozellik:
                    disk_turu = urun_ozellik_devam
                if "SSD Kapasitesi" in urun_ozellik or "Sabit Disk" in urun_ozellik:
                    disk_kapasitesi = urun_ozellik_devam
            except Exception:
                pass
                
        # --- 5. AŞAMA: Toplanan Tüm Verileri Veritabanına Yazma ---
        # Toplanan değişkenleri bir demet (tuple) haline getirip güvenli şekilde fonksiyonumuza gönderiyoruz.
        veri_paketi = (
            urunAd, urunFiyat, urun_puani, site, urun_marka_linki, 
            islemci_modeli, ekran_boyutu, isletim_sistemi, islemci_hizi, 
            ram, disk_turu, disk_kapasitesi, link_tamami
        )
        
        degerekle(veri_paketi) 
        print("-" * 100) # Konsolda ürünleri birbirinden görsel olarak ayırmak için çizgi çeker.


# KAPANIŞ VE RAPORLAMA

print("\n" + "="*50)
print(f"İşlem Tamamlandı! Trendyol'dan başarıyla kazınan toplam ürün sayısı: {trendyolToplamUrun}")
print("="*50)

# Veritabanı bağlantısı güvenli bir şekilde kapatılır.
con.close()