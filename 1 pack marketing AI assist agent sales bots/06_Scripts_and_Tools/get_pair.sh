#!/bin/bash
curl -s -X DELETE "http://127.0.0.1:8080/instance/logout/number1" -H "apikey: B6D711FCDE4D4FD5936544120E713976"
sleep 2
curl -s -X GET "http://127.0.0.1:8080/instance/connect/number1?number=77771269911" -H "apikey: B6D711FCDE4D4FD5936544120E713976"
