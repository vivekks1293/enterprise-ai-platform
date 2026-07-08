import { Conversation } from '@features/conversations/models/conversation.model';

export const MOCK_CONVERSATIONS: readonly Conversation[] = [
  {
    id: 'c-1001',
    title: 'Claims processing SOP questions',
    lastMessageAt: new Date(Date.now() - 15 * 60 * 1000),
    messageCount: 12
  },
  {
    id: 'c-1002',
    title: 'Patient eligibility verification flow',
    lastMessageAt: new Date(Date.now() - 3 * 60 * 60 * 1000),
    messageCount: 6
  },
  {
    id: 'c-1003',
    title: 'ICD-10 coding clarifications',
    lastMessageAt: new Date(Date.now() - 26 * 60 * 60 * 1000),
    messageCount: 21
  }
];
