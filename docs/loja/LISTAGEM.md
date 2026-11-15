# Chrome Web Store — texto de listagem

## Nome
IMUT-Q Receipt Checker

## Descrição curta (max 132 caracteres)
Verifica recibos de execucao quantica no navegador: hash SHA3-256, veredito 1/0/REFUSED e origem. Serena Solutions.

## Descrição completa
Recibos de execucao quantica dizem o que rodou, onde e com qual resultado. Esta extensao
confere se o recibo nao foi alterado depois de emitido.

Como funciona: o recibo carrega um hash SHA3-256 do proprio conteudo. A extensao
reconstroi o payload canonico, recalcula o hash no seu computador e compara. Se divergir,
o recibo e invalido, e voce ve isso na hora.

O que voce recebe na tela: veredito (1, 0 ou REFUSED), provedor, backend, identificador
do job, numero de tiros, tipo de proveniencia e se ha assinatura.

Limite declarado: a conferencia da assinatura pos-quantica ML-DSA-44 e feita pelo nucleo
IMUT-Q, nao no navegador. A extensao indica quando a assinatura esta presente.

Nada e enviado a servidor algum. Sem conta, sem rastreamento, sem anuncio.

## Categoria
Ferramentas (Tools)

## Finalidade unica (exigida pelo Google)
Verificar a integridade de recibos IMUT-Q gerados pela plataforma Serena Solutions.

## Permissoes
1. storage: guardar apenas a data da ultima verificacao, localmente.
2. Nenhuma permissao de host. A extensao nao acessa sites.

## Dados declarados no formulario de privacidade
Nao coleta dados do usuario. Nao vende dados. Nao usa dados para fins nao relacionados.
