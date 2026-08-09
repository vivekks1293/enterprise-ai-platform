import { Pipe, PipeTransform } from '@angular/core';

const KNOWN_LABELS: Readonly<Record<string, string>> = {
  'application/pdf': 'PDF',
  'application/msword': 'Word',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
  'application/vnd.ms-excel': 'Excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
  'application/vnd.ms-powerpoint': 'PowerPoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
  'text/plain': 'Text',
  'text/csv': 'CSV',
  'text/markdown': 'Markdown',
  'application/json': 'JSON',
  'image/png': 'PNG image',
  'image/jpeg': 'JPEG image'
};

/**
 * Formats a raw MIME type (e.g.
 * "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
 * into a short, human-readable label (e.g. "Word"). Generic — not
 * documents-specific — reusable anywhere a content type needs to be
 * shown to a user rather than a developer. Falls back to the MIME
 * subtype, uppercased, for anything not in the known list, rather
 * than showing the full raw string.
 */
@Pipe({
  name: 'eapMimeTypeLabel',
  standalone: true
})
export class MimeTypeLabelPipe implements PipeTransform {
  public transform(contentType: string | null | undefined): string {
    if (!contentType) {
      return 'Unknown';
    }
    const known = KNOWN_LABELS[contentType.toLowerCase()];
    if (known) {
      return known;
    }
    const subtype = contentType.split('/').pop();
    return subtype ? subtype.toUpperCase() : 'File';
  }
}
