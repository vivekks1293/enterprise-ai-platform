import { Pipe, PipeTransform, inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Pipe({
  name: 'markdown',
  standalone: true
})
export class MarkdownPipe implements PipeTransform {
  private readonly sanitizer = inject(DomSanitizer);

  public transform(content: string | null | undefined): SafeHtml {
    if (!content) {
      return '';
    }

    let parsed = this.escapeHtml(content);

    // Fenced Code Blocks (```lang ... ```)
    parsed = parsed.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_match, lang, code) => {
      const languageBadge = lang ? `<div class="code-lang">${lang}</div>` : '';
      return `<div class="code-block-wrapper">${languageBadge}<pre><code>${code.trim()}</code></pre></div>`;
    });

    // Inline code (`code`)
    parsed = parsed.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold (**bold**)
    parsed = parsed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italic (*italic*)
    parsed = parsed.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Unordered lists (- item)
    parsed = parsed.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
    parsed = parsed.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Paragraph line breaks (preserve spacing)
    parsed = parsed.replace(/\n\n+/g, '</p><p>');
    parsed = parsed.replace(/\n/g, '<br/>');

    const wrapped = `<div class="markdown-body"><p>${parsed}</p></div>`;
    return this.sanitizer.bypassSecurityTrustHtml(wrapped);
  }

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

