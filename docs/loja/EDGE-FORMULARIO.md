# Edge Add-ons — campos para colar no formulario

Pacote: `extension-0.1.1.zip` (Chrome e Edge usam o mesmo arquivo).
Conta: Partner Center, sem taxa.

## Nome
IMUT-Q Receipt Checker

## Descricao curta (ate 132 caracteres)
Verifica recibos IMUT-Q de execucao quantica: hash SHA3-256, veredito 1/0/REFUSED e origem. Serena Solutions.

## Descricao (ate 10.000 caracteres)
Recibos de execucao quantica dizem o que rodou, onde e com qual resultado. Esta extensao
confere se o recibo nao foi alterado depois de emitido.

Como funciona: cada recibo carrega um hash SHA3-256 do proprio conteudo. A extensao
reconstroi o payload canonico, recalcula o hash no seu computador e compara com o gravado.
Se divergir, o recibo e invalido, e voce ve isso na hora.

O que aparece na tela: veredito (1, 0 ou REFUSED), provedor, backend, identificador do job,
numero de tiros, tipo de proveniencia e se ha assinatura.

Limite declarado: a conferencia da assinatura pos-quantica ML-DSA-44 e feita pelo nucleo
IMUT-Q, nao no navegador. A extensao informa quando a assinatura esta presente.

Nada e enviado a servidor algum. Sem conta, sem rastreamento, sem anuncio.

## Categoria
Ferramentas / Produtividade

## Finalidade unica
Verificar a integridade de recibos IMUT-Q gerados pela plataforma Serena Solutions.

## Justificativa de permissao; storage
Necessaria para guardar a data da ultima verificacao no proprio navegador. Nenhum dado sai do dispositivo.

## Declaracao de dados
Nao coleta dados do usuario. Nao vende dados. Nao usa dados para fins nao relacionados.

## Politica de privacidade
Pendente: precisa de URL publica. Publicar em https://imutq.com.br/privacidade quando o dominio existir.
Alternativa sem dominio: publicar o texto no GitHub Pages do repositorio.

## Material visual obrigatorio
1. Icone 128x128 (ja no pacote).
2. De 1 a 5 capturas de tela em 1280x800 ou 640x400, mostrando o popup com um recibo real.

## Ordem de submissao
1. Partner Center, criar conta e vincular ao programa Edge.
2. Novo pacote, enviar `extension-0.1.1.zip`.
3. Colar os campos acima.
4. Enviar para certificacao. Prazo tipico: de 1 a 7 dias.
