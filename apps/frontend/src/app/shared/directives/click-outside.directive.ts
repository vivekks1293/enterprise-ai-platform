import { Directive, ElementRef, OutputEmitterRef, output, inject, HostListener } from '@angular/core';

/**
 * Emits when a click occurs outside the host element. Used by
 * dropdowns, the user menu, and modals to close on outside click.
 */
@Directive({
  selector: '[eapClickOutside]',
  standalone: true
})
export class ClickOutsideDirective {
  private readonly elementRef = inject(ElementRef<HTMLElement>);

  public readonly eapClickOutside: OutputEmitterRef<void> = output();

  @HostListener('document:click', ['$event.target'])
  public onDocumentClick(target: HTMLElement): void {
    if (!this.elementRef.nativeElement.contains(target)) {
      this.eapClickOutside.emit();
    }
  }
}
