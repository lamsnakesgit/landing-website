#!/usr/bin/expect -f
set timeout -1
spawn scp -o StrictHostKeyChecking=no -o ServerAliveInterval=60 kalkan_docker.zip root@151.244.228.104:/root/ai_lawyer/
expect "password:"
send "g2AjLzx1drew4ozpArNe\r"
expect eof

spawn ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 root@151.244.228.104 "cd /root/ai_lawyer && unzip -o kalkan_docker.zip && cd scripts/sud_parser/kalkan_docker && docker build -t kalkan_test . && docker run --rm kalkan_test"
expect "password:"
send "g2AjLzx1drew4ozpArNe\r"
expect eof
