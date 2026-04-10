import os
import sys
import platform
from PIL import Image

def op_truncate_after_n(file_paths: list[str], n: int, log) -> int:
    """Seçilen dosyaların adının N. karakterinden sonrasını sil (uzantı korunur)."""
    count = 0
    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
        folder = os.path.dirname(fpath)
        fname = os.path.basename(fpath)
        name, ext = os.path.splitext(fname)
        
        if len(name) > n:
            new_name = name[:n] + ext
            new_path = os.path.join(folder, new_name)
            if not os.path.exists(new_path):
                os.rename(fpath, new_path)
                log(f"✔ {fname}  →  {new_name}")
                count += 1
            else:
                log(f"⚠ Atlandı (var): {new_name}")
    return count


def op_rename_ext(file_paths: list[str], old_ext: str, new_ext: str, log) -> int:
    """Seçilen dosyaların uzantısını değiştir (dosya içeriğine dokunmadan)."""
    count = 0
    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
        folder = os.path.dirname(fpath)
        fname = os.path.basename(fpath)
        
        if fname.lower().endswith(f".{old_ext.lower()}"):
            stem  = os.path.splitext(fname)[0]
            new_name = f"{stem}.{new_ext}"
            new_path = os.path.join(folder, new_name)
            if not os.path.exists(new_path):
                os.rename(fpath, new_path)
                log(f"✔ {fname}  →  {new_name}")
                count += 1
            else:
                log(f"⚠ Atlandı (var): {new_name}")
    return count


def op_convert_to_jpg(file_paths: list[str], src_ext: str, log) -> int:
    """Seçilen görsel dosyalarını JPEG formatına dönüştür."""
    count = 0
    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
        folder = os.path.dirname(fpath)
        fname = os.path.basename(fpath)
        
        if fname.lower().endswith(f".{src_ext.lower()}"):
            stem  = os.path.splitext(fname)[0]
            out   = os.path.join(folder, f"{stem}.jpg")
            try:
                # Pillow dosyayı açık tutmasın diye with bloğu kullanıyoruz
                with Image.open(fpath) as img:
                    rgb_img = img.convert("RGB")
                    rgb_img.save(out, "JPEG", quality=95)
                
                if out != fpath:
                    os.remove(fpath)
                log(f"✔ {fname}  →  {stem}.jpg")
                count += 1
            except Exception as e:
                log(f"✖ {fname}: {e}")
    return count


