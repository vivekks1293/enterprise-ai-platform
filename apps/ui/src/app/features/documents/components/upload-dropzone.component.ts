import { Component, ChangeDetectionStrategy, input, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IconComponent } from '@shared/components/icon.component';

@Component({
  selector: 'app-upload-dropzone',
  standalone: true,
  imports: [CommonModule, IconComponent],
  template: `
    <div
      class="dropzone-box"
      [class.drag-active]="isDragging()"
      [class.uploading]="isUploading()"
      (dragover)="onDragOver($event)"
      (dragleave)="onDragLeave($event)"
      (drop)="onDrop($event)"
      (click)="fileInput.click()"
    >
      <input
        #fileInput
        type="file"
        class="hidden-input"
        accept=".pdf,.docx,.txt,.md"
        (change)="onFileSelected($event)"
        [disabled]="isUploading()"
      />

      <div class="dropzone-content">
        <div class="dropzone-icon">
          @if (isUploading()) {
            <div class="spinner"></div>
          } @else {
            <app-icon name="plus" [size]="28"></app-icon>
          }
        </div>

        <div class="dropzone-text">
          @if (isUploading()) {
            <p class="main-text">Uploading and validating document...</p>
            <p class="sub-text">Please wait while the server securely stores the file</p>
          } @else {
            <p class="main-text">Click to upload or drag & drop files here</p>
            <p class="sub-text">Supported formats: PDF, Word (DOCX), Markdown, Plain Text (Max 25MB)</p>
          }
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        width: 100%;
      }

      .hidden-input {
        display: none;
      }

      .dropzone-box {
        background: var(--bg-card);
        border: 2px dashed var(--border-default);
        border-radius: var(--radius-lg);
        padding: 2.25rem 1.5rem;
        cursor: pointer;
        transition: all var(--transition-smooth);
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;

        &:hover:not(.uploading) {
          border-color: var(--primary);
          background: var(--bg-card-hover);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px var(--primary-glow);
        }

        &.drag-active {
          border-color: var(--primary-light);
          background: var(--bg-chip);
          transform: scale(1.01);
        }

        &.uploading {
          cursor: wait;
          border-color: var(--primary);
          opacity: 0.9;
        }
      }

      .dropzone-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.85rem;
      }

      .dropzone-icon {
        width: 52px;
        height: 52px;
        border-radius: var(--radius-full);
        background: var(--bg-chip);
        color: var(--primary-light);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform var(--transition-fast);
      }

      .dropzone-box:hover .dropzone-icon {
        transform: scale(1.1);
      }

      .main-text {
        font-size: 0.98rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
      }

      .sub-text {
        font-size: 0.82rem;
        color: var(--text-muted);
      }

      .spinner {
        width: 22px;
        height: 22px;
        border: 2px solid var(--border-default);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UploadDropzoneComponent {
  public readonly isUploading = input<boolean>(false);
  public readonly fileDropped = output<File>();

  public readonly isDragging = signal<boolean>(false);

  public onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(true);
  }

  public onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
  }

  public onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.fileDropped.emit(files[0]);
    }
  }

  public onFileSelected(event: Event): void {
    const inputEl = event.target as HTMLInputElement;
    if (inputEl.files && inputEl.files.length > 0) {
      this.fileDropped.emit(inputEl.files[0]);
      inputEl.value = '';
    }
  }
}

