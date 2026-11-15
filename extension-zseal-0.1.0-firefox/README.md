# Z-Seal — selo do que você viu

Seleciona um trecho numa página, clica com o botão direito e sela com SHA3-256 mais
hora e URL, encadeado no selo anterior. Prova de integridade sem servidor.

## Por que existe

Print some, mensagem é editada, notícia muda de texto. O Z-Seal guarda a impressão
digital do trecho no momento em que você viu, e encadeia cada selo no anterior, de
modo que apagar um no meio quebra a corrente inteira.

## Como funciona

1. Menu de contexto captura a seleção, a URL e o título.
2. Monta o corpo do selo: índice, hora, URL, título, texto e o hash do selo anterior.
3. Calcula SHA3-256 desse corpo canônico.
4. Guarda no armazenamento local, com contador no ícone.

A verificação recalcula cada hash e confere o encadeamento. Um único caractere trocado
derruba o selo e todos os seguintes.

## O que não faz

1. Não envia nada para servidor. Sem host_permissions, sem código remoto, Manifest V3.
2. Não acessa o conteúdo de páginas fora da seleção.
3. Não promete carimbo do tempo independente: a hora é a do seu computador.

## Testes

1. Vetores oficiais do SHA3-256: "abc" e vazio conferem.
2. Cadeia de dois selos íntegra: ok.
3. Selo do meio adulterado: acusa hash divergente e elo quebrado no seguinte.

## Instalar

1. chrome://extensions, modo desenvolvedor.
2. Carregar sem compactação, apontando para esta pasta.
