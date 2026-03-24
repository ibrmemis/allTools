# dESkart - Çok Amaçlı Dosya Düzenleme Aracı

dESkart, masaüstü ortamında dosya ve klasör işlemlerini kolaylaştırmak için geliştirilmiş, Python ve CustomTkinter tabanlı modern bir arayüze sahip bir araçtır.

## Temel Özellikler
- **Karakter Kesme:** Dosya isimlerini belirli bir karakterden sonrasını silecek şekilde toplu düzenleme.
- **Toplu Format Dönüştürme:**
  - .jpeg -> .jpg (Yeniden adlandırma)
  - .bmp -> .jpg (Dönüştürme)
  - .png -> .jpg (Dönüştürme)
  - .jfif -> .jpg (Dönüştürme)
  - .pdf -> .jpg (Sayfaları görsele dökme)
- **Yapay Zeka Destekli Vesikalık Ayıklama:** Haar Cascade, Dlib ve Hibrit (ikisi birden) yöntemleriyle fotoğraflardaki yüzleri tespit edip ayrı dosyalar olarak kaydeder.
- **Sıralı Numaralandırma:** Dosyaları belirli bir numaradan başlayarak toplu adlandırma.

## Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.8+
- Gerekli paketler: `pip install -r requirements.txt`
- (Opsiyonel) Dlib özellikleri için Dlib kurulumu gerekebilir.

### Çalıştırma
Ana dizinde yer alan `main.py` dosyasını çalıştırarak uygulamayı başlatabilirsiniz:
```bash
python main.py
```

## Geliştirici
**dESkart** - [GitHub Profiliniz](https://github.com/v-burakyildiz) (Burayı güncelleyebilirsiniz).
