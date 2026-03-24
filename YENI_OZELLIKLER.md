# Yeni Özellikler - v1.8

## 1. Sayısal Sıralama (Natural Sorting) ✨

Artık dosyalar doğru sırayla görünüyor!

**Öncesi:**
- 1.jpg, 10.jpg, 11.jpg, 2.jpg, 3.jpg (alfabetik)

**Sonrası:**
- 1.jpg, 2.jpg, 3.jpg, 10.jpg, 11.jpg (sayısal)

**Nasıl kullanılır:**
- Dosya gezgininde sağ tıklayın
- "Sayısal Sırala (1,2,10...)" seçeneğini seçin

---

## 2. Gelişmiş Vesikalık Kesme Sistemi 🎯

3 farklı yüz tanıma yöntemi eklendi!

### Yöntemler:

#### 1. Haar Cascade (Hızlı) ⚡
- Çok hızlı işlem
- Ek kurulum gerektirmez
- Net ve ön plandaki yüzler için ideal
- **Çıktı:** `dosya_haar_1.png`, `dosya_haar_2.png`, ...

#### 2. Dlib (Güçlü) 💪
- Çok daha doğru sonuçlar
- Yan profilleri ve zor açıları yakalar
- Dlib kurulumu gerektirir (DLIB_KURULUM.md)
- **Çıktı:** `dosya_dlib_gelismis_1.png`, `dosya_dlib_gelismis_2.png`, ...

#### 3. Hibrit (Akıllı) 🧠 - ÖNERİLEN
- Önce Haar Cascade dener (hızlı)
- Başarısız olursa Dlib kullanır (güçlü)
- En iyi iki dünyanın birleşimi
- **Çıktı:** Hangi yöntem başarılı olursa ona göre isimlendirilir

### Akıllı İsimlendirme

Artık hangi yöntemin kullanıldığını dosya adından anlayabilirsiniz:

- `foto_haar_1.jpg` → Haar Cascade başarılı oldu
- `foto_dlib_gelismis_1.jpg` → Haar başarısız, Dlib başarılı oldu

### Test Sonuçları

**Test dosyası:** 1.PNG (36 kişilik çoklu vesikalık)
- ✅ Haar Cascade: 36 yüz bulundu
- ⚡ Süre: Birkaç saniye
- 📁 Çıktı: `1_haar_1.PNG`, `1_haar_2.PNG`, ... `1_haar_36.PNG`

---

## Kullanım Örnekleri

### Sayısal Sıralama
1. Dosya gezginini açın
2. Sağ tıklayın
3. "Sayısal Sırala (1,2,10...)" seçin
4. Dosyalar doğru sırayla görünecek!

### Vesikalık Kesme
1. Çoklu vesikalık içeren dosyayı seçin
2. İstediğiniz yöntemi seçin:
   - Hızlı işlem için: Haar Cascade
   - Maksimum doğruluk için: Dlib (kurulum gerekli)
   - Genel kullanım için: Hibrit (önerilen)
3. "Çalıştır" butonuna tıklayın
4. Kesilen yüzler aynı klasöre kaydedilecek

---

## Teknik Detaylar

### Sayısal Sıralama
- `natural_sort_key()` fonksiyonu kullanılır
- Regex ile sayıları ayırır ve doğru sıralar
- Türkçe karakterlerle uyumlu

### Vesikalık Kesme
- **Haar Cascade:** OpenCV cascade classifier
- **Dlib:** HOG tabanlı dedektör
- **Padding:** Yüz + %60 üst, %50 alt, %45 yan boşluk
- **Format:** Orijinal dosya formatı korunur

---

## Kurulum

### Temel Özellikler (Haar Cascade)
```bash
pip install -r requirements.txt
```

### Gelişmiş Özellikler (Dlib)
Detaylı kurulum için `DLIB_KURULUM.md` dosyasına bakın.

**Hızlı kurulum (Windows):**
1. Python versiyonunuzu kontrol edin: `python --version`
2. Uygun wheel'i indirin (örn: dlib-19.24.1-cp311-cp311-win_amd64.whl)
3. Kurun: `pip install dlib-19.24.1-cp311-cp311-win_amd64.whl`

---

## Sorun Giderme

### "Çoklu vesikalık tespit edilemedi"
- ✅ Hibrit yöntemi deneyin
- ✅ Görsel kalitesini artırın
- ✅ Yüzlerin net olduğundan emin olun

### Dlib kurulum hatası
- ✅ Önceden derlenmiş wheel kullanın (en kolay)
- ✅ CMake kurun (cmake.org)
- ✅ Visual Studio Build Tools kurun

### Yanlış sıralama
- ✅ "Sayısal Sırala" seçeneğini kullanın
- ✅ Dosya adlarında sayılar varsa otomatik çalışır

---

## Gelecek Güncellemeler

- [ ] Toplu yeniden adlandırma için sayısal sıralama
- [ ] Daha fazla yüz tanıma modeli (MTCNN, RetinaFace)
- [ ] Vesikalık boyutu standardizasyonu
- [ ] Arka plan kaldırma özelliği

---

**Versiyon:** 1.8  
**Tarih:** 2026-03-12  
**Geliştirici:** dESkart Team
