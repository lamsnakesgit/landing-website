import paramiko

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('151.241.100.226', username='root', password='r0oLNJP3xCO7O4SnL0bj', timeout=10)
        
        stdin, stdout, stderr = ssh.exec_command('ls -l /root/ai_lawyer/kalkan_docker/output/pdfs/ | wc -l')
        out = stdout.read().decode('utf-8', errors='ignore')
        print("Total files downloaded so far:", out.strip())
        
        stdin, stdout, stderr = ssh.exec_command('tail -n 20 /root/ai_lawyer/kalkan_docker/run_all_years.log')
        out2 = stdout.read().decode('utf-8', errors='ignore')
        print("Latest log:")
        print(out2.strip())
        
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
