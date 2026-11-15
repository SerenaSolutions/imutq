# qBraid × Intel Quantum SDK — investigação de acesso

Data: 15/11/2026 · Autor: investigação automatizada (IMUT-Q) · Credencial: `QUANTUM_LAB_TOKEN` (X-API-Key, não impressa)

---

## Veredito

**Com esta chave nada permite executar código Intel de forma programática** — a API do qBraid expõe um
catálogo de ambientes e uma fila de *jobs por dispositivo* (QRN), e nenhum dos 40 dispositivos
disponíveis é da Intel; executar Intel exige notebook interativo numa instância Lab com a **imagem
dedicada Intel**, que não é provisionável apenas com a API key.

A conta **tem** acesso ao ambiente: o ambiente `intelqsdk` (Intel Quantum SDK v1.1) existe, é público e
está aprovado. O que não existe é caminho de execução via API.

| Pergunta | Resposta |
|---|---|
| Existe ambiente Intel no catálogo? | **Sim** — `intelq_r7zabv` / `intelqsdk`, HTTP 200 |
| Existe QPU/simulador Intel na API de devices? | **Não** — 0 de 40, e `intel:*` devolve HTTP 404 |
| Execução programática (REST/SDK/CLI de jobs)? | **Não** — nenhum `format` de programa suporta Intel |
| Execução via notebook interativo? | **Sim**, na imagem `lab-intel` (Lab → perfil *Small · Intel Quantum SDK*) |
| Custo do ambiente Intel | **$0,12/h** (0,2 créditos/min); igual ao perfil Starter sem Intel |

---

## 1. Credencial e método

- Token presente na variável `QUANTUM_LAB_TOKEN` (68 caracteres). **Nunca impresso, logado ou gravado.**
- Header `X-API-Key` autentica. Verificado nos dois sentidos:

  | Requisição | Status | Corpo |
  |---|---|---|
  | `GET /api/v1/devices` **com** a chave | **200** | 40 dispositivos |
  | `GET /api/v1/devices` **sem** a chave | **401** | `No valid authentication provided` |
  | `GET /api/v1/devices` com chave inválida | **401** | `Invalid API key format` |
  | `GET /api/v1/environments` **sem** a chave | **401** | `No valid authentication provided` |

  Ou seja: os **200** representam acesso real e autorizado, e os **404** de "Route not found" são
  respostas de roteamento (a rota não existe), não de permissão — o que torna inequívoca a conclusão
  de que `lab`, `images`, `qpus` e `backends` simplesmente não existem na API.
- Dois hosts respondem de forma equivalente nos caminhos testados:
  - `https://api.qbraid.com/api/v1` (usado nos fatos confirmados)
  - `https://api-v2.qbraid.com/api/v1` — **é o base URL oficial documentado** (ver `docs.qbraid.com/llms.txt`)
- Spec oficial: `https://docs.qbraid.com/openapi-v2.json` → **HTTP 200**, `info.version = 2`,
  `servers[0].url = https://api-v2.qbraid.com/api/v1`.

O spec oficial foi a evidência decisiva: **23 paths, nenhum de ambiente, lab, imagem, instância,
notebook ou kernel**. A rota `/environments` que funciona **não está no spec** — é endpoint extra,
não documentado, sem contrato de estabilidade.

---

## 2. Endpoints de ambiente / laboratório / imagem — status HTTP real

### 2.1 O que existe de fato (HTTP 200)

| Método | URL | Status | Conteúdo |
|---|---|---|---|
| GET | `https://api.qbraid.com/api/v1/environments` | **200** | 46 ambientes; `pagination.total = 46` |
| GET | `https://api.qbraid.com/api/v1/environments/intelq_r7zabv` | **200** | registro completo do ambiente Intel |
| GET | `https://api.qbraid.com/api/v1/devices` | **200** | 40 dispositivos (15 SIMULATOR + 25 QPU); **0 Intel** |
| GET | `https://api.qbraid.com/api/v1/providers` | **200** | 8 vendors: aws, azure, ibm, ionq, openquantum, qbraid, qperfect, rigetti |
| GET | `https://api-v2.qbraid.com/api/v1/jobs` | **200** | fila de jobs da conta (vazia: `total: 0`) |
| GET | `https://api-v2.qbraid.com/api/v1/compute/profiles` | **200** | 33 perfis de instância, **inclui `2vCPU_4GB_INTEL`** |
| GET | `https://api-v2.qbraid.com/api/v1/billing/credits/balance` | **200** | `qbraidCredits: 0`, `awsCredits: 0` |
| GET | `https://api-v2.qbraid.com/api/v1/billing/credits/pricing` | **200** | `creditRate: 100` (100 créditos = US$ 1), mínimo US$ 5 |
| GET | `https://api-v2.qbraid.com/api/v1/usage/simulator` | **200** | cotas diárias dos simuladores gratuitos (100 execuções) |