def op_pdf_to_jpg(file_paths: list[str], dpi: int, log) -> int:
    """Seçilen PDF dosyalarının sayfalarını JPEG'e dönüştür."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        log("✖ pdf2image kurulu değil. 'pip install pdf2image' çalıştırın.")
        return 0
        
    # Windows için yerel Poppler dizinini kontrol et
    poppler_path = None
    if platform.system() == "Windows":
        import sys
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller ile derlenmişse (.exe içinden çalışıyorsa)
            base_dir = sys._MEIPASS
        else:
            # Normal python betiği olarak çalışıyorsa
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Poppler genelde Library/bin veya düz bin içinde olabilir
        lib_bin = os.path.join(base_dir, "bin", "poppler", "Library", "bin")
        root_bin = os.path.join(base_dir, "bin", "poppler", "bin")
        
        if os.path.exists(lib_bin):
            poppler_path = lib_bin
        elif os.path.exists(root_bin):
            poppler_path = root_bin
        else:
            log("✖ DiKKAT: Poppler yüklü görünmüyor.")
            log("Lütfen klasördeki 'python install_poppler.py' komutunu çalıştırarak gerekli dosyaları indirin.")
            return 0

    count = 0
    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
        folder = os.path.dirname(fpath)
        fname = os.path.basename(fpath)
        
        if fname.lower().endswith(".pdf"):
            stem  = os.path.splitext(fname)[0]
            try:
                pages = convert_from_path(fpath, dpi=dpi, poppler_path=poppler_path)
                for i, page in enumerate(pages, 1):
                    out_name = f"{stem}_p{i:03d}.jpg" if len(pages) > 1 else f"{stem}.jpg"
                    page.save(os.path.join(folder, out_name), "JPEG", quality=95)
                    log(f"✔ {fname} sayfa {i}  →  {out_name}")
                count += len(pages)
            except Exception as e:
                log(f"✖ {fname}: {e}")
    return count

def op_rotate_images(file_paths: list[str], angle: int, log) -> int:
    """Seçilen resim dosyalarını belirtilen açıda döndürerek üzerine yazar."""
    count = 0
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".jfif"}
    
    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
            
        fname = os.path.basename(fpath)
        ext = os.path.splitext(fname)[1].lower()
        
        if ext in valid_exts:
            try:
                img = Image.open(fpath)
                
                # Expand=True döndürmelerde kırpılmayı engeller
                rotated = img.rotate(-angle, expand=True) 
                
                # Orijinal dosyayı tamamen aynı yere kaydet
                rotated.save(fpath) 
                log(f"✔ {fname}  →  {angle}° döndürüldü.")
                count += 1
            except Exception as e:
                log(f"✖ {fname}: Döndürülemedi ({e})")
    
    return count

def op_rename_sequence(file_paths: list[str], start_num: int, log) -> int:
    """Seçilen dosyaları alfabetik sıraya göre belirterek yeniden adlandırır ve txt raporu oluşturur."""
    if not file_paths:
        return 0
        
    # Güvenlik ve sırayı koruma: Dosyaları isme göre alfabetik sırala
    sorted_paths = sorted(file_paths, key=lambda x: os.path.basename(x).lower())
    
    count = 0
    current_num = start_num
    rename_log = []
    
    # Tüm dosyalar genellikle aynı klasördedir, ilk dosyanın klasörünü hedef alalım
    target_folder = os.path.dirname(sorted_paths[0])
    
    # Çakışmaları önlemek için önce dosyaları geçici bir isme taşıyoruz
    import uuid
    import time
    
    temp_mappings = []
    
    # Aşama 1: Geçici isimlendirme (Dosya isimleri kendi içinde çakışmasın diye)
    for fpath in sorted_paths:
        if not os.path.isfile(fpath):
            continue
            
        folder = os.path.dirname(fpath)
        fname = os.path.basename(fpath)
        ext = os.path.splitext(fname)[1]
        
        # Geçici rastgele isim
        temp_name = f"__temp_{uuid.uuid4().hex[:8]}{ext}"
        temp_path = os.path.join(folder, temp_name)
        
        try:
            os.rename(fpath, temp_path)
            temp_mappings.append({
                "original_path": fpath,
                "original_name": fname,
                "temp_path": temp_path,
                "folder": folder,
                "ext": ext
            })
        except Exception as e:
            log(f"✖ HATA (Geçici Adlandırma) {fname}: {e}")
            
    # Aşama 2: Asıl numaralandırma
    for item in temp_mappings:
        new_name = f"{current_num}{item['ext']}"
        new_path = os.path.join(item["folder"], new_name)
        
        try:
            os.rename(item["temp_path"], new_path)
            log(f"✔ {item['original_name']}  →  {new_name}")
            rename_log.append(f"{item['original_name']} -> {new_name}")
            count += 1
            current_num += 1
        except Exception as e:
            # Hata durumunda geçici dosyayı orijinal ismine geri getirmeye çalış
            log(f"✖ HATA (Numaralandırma) {item['original_name']} -> {new_name}: {e}")
            try:
                os.rename(item["temp_path"], item["original_path"])
            except:
                pass

    # Aşama 3: Log dosyasını yazdır
    if rename_log:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = f"rename_log_{timestamp}.txt"
        log_filepath = os.path.join(target_folder, log_filename)
        
        try:
            with open(log_filepath, "w", encoding="utf-8") as f:
                f.write(f"--- Sıralı Yeniden Adlandırma Logu ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n")
                f.write(f"Başlangıç Numarası: {start_num}\n")
                f.write("-" * 50 + "\n")
                for record in rename_log:
                    f.write(record + "\n")
            log(f"📝 Değişiklik raporu kaydedildi: {log_filename}")
        except Exception as e:
            log(f"✖ Rapor dosyası oluşturulamadı: {e}")
            log(f"✖ Rapor dosyası oluşturulamadı: {e}")
            
    return count

def op_extract_photos(file_paths: list[str], log) -> int:
    """Yapay Zeka (Haar Cascade) ile resimdeki yüzleri algılayıp ayrı vesikalık dosyaları olarak keser."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        log("✖ Hata: OpenCV (cv2) kütüphanesi bulunamadı! Lütfen 'pip install opencv-python numpy' komutunu çalıştırın.")
        return 0

    if not file_paths:
        return 0
        
    # Modelin yolunu belirle (Normal ortam ve PyInstaller .exe ortamı)
    if hasattr(sys, '_MEIPASS'):
        cascade_path = os.path.join(sys._MEIPASS, 'bin', 'haarcascades', 'haarcascade_frontalface_default.xml')
    else:
        cascade_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin', 'haarcascades', 'haarcascade_frontalface_default.xml')

    if not os.path.exists(cascade_path):
        log(f"✖ Hata: Yüz tanıma modeli bulunamadı!\nAranan yol: {cascade_path}")
        return 0

    face_cascade = cv2.CascadeClassifier(cascade_path)
    total_faces_extracted = 0

    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
            
        fname = os.path.basename(fpath)
        folder = os.path.dirname(fpath)
        name, ext = os.path.splitext(fname)
        
        # Türkçe/özel karakterli dosya yollarını OpenCV'nin okuyabilmesi için numpy ile okuyoruz
        with open(fpath, "rb") as stream:
            bytes_array = bytearray(stream.read())
        numpy_array = np.asarray(bytes_array, dtype=np.uint8)
        img = cv2.imdecode(numpy_array, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            log(f"✖ {fname}: Görüntü okunamadı kardeş")
            continue

        # Gri tonlamaya çevir (Haar Cascade gri resimde çalışır)
        if len(img.shape) == 3:
            # Alpha channel varsa BGR'ye dönüştür, yoksa direkt GRAY yap
            if img.shape[2] == 4:
                img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) # BGRA -> BGR
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Yüzleri algıla
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)
        )

        if len(faces) < 2:
            log(f"⚠ {fname}: Çoklu vesikalık tespit edilemedi (Bulunan Yüz: {len(faces)}). Atlanıyor.")
            continue
            
        log(f"🔍 {fname}: {len(faces)} adet yüz/vesikalık tespit edildi. Kesiliyor...")

        # Her bir yüz için genişletilmiş bir çerçeve kesiyoruz
        for i, (x, y, w, h) in enumerate(faces):
            # Normalde (x,y, w,h) sadece yüzü çevreler. Biz tüm kafayı/omuzu almak için bunu genişleteceğiz.
            # Yüz, oluşturacağımız çerçevenin ortalama %50-%60'ını kaplamalıdır.
            
            # Üstten (alın/saç) daha fazla pay, alttan (çene/boyun/omuz) biraz pay
            top_padding = int(h * 0.6)
            bottom_padding = int(h * 0.5)
            # Sağdan ve soldan (kulaklar/omuz kenarı) pay
            side_padding = int(w * 0.45)
            
            new_x = max(0, x - side_padding)
            new_y = max(0, y - top_padding)
            new_w = min(img.shape[1] - new_x, w + (side_padding * 2))
            new_h = min(img.shape[0] - new_y, h + top_padding + bottom_padding)
            
            # Vesikalık gibi dikine (Portrait) oranını zorlamak istersek (örneğin 4.5 x 6 cm oranı ~ 1:1.33)
            # Burada standart genişletme yaptık.

            face_img = img[new_y:new_y+new_h, new_x:new_x+new_w]
            
            # Kaydet
            out_name = f"{name}_{i+1}{ext}"
            out_path = os.path.join(folder, out_name)
            
            # Türkçe yollar için imencode
            is_success, buffer = cv2.imencode(ext, face_img)
            if is_success:
                with open(out_path, "wb") as f_out:
                    f_out.write(buffer)
                total_faces_extracted += 1
            else:
                log(f"✖ {out_name} kaydedilemedi!")
                
        log(f"✔ {fname} içindeki {len(faces)} resim başarıyla ayrıldı.")

    return total_faces_extracted


