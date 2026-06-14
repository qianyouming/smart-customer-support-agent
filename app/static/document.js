const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getDocumentId() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  return parts[1] || "";
}

function renderError(message) {
  $("#documentTitle").textContent = "文档加载失败";
  $("#documentMeta").textContent = "请返回工作台重新选择文档。";
  $("#documentStatus").className = "document-status error";
  $("#documentStatus").textContent = message;
  $("#chunkToc").innerHTML = "";
  $("#documentChunks").innerHTML = "";
}

function renderDocument(document) {
  document.title = document.filename;
  $("#documentTitle").textContent = document.filename;
  $("#documentMeta").textContent = `${document.content_type} · ${document.chunks_count} chunks`;
  $("#documentStatus").hidden = true;

  $("#chunkToc").innerHTML = document.chunks
    .map(
      (chunk) => `
        <a href="#chunk-${chunk.chunk_index}">
          Chunk ${chunk.chunk_index + 1}
        </a>
      `,
    )
    .join("");

  $("#documentChunks").innerHTML = document.chunks
    .map(
      (chunk) => `
        <article id="chunk-${chunk.chunk_index}" class="document-chunk-card">
          <div class="document-chunk-head">
            <strong>Chunk ${chunk.chunk_index + 1}</strong>
            <span>${escapeHtml(document.filename)}</span>
          </div>
          <p>${escapeHtml(chunk.content)}</p>
        </article>
      `,
    )
    .join("");
}

async function loadDocument() {
  const documentId = getDocumentId();
  if (!documentId) {
    renderError("缺少文档 ID。");
    return;
  }

  try {
    const response = await fetch(`/api/files/${encodeURIComponent(documentId)}`);
    if (response.status === 404) {
      renderError("这个文档不存在，可能已经被删除。");
      return;
    }
    if (!response.ok) {
      throw new Error("document request failed");
    }
    renderDocument(await response.json());
  } catch {
    renderError("文档内容加载失败，请稍后再试。");
  }
}

loadDocument();
