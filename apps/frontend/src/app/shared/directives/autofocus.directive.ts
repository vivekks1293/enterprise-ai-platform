import { AfterViewInit, Directive, ElementRef, inject } from '@angular/core';

/** Focuses the host element after it renders. Useful for modals and search boxes. */
@Directive({
  selector: '[eapAutofocus]',
  standalone: true
})
export class AutofocusDirective implements AfterViewInit {
  private readonly elementRef = inject(ElementRef<HTMLElement>);

  public ngAfterViewInit(): void {
    queueMicrotask(() => this.elementRef.nativeElement.focus());
  }
}
