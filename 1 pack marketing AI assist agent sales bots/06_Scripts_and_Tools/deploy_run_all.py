import paramiko
import os
import sys

host = '151.241.100.226'
port = 22
user = 'root'
password = 'r0oLNJP3xCO7O4SnL0bj'

base_local = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scripts/sud_parser/kalkan_docker'
base_remote = '/root/ai_lawyer/kalkan_docker'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting to VPS...")
    ssh.connect(host, port, user, password, timeout=60)
    
    sftp = ssh.open_sftp()
    
    files_to_upload = [
        'sud_parser.py', 
        'run_all_years.py',
        'upload_to_gdrive.py',
        'Dockerfile'
    ]
    for fname in files_to_upload:
        print(f"Uploading {fname}...")
        sftp.put(os.path.join(base_local, fname), os.path.join(base_remote, fname))
        
    sftp.close()

    print("Skipping docker build, as we map sud_parser.py directly...")

    print("\nStarting run_all_years.py in background via nohup...")
    # run_all_years runs the docker containers sequentially
    start_cmd = f'cd {base_remote} && nohup python3 run_all_years.py > run_all_years.log 2>&1 < /dev/null &'
    ssh.exec_command(start_cmd)
    
    print("✅ Background task started. Check /root/ai_lawyer/run_all_years.log on VPS for progress.")
    ssh.close()

if __name__ == "__main__":
    main()
