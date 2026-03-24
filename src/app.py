import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import customtkinter as ctk

from src.config import *
from src.operations import (
    op_truncate_after_n, op_rename_ext, op_convert_to_jpg, op_pdf_to_jpg, op_rotate_images,
    op_rename_sequence, op_extract_photos, op_extract_photos_dlib, op_extract_photos_hybrid
)
from src.file_explorer import FileExplorerGrid

class TruncatePreviewModal(ctk.CTkToplevel):
    """Karakter kesme öncesi değişiklikleri gösteren önizleme penceresi."""
    def __init__(self, master, file_paths, n, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Kesme Önizlemesi")
        self.geometry("600x450")
        
        # Dialogu üstte ve modal tut
        # Windows bazen topmost'a rağmen arkaya atabilir, transient o yüzden önemli.
        self.transient(master)
        self.grab_set() 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.result = False
        
        # Başlık
        ctk.CTkLabel(
            self, text=f"İlk {n} karakter sonrası silinecek. Onaylıyor musunuz?", 
            font=FONT_HEAD, text_color=TEXT
        ).grid(row=0, column=0, pady=15, padx=20, sticky="w")
        
        # Kaydırılabilir liste
        scroll = ctk.CTkScrollableFrame(self, fg_color=CARD, corner_radius=10)
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        for path in file_paths:
            if not os.path.isfile(path): continue
            
            fname = os.path.basename(path)
            name, ext = os.path.splitext(fname)
            
            if len(name) > n:
                new_name = name[:n] + ext
                lbl_text = f"📄 {fname}   ➔   {new_name}"
                color = TEXT
            else:
                lbl_text = f"📄 {fname}   ➔   (Değişmeyecek)"
                color = SUBTEXT
                
            ctk.CTkLabel(scroll, text=lbl_text, font=FONT_MONO, text_color=color).pack(anchor="w", pady=2, padx=5)
            
        # Alt butonlar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=15, padx=20, sticky="e")
        
        ctk.CTkButton(
            btn_frame, text="İptal", fg_color=BORDER, hover_color=CARD, 
            text_color=TEXT, font=FONT_BODY, command=self._cancel, width=100
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="Onayla ve Çalıştır", fg_color=ACCENT, hover_color=ACCENT2, 
            text_color="#ffffff", font=FONT_BODY, command=self._confirm, width=150
        ).pack(side="left")
        
    def _cancel(self):
        self.result = False
        self.destroy()
        
    def _confirm(self):
        self.result = True
        self.destroy()

class AllToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_theme()
        self.title("dESkart dosya düzenleme v1.7")
        self.geometry("1100x800")
        self.minsize(800, 600)
        self.configure(fg_color=BG)
        
        # Pencere ikonu ayarı
        try:
            if os.path.exists("fav.ico"):
                self.iconbitmap("fav.ico")
        except Exception:
            pass

        self._folder = tk.StringVar(value="")
        self._n_var  = tk.StringVar(value="4")
        self._dpi_var = tk.StringVar(value="150")
        self._apply_to_all = tk.BooleanVar(value=False)

        # İşlem seçenek değişkenleri
        self._opts = {
            "truncate":   tk.BooleanVar(),
            "jpeg2jpg":   tk.BooleanVar(),
            "bmp2jpg":    tk.BooleanVar(),
            "png2jpg":    tk.BooleanVar(),
            "jfif2jpg":   tk.BooleanVar(),
            "pdf2jpg":    tk.BooleanVar(),
            "ext_photos": tk.BooleanVar(),
            "ext_photos_dlib": tk.BooleanVar(),
            "ext_photos_hybrid": tk.BooleanVar(),
            "seq_rename": tk.BooleanVar(),
        }

        # Ardışık isim değiştirme başlangıç numarası
        self._seq_start_var = tk.StringVar(value="1")

        self._build_ui()
        self.after(500, self._init_windnd)

    def _init_windnd(self):
        try:
            import windnd
            # İşletim sistemi dnd olayını ana pencereye bağlıyoruz
            windnd.hook_dropfiles(self.winfo_id(), func=lambda files: self._file_explorer._on_drag_drop(files))
        except Exception as e:
            print(f"windnd hook failed: {e}")

    # ── UI İnşası ──────────────────────────────────
    def _build_ui(self):
        # ── Üst başlık ──
        header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="⚙  dESkart",
            font=FONT_TITLE, text_color=TEXT
        ).pack(side="left", padx=24, pady=14)

        ctk.CTkLabel(
            header, text="dosya düzenleme v1.7",
            font=FONT_BODY, text_color=SUBTEXT
        ).pack(side="left", padx=0, pady=14)

        # ── Ana içerik ──
        body = ctk.CTkFrame(self, fg_color=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(16, 20))
        body.columnconfigure(0, weight=0, minsize=320) # Sol panel sabit minimum genişlikte
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Sol panel — tüm form işlemleri
        left = ctk.CTkScrollableFrame(body, fg_color=PANEL, corner_radius=14)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=0)
        self._build_left_panel(left)

        # Sağ panel — sekmeler (Dosyalar ve Log)
        self._tab_view = ctk.CTkTabview(body, fg_color=PANEL, corner_radius=14)
        self._tab_view.grid(row=0, column=1, sticky="nsew", pady=(0, 0))
        self._tab_view.add("Dosya Gezgini")
        self._tab_view.add("İşlem Günlüğü")

        self._build_file_explorer(self._tab_view.tab("Dosya Gezgini"))
        self._build_log(self._tab_view.tab("İşlem Günlüğü"))

    def _build_left_panel(self, parent):
        parent.columnconfigure(0, weight=1)

        # -- Klasör Seçimi --
        folder_frame = ctk.CTkFrame(parent, fg_color="transparent")
        folder_frame.pack(fill="x", padx=12, pady=(15, 8))
        
        ctk.CTkLabel(
            folder_frame, text="📁  Klasör Seçimi",
            font=FONT_HEAD, text_color=TEXT
        ).pack(anchor="w", pady=(0, 4))
        
        entry = ctk.CTkEntry(
            folder_frame, textvariable=self._folder,
            font=FONT_MONO, height=34,
            fg_color=CARD, border_color=BORDER,
            text_color=TEXT, placeholder_text="Açmak için klasör seçin..."
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            folder_frame, text="Seç", width=60, height=34,
            font=FONT_BODY, fg_color=ACCENT, hover_color=ACCENT2,
            command=self._pick_folder
        ).pack(side="right")

        ctk.CTkFrame(parent, fg_color=BORDER, height=1).pack(fill="x", padx=12, pady=(4, 8))

        # -- Uygula Alanı --
        apply_opt_frame = ctk.CTkFrame(parent, fg_color="transparent")
        apply_opt_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        ctk.CTkSwitch(
            apply_opt_frame, text="Tüm Dosyalara Uygula",
            variable=self._apply_to_all, font=FONT_BODY, text_color=TEXT,
            progress_color=ACCENT, button_color=TEXT, button_hover_color=SUBTEXT
        ).pack(side="left")

        self._status = ctk.CTkLabel(
            parent, text="Hazır", font=FONT_BODY, text_color=SUBTEXT
        )
        self._status.pack(pady=(0, 4))
        
        ctk.CTkButton(
            parent,
            text="▶  Seçili Dosyalara Uygula",
            font=("Segoe UI", 13, "bold"),
            height=40,
            fg_color=ACCENT, hover_color=ACCENT2,
            corner_radius=8,
            command=self._run
        ).pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkFrame(parent, fg_color=BORDER, height=1).pack(fill="x", padx=12, pady=(4, 8))

        # -- İşlemler --
        ctk.CTkLabel(
            parent, text="İşlemler (Seçili Dosyalara)",
            font=FONT_HEAD, text_color=TEXT
        ).pack(anchor="w", padx=12, pady=(0, 4))

        # 1. DOSYA İSİM İŞLEMLERİ (Karakter Kes & Numara Ver)
        name_frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=8)
        name_frame.pack(fill="x", padx=12, pady=4)
        
        t_row = ctk.CTkFrame(name_frame, fg_color="transparent")
        t_row.pack(fill="x", padx=10, pady=(10, 4))
        ctk.CTkCheckBox(
            t_row, text="N. karakterden sonrasını sil N =", variable=self._opts["truncate"],
            checkbox_width=20, checkbox_height=20, font=FONT_BODY, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left")
        ctk.CTkEntry(
            t_row, textvariable=self._n_var,
            width=50, height=26, font=FONT_BODY,
            fg_color=BG, border_color=BORDER, text_color=TEXT
        ).pack(side="left", padx=6)

        s_row = ctk.CTkFrame(name_frame, fg_color="transparent")
        s_row.pack(fill="x", padx=10, pady=(4, 10))
        ctk.CTkCheckBox(
            s_row, text="Numaralandırarak Adlandır. Başlangıç =", variable=self._opts["seq_rename"],
            checkbox_width=20, checkbox_height=20, font=FONT_BODY, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left")
        ctk.CTkEntry(
            s_row, textvariable=self._seq_start_var,
            width=50, height=26, font=FONT_BODY,
            fg_color=BG, border_color=BORDER, text_color=TEXT
        ).pack(side="left", padx=6)

        # 2. FORMAT DÖNÜŞTÜRME
        conv_frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=8)
        conv_frame.pack(fill="x", padx=12, pady=4)
        
        row1 = ctk.CTkFrame(conv_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(10, 4))
        ctk.CTkCheckBox(
            row1, text="🖼 .jpeg → .jpg", variable=self._opts["jpeg2jpg"], font=FONT_BODY,
            checkbox_width=20, checkbox_height=20, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left", expand=True, anchor="w")
        ctk.CTkCheckBox(
            row1, text="🖼 .png → .jpg", variable=self._opts["png2jpg"], font=FONT_BODY,
            checkbox_width=20, checkbox_height=20, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left", expand=True, anchor="w")
        
        row2 = ctk.CTkFrame(conv_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=4)
        ctk.CTkCheckBox(
            row2, text="🖼 .bmp → .jpg", variable=self._opts["bmp2jpg"], font=FONT_BODY,
            checkbox_width=20, checkbox_height=20, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left", expand=True, anchor="w")
        ctk.CTkCheckBox(
            row2, text="🖼 .jfif → .jpg", variable=self._opts["jfif2jpg"], font=FONT_BODY,
            checkbox_width=20, checkbox_height=20, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left", expand=True, anchor="w")

        pdf_row = ctk.CTkFrame(conv_frame, fg_color="transparent")
        pdf_row.pack(fill="x", padx=10, pady=(4, 10))
        ctk.CTkCheckBox(
            pdf_row, text="📄 .pdf → .jpg", variable=self._opts["pdf2jpg"], font=FONT_BODY,
            checkbox_width=20, checkbox_height=20, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left")
        ctk.CTkLabel(pdf_row, text="DPI:", font=FONT_SMALL, text_color=SUBTEXT).pack(side="left", padx=(10, 4))
        ctk.CTkEntry(
            pdf_row, textvariable=self._dpi_var,
            width=50, height=26, font=FONT_BODY,
            fg_color=BG, border_color=BORDER, text_color=TEXT
        ).pack(side="left", padx=0)

        # 3. YÜZ KESİCİ SEÇENEKLERİ
        face_frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=8)
        face_frame.pack(fill="x", padx=12, pady=4)
        
        ctk.CTkLabel(face_frame, text="✂️ Vesikalıkları Kes/Ayır:", font=FONT_BODY, text_color=SUBTEXT).pack(anchor="w", padx=10, pady=(8,4))
        
        f_row = ctk.CTkFrame(face_frame, fg_color="transparent")
        f_row.pack(fill="x", padx=10, pady=(0, 4))
        ctk.CTkCheckBox(
            f_row, text="Haar Cascade", variable=self._opts["ext_photos"],
            checkbox_width=20, checkbox_height=20, font=FONT_BODY, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left", expand=True, anchor="w")
        ctk.CTkCheckBox(
            f_row, text="Dlib", variable=self._opts["ext_photos_dlib"],
            checkbox_width=20, checkbox_height=20, font=FONT_BODY, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left", expand=True, anchor="w")
        
        f_row2 = ctk.CTkFrame(face_frame, fg_color="transparent")
        f_row2.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkCheckBox(
            f_row2, text="Hibrit (Haar + Dlib)", variable=self._opts["ext_photos_hybrid"],
            checkbox_width=20, checkbox_height=20, font=FONT_BODY, fg_color=ACCENT, hover_color=ACCENT2
        ).pack(side="left", expand=True, anchor="w")

        # Tümünü seç / kaldır
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(10,12))
        ctk.CTkButton(
            btn_row, text="Tümünü Seç", height=30, font=FONT_SMALL,
            fg_color=CARD, hover_color=BORDER, text_color=SUBTEXT,
            command=self._select_all
        ).pack(side="left", expand=True, fill="x", padx=(0,4))
        ctk.CTkButton(
            btn_row, text="Temizle", height=30, font=FONT_SMALL,
            fg_color=CARD, hover_color=BORDER, text_color=SUBTEXT,
            command=self._deselect_all
        ).pack(side="left", expand=True, fill="x", padx=(4,0))

    def _build_log(self, parent):
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(12,4))
        ctk.CTkLabel(hdr, text="📋  İşlem Günlüğü", font=FONT_HEAD, text_color=TEXT).pack(side="left")
        ctk.CTkButton(
            hdr, text="Log Temizle", width=70, height=26,
            font=FONT_SMALL, fg_color=CARD, hover_color=BORDER, text_color=SUBTEXT,
            command=self._clear_log
        ).pack(side="right")

        self._log_box = ctk.CTkTextbox(
            parent, font=FONT_MONO, fg_color=BG,
            text_color=TEXT, border_color=BORDER,
            scrollbar_button_color=BORDER,
            activate_scrollbars=True
        )
        self._log_box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,12))
        self._log_box.configure(state="disabled")

    def _build_file_explorer(self, parent):
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        # --- Üst Bilgi Barı ---
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(12,4))
        
        info_label = ctk.CTkLabel(
            hdr, 
            text="Dosya veya klasörlere sağ tıklayarak işlem yapın (Çoklu seçim: Ctrl/Shift + Tıkla)", 
            font=FONT_SMALL, text_color=SUBTEXT
        )
        info_label.pack(side="left")
        
        ctk.CTkButton(
            hdr, text="Yenile", width=70, height=26,
            font=FONT_SMALL, fg_color=CARD, hover_color=BORDER, text_color=TEXT,
            command=self._refresh_file_list
        ).pack(side="right")

        # --- Grid Tabanlı Dosya Gezgini ---
        self._file_explorer = FileExplorerGrid(parent)
        self._file_explorer.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,12))

    # ── Yardımcı ──────────────────────────────────
    def _pick_folder(self):
        path = filedialog.askdirectory(title="Klasör Seç")
        if path:
            self._folder.set(path)
            self._log(f"📁 Klasör Açıldı: {path}\n")
            self._refresh_file_list()
            self._tab_view.set("Dosya Gezgini")

    def _refresh_file_list(self):
        folder = self._folder.get().strip()
        if not folder or not os.path.isdir(folder):
            return
        
        # Seçilen yeni klasörü veya mevcut klasörü yenilerken önbelleği temizle
        from src.file_explorer import FileItemCache
        FileItemCache._cache.clear()
        
        self._file_explorer.populate(folder)

    def _select_all(self):
        for v in self._opts.values():
            v.set(True)

    def _deselect_all(self):
        for v in self._opts.values():
            v.set(False)

    def _log(self, msg: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", msg + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def _set_status(self, msg, color=SUBTEXT):
        self._status.configure(text=msg, text_color=color)

    # ── Ana çalıştır ──────────────────────────────
    def _run(self):
        folder = self._folder.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Hata", "Lütfen önce geçerli bir klasör seçin.")
            return
            
        if self._apply_to_all.get():
            selected_files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            if not selected_files:
                messagebox.showwarning("Uyarı", "Seçili klasörde hiçbir dosya bulunamadı!")
                return
        else:
            selected_files = self._file_explorer.get_selected_files()
            if not selected_files:
                messagebox.showwarning("Uyarı", "Gezginden hiçbir dosya seçmediniz!\n\nİşlem yapılacak dosyaları listeden seçin veya 'Tüm Dosyalara Uygula' özelliğini açın.")
                return

        selected_operations = [k for k, v in self._opts.items() if v.get()]
        if not selected_operations:
            messagebox.showwarning("Uyarı", "Lütfen soldan en az bir işlem seçin.")
            return

        # ── İşlem Öncesi Kontroller & Önizlemeler ──
        if "truncate" in selected_operations:
            try:
                n = int(self._n_var.get().strip())
                if n <= 0: raise ValueError 
            except ValueError:
                messagebox.showerror("Hata", "Lütfen 0'dan büyük geçerli bir kesme sayısı (sayısal) giriniz.")
                return
                
            # Modal önizleme çağır (Önizleme boyunca ana ekran bekler)
            preview = TruncatePreviewModal(self, selected_files, n)
            self.wait_window(preview)
            
            if not preview.result:
                self._log("✖ Kesme işlemi kullanıcı tarafından iptal edildi.")
                return # Tüm run döngüsünü bitir

        if "seq_rename" in selected_operations:
            try:
                seq_start = int(self._seq_start_var.get().strip())
                if seq_start < 0: raise ValueError
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir başlangıç numarası (örneğin: 1) giriniz.")
                return
                
        # Run worker thread
        threading.Thread(target=self._run_worker, args=(selected_files, selected_operations), daemon=True).start()

    def _run_worker(self, selected_files, selected_operations):
        self._set_status("⏳ Çalışıyor...", WARNING)
        total = 0
        self._log("─" * 50)
        self._log(f"🚀 Başlatıldı → Seçilen {len(selected_files)} dosya işlenecek.")
        self._log("─" * 50)
        self._tab_view.set("İşlem Günlüğü")

        try:
            if "truncate" in selected_operations:
                n = int(self._n_var.get().strip()) # Validate yukarıda yapıldı
                self._log(f"\n[1] İlk {n} karakter sonrası siliniyor...")
                c = op_truncate_after_n(selected_files, n, self._log)
                self._log(f"   ✅ {c} dosya işlendi.")
                total += c

            if "jpeg2jpg" in selected_operations:
                self._log("\n[2] .jpeg → .jpg yeniden adlandırılıyor...")
                c = op_rename_ext(selected_files, "jpeg", "jpg", self._log)
                self._log(f"   ✅ {c} dosya işlendi.")
                total += c

            if "bmp2jpg" in selected_operations:
                self._log("\n[3] .bmp → .jpg dönüştürülüyor...")
                c = op_convert_to_jpg(selected_files, "bmp", self._log)
                self._log(f"   ✅ {c} dosya işlendi.")
                total += c

            if "png2jpg" in selected_operations:
                self._log("\n[4] .png → .jpg dönüştürülüyor...")
                c = op_convert_to_jpg(selected_files, "png", self._log)
                self._log(f"   ✅ {c} dosya işlendi.")
                total += c
                
            if "jfif2jpg" in selected_operations:
                self._log("\n[5] .jfif → .jpg dönüştürülüyor...")
                c = op_convert_to_jpg(selected_files, "jfif", self._log)
                self._log(f"   ✅ {c} dosya işlendi.")
                total += c

            if "pdf2jpg" in selected_operations:
                try:
                    dpi = int(self._dpi_var.get().strip())
                except ValueError:
                    self._log("\n✖ HATA: Lütfen geçerli bir DPI çözünürlüğü (sayısal) giriniz.")
                    self._set_status("Hata oluştu", DANGER)
                    return
                self._log(f"\n[6] .pdf → .jpg dönüştürülüyor (DPI={dpi})...")
                c = op_pdf_to_jpg(selected_files, dpi, self._log)
                self._log(f"   ✅ {c} sayfa işlendi.")
                total += c
                
            if "ext_photos" in selected_operations:
                self._log(f"\n[7] Yapay Zeka (Haar Cascade) ile vesikalıklar tespit edilip kesiliyor...")
                c = op_extract_photos(selected_files, self._log)
                self._log(f"   ✅ {c} adet yüz başarıyla ayrı dosyalara çıkarıldı.")
                total += c
            
            if "ext_photos_dlib" in selected_operations:
                self._log(f"\n[7b] Yapay Zeka (Dlib) ile vesikalıklar tespit edilip kesiliyor...")
                c = op_extract_photos_dlib(selected_files, self._log)
                self._log(f"   ✅ {c} adet yüz başarıyla ayrı dosyalara çıkarıldı.")
                total += c
            
            if "ext_photos_hybrid" in selected_operations:
                self._log(f"\n[7c] Yapay Zeka (Hibrit: Haar + Dlib) ile vesikalıklar tespit edilip kesiliyor...")
                c = op_extract_photos_hybrid(selected_files, self._log)
                self._log(f"   ✅ {c} adet yüz başarıyla ayrı dosyalara çıkarıldı.")
                total += c
                
            if "seq_rename" in selected_operations:
                seq_start = int(self._seq_start_var.get().strip())
                self._log(f"\n[8] Seçili dosyalar sırayla ({seq_start}'den başlayarak) baştan adlandırılıyor...")
                c = op_rename_sequence(selected_files, seq_start, self._log)
                self._log(f"   ✅ {c} dosya yeniden adlandırıldı.")
                total += c

        except Exception as e:
            self._log(f"\n✖ Beklenmeyen hata: {e}")
            self._set_status("Hata oluştu", DANGER)
            return

        self._log("─" * 50)
        self._log(f"🏁 Tamamlandı. Toplam {total} işlem yapıldı.")
        self._log("─" * 50 + "\n")
        self._set_status(f"✅ Tamamlandı — {total} işlem", SUCCESS)
        
        # After operation, refresh the explorer on the main thread in case files were renamed/deleted
        # also deselect operations
        self.after(500, self._post_run_cleanup)

    def _post_run_cleanup(self):
        self._refresh_file_list()
        self._deselect_all()
