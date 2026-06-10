#include <oqs/oqs.h>
#include <oqs/kem.h>
#include <oqs/sig.h>

#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void die(const char *message) {
	fprintf(stderr, "%s\n", message);
	exit(1);
}

static int hex_value(char c) {
	if (c >= '0' && c <= '9') return c - '0';
	if (c >= 'a' && c <= 'f') return c - 'a' + 10;
	if (c >= 'A' && c <= 'F') return c - 'A' + 10;
	return -1;
}

static uint8_t *hex_decode(const char *hex, size_t *out_len) {
	size_t len = strlen(hex);
	if (len % 2 != 0) die("invalid hex input");
	uint8_t *out = malloc(len / 2);
	if (out == NULL) die("allocation failed");
	for (size_t i = 0; i < len; i += 2) {
		int hi = hex_value(hex[i]);
		int lo = hex_value(hex[i + 1]);
		if (hi < 0 || lo < 0) die("invalid hex input");
		out[i / 2] = (uint8_t) ((hi << 4) | lo);
	}
	*out_len = len / 2;
	return out;
}

static char *hex_encode(const uint8_t *data, size_t len) {
	static const char table[] = "0123456789abcdef";
	char *out = malloc((len * 2) + 1);
	if (out == NULL) die("allocation failed");
	for (size_t i = 0; i < len; i++) {
		out[i * 2] = table[data[i] >> 4];
		out[(i * 2) + 1] = table[data[i] & 0x0f];
	}
	out[len * 2] = '\0';
	return out;
}

static void kem_keygen(const char *alg) {
	OQS_KEM *kem = OQS_KEM_new(alg);
	if (kem == NULL) die("unsupported or disabled KEM algorithm");
	uint8_t *pk = malloc(kem->length_public_key);
	uint8_t *sk = malloc(kem->length_secret_key);
	if (pk == NULL || sk == NULL) die("allocation failed");
	if (OQS_KEM_keypair(kem, pk, sk) != OQS_SUCCESS) die("KEM keygen failed");
	char *pk_hex = hex_encode(pk, kem->length_public_key);
	char *sk_hex = hex_encode(sk, kem->length_secret_key);
	printf("{\"public_key\":\"%s\",\"secret_key\":\"%s\"}\n", pk_hex, sk_hex);
	free(pk_hex);
	free(sk_hex);
	free(pk);
	free(sk);
	OQS_KEM_free(kem);
}

static void kem_encaps(const char *alg, const char *pk_arg) {
	size_t pk_len = 0;
	uint8_t *pk = hex_decode(pk_arg, &pk_len);
	OQS_KEM *kem = OQS_KEM_new(alg);
	if (kem == NULL) die("unsupported or disabled KEM algorithm");
	if (pk_len != kem->length_public_key) die("invalid KEM public key length");
	uint8_t *ct = malloc(kem->length_ciphertext);
	uint8_t *ss = malloc(kem->length_shared_secret);
	if (ct == NULL || ss == NULL) die("allocation failed");
	if (OQS_KEM_encaps(kem, ct, ss, pk) != OQS_SUCCESS) die("KEM encaps failed");
	char *ct_hex = hex_encode(ct, kem->length_ciphertext);
	char *ss_hex = hex_encode(ss, kem->length_shared_secret);
	printf("{\"ciphertext\":\"%s\",\"shared_secret\":\"%s\"}\n", ct_hex, ss_hex);
	free(ct_hex);
	free(ss_hex);
	free(ct);
	free(ss);
	free(pk);
	OQS_KEM_free(kem);
}

static void kem_decaps(const char *alg, const char *sk_arg, const char *ct_arg) {
	size_t sk_len = 0;
	size_t ct_len = 0;
	uint8_t *sk = hex_decode(sk_arg, &sk_len);
	uint8_t *ct = hex_decode(ct_arg, &ct_len);
	OQS_KEM *kem = OQS_KEM_new(alg);
	if (kem == NULL) die("unsupported or disabled KEM algorithm");
	if (sk_len != kem->length_secret_key) die("invalid KEM secret key length");
	if (ct_len != kem->length_ciphertext) die("invalid KEM ciphertext length");
	uint8_t *ss = malloc(kem->length_shared_secret);
	if (ss == NULL) die("allocation failed");
	if (OQS_KEM_decaps(kem, ss, ct, sk) != OQS_SUCCESS) die("KEM decaps failed");
	char *ss_hex = hex_encode(ss, kem->length_shared_secret);
	printf("{\"shared_secret\":\"%s\"}\n", ss_hex);
	free(ss_hex);
	free(ss);
	free(sk);
	free(ct);
	OQS_KEM_free(kem);
}

