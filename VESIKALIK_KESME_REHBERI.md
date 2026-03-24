# Çoklu Vesikalık Kesme Özelliği

## Özellikler

Uygulama artık 3 farklı yüz tanıma yöntemi sunuyor:

### 1. Haar Cascade (Hızlı) ⚡
- **Avantajlar**: Çok hızlı, ek kurulum gerektirmez
- **Dezavantajlar**: Bazı yüzleri kaçırabilir, özellikle yan profil veya düşük kaliteli görsellerde
- **Ne zaman kullanılır**: Hızlı işlem gerektiğinde, yüzler net ve ön planda olduğunda

### 2. Dlib (Güçlü) 💪
- **Avantajlar**: Çok daha doğru, yan profilleri ve zor açıları yakalayabilir
- **Dezavantajlar**: Daha yavaş, dlib kurulumu gerektirir
- **Ne zaman kullanılır**: Haar Cascade başarısız olduğunda, maksimum doğruluk gerektiğinde
- **Kurulum**: `DLIB_KURULUM.md` dosyasına bakın

### 3. Hibrit (Akıllı) 🧠
- **Avantajlar**: En iyi iki dünyanın birleşimi
- **Nasıl çalışır**: 
  1. Önce Haar Cascade ile hızlı tarama yapar
  2. 2'den az yüz bulursa, Dlib ile tekrar dener
  3. Hangi yöntem başarılı olursa onu kullanır
- **Ne zaman kullanılır**: Genel kullanım için en iyi seçenek

## Kullanım

1. Uygulamayı açın
2. Çoklu vesikalık içeren dosyayı seçin
3. İstediğiniz yöntemi seçin:
   - ✂️ Çoklu Vesikalıkları Kes/Ayır (Haar Cascade - Hızlı)
   - ✂️ Çoklu Vesikalıkları Kes/Ayır (Dlib - Güçlü)
   - ✂️ Çoklu Vesikalıkları Kes/Ayır (Hibrit - Önce Haar, sonra Dlib)
4. "Çalıştır" butonuna tıklayın

## Çıktı Dosyaları

Kesilen yüzler hangi yöntem başarılı olursa ona göre farklı isimlerle kaydedilir:

### Haar Cascade başarılı olduğunda:
- `dosya_adı_haar_1.png`, `dosya_adı_haar_2.png`, ...
- Örnek: `1_haar_1.PNG`, `1_haar_2.PNG`, ...

### Dlib başarılı olduğunda (Haar başarısız):
- `dosya_adı_dlib_gelismis_1.png`, `dosya_adı_dlib_gelismis_2.png`, ...
- Örnek: `foto_dlib_gelismis_1.jpg`, `foto_dlib_gelismis_2.jpg`, ...

Bu sayede hangi yöntemin kullanıldığını dosya adından anlayabilirsiniz!

## Test Sonuçları

`z.png` dosyası ile test:
- **Haar Cascade**: 36 yüz bulundu ve başarıyla kesildi ✅
- **Süre**: Çok hızlı (birkaç saniye)

## Sorun Giderme

### "Çoklu vesikalık tespit edilemedi" hatası
- Hibrit yöntemi deneyin
- Görsel kalitesini artırın
- Yüzlerin net ve görünür olduğundan emin olun

### Dlib kurulum hatası
- `DLIB_KURULUM.md` dosyasındaki adımları takip edin
- Önceden derlenmiş wheel kullanın (en kolay yöntem)

### Yanlış kesimler
- Padding değerlerini ayarlamak için `src/operations.py` dosyasını düzenleyin
- `top_padding`, `bottom_padding`, `side_padding` değerlerini değiştirin

## Teknik Detaylar

### Haar Cascade
- OpenCV'nin cascade classifier'ını kullanır
- `haarcascade_frontalface_default.xml` modeli
- Parametreler: `scaleFactor=1.1`, `minNeighbors=5`, `minSize=(50, 50)`

### Dlib
- HOG (Histogram of Oriented Gradients) tabanlı dedektör
- `get_frontal_face_detector()` kullanır
- `upsample_num_times=1` ile daha fazla yüz bulur

### Padding Değerleri
- Üst: Yüz yüksekliğinin %60'ı (alın/saç için)
- Alt: Yüz yüksekliğinin %50'si (çene/boyun/omuz için)
- Yan: Yüz genişliğinin %45'i (kulaklar/omuz kenarı için)
