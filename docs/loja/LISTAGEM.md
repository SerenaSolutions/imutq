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

---

# Z-Seal — texto de listagem

## Nome
Z-Seal — selo do que voce viu

## Descricao curta
Sela trechos de paginas com SHA3-256, hora e URL, em cadeia verificavel. Sem servidor, sem conta.

## Descricao completa
Print some. Mensagem e editada. Noticia muda de texto depois de publicada.

O Z-Seal guarda a impressao digital do trecho que voce viu: seleciona o texto, clica com
o botao direito e escolhe Selar trecho com Z-Seal. Ele calcula SHA3-256 do texto junto
com a hora e a URL, e encadeia o selo no anterior, como um livro-razao.

Abra o icone da extensao para ver a cadeia. Se um unico caractere de qualquer selo for
alterado, a verificacao acusa cadeia quebrada e mostra o indice exato.

Tudo acontece no seu navegador. Nada e enviado a servidor algum, nao ha conta e nao ha
rastreamento.

## Finalidade unica
Criar e verificar selos locais de integridade para trechos de texto selecionados pelo usuario.

## Permissoes
1. contextMenus: oferecer a opcao de selar no botao direito.
2. storage: guardar os selos e a cadeia no proprio navegador.
3. activeTab: ler a URL e o titulo da aba no momento em que voce sela.
