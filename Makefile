.PHONY: oqs-lib oqs-bridge clean-bridge test

OQS_VENDOR := vendor/liboqs-analysis
OQS_BRIDGE := build/oqs_bridge

oqs-lib:
	$(MAKE) -C $(OQS_VENDOR)

oqs-bridge: oqs-lib
	mkdir -p build
	cc -std=gnu11 -O2 \
		-I$(OQS_VENDOR)/include \
		-I$(OQS_VENDOR)/include/oqs \
		-I$(OQS_VENDOR)/src \
		-I$(OQS_VENDOR)/build/include \
		-o $(OQS_BRIDGE) bridge/oqs_bridge.c \
		$(OQS_VENDOR)/build/lib/liboqs.a \
		$(OQS_VENDOR)/build/lib/liboqs-internal.a \
		-lm -lcrypto -lpthread

clean-bridge:
	rm -f $(OQS_BRIDGE)

test:
	python3 -m pytest
