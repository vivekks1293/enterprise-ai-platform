export const environment = {
  production: true,
  debugMode: false,
  appName: 'Enterprise AI Platform',
  appVersion: '0.1.0',
  apiBaseUrl: 'http://localhost:8000/api/v1/',
  streamingBaseUrl: '/api/stream',
  enableMockData: false,
  featureFlags: {
    streamingEnabled: true,
    toolCallingEnabled: false
  }
};
