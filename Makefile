run:
	PYTHONPATH=src python3 -m multiq.cli executar --backend ibm_fez --shots 1024
verify:
	PYTHONPATH=src python3 -m multiq.cli verificar --recebido receipts/2026-11-15/lote.json
