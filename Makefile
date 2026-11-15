RUST=./rust/target/release/imutq

build:
	cd rust && cargo build --release

run:
	PYTHONPATH=src python3 -m imutq.cli executar --backend ibm_fez --shots 1024

verify: build
	$(RUST) verificar receipts/2026-11-15/lote.json receipts/2026-11-15/simulador.json

test:
	PYTHONPATH=src python3 -m pytest -q tests/test_receipt.py