### 2.2 O que **não** existe (HTTP 404 confirmado)

Rotas testadas com a chave válida, todas devolvendo `404 Route ... not found`:

| URL testada | Status |
|---|---|
| `/api/v1/lab` | 404 |
| `/api/v1/labs` | 404 |
| `/api/v1/images` | 404 |
| `/api/v1/images/list` | 404 |
| `/api/v1/lab/images` | 404 |
| `/api/v1/lab/instances` | 404 |
| `/api/v1/qpus` | 404 |
| `/api/v1/backends` | 404 |
| `/api/v1/runtimes` | 404 |
| `/api/v1/simulators` | 404 |
| `/api/v1/notebooks` | 404 |
| `/api/v1/sessions` | 404 |
| `/api/v1/sandbox` · `/sandboxes` | 404 |
| `/api/v1/instances` · `/instance-profiles` | 404 |
| `/api/v1/programs` | 404 |
| `/api/v1/runs` · `/executions` · `/executions/submit` | 404 |
| `/api/v1/groups` | 404 |
| `/api/v1/container-images` | 404 |
| `/api/v1/compute` · `/compute/instances` · `/compute/servers` · `/compute/clusters` · `/compute/availability` | 404 |
| `/api/v1/environments/intelq_r7zabv/install` | 404 |
| `/api/v1/environments/intelq_r7zabv/launch` | 404 |
| `/api/v1/environments/intelq_r7zabv/packages` | 404 |
| `/api/v1/environments/intelq_r7zabv/cost` | 404 |
| `/api/v1/pricing` · `/credits` · `/usage` · `/plans` | 404 |
| `/api/v1/account` · `/users/me` · `/account/usage` | 404 |

> Não existe endpoint de instalação, ativação ou lançamento de ambiente. `/environments` é **somente
> leitura de catálogo** — não há `POST` para instalar nem para abrir instância.

### 2.3 O ambiente Intel — registro real (`HTTP 200`)

```
GET https://api.qbraid.com/api/v1/environments/intelq_r7zabv
```

| Campo | Valor |
|---|---|
| `_id` | `6a68a001865710789a3c614f` |
| `slug` | `intelq_r7zabv` |
| `name` | `intelqsdk` |
| `description` | `Intel Quantum SDK v1.1 — C++ quantum compiler + simulator with Python interface` |
| `groups` | `intel_vh8t2j` — "Intel Quantum SDK" |
| `visibility` | `public` |
| `reviewStatus` | `APPROVED` |
| `platform` | `linux-x86_64` |
| `pythonVersion` | `3.12` |
| `mirrorStatus` | `partial` |
| `installCount` | `0` |
| `owner` | `entangled_qubit` |
| `createdAt` | `2026-07-28T12:26:41.927Z` |
| `envS3Url` | `https://storage.googleapis.com/qbraid-envs-v2-prod/intelq_r7zabv_environment.tar.zst` |

Pacotes relevantes: `intelqsdk==1.0`, `intel-cmplr-lib-rt==2026.1.0`, `intel-openmp==2023.2.4`,
`impi-rt==2021.18.1`, `mkl==2023.2.0`, `tbb==2021.13.1`, `openqasm-bridge=0.0.2`, `quimb==1.11.2`,
`numpy==2.2.6`, `scipy==1.15.3`.

**Ressalvas honestas sobre este registro:**
- `installCount: 0` — ninguém instalou este ambiente ainda; não há evidência de uso bem-sucedido.
- `mirrorStatus: partial` — o espelhamento está incompleto.
- A descrição diz "v1.1", mas o pacote fixado é `intelqsdk==1.0`. **Inconsistência não resolvida**
  (provável divergência entre versão do SDK e versão do pacote PyPI, mas não foi verificada).
- `openqasm-bridge=0.0.2` usa `=` simples, não `==` — pin malformado no manifesto.

---