def op_extract_photos_dlib(file_paths: list[str], log) -> int:
    """
    Dlib kütüphanesi ile resimdeki yüzleri algılayıp ayrı vesikalık dosyaları olarak keser.
    Haar Cascade'den daha güçlü ve doğru sonuçlar verir.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        log("✖ Hata: OpenCV (cv2) kütüphanesi bulunamadı! Lütfen 'pip install opencv-python numpy' komutunu çalıştırın.")
        return 0
    
    try:
        import dlib
    except ImportError:
        log("✖ Hata: dlib kütüphanesi bulunamadı!")
        log("📦 Kurulum için: pip install dlib")
        log("⚠ Not: dlib kurulumu zaman alabilir ve CMake gerektirir.")
        return 0

    if not file_paths:
        return 0
    
    log("🔧 Dlib yüz dedektörü yükleniyor...")
    # Dlib'in HOG tabanlı yüz dedektörünü kullan (model dosyası gerektirmez)
    detector = dlib.get_frontal_face_detector()
    
    total_faces_extracted = 0

    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
            
        fname = os.path.basename(fpath)
        folder = os.path.dirname(fpath)
        name, ext = os.path.splitext(fname)
        
        # Türkçe/özel karakterli dosya yollarını OpenCV'nin okuyabilmesi için numpy ile okuyoruz
        with open(fpath, "rb") as stream:
            bytes_array = bytearray(stream.read())
        numpy_array = np.asarray(bytes_array, dtype=np.uint8)
        img = cv2.imdecode(numpy_array, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            log(f"✖ {fname}: Görüntü okunamadı.")
            continue

        # BGR'den RGB'ye çevir (dlib RGB bekler)
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            else:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        # Yüzleri algıla (upsample_num_times=1 daha fazla yüz bulur ama yavaştır)
        log(f"🔍 {fname}: Yüzler aranıyor...")
        faces = detector(img_rgb, 1)

        if len(faces) < 2:
            log(f"⚠ {fname}: Çoklu vesikalık tespit edilemedi (Bulunan Yüz: {len(faces)}). Atlanıyor.")
            continue
            
        log(f"✅ {fname}: {len(faces)} adet yüz/vesikalık tespit edildi. Kesiliyor...")

        # Her bir yüz için genişletilmiş bir çerçeve kesiyoruz
        for i, face in enumerate(faces):
            # dlib rectangle objesi: left(), top(), right(), bottom()
            x = face.left()
            y = face.top()
            w = face.right() - face.left()
            h = face.bottom() - face.top()
            
            # Yüzü genişlet (baş, omuz, boyun için)
            top_padding = int(h * 0.6)
            bottom_padding = int(h * 0.5)
            side_padding = int(w * 0.45)
            
            new_x = max(0, x - side_padding)
            new_y = max(0, y - top_padding)
            new_x2 = min(img.shape[1], x + w + side_padding)
            new_y2 = min(img.shape[0], y + h + bottom_padding)
            
            face_img = img[new_y:new_y2, new_x:new_x2]
            
            # Kaydet
            out_name = f"{name}_dlib_{i+1}{ext}"
            out_path = os.path.join(folder, out_name)
            
            # Türkçe yollar için imencode
            is_success, buffer = cv2.imencode(ext, face_img)
            if is_success:
                with open(out_path, "wb") as f_out:
                    f_out.write(buffer)
                total_faces_extracted += 1
            else:
                log(f"✖ {out_name} kaydedilemedi!")
                
        log(f"✔ {fname} içindeki {len(faces)} resim başarıyla ayrıldı.")

    return total_faces_extracted


def op_extract_photos_hybrid(file_paths: list[str], log, start_num: int = 1) -> int:
    """
    Hibrit yöntem: Önce Haar Cascade dener, başarısız olursa dlib kullanır.
    Yüzler sol üstten sağa-aşağı sıralanır ve start_num'dan başlayarak
    sade rakamla isimlendirilir: 1.png, 2.png, ...
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        log("✖ Hata: OpenCV (cv2) kütüphanesi bulunamadı! Lütfen 'pip install opencv-python numpy' komutunu çalıştırın.")
        return 0

    if not file_paths:
        return 0
    
    # Haar Cascade yolunu belirle
    if hasattr(sys, '_MEIPASS'):
        cascade_path = os.path.join(sys._MEIPASS, 'bin', 'haarcascades', 'haarcascade_frontalface_default.xml')
    else:
        cascade_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin', 'haarcascades', 'haarcascade_frontalface_default.xml')

    use_haar = os.path.exists(cascade_path)
    if use_haar:
        face_cascade = cv2.CascadeClassifier(cascade_path)
    else:
        log("⚠ Haar Cascade modeli bulunamadı, sadece dlib kullanılacak.")
    
    # Dlib'i yükle
    try:
        import dlib
        detector = dlib.get_frontal_face_detector()
        use_dlib = True
        log("✅ Dlib yüz dedektörü yüklendi.")
    except ImportError:
        use_dlib = False
        log("⚠ Dlib bulunamadı, sadece Haar Cascade kullanılacak.")
        if not use_haar:
            log("✖ Hiçbir yüz tanıma yöntemi kullanılamıyor!")
            return 0
    
    total_faces_extracted = 0

    for fpath in file_paths:
        if not os.path.isfile(fpath):
            continue
            
        fname = os.path.basename(fpath)
        folder = os.path.dirname(fpath)
        name, ext = os.path.splitext(fname)
        
        # Görüntüyü yükle
        with open(fpath, "rb") as stream:
            bytes_array = bytearray(stream.read())
        numpy_array = np.asarray(bytes_array, dtype=np.uint8)
        img = cv2.imdecode(numpy_array, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            log(f"✖ {fname}: Görüntü okunamadı.")
            continue

        faces = []
        method_used = ""
        
        # Önce Haar Cascade dene
        if use_haar:
            if len(img.shape) == 3:
                if img.shape[2] == 4:
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                else:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img

            haar_faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(50, 50)
            )
            
            if len(haar_faces) >= 2:
                faces = [(x, y, w, h) for (x, y, w, h) in haar_faces]
                method_used = "Haar Cascade"
                log(f"✅ {fname}: Haar Cascade ile {len(faces)} yüz bulundu.")
        
        # Haar başarısız olduysa veya yeterli yüz bulamadıysa dlib dene
        if len(faces) < 2 and use_dlib:
            log(f"⚠ {fname}: Haar Cascade yetersiz kaldı. Dlib ile gelişmiş tarama başlatılıyor...")
            
            if len(img.shape) == 3:
                if img.shape[2] == 4:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                else:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

            dlib_faces = detector(img_rgb, 1)
            
            if len(dlib_faces) >= 2:
                faces = []
                for face in dlib_faces:
                    x = face.left()
                    y = face.top()
                    w = face.right() - face.left()
                    h = face.bottom() - face.top()
                    faces.append((x, y, w, h))
                method_used = "Dlib"
                log(f"✅ {fname}: Dlib ile {len(faces)} yüz bulundu! (Haar bulamadı, Dlib başardı)")

        if len(faces) < 2:
            log(f"⚠ {fname}: Çoklu vesikalık tespit edilemedi (Bulunan Yüz: {len(faces)}). Atlanıyor.")
            continue

        # ── Yüzleri sol üstten sağa-aşağıya doğru sırala ──────────────────
        # Önce satır (y konumu), aynı satırdaysa sütun (x konumu) öncelikli.
        # Satır toleransı: yüz yüksekliğinin yarısı kadar y farkı aynı satır sayılır.
        row_tolerance = min(h for (_, _, _, h) in faces) // 2
        faces_sorted = sorted(faces, key=lambda f: (f[1] // max(row_tolerance, 1), f[0]))
        # ────────────────────────────────────────────────────────────────────

        log(f"🔍 {fname}: {method_used} kullanılarak {len(faces_sorted)} adet yüz sol üstten sağa-aşağı sırayla kesiliyor...")

        # Her bir yüz için genişletilmiş bir çerçeve kes
        for i, (x, y, w, h) in enumerate(faces_sorted):
            top_padding = int(h * 0.6)
            bottom_padding = int(h * 0.5)
            side_padding = int(w * 0.45)

            new_x = max(0, x - side_padding)
            new_y = max(0, y - top_padding)
            new_w = min(img.shape[1] - new_x, w + (side_padding * 2))
            new_h = min(img.shape[0] - new_y, h + top_padding + bottom_padding)

            face_img = img[new_y:new_y+new_h, new_x:new_x+new_w]

            # Sade rakamla isimlendirme: start_num'dan başlayarak artan sayı
            out_num = start_num + total_faces_extracted
            out_name = f"{out_num}{ext}"
            out_path = os.path.join(folder, out_name)

            is_success, buffer = cv2.imencode(ext, face_img)
            if is_success:
                with open(out_path, "wb") as f_out:
                    f_out.write(buffer)
                log(f"   ✔ [{out_num}] → {out_name}  (x={x}, y={y})")
                total_faces_extracted += 1
            else:
                log(f"✖ {out_name} kaydedilemedi!")

        log(f"✔ {fname} içindeki {len(faces_sorted)} resim başarıyla ayrıldı ({method_used}).")

    return total_faces_extracted
