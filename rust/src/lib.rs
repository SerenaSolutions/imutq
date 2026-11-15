// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Solutions
//! Nucleo do IMUT-Q. A mesma verificacao roda na CLI e no navegador via WebAssembly.
pub mod canonica;
pub mod verificacao;

#[cfg(target_arch = "wasm32")]
mod abi {
    use crate::verificacao::verificar_bytes;

    /// Aloca um buffer no heap do modulo. A extensao escreve o JSON nele.
    #[no_mangle]
    pub extern "C" fn alocar(n: usize) -> *mut u8 {
        let mut v = Vec::<u8>::with_capacity(n);
        let p = v.as_mut_ptr();
        std::mem::forget(v);
        p
    }

    /// Libera o buffer devolvido por `alocar`.
    #[no_mangle]
    pub extern "C" fn liberar(p: *mut u8, n: usize) {
        unsafe { drop(Vec::from_raw_parts(p, 0, n)); }
    }

    /// 1 integro e assinado, 0 invalido, -1 json invalido.
    #[no_mangle]
    pub extern "C" fn verificar(p: *const u8, n: usize) -> i32 {
        let bytes = unsafe { std::slice::from_raw_parts(p, n) };
        verificar_bytes(bytes)
    }
}
