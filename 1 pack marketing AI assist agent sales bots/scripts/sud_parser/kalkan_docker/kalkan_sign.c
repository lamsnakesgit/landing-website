#include <stdio.h>
#include <dlfcn.h>
#include <string.h>
#include <stdlib.h>
#include "KalkanCrypt.h"

/* KC_CERT_CA = 0x201, KC_CERT_INTERMEDIATE = 0x202 */
#define KC_CERT_CA           0x201
#define KC_CERT_INTERMEDIATE 0x202

typedef int (*KC_GetFunctionList1)(stKCFunctionsType **KCfunc);

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <p12_path> <password> <xml_string>\n", argv[0]);
        return 1;
    }
    const char *p12  = argv[1];
    const char *pwd  = argv[2];
    const char *xml  = argv[3];

    void *handle = dlopen("libkalkancryptwr-64.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "dlopen error: %s\n", dlerror());
        return 1;
    }

    KC_GetFunctionList1 getFuncs = (KC_GetFunctionList1)dlsym(handle, "KC_GetFunctionList");
    if (!getFuncs) {
        fprintf(stderr, "KC_GetFunctionList not found\n");
        return 1;
    }

    stKCFunctionsType *kc;
    getFuncs(&kc);

    unsigned long rv = kc->KC_Init();
    if (rv != 0) {
        fprintf(stderr, "KC_Init failed: %lu\n", rv);
        return 1;
    }

    /* Загружаем корневой сертификат НУЦ РК (ROOT CA) из SDK-шного PEM */
    rv = kc->X509LoadCertificateFromFile("/certs/root_gost_2022.pem", KC_CERT_CA);
    if (rv != 0) {
        fprintf(stderr, "Предупреждение: X509LoadCertificateFromFile(root) = %lu\n", rv);
    } else {
        fprintf(stderr, "✅ ROOT CA загружен\n");
    }

    /* Загружаем промежуточный сертификат НУЦ (NCA) */
    rv = kc->X509LoadCertificateFromFile("/certs/nca_gost_2022.pem", KC_CERT_INTERMEDIATE);
    if (rv != 0) {
        fprintf(stderr, "Предупреждение: X509LoadCertificateFromFile(nca) = %lu\n", rv);
    } else {
        fprintf(stderr, "✅ NCA CA загружен\n");
    }

    /* Загружаем ключ из p12 */
    rv = kc->KC_LoadKeyStore(1, (char*)pwd, strlen(pwd), (char*)p12, strlen(p12), "");
    if (rv != 0) {
        int errLen = 65534;
        char err_str[65534];
        kc->KC_GetLastErrorString(&err_str[0], &errLen);
        fprintf(stderr, "KC_LoadKeyStore failed %lu\n%s\n", rv, err_str);
        return 1;
    }
    fprintf(stderr, "✅ Ключ загружен: %s\n", p12);

    /* Буфер 4MB для подписанного XML */
    int outLen = 4 * 1024 * 1024;
    unsigned char *outBuf = (unsigned char*)malloc(outLen);
    if (!outBuf) {
        fprintf(stderr, "malloc failed\n");
        return 1;
    }

    /* Подписываем XML
     * alias = "" — используется загруженный ключ
     * flags = 0  — стандарт (без timestamp)
     */
    rv = kc->SignXML(
        "",          /* alias */
        0,           /* flags */
        (char*)xml,  /* inData */
        strlen(xml), /* inDataLength */
        outBuf,      /* outSign */
        &outLen,     /* outSignLength */
        "",          /* signNodeId */
        "",          /* parentSignNode */
        ""           /* parentNameSpace */
    );

    if (rv != 0) {
        int errLen = 65534;
        char err_str[65534];
        kc->KC_GetLastErrorString(&err_str[0], &errLen);
        fprintf(stderr, "SignXML failed %lu\n%s\n", rv, err_str);
        free(outBuf);
        return 1;
    }

    /* Выводим подписанный XML в stdout */
    outBuf[outLen] = '\0';
    printf("%s", (char*)outBuf);
    fflush(stdout);

    free(outBuf);
    dlclose(handle);
    return 0;
}
