export interface PaginatedResult<T> {
  readonly items: readonly T[];
  readonly page: number;
  readonly pageSize: number;
  readonly totalCount: number;
}

export interface SelectOption<T = string> {
  readonly label: string;
  readonly value: T;
}
