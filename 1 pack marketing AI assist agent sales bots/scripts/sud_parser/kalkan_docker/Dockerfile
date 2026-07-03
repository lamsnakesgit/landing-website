FROM almalinux:8

RUN dnf update -y && dnf install -y \
    python39 python39-pip \
    libxml2 \
    xmlsec1 \
    xmlsec1-openssl \
    pcsc-lite \
    libtool-ltdl \
    mesa-libGL \
    wget tar gcc make \
    && dnf clean all

# Собираем GNU libiconv (символ `libiconv` нужен KalkanCrypt)
RUN wget https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.17.tar.gz && \
    tar xzf libiconv-1.17.tar.gz && \
    cd libiconv-1.17 && \
    ./configure --prefix=/usr --enable-shared && \
    make && make install && \
    ldconfig && \
    cd / && rm -rf libiconv-1.17*

WORKDIR /app

# Копируем библиотеки Kalkan (cp -L разворачивает симлинки, гарантируя реальные байты)
COPY lib/libkalkancrypto.so /usr/lib64/libkalkancrypto.so
COPY lib/libkalkancryptwr-64.so.2.0.2 /usr/lib64/libkalkancryptwr-64.so.2.0.2
RUN cp /usr/lib64/libkalkancryptwr-64.so.2.0.2 /usr/lib64/libkalkancryptwr-64.so && \
    cp /usr/lib64/libkalkancryptwr-64.so.2.0.2 /usr/lib/libkalkancryptwr-64.so && \
    ldconfig

RUN python3 -m pip install --upgrade pip && \
    pip3 install scikit-build && \
    pip3 install requests urllib3 beautifulsoup4 ddddocr Pillow

COPY KalkanCrypt.h .
COPY kalkan_sign.c .
COPY auth_kalkan.py .
COPY sud_parser.py .
COPY search_cases.py .
COPY certs /certs

# Устанавливаем корневые сертификаты НУЦ РК в системное хранилище (как в SDK install_production_centos.sh)
RUN find /certs -name "*.pem" -exec cp {} /usr/share/pki/ca-trust-source/anchors/ \; && \
    find /certs -name "*.cer" -exec cp {} /usr/share/pki/ca-trust-source/anchors/ \; && \
    update-ca-trust extract && echo "✅ CA trust updated"

ENV LD_LIBRARY_PATH=/usr/lib:/usr/lib64

RUN gcc -o kalkan_sign kalkan_sign.c -ldl

RUN mkdir -p /output
CMD ["python3", "-u", "sud_parser.py"]
