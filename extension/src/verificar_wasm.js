// SPDX-License-Identifier: Apache-2.0
// Verificacao ML-DSA-44 no navegador: o mesmo nucleo Rust, compilado para WebAssembly.
// O wasm viaja dentro do pacote; nada e baixado de servidor (Manifest V3, sem codigo remoto).
let instancia = null;
let carregando = null;

async function carregarWasm() {
  if (instancia) return instancia;
  if (carregando) return carregando;
  carregando = (async () => {
    const url = chrome.runtime.getURL("src/ml_dsa_44.wasm");
    const resp = await fetch(url);
    const bytes = await resp.arrayBuffer();
    const { instance } = await WebAssembly.instantiate(bytes, {});
    instancia = instance.exports;
    return instancia;
  })();
  return carregando;
}

// 1 = integro e assinado, 0 = invalido, -1 = json invalido, null = wasm indisponivel
async function verificarAssinatura(objeto) {
  try {
    const { alocar, liberar, verificar, memory } = await carregarWasm();
    const buf = new TextEncoder().encode(JSON.stringify(objeto));
    const ptr = alocar(buf.length);
    new Uint8Array(memory.buffer, ptr, buf.length).set(buf);
    const r = verificar(ptr, buf.length);
    liberar(ptr, buf.length);
    return r;
  } catch (e) {
    return null;
  }
}
