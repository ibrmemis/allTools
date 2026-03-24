import urllib.request
import json
import zipfile
import tempfile
import os
import shutil

def download_and_extract_poppler():
    print("Checking for the latest Poppler release...")
    api_url = "https://api.github.com/repos/oschwartz10612/poppler-windows/releases/latest"
    
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    assets = data.get("assets", [])
    if not assets:
        print("No poppler zip found!")
        return

    download_url = assets[0]["browser_download_url"]
    print(f"Downloading: {download_url}")
    
    app_dir = os.path.abspath(os.path.dirname(__file__))
    bin_dir = os.path.join(app_dir, "bin", "poppler")
    
    if os.path.exists(bin_dir):
        import stat
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(bin_dir, onerror=remove_readonly)
    os.makedirs(bin_dir, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        urllib.request.urlretrieve(download_url, tmp.name)
        zip_path = tmp.name
        
    print("Extracting files...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # zip icinde genelde 'poppler-24.08.0' gibi bir kok klasor olur
        zip_ref.extractall(bin_dir)
        
    # Kök klasörün adını tespit edip içeriğini direkt bin_dir altına taşıyalım
    extracted_items = os.listdir(bin_dir)
    if len(extracted_items) == 1 and os.path.isdir(os.path.join(bin_dir, extracted_items[0])):
        inner_dir = os.path.join(bin_dir, extracted_items[0])
        for item in os.listdir(inner_dir):
            shutil.move(os.path.join(inner_dir, item), bin_dir)
        os.rmdir(inner_dir)

    os.unlink(zip_path)
    print(f"Poppler installed successfully: {bin_dir}")

if __name__ == "__main__":
    download_and_extract_poppler()
