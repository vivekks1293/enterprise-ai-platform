import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function requiredTrimmed(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = (control.value as string | null)?.trim();
    return value ? null : { requiredTrimmed: true };
  };
}

export function minLengthTrimmed(min: number): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = (control.value as string | null)?.trim() ?? '';
    return value.length >= min ? null : { minLengthTrimmed: { requiredLength: min, actualLength: value.length } };
  };
}

export function emailFormat(): ValidatorFn {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value as string | null;
    if (!value) {
      return null;
    }
    return pattern.test(value) ? null : { emailFormat: true };
  };
}
