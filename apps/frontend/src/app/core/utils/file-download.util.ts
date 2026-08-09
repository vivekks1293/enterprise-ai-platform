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

/**
 * Extracts a filename from a Content-Disposition header value, e.g.
 * `attachment; filename="report.pdf"` or the RFC 5987 extended form
 * `attachment; filename*=UTF-8''report.pdf`. Returns null if the
 * header is absent or doesn't contain a recognizable filename, so
 * callers can fall back to a filename they already know client-side
 * (e.g. from the document's own metadata) rather than failing outright.
 */
export function extractFilenameFromContentDisposition(headerValue: string | null): string | null {
  if (!headerValue) {
    return null;
  }

  const extendedMatch = /filename\*=(?:UTF-8'')?([^;]+)/i.exec(headerValue);
  if (extendedMatch?.[1]) {
    try {
      return decodeURIComponent(extendedMatch[1].trim().replace(/["']/g, ''));
    } catch {
      // Malformed percent-encoding — fall through to the simple form below.
    }
  }

  const simpleMatch = /filename="?([^";]+)"?/i.exec(headerValue);
  return simpleMatch?.[1]?.trim() ?? null;
}
