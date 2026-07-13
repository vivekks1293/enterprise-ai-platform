export interface FeatureFlags {
  readonly streamingEnabled: boolean;
  readonly toolCallingEnabled: boolean;
}

export interface AppConfig {
  readonly appName: string;
  readonly appVersion: string;
  readonly apiBaseUrl: string;
  /** Defaults to apiBaseUrl when not set — kept distinct because a backend may
   *  terminate SSE/streaming connections on separate infrastructure (e.g. a
   *  dedicated gateway) from its regular REST API. */
  readonly streamingBaseUrl: string;
  readonly production: boolean;
  readonly debugMode: boolean;
  readonly enableMockData: boolean;
  readonly featureFlags: FeatureFlags;
}
