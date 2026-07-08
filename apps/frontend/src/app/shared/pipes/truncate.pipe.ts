import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'eapTruncate',
  standalone: true
})
export class TruncatePipe implements PipeTransform {
  public transform(value: string | null | undefined, maxLength = 80): string {
    if (!value) {
      return '';
    }
    return value.length > maxLength ? `${value.slice(0, maxLength).trimEnd()}…` : value;
  }
}
