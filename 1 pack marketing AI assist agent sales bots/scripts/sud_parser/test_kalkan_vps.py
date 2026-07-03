import ctypes
import os
import sys

ctypes.CDLL("libpcsclite.so.1", mode=ctypes.RTLD_GLOBAL)

LIB_PATH = "/root/ai_lawyer/kalkan/libkalkancrypto.so"

class KalkanCrypt:
    def __init__(self, lib_path=LIB_PATH):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Library not found at {lib_path}")
        self.lib = ctypes.CDLL(lib_path)
        
        # Init()
        self.lib.KC_Init.restype = ctypes.c_int
        res = self.lib.KC_Init()
        if res != 0:
            raise Exception(f"KC_Init failed with code {res}")
            
    def load_key_store(self, p12_path, password):
        self.lib.KC_LoadKeyStore.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self.lib.KC_LoadKeyStore.restype = ctypes.c_int
        
        res = self.lib.KC_LoadKeyStore(
            1, 
            p12_path.encode('utf-8'), 
            password.encode('utf-8'), 
            b""
        )
        if res != 0:
            raise Exception(f"KC_LoadKeyStore failed with code {res}")

if __name__ == "__main__":
    print("Testing KalkanCrypt on VPS...")
    p12_file = None
    for f in os.listdir("/root/ai_lawyer/kalkan"):
        if f.startswith("GOST") and f.endswith(".p12"):
            p12_file = os.path.join("/root/ai_lawyer/kalkan", f)
            break
            
    if not p12_file:
        print("❌ GOST .p12 file not found!")
        sys.exit(1)
        
    password = "Prioritize_resource3!"
    
    try:
        kc = KalkanCrypt()
        print("✅ KC_Init successful!")
        kc.load_key_store(p12_file, password)
        print("✅ KC_LoadKeyStore successful! The password is correct and keys are loaded.")
    except Exception as e:
        print(f"❌ Error: {e}")
