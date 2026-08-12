import type { Inflections } from '@/types/word';

export const inflectionEntries = (inflections: Inflections | null): Array<[string, string]> =>
  inflections ? Object.entries(inflections).filter((entry): entry is [string, string] => Boolean(entry[1])) : [];
