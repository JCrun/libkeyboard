from ctypes import cdll
try:
    cdll.LoadLibrary("libiconv.dll") 
    cdll.LoadLibrary("libzbar-64.dll") 
    print("✅ DLL loaded successfully!")
except Exception as e:
    print(f"❌ Failed: {e}")