## 3. Documentação pública — o que traz Intel Quantum SDK

Fonte oficial: <https://docs.qbraid.com/v2/lab/user-guide/featured-environments/intel-quantum-sdk.md>
(HTTP 200, ~12 KB). Localizada via índice oficial <https://docs.qbraid.com/llms.txt>.

O documento é explícito:

> "The Intel® Quantum SDK environment is **only available on the dedicated Intel Lab image**. You must
> launch that image first; the environment then becomes visible in the Environment Manager, where you
> install it to get the Python virtual environment, the compiler, and the Jupyter kernel."

**Não há outro ambiente do Quantum Lab com Intel Quantum SDK ou Intel QDK.** Varredura dos 46 ambientes
retornou exatamente **1** ocorrência de "Intel" (`intelq_r7zabv`). O "Intel QDK" (Microsoft Q#/QDK) não
aparece em nenhum ambiente nem em nenhum path do spec.

### Fluxo documentado (100% interativo, via UI)

1. Dashboard → card **Launch qBraid Lab** → perfil **"Small · Intel Quantum SDK"** → **Launch**
   (primeira vez baixa a imagem: 2–3 min).
2. **Environment Manager** → **Add** → grupo **"Intel Quantum SDK"** → painel **`intelqsdk`** → **Install**
   (instala em `~/.qbraid/environments/`).
3. Botão **Add kernel** → registra o kernel **`Python 3 [Intel Quantum SDK]`**.

Equivalentes por CLI (rodam **dentro** da instância, não substituem o lançamento da imagem):

```bash
qbraid envs available              # lista o ambiente intelqsdk
qbraid envs install intelq_r7zabv  # instala pelo slug
qbraid envs list                   # descobre o envId
qbraid kernels add <envId>         # registra o kernel
```

### O que contém

- `intel-quantum-compiler` (baseado em LLVM/Clang), simulador full-state Intel e demais backends.
- Interface Python `intelqsdk.cbindings` (compila C++ a partir de Python).
- Tradução OpenQASM 2.0 → C++ via `openqasm_bridge` ou `intel-quantum-compiler -B arquivo.qasm`.
- Ambiente autocontido: sem `pip install` extra, sem `source`, nada do sistema.

---

## 4. Programático ou apenas notebook? — **Apenas notebook interativo**

Três evidências independentes, todas negativas para execução programática:

**(a) Nenhum dispositivo Intel na fila de jobs.**
`GET /api/v1/devices` → 40 dispositivos, vendors `{aws, azure, ibm, ionq, openquantum, qbraid, qperfect,
rigetti}`. Zero Intel. Teste direto de resolução:

```
GET https://api-v2.qbraid.com/api/v1/jobs/cost-estimate?deviceQrn=intel:intel:sim:iqs&shots=100
  -> HTTP 404  {"message":"Device not found: intel:intel:sim:iqs","code":"NOT_FOUND"}

GET https://api-v2.qbraid.com/api/v1/jobs/cost-estimate?deviceQrn=qbraid:qbraid:sim:qir-sv&shots=100
  -> HTTP 200  {"pricingAvailable":true,"estimatedCost":0}
```

O controle com QRN válido devolve 200; o QRN Intel devolve 404. Não é falha de autenticação nem de
formato — o dispositivo não existe.

**(b) O formato de programa de job não suporta Intel.**
`POST /api/v1/jobs` exige `{shots, deviceQrn, program}`. O enum `Program.format` do spec oficial é:

```
qasm2 | qasm3 | qir.bc | qir.ll | analog | pulser.sequence | quil | ionq.circuit.v0 | problem
```

Não há formato para `quantum_kernel` C++ do Intel SDK. Um job Intel é **inexprimível** no contrato da API.
Busca por `intel`/`iqsdk` em todo o `openapi-v2.json`: **0 ocorrências**.

**(c) O ambiente é local à instância Lab, não um serviço remoto.**
A instalação grava em `~/.qbraid/environments/intelq_xxxx/pyenv`, com `PATH` apontando para
`$IQSDK_SHARE` e `LD_LIBRARY_PATH` para as libs Intel. O compilador e o simulador são **binários
linux-x86_64 executados dentro do container do usuário**. Não há endpoint que receba um `quantum_kernel`
e devolva resultados.

**(d) Bônus — nem o lançamento da instância é possível só com a API key.**
`GET /api/v1/compute/profiles/2vcpu_4gb_intel` → **HTTP 400 `EMAIL_REQUIRED`**
("Email is required"). O mesmo ocorre com qualquer profile. O `X-API-Key` identifica a chave, mas a
camada de compute exige identidade de usuário (`userId`/email) que a chave sozinha não fornece.
O `qbraid compute up <profile>` do CLI exige `qbraid configure` com login.

### Conclusão da tarefa 3

Com **esta chave**, o acesso a Intel é: **catálogo (leitura)** sim; **execução** não, nem programática
nem remota. O único caminho real é abrir o Lab na imagem Intel e rodar notebook/kernel interativo — o
que exige sessão de navegador/UI, fora do alcance de uma API key.

---

## 5. Custo e créditos

### 5.1 O ambiente Intel em si

De `GET /api/v1/compute/profiles` → perfil `2vCPU_4GB_INTEL`:

| Campo | Valor |
|---|---|
| `display_name` | **Small · Intel Quantum SDK** |
| `slug` | `2vCPU_4GB_INTEL` |
| `_id` | `6775c298a6d62c9e32d6ab5d` |
| `rateDollar` | **0.002** por **minuto** → **US$ 0,12/h** |
| `creditCost` | **0.2** créditos por minuto → **12 créditos/h** |
| `plan` | `Free` — "covered by your plan" |
| `gpu` | `false` |
| `ide` | `jupyterlab` |
| `hasCapacity` | `true` |
| `audience` | "Beginners exploring Intel's quantum toolchain." |
| `kubespawner_override.image` | `us-central1-docker.pkg.dev/qbraid-prod/jupyterhub/lab-intel:latest` |
| recursos | 1.8 vCPU garantido, 4 GB RAM |

**Não há prêmio por usar Intel.** Comparação direta:

| Perfil | `rateDollar`/min | `creditCost`/min | Plano |
|---|---|---|---|
| `2vCPU_4GB` (Small) | 0.002 | 0.2 | Free |
| **`2vCPU_4GB_INTEL` (Small · Intel)** | **0.002** | **0.2** | **Free** |
| `2vCPU_4GB_VSCODE` (Small · VS Code) | 0.002 | 0.2 | Free |
| `4vCPU_8GB` (Medium) | 0.004 | 0.4 | Standard |
| `8vCPU_25GB` (Large) | 0.008 | 0.8 | Pro |

Consumo é por **tempo de instância ligada**, não por job. O SDK, o compilador e o simulador não
consomem créditos por execução — diferente de QPU.

### 5.2 Conversão e saldo

```
GET https://api-v2.qbraid.com/api/v1/billing/credits/pricing
  -> 200  {"creditRate":100,"minPurchaseUSD":5,"currency":"USD",
           "examples":[{"usd":5,"credits":500}, ...]}
```

100 créditos = US$ 1 → 0,2 créditos/min = **US$ 0,002/min = US$ 0,12/h**, consistente com `rateDollar`.

```
GET https://api-v2.qbraid.com/api/v1/billing/credits/balance
  -> 200  {"qbraidCredits":0,"awsCredits":0}
```

**A conta tem saldo zero.** Implicações honestas:
- O plano Free cobre o perfil Starter (inclusive o Intel) dentro da franquia de CPU-horas.
- Qualquer consumo **além** da franquia, ou job pago em QPU, falharia por falta de créditos.
- Não foi possível verificar a franquia exata de CPU-horas do plano: não há endpoint de plano/assinatura
  (`/plans`, `/account`, `/account/usage` → todos 404).

### 5.3 Custo de jobs (irrelevante para Intel, mas registrado)

Nenhum dispositivo tem `pricing` Intel. Para referência, o único `pricing` não nulo observado foi
`aws:aws:sim:dm1` → `{"perTask":0,"perShot":0,"perMinute":7.5}`. Os QPUs IBM trazem `pricing: null`
(preço não exposto nesse campo). **Não há informação oficial de custo para execução Intel porque não há
execução Intel ofertada.**

---

## 6. Consequência para o IMUT-Q

O `README.md` já declara: *"Sem adaptadores para Cirq, QIR, Braket ou Intel nesta versão."* Esta
investigação **confirma e justifica** essa decisão:

1. **Não implementar adaptador Intel sobre a API qBraid.** Não existe dispositivo, não existe formato de
   programa, não existe endpoint de submissão. Um adaptador seria código morto.
2. **Não há `job_id` Intel** — logo, não há proveniência primária a capturar. O recibo IMUT-Q v2 exige
   `job_id` na submissão; o caminho Intel é notebook interativo sem job remoto identificável.
3. **Se Intel for requisito de produto**, os caminhos reais são:
   - auto-hospedar o Intel Quantum SDK (Intel distribui gratuitamente para uso não comercial) e rodar o
     simulador local; ou
   - usar a imagem `lab-intel` com sessão interativa, e tratar a saída como evidência manual, não como
     proveniência verificável.

---

## 7. Reprodução das evidências

Requer `curl` e `jq` (este último ausente no sandbox onde a investigação rodou — lá os JSONs foram
inspecionados com `python3 -c "import json..."`, equivalente).

```bash
# Todas as chamadas usam apenas o header, sem imprimir o token
H="X-API-Key: $QUANTUM_LAB_TOKEN"

curl -s -o /dev/null -w "%{http_code}\n" -H "$H" https://api.qbraid.com/api/v1/environments
curl -s -H "$H" https://api.qbraid.com/api/v1/environments | jq '.pagination'
curl -s -H "$H" https://api.qbraid.com/api/v1/environments/intelq_r7zabv | jq '.data.slug, .data.description'
curl -s -H "$H" https://api.qbraid.com/api/v1/devices | jq '[.data[] | select(.vendor=="intel")] | length'
curl -s -o /dev/null -w "%{http_code}\n" -H "$H" https://api.qbraid.com/api/v1/qpus      # 404
curl -s -o /dev/null -w "%{http_code}\n" -H "$H" https://api.qbraid.com/api/v1/backends  # 404
curl -s -o /dev/null -w "%{http_code}\n" -H "$H" https://api.qbraid.com/api/v1/images    # 404
curl -s -o /dev/null -w "%{http_code}\n" -H "$H" https://api.qbraid.com/api/v1/lab       # 404

curl -s -H "$H" "https://api-v2.qbraid.com/api/v1/jobs/cost-estimate?deviceQrn=intel:intel:sim:iqs&shots=100"
curl -s -H "$H" "https://api-v2.qbraid.com/api/v1/jobs/cost-estimate?deviceQrn=qbraid:qbraid:sim:qir-sv&shots=100"
curl -s -H "$H" https://api-v2.qbraid.com/api/v1/compute/profiles | jq '.data[] | select(.slug=="2vCPU_4GB_INTEL")'
curl -s -H "$H" https://api-v2.qbraid.com/api/v1/billing/credits/balance
curl -s -H "$H" https://api-v2.qbraid.com/api/v1/billing/credits/pricing

# Spec oficial (sem chave)
curl -s https://docs.qbraid.com/openapi-v2.json | jq '.paths | keys | length'   # 23
```

---

## 8. O que não foi verificado

- **Não foi feito login no Lab** — não havia sessão de navegador. Logo, **não foi confirmado na prática**
  que a instalação do `intelqsdk` e a compilação de um `quantum_kernel` funcionam. Toda a seção 3 vem da
  documentação oficial, não de execução observada. Agravantes: `installCount: 0` e `mirrorStatus: partial`.
- Franquia de CPU-horas do plano Free: não exposta por endpoint.
- Se o `lab-intel:latest` está efetivamente disponível no registry (não testado puxar a imagem).
- Divergência "v1.1" vs `intelqsdk==1.0` não resolvida.
- Compatibilidade do `openqasm-bridge` do ambiente com Qiskit atual não testada.

---

## Referências

- Docs Intel no qBraid: <https://docs.qbraid.com/v2/lab/user-guide/featured-environments/intel-quantum-sdk.md>
- Índice de docs: <https://docs.qbraid.com/llms.txt>
- Spec OpenAPI: <https://docs.qbraid.com/openapi-v2.json>
- Pricing: <https://docs.qbraid.com/v2/home/pricing.md>
- CLI compute: <https://docs.qbraid.com/v2/cli/api-reference/qbraid_compute.md>
- CLI envs: <https://docs.qbraid.com/v2/cli/api-reference/qbraid_envs.md>
- Intel Quantum SDK (Intel): <https://www.intel.com/content/www/us/en/developer/tools/oneapi/quantum-sdk.html>
- Citação do SDK: Khalate et al., [arXiv:2202.11142](https://doi.org/10.48550/arXiv.2202.11142) (2022)
