/**
 * Triggers a browser "Save As" for an in-memory Blob via a temporary,
 * invisible anchor element. Generic — not tied to documents/Knowledge
 * specifically, reusable for any future feature that needs to turn a
 * fetched Blob into a file download (exports, reports, etc.).
 */
export function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}
