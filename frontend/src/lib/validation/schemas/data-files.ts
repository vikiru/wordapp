import { z } from 'zod';

import { GeneratedWordSchema } from './word';

const ISO_DATE_KEY = /^\d{4}-\d{2}-\d{2}$/;

export const WordsFileSchema = z.array(GeneratedWordSchema);
export const WordsTodayFileSchema = z.array(GeneratedWordSchema);
export const WotdFileSchema = z.array(GeneratedWordSchema);
export const ArchiveFileSchema = z.record(
  z.string().regex(ISO_DATE_KEY, 'archive key must be an ISO date (YYYY-MM-DD)'),
  z.array(GeneratedWordSchema),
);

export type WordsFile = z.infer<typeof WordsFileSchema>;
export type WordsTodayFile = z.infer<typeof WordsTodayFileSchema>;
export type WotdFile = z.infer<typeof WotdFileSchema>;
export type ArchiveFile = z.infer<typeof ArchiveFileSchema>;
