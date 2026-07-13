import { ChangeDetectionStrategy, Component, forwardRef, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';

@Component({
  selector: 'eap-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './input.component.html',
  styleUrl: './input.component.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => InputComponent),
      multi: true
    }
  ]
})
export class InputComponent implements ControlValueAccessor {
  public readonly label = input<string | undefined>(undefined);
  public readonly placeholder = input<string>('');
  public readonly type = input<'text' | 'email' | 'password' | 'number'>('text');
  public readonly errorMessage = input<string | undefined>(undefined);
  /** Reserves trailing space inside the field for projected content
   *  (e.g. a password show/hide toggle) via the `suffix` slot. Generic
   *  and reusable — not specific to any one field's needs. */
  public readonly hasSuffix = input<boolean>(false);

  protected value = '';
  protected disabled = false;

  private onChange: (value: string) => void = () => {};
  private onTouched: () => void = () => {};

  public writeValue(value: string): void {
    this.value = value ?? '';
  }

  public registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  public registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  public setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  protected handleInput(value: string): void {
    this.value = value;
    this.onChange(value);
  }

  protected handleBlur(): void {
    this.onTouched();
  }
}
