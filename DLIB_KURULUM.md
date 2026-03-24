# Dlib Kurulum Rehberi

Dlib kütüphanesi, Haar Cascade'den daha güçlü yüz tanıma sağlar. Ancak kurulumu biraz daha karmaşıktır.

## Windows için Kolay Kurulum

### Yöntem 1: Önceden Derlenmiş Wheel (Önerilen)

1. Python versiyonunuzu kontrol edin:
```bash
python --version
```

2. Uygun wheel dosyasını indirin:
- Python 3.11 için: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl
- Python 3.10 için: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp310-cp310-win_amd64.whl
- Python 3.9 için: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp39-cp39-win_amd64.whl

3. İndirdiğiniz dosyayı kurun:
```bash
pip install dlib-19.24.1-cp311-cp311-win_amd64.whl
```

### Yöntem 2: CMake ile Kurulum

1. CMake'i indirin ve kurun: https://cmake.org/download/
   - Kurulum sırasında "Add CMake to system PATH" seçeneğini işaretleyin

2. Visual Studio Build Tools'u indirin: https://visualstudio.microsoft.com/downloads/
   - "Desktop development with C++" seçeneğini işaretleyin

3. Terminali yeniden başlatın ve şunu çalıştırın:
```bash
pip install dlib
```

## Kullanım

Uygulama içinde 3 farklı yüz tanıma yöntemi bulunur:

1. **Haar Cascade (Hızlı)**: Temel yüz tanıma, hızlı ama bazen yüzleri kaçırabilir
2. **Dlib (Güçlü)**: Daha doğru ve güvenilir, ancak dlib kurulumu gerektirir
3. **Hibrit (Akıllı)**: Önce Haar Cascade dener, başarısız olursa Dlib kullanır

## Test

Dlib'in doğru kurulduğunu test etmek için:
```bash
python -c "import dlib; print('Dlib başarıyla kuruldu!')"
```

## Sorun Giderme

- **CMake bulunamadı hatası**: CMake'i PATH'e ekleyin veya önceden derlenmiş wheel kullanın
- **Visual Studio hatası**: Visual Studio Build Tools'u kurun
- **Uzun süre alıyor**: Önceden derlenmiş wheel kullanın (Yöntem 1)
