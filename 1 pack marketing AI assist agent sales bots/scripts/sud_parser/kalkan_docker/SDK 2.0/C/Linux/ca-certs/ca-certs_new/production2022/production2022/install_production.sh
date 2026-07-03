#!/bin/bash

if [ -e /usr/local/share/ca-certificates/extra/ ]; 
then 
	echo "Folder already exists"
else
	sudo mkdir /usr/local/share/ca-certificates/extra
fi

sudo cp -a production/*.pem /etc/ssl/certs/

cd production
for f in *.pem; do 
    mv -- "$f" "${f%.pem}.crt"
done
cd ..

sudo cp -a production/*.crt /usr/local/share/ca-certificates/extra/

sudo update-ca-certificates

cd production
for f in *.crt; do 
    mv -- "$f" "${f%.crt}.pem"
done
cd ..
