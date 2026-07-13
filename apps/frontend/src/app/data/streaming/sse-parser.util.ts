import { SseFrame } from '@data/streaming/stream-event.model';

/**
 * Parses the `text/event-stream` wire format into discrete frames.
 * Implemented by hand (rather than relying on the native `EventSource`)
 * because `EventSource` cannot send custom headers, which rules it out
 * for bearer-token auth. This parser is fed raw text chunks as they
 * arrive from a `fetch` + `ReadableStream` and is stateful because a
 * chunk boundary can land in the middle of a frame.
 *
 * Wire format per frame (blank line terminates a frame):
 *   event: token
 *   data: {"text":"hel"}
 *   id: 42
 *   <blank line>
 */
export class SseFrameParser {
  private buffer = '';

  public feed(chunk: string): SseFrame[] {
    this.buffer += chunk;
    const frames: SseFrame[] = [];

    let boundary = this.buffer.indexOf('\n\n');
    while (boundary !== -1) {
      const rawFrame = this.buffer.slice(0, boundary);
      this.buffer = this.buffer.slice(boundary + 2);
      const parsed = this.parseFrame(rawFrame);
      if (parsed) {
        frames.push(parsed);
      }
      boundary = this.buffer.indexOf('\n\n');
    }

    return frames;
  }

  private parseFrame(rawFrame: string): SseFrame | null {
    let event = 'message';
    const dataLines: string[] = [];
    let id: string | undefined;

    for (const line of rawFrame.split('\n')) {
      if (line.startsWith('event:')) {
        event = line.slice('event:'.length).trim();
      } else if (line.startsWith('data:')) {
        dataLines.push(line.slice('data:'.length).trim());
      } else if (line.startsWith('id:')) {
        id = line.slice('id:'.length).trim();
      }
      // Comment lines (starting with ':') and unrecognized fields are ignored.
    }

    if (dataLines.length === 0) {
      return null;
    }

    return { event, data: dataLines.join('\n'), id };
  }
}
