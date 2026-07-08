export interface AppConfig {
  readonly appName: string;
  readonly apiBaseUrl: string;
  readonly production: boolean;
  readonly enableMockData: boolean;
}
