/*

use this python script to generate the optimized charset 
for DES bruteforce from original charset

charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
optimized_charset = ""
a = set()
for c in charset: 
    if ord(c)&0xfe not in a: 
        optimized_charset += c
        a.add(ord(c)&0xfe)
print optimized_charset

*/

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <openssl/des.h>

static long long unsigned nrkeys = 0; 

#define KEYLEN  8
#define CHARSET "ABDFHJLNPRTVXZ"

char * Encrypt( char *Key, char *Msg, int size)
{
        static char*    Res;
        free(Res);
        int             n=0;
        DES_cblock      Key2;
        DES_key_schedule schedule;
        Res = ( char * ) malloc( size );
        memcpy( Key2, Key,KEYLEN);
        DES_set_odd_parity( &Key2 );
        DES_set_key_checked( &Key2, &schedule );
        DES_ecb_encrypt( ( unsigned char (*) [KEYLEN] ) Msg, ( unsigned char (*) [KEYLEN] ) Res,
                           &schedule, DES_ENCRYPT );
         return (Res);
}
char * Decrypt( char *Key, char *Msg, int size)
{
        static char*    Res;
        free(Res);
        int             n=0;
        DES_cblock      Key2;
        DES_key_schedule schedule;
        Res = ( char * ) malloc( size );
        memcpy( Key2, Key,KEYLEN);
        DES_set_odd_parity( &Key2 );
        DES_set_key_checked( &Key2, &schedule );
        DES_ecb_encrypt( ( unsigned char (*) [KEYLEN]) Msg, ( unsigned char (*) [KEYLEN]) Res,
                           &schedule, DES_DECRYPT );
        return (Res);
}

void ex_program(int sig) {
    printf("\n\nProgram terminated %lld keys searched.\n", nrkeys);
    (void) signal(SIGINT, SIG_DFL);
    exit(0);
}

int main()
{
    (void) signal(SIGINT, ex_program);
    register int counter, i, len = 8; // counters and password length

    char *ciphertext = "\x78\x16\x5e\xcc\xbf\x53\xcd\xb1\x10\x85\xe8\xe5\xe3\x62\x6b\xa9\xbd\xef\xd5\xe9\xde\x62\xce\x91";
    char *plaintext = "\xde\xad\x23\x4a\x1f\x13\xbe\xef";

    char letters[] = CHARSET; 
    int nbletters = sizeof(letters)-1;
    int entry[len];

    char key[KEYLEN],encrypted[KEYLEN];

    // Initialize key array
    for(i=0 ; i<len ; i++) entry[i] = 0;
    
    do {
        for(i=0 ; i<len ; i++) key[i] = letters[entry[i]];
        nrkeys++;
        if(nrkeys % 10000000 == 0) {
            printf("Current key: %s\n", key);
        }

        memcpy(encrypted, Encrypt(key, plaintext, KEYLEN), KEYLEN);

        if (memcmp(ciphertext, encrypted, KEYLEN) == 0)
        {
            printf("The key is: %s\n", key);
            printf("%lld keys searched", nrkeys);
            exit(0);
        }
        for(i=0 ; i<len && ++entry[i] == nbletters; i++) entry[i] = 0;
    } while(i<len);

    return 0;
}