static void sig_keygen(const char *alg) {
	OQS_SIG *sig = OQS_SIG_new(alg);
	if (sig == NULL) die("unsupported or disabled signature algorithm");
	uint8_t *pk = malloc(sig->length_public_key);
	uint8_t *sk = malloc(sig->length_secret_key);
	if (pk == NULL || sk == NULL) die("allocation failed");
	if (OQS_SIG_keypair(sig, pk, sk) != OQS_SUCCESS) die("signature keygen failed");
	char *pk_hex = hex_encode(pk, sig->length_public_key);
	char *sk_hex = hex_encode(sk, sig->length_secret_key);
	printf("{\"public_key\":\"%s\",\"secret_key\":\"%s\"}\n", pk_hex, sk_hex);
	free(pk_hex);
	free(sk_hex);
	free(pk);
	free(sk);
	OQS_SIG_free(sig);
}

static void sig_sign(const char *alg, const char *sk_arg, const char *msg_arg) {
	size_t sk_len = 0;
	size_t msg_len = 0;
	uint8_t *sk = hex_decode(sk_arg, &sk_len);
	uint8_t *msg = hex_decode(msg_arg, &msg_len);
	OQS_SIG *sig = OQS_SIG_new(alg);
	if (sig == NULL) die("unsupported or disabled signature algorithm");
	if (sk_len != sig->length_secret_key) die("invalid signature secret key length");
	uint8_t *signature = malloc(sig->length_signature);
	size_t signature_len = 0;
	if (signature == NULL) die("allocation failed");
	if (OQS_SIG_sign(sig, signature, &signature_len, msg, msg_len, sk) != OQS_SUCCESS) die("sign failed");
	char *signature_hex = hex_encode(signature, signature_len);
	printf("{\"signature\":\"%s\"}\n", signature_hex);
	free(signature_hex);
	free(signature);
	free(sk);
	free(msg);
	OQS_SIG_free(sig);
}

static void sig_verify(const char *alg, const char *pk_arg, const char *msg_arg, const char *sig_arg) {
	size_t pk_len = 0;
	size_t msg_len = 0;
	size_t signature_len = 0;
	uint8_t *pk = hex_decode(pk_arg, &pk_len);
	uint8_t *msg = hex_decode(msg_arg, &msg_len);
	uint8_t *signature = hex_decode(sig_arg, &signature_len);
	OQS_SIG *sig = OQS_SIG_new(alg);
	if (sig == NULL) die("unsupported or disabled signature algorithm");
	if (pk_len != sig->length_public_key) die("invalid signature public key length");
	OQS_STATUS status = OQS_SIG_verify(sig, msg, msg_len, signature, signature_len, pk);
	printf("{\"valid\":%s}\n", status == OQS_SUCCESS ? "true" : "false");
	free(pk);
	free(msg);
	free(signature);
	OQS_SIG_free(sig);
}

int main(int argc, char **argv) {
	if (argc < 3) {
		die("usage: oqs_bridge <command> <algorithm> [hex args...]");
	}

	const char *command = argv[1];
	const char *alg = argv[2];
	OQS_init();

	if (strcmp(command, "kem-keygen") == 0 && argc == 3) {
		kem_keygen(alg);
	} else if (strcmp(command, "kem-encaps") == 0 && argc == 4) {
		kem_encaps(alg, argv[3]);
	} else if (strcmp(command, "kem-decaps") == 0 && argc == 5) {
		kem_decaps(alg, argv[3], argv[4]);
	} else if (strcmp(command, "sig-keygen") == 0 && argc == 3) {
		sig_keygen(alg);
	} else if (strcmp(command, "sign") == 0 && argc == 5) {
		sig_sign(alg, argv[3], argv[4]);
	} else if (strcmp(command, "verify") == 0 && argc == 6) {
		sig_verify(alg, argv[3], argv[4], argv[5]);
	} else {
		die("invalid command or argument count");
	}

	OQS_destroy();
	return 0;
}
