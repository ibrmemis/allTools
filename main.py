from src.utils import check_and_install

# Bağımlılık kontrolü (uygulama import edilmeden önce yapılmalı)
check_and_install("Pillow", "PIL")
check_and_install("pdf2image")
check_and_install("customtkinter")

if __name__ == "__main__":
    from src.app import AllToolsApp
    app = AllToolsApp()
    app.mainloop()
