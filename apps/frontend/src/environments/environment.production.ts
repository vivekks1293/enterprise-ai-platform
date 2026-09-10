export const environment = {
  production: true,
  debugMode: false,
  appName: 'Enterprise AI Platform',
  appVersion: '0.1.0',
  apiBaseUrl: 'https://en-cb81a6aa581641349bf37d21bfdb0c56.ecs.ap-south-1.on.aws/api/v1',
  streamingBaseUrl: 'https://en-cb81a6aa581641349bf37d21bfdb0c56.ecs.ap-south-1.on.aws/api/v1',
  enableMockData: false,
  featureFlags: {
    streamingEnabled: true,
    toolCallingEnabled: false
  }
};
