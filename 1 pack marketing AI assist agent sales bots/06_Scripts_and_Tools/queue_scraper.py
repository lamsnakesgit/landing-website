import os
import subprocess
import time

# Define the batches of years
year_batches = [
    ["2024", "2023"],
    ["2022", "2021"],
    ["2020", "2019"],
    ["2018", "2017"]
]

def run_batch(years):
    print(f"========== Starting batch: {years} ==========")
    cmd = [
        "docker", "run", "--rm",
        "-v", "/root/ai_lawyer/kalkan_docker/mass_downloader.py:/app/mass_downloader.py",
        "-v", "/root/ai_lawyer/kalkan_docker/data:/data",
        "-v", "/root/ai_lawyer/kalkan_docker/keys:/keys",
        "kalkan_parser:latest",
        "python3", "mass_downloader.py"
    ] + years
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Finished batch: {years}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in batch {years}: {e}")

if __name__ == "__main__":
    for batch in year_batches:
        run_batch(batch)
        print("Sleeping for 60 seconds before next batch...")
        time.sleep(60)
    print("🎉 All queued year batches completed!")
