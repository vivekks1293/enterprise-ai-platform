import { Pipe, PipeTransform } from '@angular/core';

const UNITS = ['B', 'KB', 'MB', 'GB', 'TB'] as const;

@Pipe({
  name: 'eapFileSize',
  standalone: true
})
export class FileSizePipe implements PipeTransform {
  public transform(bytes: number | null | undefined): string {
    if (bytes === null || bytes === undefined || Number.isNaN(bytes)) {
      return '—';
    }
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    let value = bytes / 1024;
    let unitIndex = 1;
    while (value >= 1024 && unitIndex < UNITS.length - 1) {
      value /= 1024;
      unitIndex += 1;
    }

    return `${value.toFixed(value < 10 ? 1 : 0)} ${UNITS[unitIndex]}`;
  }
}
