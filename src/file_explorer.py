import os
import shutil
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
from PIL import Image
import subprocess

from src.config import BG, PANEL, TEXT, SUBTEXT, ACCENT, BORDER, CARD
from src.utils import natural_sort_key

class FileItemCache:
    """Thumbnail yaratmamak için basit bir bellek önbelleği."""
    _cache = {}

    @classmethod
    def get_thumbnail(cls, path, size=(80, 80)):
        if path in cls._cache:
            return cls._cache[path]
        
        try:
            with Image.open(path) as pil_image:
                pil_image.thumbnail(size)
                ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)
            cls._cache[path] = ctk_img
            return ctk_img
        except Exception:
            return None

class FileItemCard(ctk.CTkFrame):
    """Her bir dosya/klasörü temsil eden büyük ikonlu kart (Thumbnail)."""
    def __init__(self, master, name, path, is_dir, on_click, on_right_click, on_drag_start=None, on_drag_end=None, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=8, width=120, height=125, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.is_selected = False
        self.on_click_callback = on_click
        self.on_right_click_callback = on_right_click
        self.on_drag_start_callback = on_drag_start
        self.on_drag_end_callback = on_drag_end
        
        # Olay bağlamaları için tüm alt widgetlara etkinlik eklemeliyiz
        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Button-3>", lambda e: self.on_right_click_callback(e, self.path))
        
        # İçerik
        self._build_content()
        
    def _build_content(self):
        # Ikon veya Thumbnail
        self.icon_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 48))
        self.icon_label.pack(expand=True, pady=(10, 0))
        
        if self.is_dir:
            self.icon_label.configure(text="📁", text_color=ACCENT)
        else:
            ext = os.path.splitext(self.path)[1].lower()
            if ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".jfif"]:
                # Resim dosyası ise thumbnail yükle
                thumb = FileItemCache.get_thumbnail(self.path)
                if thumb:
                    self.icon_label.configure(image=thumb, text="")
                else:
                    self.icon_label.configure(text="🖼", text_color=ACCENT)
            elif ext == ".pdf":
                self.icon_label.configure(text="📄", text_color="#ef4444") # Kırmızı PDF ikonu
            else:
                self.icon_label.configure(text="📄", text_color=TEXT)
                
        # Isim (Taşmayı önlemek için kesilebilir ama uzantı daima görünmeli)
        name_part, ext_part = os.path.splitext(self.name)
        if len(self.name) > 18:
            # Uzantıyı koruyarak ismi kırp
            max_name_len = 15 - len(ext_part)
            if max_name_len < 1: max_name_len = 1
            display_name = name_part[:max_name_len] + ".." + ext_part
        else:
            display_name = self.name
            
        self.name_label = ctk.CTkLabel(self, text=display_name, font=("Segoe UI", 11), text_color=TEXT)
        self.name_label.pack(side="bottom", fill="x", pady=(0, 10), padx=5)
        
        # Event Propagation to children
        self.icon_label.bind("<Button-1>", self._on_left_click)
        self.icon_label.bind("<Button-3>", lambda e: self.on_right_click_callback(e, self.path))
        self.name_label.bind("<Button-1>", self._on_left_click)
        self.name_label.bind("<Button-3>", lambda e: self.on_right_click_callback(e, self.path))
        
        if self.on_drag_start_callback:
            self.icon_label.bind("<B1-Motion>", lambda e: self.on_drag_start_callback(self.path, e))
            self.name_label.bind("<B1-Motion>", lambda e: self.on_drag_start_callback(self.path, e))
            self.bind("<B1-Motion>", lambda e: self.on_drag_start_callback(self.path, e))
        if self.on_drag_end_callback:
            self.icon_label.bind("<ButtonRelease-1>", lambda e: self.on_drag_end_callback(e))
            self.name_label.bind("<ButtonRelease-1>", lambda e: self.on_drag_end_callback(e))
            self.bind("<ButtonRelease-1>", lambda e: self.on_drag_end_callback(e))

    def _on_left_click(self, event):
        ctrl_pressed = (event.state & 0x0004) != 0
        shift_pressed = (event.state & 0x0001) != 0
        self.on_click_callback(self.path, ctrl_pressed, shift_pressed)

    def set_selected(self, state: bool):
        self.is_selected = state
        if state:
            self.configure(fg_color=ACCENT, border_color=TEXT, border_width=2)
            self.name_label.configure(text_color="#ffffff")
        else:
            self.configure(fg_color="transparent", border_width=0)
            self.name_label.configure(text_color=TEXT)

