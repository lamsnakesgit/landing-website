import os
import subprocess
import sys

class KalkanAuth:
    def __init__(self):
        self.sign_bin = "/app/kalkan_sign"
        if not os.path.exists(self.sign_bin):
            print(f"Warning: {self.sign_bin} not found!")

    def load_key_store(self, password):
        # Dummy xml string for now
        xml = "<test>dummy</test>"
        
        p12_paths = []
        for f in os.listdir("/keys"):
            if f.startswith("GOST") and f.endswith(".p12"):
                p12_paths.append(f"/keys/{f}")
                
        if not p12_paths:
            print("No GOST keys found in /keys!")
            return False
            
        success = False
        for p12_path in p12_paths:
            print(f"Trying Key file: {p12_path} ({os.path.getsize(p12_path)} bytes)")
            print(f"Calling kalkan_sign with {p12_path}")
            
            try:
                print(f"Using password: {repr(password)}")
                result = subprocess.run(
                    [self.sign_bin, p12_path, password, xml],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    check=False
                )
                print(f"Stdout:\n{result.stdout}")
                print(f"Stderr:\n{result.stderr}")
                if result.returncode == 0:
                    print(f"✅ Successfully loaded key and signed XML with {p12_path}!")
                    success = True
                    break
                else:
                    print(f"❌ Failed to load key {p12_path}: Return code {result.returncode}")
            except Exception as e:
                print(f"Failed to execute kalkan_sign: {e}")
                
        return success

if __name__ == "__main__":
    print("=== Testing KalkanCrypt via C Wrapper ===", flush=True)
    password = os.environ.get("ECP_PASSWORD", "Prioritize_resource3!")
    
    auth = KalkanAuth()
    res = auth.load_key_store(password)
    
    if res:
        print("✅ Success!")
    else:
        print("❌ Failed!")
        sys.exit(1)
