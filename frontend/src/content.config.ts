import { defineCollection } from 'astro:content';
import { file } from 'astro/loaders';
import { z } from 'astro/zod';
import { GeneratedWordSchema } from '@/types/word';

const words = defineCollection({
  loader: file('src/data/words.json'),
  schema: GeneratedWordSchema,
});

const wordsToday = defineCollection({
  loader: file('src/data/words_today.json'),
  schema: GeneratedWordSchema,
});

const archive = defineCollection({
  loader: file('src/data/archive.json'),
  schema: z.array(GeneratedWordSchema),
});

const wotd = defineCollection({
  loader: file('src/data/wotd.json'),
  schema: GeneratedWordSchema,
});

export const collections = { words, words_today: wordsToday, archive, wotd };
