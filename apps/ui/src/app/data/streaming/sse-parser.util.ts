export interface SseFrame {
  readonly event: string;
  readonly data: string;
  readonly id?: string;
}

export class SseFrameParser {
  private buffer = '';

  public *feed(chunk: string): Generator<SseFrame> {
    this.buffer += chunk;
    const lines = this.buffer.split(/\r\n|\r|\n/);

    // Keep incomplete trailing line in buffer
    this.buffer = lines.pop() ?? '';

    let event = 'message';
    let data = '';
    let id: string | undefined;

    for (const line of lines) {
      if (line === '') {
        // Double newline signals dispatch of complete frame
        if (data !== '') {
          yield { event, data: data.replace(/\n$/, ''), id };
        }
        event = 'message';
        data = '';
        id = undefined;
        continue;
      }

      if (line.startsWith(':')) {
        // Comment / keepalive ping
        continue;
      }

      const colonIndex = line.indexOf(':');
      if (colonIndex === -1) {
        continue;
      }

      const field = line.slice(0, colonIndex).trim();
      const value = line.slice(colonIndex + 1).replace(/^\s/, '');

      if (field === 'event') {
        event = value;
      } else if (field === 'data') {
        data += value + '\n';
      } else if (field === 'id') {
        id = value;
      }
    }
  }
}

