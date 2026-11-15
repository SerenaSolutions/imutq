// SPDX-License-Identifier: Apache-2.0
// Z-Seal: sela a selecao e encadeia no selo anterior. Tudo local, sem codigo remoto.
importScripts("sha3.js", "canonical.js", "selo.js");

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "zseal-selar",
    title: "Selar trecho com Z-Seal",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "zseal-selar") return;
  const texto = (info.selectionText || "").trim();
  if (!texto) return;
  const { selos = [] } = await chrome.storage.local.get("selos");
  const novo = criarSelo({
    texto,
    url: info.pageUrl || (tab && tab.url) || "",
    titulo: (tab && tab.title) || "",
    anterior: selos.length ? selos[selos.length - 1] : null,
    indice: selos.length + 1,
    agora: new Date().toISOString()
  });
  selos.push(novo);
  await chrome.storage.local.set({ selos });
  chrome.action.setBadgeText({ text: String(selos.length) });
  chrome.action.setBadgeBackgroundColor({ color: "#1f6feb" });
});
