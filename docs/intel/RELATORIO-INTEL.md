# Intel Quantum SDK — o que está documentado e o que falta confirmar

Revisão de 15/11/2026 depois de uma consulta crítica a fontes públicas. Corrige
afirmações anteriores que iam além da evidência.

## Regra de leitura

Cada linha abaixo vale para a interface e a versão citadas. Nada aqui é uma
conclusão sobre "o SDK inteiro".

| Afirmação | Escopo real | Situação |
|---|---|---|
| IQS é projeto público da Intel, Apache-2.0 | github.com/intel/intel-qs | DOCUMENTADO |
| A interface Python (docs v1.1, `intelqsdk.cbindings`) recebe OpenQASM 2.0 | essa interface, essa versão | DOCUMENTADO |
| API C++ com `quantum_kernel` e compilador `-B` | documentação do SDK | DOCUMENTADO |
| Não existe dialeto "intelqasm" | busca na documentação oficial | REFUTADO como nome; não afirma nada sobre dialetos internos |
| OpenQASM 3, QIR, MLIR | nenhuma menção encontrada | AUSÊNCIA DE EVIDÊNCIA, não prova de ausência |
| Tunney e T12 | não confirmado publicamente o que designam | ABERTO: pode ser hardware, alvo de compilação ou modelo de simulação |
| Compatibilidade LLVM implica QIR ou MLIR | não | REFUTADO: são camadas distintas |

Retratação: a versão anterior deste relatório dizia "o SDK aceita apenas QASM 2.0" e
"Tunney/T12 indisponíveis". As duas frases extrapolavam. O correto é: a interface
Python documentada recebe QASM 2.0, e não há cronograma público confirmado para o
resto.

## Cadastro

DOCUMENTADO: programas da Intel exigem domínio empresarial e, em alguns casos, acordo
de confidencialidade corporativo (CNDA). O Developer Zone Premier é um desses
programas e não serve como prova dos requisitos do Developer Cloud ou do Quantum SDK.

ABERTO: se um domínio `.com.br` de MEI ou CNPJ brasileiro é aceito no cadastro do
Quantum SDK. Só o suporte do programa responde. MEI é modalidade de formalização;
CNPJ é cadastro; nenhum dos dois é garantia de aprovação.

## IQS no IMUT-Q

Decisão: o IQS é adotado como *ambiente de referência da Serena Solutions*, versionado
e explicitamente simulado. Não será chamado de "backend oficial do SDK para quem não
tem cadastro", porque essa modalidade não está confirmada.

Fórmula aprovada para recibos:

> Resultado obtido em simulação local com Intel Quantum Simulator, versão/commit X,
> adotado pela Serena Solutions como ambiente de referência do IMUT-Q.

## Limite da assinatura

ML-DSA-44 autentica o emissor e protege a integridade do recibo. Não prova que o
cálculo está correto, não prova execução em hardware quântico e não expressa endosso
da Intel. O esquema mantém essas alegações separadas: `veredito` fala do resultado,
`proveniencia` fala de onde veio, `assinatura` fala de quem emitiu.

## Perguntas formais para a Intel

1. Domínio `.com.br` com MEI ou CNPJ é aceito no cadastro do Quantum SDK?
2. Existe sandbox, avaliação ou programa de parceiro para empresa brasileira de software?
3. O IQS pode ser citado como ambiente de referência em recibos auditáveis?
4. Há roadmap público, com datas, para OpenQASM 3, QIR ou MLIR?
5. Tunney e T12 designam hardware, alvo de compilação ou modelo? Há acesso externo e
   qual programa admite empresa brasileira?

## Caminho enquanto as respostas não chegam

1. IQS local, versão e commit registrados.
2. QASM 2.0 emitido do ZYQL e traduzido com `-B`.
3. Recibo com `provedor=Intel`, `backend=iqs`, `proveniencia=simulada_sdk`.
4. Conferência pelo núcleo Rust, que não depende do SDK.
