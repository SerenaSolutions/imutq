# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Solutions
"""Adaptadores de provedor do IMUT-Q.

Cada adaptador emite QASM, submete quando ha SDK/acesso e propoe um candidato a
recibo v2. Nenhum adaptador decide veredito final nem sela assinatura: essa
autoridade e do nucleo Rust (`imutq verificar` / `imutq veredito`).
"""

__all__ = ["intel"]