class FileItemListRow(ctk.CTkFrame):
    """Her bir dosya/klasörü yatay sıralı temsil eden Satır (List View)."""
    def __init__(self, master, name, path, is_dir, on_click, on_right_click, on_drag_start=None, on_drag_end=None, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=6, height=44, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.is_selected = False
        self.on_click_callback = on_click
        self.on_right_click_callback = on_right_click
        self.on_drag_start_callback = on_drag_start
        self.on_drag_end_callback = on_drag_end
        
        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Button-3>", lambda e: self.on_right_click_callback(e, self.path))
        if self.on_drag_start_callback:
            self.bind("<B1-Motion>", lambda e: self.on_drag_start_callback(self.path, e))
        if self.on_drag_end_callback:
            self.bind("<ButtonRelease-1>", lambda e: self.on_drag_end_callback(e))
        
        self._build_content()
        
    def _build_content(self):
        # Icon
        self.icon_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 24), width=40)
        self.icon_label.pack(side="left", padx=(10, 5))
        
        if self.is_dir:
            self.icon_label.configure(text="📁", text_color=ACCENT)
        else:
            ext = os.path.splitext(self.path)[1].lower()
            if ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".jfif"]:
                # Liste görünümünde performans için önizlemeyi kapattık, ikon göster
                self.icon_label.configure(text="🖼", text_color=ACCENT)
            elif ext == ".pdf":
                self.icon_label.configure(text="📄", text_color="#ef4444")
            else:
                self.icon_label.configure(text="📄", text_color=TEXT)
                
        # Name
        # Liste görünümünde daha fazla alan var, ama yine de taşarsa uzantıyı koru
        name_part, ext_part = os.path.splitext(self.name)
        if len(self.name) > 50:
            max_name_len = 45 - len(ext_part)
            if max_name_len < 1: max_name_len = 1
            display_name = name_part[:max_name_len] + "..." + ext_part
        else:
            display_name = self.name
            
        self.name_label = ctk.CTkLabel(self, text=display_name, font=("Segoe UI", 13), text_color=TEXT, anchor="w")
        self.name_label.pack(side="left", fill="x", expand=True, padx=5)
        
        self.icon_label.bind("<Button-1>", self._on_left_click)
        self.icon_label.bind("<Button-3>", lambda e: self.on_right_click_callback(e, self.path))
        self.name_label.bind("<Button-1>", self._on_left_click)
        self.name_label.bind("<Button-3>", lambda e: self.on_right_click_callback(e, self.path))

        if self.on_drag_start_callback:
            self.icon_label.bind("<B1-Motion>", lambda e: self.on_drag_start_callback(self.path, e))
            self.name_label.bind("<B1-Motion>", lambda e: self.on_drag_start_callback(self.path, e))
            self.bind("<B1-Motion>", lambda e: self.on_drag_start_callback(self.path, e))
        if self.on_drag_end_callback:
            self.icon_label.bind("<ButtonRelease-1>", lambda e: self.on_drag_end_callback(e))
            self.name_label.bind("<ButtonRelease-1>", lambda e: self.on_drag_end_callback(e))
            self.bind("<ButtonRelease-1>", lambda e: self.on_drag_end_callback(e))

    def _on_left_click(self, event):
        ctrl_pressed = (event.state & 0x0004) != 0
        shift_pressed = (event.state & 0x0001) != 0
        self.on_click_callback(self.path, ctrl_pressed, shift_pressed)

    def set_selected(self, state: bool):
        self.is_selected = state
        if state:
            self.configure(fg_color=ACCENT)
            self.name_label.configure(text_color="#ffffff")
        else:
            self.configure(fg_color="transparent")
            self.name_label.configure(text_color=TEXT)


