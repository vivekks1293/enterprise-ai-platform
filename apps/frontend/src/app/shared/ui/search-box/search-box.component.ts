import { ChangeDetectionStrategy, Component, DestroyRef, inject, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'eap-search-box',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-search-box">
      <input
        class="eap-form-control"
        type="search"
        [placeholder]="placeholder()"
        [(ngModel)]="query"
        (ngModelChange)="onQueryChange($event)"
      />
    </div>
  `,
  styles: `
    .eap-search-box {
      width: 100%;
      max-width: 320px;
    }
  `
})
export class SearchBoxComponent {
  public readonly placeholder = input<string>('Search…');
  public readonly debounceMs = input<number>(300);
  public readonly searchChange = output<string>();

  protected query = '';

  private readonly destroyRef = inject(DestroyRef);
  private readonly queryChanges$ = new Subject<string>();

  constructor() {
    this.queryChanges$
      .pipe(debounceTime(this.debounceMs()), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe((value) => this.searchChange.emit(value));
  }

  protected onQueryChange(value: string): void {
    this.queryChanges$.next(value);
  }
}
