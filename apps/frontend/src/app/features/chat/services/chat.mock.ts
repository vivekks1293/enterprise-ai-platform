import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';

function minutesAgo(minutes: number): Date {
  return new Date(Date.now() - minutes * 60 * 1000);
}

export const MOCK_CONVERSATIONS: readonly ChatConversationSummary[] = [
  {
    id: 'conv-1',
    title: 'Quarterly roadmap planning',
    preview: 'Can you help me structure the Q3 roadmap review?',
    updatedAt: minutesAgo(8),
    pinned: true
  },
  {
    id: 'conv-2',
    title: 'API rate limit investigation',
    preview: 'The 429 errors seem to spike around 9am UTC.',
    updatedAt: minutesAgo(42),
    pinned: true
  },
  {
    id: 'conv-3',
    title: 'Onboarding doc rewrite',
    preview: 'Draft a shorter version of the setup guide.',
    updatedAt: minutesAgo(130),
    pinned: false
  },
  {
    id: 'conv-4',
    title: 'Vendor comparison notes',
    preview: 'Summarize the tradeoffs between the two vendors.',
    updatedAt: minutesAgo(600),
    pinned: false
  },
  {
    id: 'conv-5',
    title: 'Release notes draft',
    preview: 'New conversation',
    updatedAt: minutesAgo(1400),
    pinned: false
  }
];

export const MOCK_MESSAGES: ReadonlyMap<string, readonly ChatMessage[]> = new Map([
  [
    'conv-1',
    [
      {
        id: 'msg-1a',
        role: 'user',
        content: 'Can you help me structure the Q3 roadmap review? We have five workstreams to cover.',
        createdAt: minutesAgo(12),
        status: 'complete'
      },
      {
        id: 'msg-1b',
        role: 'assistant',
        content:
          'Happy to help. A clean structure for five workstreams: start with a one-slide summary of overall progress, then give each workstream its own section with status, key risks, and next milestone. Close with a cross-cutting risks slide and the asks you need from leadership.',
        createdAt: minutesAgo(11),
        status: 'complete'
      },
      {
        id: 'msg-1c',
        role: 'user',
        content: 'That works. Can you also suggest how to handle the workstream that is behind schedule?',
        createdAt: minutesAgo(9),
        status: 'complete'
      }
    ]
  ],
  [
    'conv-2',
    [
      {
        id: 'msg-2a',
        role: 'user',
        content: 'The 429 errors seem to spike around 9am UTC. Any idea what could cause that pattern?',
        createdAt: minutesAgo(45),
        status: 'complete'
      },
      {
        id: 'msg-2b',
        role: 'assistant',
        content:
          'A recurring spike at a fixed time usually points to a scheduled job rather than organic traffic — worth checking for a cron task, a batch sync, or a client-side polling interval that lines up with 9am UTC.',
        createdAt: minutesAgo(43),
        status: 'complete'
      }
    ]
  ]
]);

/**
 * Rotated through by ChatFacade.sendMessage() to simulate an assistant
 * reply. Purely illustrative placeholder text — clearly generic so it's
 * never mistaken for a real model output. Replaced entirely once
 * StreamingClientService is wired up.
 */
export const MOCK_ASSISTANT_REPLIES: readonly string[] = [
  "Thanks for the context — here's a placeholder response while this workspace is validated. Real AI responses will stream in here once the model integration lands.",
  'This is a simulated reply used to test message rendering, spacing, and scroll behavior. No model is generating this text yet.',
  "Placeholder response: this exact message slot is where streamed tokens will appear once the AI integration is connected in the next phase."
];