class FileExplorerGrid(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, **kwargs)
        
        self.root_path = None
        self.sort_mode = "name"
        self.view_mode = "grid" # "grid" veya "list"
        
        self.items_data = [] # Tüm dosya ve yol bilgileri listesi
        self._cards = [] # Görsel kart objeleri
        self.selected_paths = set()
        self._last_selected_index = None
        self._is_dragging = False
        
        # Kes/Yapıştır panosu
        self._clipboard = set()
        self._clipboard_action = None # "cut" ya da "copy" için ileride büyütebiliriz
        
        # Sağ tık menüsü (Context Menu)
        self.context_menu = tk.Menu(self, tearoff=0, bg=PANEL, fg=TEXT, activebackground=ACCENT, activeforeground="#ffffff")
        self.context_menu.add_command(label="Yenile", command=self._refresh_root)
        self.context_menu.add_separator()
        
        view_menu = tk.Menu(self.context_menu, tearoff=0, bg=PANEL, fg=TEXT, activebackground=ACCENT, activeforeground="#ffffff")
        view_menu.add_command(label="Büyük Simgeler (Izgara)", command=lambda: self._set_view_mode("grid"))
        view_menu.add_command(label="Liste (Satırlar)", command=lambda: self._set_view_mode("list"))
        self.context_menu.add_cascade(label="Görünüm", menu=view_menu)
        
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Photoshop ile Aç", command=self._open_in_photoshop)
        self.context_menu.add_separator()
        
        self.context_menu.add_command(label="Ada Göre Sırala", command=lambda: self._set_sort_mode("name"))
        self.context_menu.add_command(label="Sayısal Sırala (1,2,10...)", command=lambda: self._set_sort_mode("natural"))
        self.context_menu.add_command(label="Türe Göre Sırala", command=lambda: self._set_sort_mode("type"))
        self.context_menu.add_separator()
        
        # Döndürme Alt Menüsü
        rot_menu = tk.Menu(self.context_menu, tearoff=0, bg=PANEL, fg=TEXT, activebackground=ACCENT, activeforeground="#ffffff")
        rot_menu.add_command(label="90° (Sağa)", command=lambda: self._handle_rotation(90))
        rot_menu.add_command(label="180° (Ters)", command=lambda: self._handle_rotation(180))
        rot_menu.add_command(label="270° (Sola)", command=lambda: self._handle_rotation(270))
        self.context_menu.add_cascade(label="Görseli Döndür...", menu=rot_menu)
        
        self.context_menu.add_command(label="Yeniden Adlandır", command=self._rename_item)
        self.context_menu.add_command(label="Sil", command=self._delete_item)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Kes", command=lambda: self._cut_selection(None))
        self.context_menu.add_command(label="Yapıştır", command=lambda: self._paste_selection(None))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Yeni Klasör", command=self._create_folder)

        # Context menu action için tıklanan hedefin geçici referansı
        self._context_target_path = None

        # Arka plan sağ tıklama
        self.bind("<Button-3>", lambda e: self._show_context_menu(e, self.root_path))
        
        # Olay Bağlamaları
        self.bind("<Configure>", self._on_resize, add="+")
        
        # Seçim Kısayolları (Tümünü Seç)
        self.bind_all("<Control-a>", self._select_all_items)
        self.bind_all("<Control-A>", self._select_all_items)
        
        # Panoya Kısayollar
        self.bind_all("<Control-x>", self._cut_selection)
        self.bind_all("<Control-X>", self._cut_selection)
        self.bind_all("<Control-v>", self._paste_selection)
        self.bind_all("<Control-V>", self._paste_selection)
        
        # Silme Kısayolu (Delete tuşu)
        self.bind_all("<Delete>", self._on_delete_key)
        
    def populate(self, path):
        """Dizini okur ve Grid'i baştan çizer."""
        self.root_path = path
        self.selected_paths.clear()
        self.items_data.clear()
        self._last_selected_index = None
        
        # Eski kartları temizle
        for card in self._cards:
            card.destroy()
        self._cards.clear()
        
        if not path or not os.path.exists(path):
            return
            
        try:
            items = os.listdir(path)
        except PermissionError:
            return

        directories = []
        files = []
        
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            else:
                files.append(item)

        # Sıralama
        directories.sort(key=str.lower)
        if self.sort_mode == "type":
            files.sort(key=lambda f: (os.path.splitext(f)[1].lower(), f.lower()))
        elif self.sort_mode == "natural":
            files.sort(key=natural_sort_key)
        else:
            files.sort(key=str.lower)
            
        for d in directories:
            self.items_data.append({"name": d, "path": os.path.join(path, d), "is_dir": True})
            
        for f in files:
            self.items_data.append({"name": f, "path": os.path.join(path, f), "is_dir": False})
            
        self._build_cards()

    def _find_card_by_widget(self, widget):
        current = widget
        while current:
            if isinstance(current, (FileItemCard, FileItemListRow)):
                return current
            current = current.master
        return None

    def _on_internal_drag_start(self, path, event):
        print(f"[Drag Start] path: {path}")
        self._is_dragging = True
        self.winfo_toplevel().configure(cursor="fleur")
        
        # Sürüklenen öğe seçili değilse, tekil seçim yap
        if path not in self.selected_paths:
            self._on_card_click(path, False, False)

    def _on_internal_drag_end(self, event):
        print(f"[Drag End] Event fired. is_dragging: {self._is_dragging}")
        if not self._is_dragging: return
        self._is_dragging = False
        self.winfo_toplevel().configure(cursor="")
        
        x, y = event.x_root, event.y_root
        
        # Koordinat tabanlı hedef bulma (winfo_containing bazen customtkinter içinde sapıtabilir)
        target_card = None
        for card in self._cards:
            cx = card.winfo_rootx()
            cy = card.winfo_rooty()
            cw = card.winfo_width()
            ch = card.winfo_height()
            if cx <= x <= cx + cw and cy <= y <= cy + ch:
                target_card = card
                break
                
        print(f"[Drag End] target_card resolved: {target_card.path if target_card else 'None'}, is_dir: {target_card.is_dir if target_card else 'N/A'}")
        
        # Eğer bir klasörün üstüne bırakıldıysa ve bu klasör seçili olanlardan biri değilse
        if target_card and target_card.is_dir and target_card.path not in self.selected_paths:
            moved = False
            for src in list(self.selected_paths):
                src_basename = os.path.basename(src)
                dest = os.path.join(target_card.path, src_basename)
                if src != dest:
                    try:
                        print(f"[Drag End] Moving {src} -> {dest}")
                        shutil.move(src, dest)
                        moved = True
                        self.selected_paths.remove(src)
                    except Exception as e:
                        print(f"Internal Drop Error: {e}")
            
            if moved:
                print("[Drag End] Move successful. Refreshing...")
                self._refresh_root()

    def _build_cards(self):
        for data in self.items_data:
            if self.view_mode == "grid":
                card = FileItemCard(
                    self, 
                    name=data["name"], 
                    path=data["path"], 
                    is_dir=data["is_dir"], 
                    on_click=self._on_card_click,
                    on_right_click=self._show_context_menu,
                    on_drag_start=self._on_internal_drag_start,
                    on_drag_end=self._on_internal_drag_end
                )
            else:
                card = FileItemListRow(
                    self, 
                    name=data["name"], 
                    path=data["path"], 
                    is_dir=data["is_dir"], 
                    on_click=self._on_card_click,
                    on_right_click=self._show_context_menu,
                    on_drag_start=self._on_internal_drag_start,
                    on_drag_end=self._on_internal_drag_end
                )
            self._cards.append(card)
        self._layout_grid()
        self._update_cut_visuals()

    def _update_cut_visuals(self):
        """Kesilen dosyaların ikonlarını/yazılarını soluklaştırır."""
        for card in self._cards:
            if card.path in self._clipboard:
                # Kesilenleri daha saydam hissettir veya adını gri yap
                card.name_label.configure(text_color=SUBTEXT)
            elif not card.is_selected:
                card.name_label.configure(text_color=TEXT)

    def _cut_selection(self, event):
        """Seçilenleri kesmek için iç panoya (clipboard) alır."""
        if not self.root_path: return
        
        # Sadece textbox/entry değilse kısayolu işle
        if event and hasattr(event, "widget"):
            w_class = event.widget.winfo_class()
            if "Entry" in w_class or "Text" in w_class:
                return
        
        if not self.selected_paths:
            return
            
        self._clipboard = set(self.selected_paths)
        self._clipboard_action = "cut"
        self._update_cut_visuals()

    def _paste_selection(self, event):
        """Panodaki dosyaları bulunulan klasöre taşır."""
        if not self.root_path: return
        
        if event and hasattr(event, "widget"):
            w_class = event.widget.winfo_class()
            if "Entry" in w_class or "Text" in w_class:
                return
        
        if not self._clipboard or self._clipboard_action != "cut":
            return
            
        # Hedef klasör: Eğer biri klasöre sağ tıklayıp yapıştır dediyse o klasör, 
        # aksi halde şu an açık olan (arka plan) klasör
        target_dir = self.root_path
        if self._context_target_path and os.path.isdir(self._context_target_path) and self._context_target_path != self.root_path:
            # Sağ tıklanan öğe bir alt klasörse ve seçiliyse, target o olsun (Windows benzeri)
            # Ancak ctrl+v ile event geldiyse _context_target_path kullanmak hatalı olabilir.
            # O yüzden event yoksa (sağ tık) bunu dikkate al.
            if event is None:
                target_dir = self._context_target_path
            
        pasted_count = 0
        for src in self._clipboard:
            if not os.path.exists(src): continue
            
            basename = os.path.basename(src)
            dest = os.path.join(target_dir, basename)
            
            # Aynı dosyayı aynı yere yapıştıramayız
            if src == dest: continue
            
            try:
                shutil.move(src, dest)
                pasted_count += 1
            except Exception as e:
                print(f"Paste Error: {e}")
                
        if pasted_count > 0:
            self._clipboard.clear()
            self._refresh_root()

    def _on_drag_drop(self, files):
        """windnd tarafından çağrılan dışarıdan drag&drop işleyicisi."""
        if not self.root_path: return
        
        moved_count = 0
        for encoded_file in files:
            # windnd isimleri bytes (cp1254 veya utf-8) olarak döndürür
            try:
                src = encoded_file.decode("utf-8")
            except UnicodeDecodeError:
                src = encoded_file.decode("cp1254")
                
            if not os.path.exists(src): continue
            
            basename = os.path.basename(src)
            dest = os.path.join(self.root_path, basename)
            
            if src != dest:
                try:
                    # Başka yerlerden gelenleri bizim klasörümüze KOPYALAYALIM (Move yerine dışarıdan copy daha güvenli)
                    # Ancak aynı HDD deyse move da istenebilir. Kullanıcı Windows tarzı bekliyorsa, 
                    # genelde farklı disk ise kopyalanır, aynıysa taşınır. Biz varsayılan copy/move şimdilik shutil.copy2 ile kopyalıyoruz
                    # (Veya kullanıcı sürükle & bırak dediğine göre kesip de alabiliriz, ama kopyalamak veriyi kaybetmemek adına daha güvenlidir.)
                    if os.path.isdir(src):
                        shutil.copytree(src, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dest)
                    moved_count += 1
                except Exception as e:
                    print(f"DnD Error: {e}")
                    
        if moved_count > 0:
            self._refresh_root()

    def _layout_grid(self):
        """Kartları pencere genişliğine veya liste moduna göre dizer."""
        if not self._cards:
            return
            
        self.update_idletasks()
        frame_width = self.winfo_width()
        
        if self.view_mode == "grid":
            # Yanyana dizilim için hesaplanan genişlik (120 kart genişliği + min padding)
            card_width = 120 + 8
            columns = max(1, frame_width // card_width)
            
            for index, card in enumerate(self._cards):
                r = index // columns
                c = index % columns
                card.grid(row=r, column=c, padx=4, pady=4, sticky="n")
        else:
            # List mode
            for index, row_card in enumerate(self._cards):
                row_card.grid(row=index, column=0, padx=10, pady=2, sticky="ew")
            # Ana çerçevenin esnemesi için grid columnconfigure
            self.columnconfigure(0, weight=1)

    def _on_resize(self, event):
        """Pencere boyutu değiştiğinde akıcı tasarımı (flow) yeniler."""
        self._layout_grid()

    def _on_card_click(self, path, ctrl_pressed, shift_pressed):
        """Sol tık işleyicisi - Seçimleri yönetir."""
        # Tıklanan elemanın sırasını bul
        current_index = next((i for i, data in enumerate(self.items_data) if data["path"] == path), -1)
        if current_index == -1: return

        if shift_pressed and self._last_selected_index is not None:
            # Shift seçimi: Son seçilen ile tıklanan arasındaki her şeyi seç
            start_idx = min(self._last_selected_index, current_index)
            end_idx = max(self._last_selected_index, current_index)
            
            if not ctrl_pressed:
                self.selected_paths.clear()
                
            for i in range(start_idx, end_idx + 1):
                self.selected_paths.add(self.items_data[i]["path"])
        elif ctrl_pressed:
            # Ctrl seçimi: Toggle işlemi
            if path in self.selected_paths:
                self.selected_paths.remove(path)
                self._last_selected_index = None # Çıkardığımız için shift referansını kır
            else:
                self.selected_paths.add(path)
                self._last_selected_index = current_index
        else:
            # Normal sol tık: Tekil seçim
            self.selected_paths = {path}
            self._last_selected_index = current_index
            
        self._update_card_visuals()

    def _update_card_visuals(self):
        for card in self._cards:
            card.set_selected(card.path in self.selected_paths)

    def _select_all_items(self, event=None):
        """Ctrl+A kısayolu tetiklendiğinde tüm elemanları seçer."""
        # Eğer yazı yazılan bir kutu aktifse, Ctrl+A kısayolunu engelleme (yazıyı seçsin)
        widget_type = str(type(event.widget)).lower()
        if "entry" in widget_type or "text" in widget_type:
            return

        self.selected_paths.clear()
        for data in self.items_data:
            self.selected_paths.add(data["path"])
        self._update_card_visuals()
        
        if event: 
            return "break" # Eventin başka yerlere sıçramasını engelle

    def _on_delete_key(self, event=None):
        """Delete tuşuna basıldığında seçili dosyaları siler."""
        # Eğer bir metin kutusu aktifse, yazıyı silmesine izin ver, dosyaları silme
        widget_type = str(type(event.widget)).lower()
        if "entry" in widget_type or "text" in widget_type:
            return
            
        self._delete_item()

    def get_selected_files(self):
        """Yalnızca DOSYA olan seçimlerin yollarını döndürür."""
        paths = []
        for path in self.selected_paths:
            if os.path.isfile(path):
                paths.append(path)
        return paths

    # ── SAĞ TIK VE DOSYA YÖNETİMİ METOTLARI ──
    def _refresh_root(self):
        if self.root_path and os.path.exists(self.root_path):
            # Yenileme yaparken eski önbelleği temizle ki değişen (döndürülen) resimler yeniden yüklensin
            FileItemCache._cache.clear()
            self.populate(self.root_path)

    def _set_sort_mode(self, mode):
        if self.sort_mode != mode:
            self.sort_mode = mode
            self._refresh_root()

    def _set_view_mode(self, mode):
        if self.view_mode != mode:
            self.view_mode = mode
            self._refresh_root()

    def _handle_rotation(self, angle):
        if not self.selected_paths:
            messagebox.showwarning("Uyarı", "Döndürülecek hiçbir dosya seçilmedi.")
            return

        # Modüler çağırma (app.py threading üzerinden çalışmadığı için UI dondurabilir,
        # fakat çok yüklü fotoğraflar değilse sorun teşkil etmeyecektir).
        from src.operations import op_rotate_images
        
        # Basit bir log konsolu (işlemleri debug için görmek istersek)
        def silent_log(msg): pass
            
        files_to_rotate = [p for p in self.selected_paths if os.path.isfile(p)]
        if not files_to_rotate: return
        
        c = op_rotate_images(files_to_rotate, angle, silent_log)
        self._refresh_root()
        messagebox.showinfo("Döndürme Başarılı", f"{c} adet görsel başarıyla döndürüldü!")

    def _open_in_photoshop(self):
        if not self.selected_paths:
            return
            
        files_to_open = [p for p in self.selected_paths if os.path.isfile(p)]
        if not files_to_open:
            messagebox.showwarning("Uyarı", "Açılacak bir dosya seçilmedi.")
            return

        # Windows Registry üzerinden Photoshop yolunu bulmaya çalışalım
        photoshop_path = "photoshop" # PATH'de varsa diye varsayılan
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Photoshop.exe") as key:
                photoshop_path = winreg.QueryValue(key, None)
        except Exception:
            pass # Bulunamazsa 'photoshop' komutu denenir

        try:
            # Photoshop'u seçili tüm dosyalar parametre olarak geçilerek başlat
            subprocess.Popen([photoshop_path] + files_to_open)
        except FileNotFoundError:
            messagebox.showerror("Hata", "Bilgisayarınızda Adobe Photoshop bulunamadı veya sistem yolunda kayıtlı değil.")
        except Exception as e:
            messagebox.showerror("Hata", f"Photoshop başlatılamadı:\n{e}")

    def _show_context_menu(self, event, target_path):
        self._context_target_path = target_path
        
        # Eğer sağ tıklanan öğe seçili değilse, seçimi sadece ona düşür (Windows gibi)
        if target_path and target_path != self.root_path and target_path not in self.selected_paths:
            self.selected_paths = {target_path}
            self._update_card_visuals()
            
        self.context_menu.post(event.x_root, event.y_root)

    def _rename_item(self):
        target = self._context_target_path
        if not target or target == self.root_path: return

        old_name = os.path.basename(target)
        new_name = simpledialog.askstring("Yeniden Adlandır", "Yeni isim girin:", initialvalue=old_name, parent=self)
        
        if new_name and new_name != old_name:
            folder = os.path.dirname(target)
            new_path = os.path.join(folder, new_name)
            try:
                os.rename(target, new_path)
                self._refresh_root()
            except Exception as e:
                messagebox.showerror("Hata", f"Yeniden adlandırma başarısız:\n{e}")

    def _delete_item(self):
        if not self.selected_paths: return

        count = len(self.selected_paths)
        msg_text = f"Seçili {count} öğeyi kalıcı olarak silmek istediğinize emin misiniz?" if count > 1 else f"Öğeyi kalıcı olarak silmek istediğinize emin misiniz?"
        
        confirm = messagebox.askyesno("Silmeyi Onayla", msg_text, icon='warning')
        if not confirm:
            return

        for path in self.selected_paths:
            if not os.path.exists(path): continue
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                messagebox.showerror("Hata", f"'{os.path.basename(path)}' silinemedi:\n{e}")
                
        self._refresh_root()

    def _create_folder(self):
        target = self._context_target_path or self.root_path
        if not target: return

        target_dir = target if os.path.isdir(target) else os.path.dirname(target)
        folder_name = simpledialog.askstring("Yeni Klasör", "Klasör ismi girin:", parent=self)
        
        if not folder_name: return
            
        new_dir_path = os.path.join(target_dir, folder_name)
        try:
            os.mkdir(new_dir_path)
            self._refresh_root()
        except FileExistsError:
            messagebox.showerror("Hata", "Aynı isimli bir klasör veya dosya zatan var.")
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör oluşturulamadı:\n{e}")
