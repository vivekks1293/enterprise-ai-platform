import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'eapRelativeTime',
  standalone: true
})
export class RelativeTimePipe implements PipeTransform {
  public transform(value: Date | string | null | undefined): string {
    if (!value) {
      return '';
    }
    const date = typeof value === 'string' ? new Date(value) : value;
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  }
}
