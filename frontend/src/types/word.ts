import { z } from 'zod';

/**
 * Word domain contract mirroring `packages/data/src/data/models/word.py`
 * (names, optionality, nullability, list bounds). snake_case field names are
 * the JSON wire format; TS naming applies to schema/type names only.
 */

export const PronunciationSchema = z.object({
  ipa: z.string().nullable().optional(),
  phonetic: z.string().nullable().optional(),
});

export const EtymologySchema = z.object({
  origin_language: z.string().nullable().optional(),
  original_word: z.string().nullable().optional(),
  first_recorded: z.string().nullable().optional(),
  explanation: z.string().nullable().optional(),
});

export const WordSenseSchema = z.object({
  part_of_speech: z.string(),
  definition: z.string(),
  examples: z.array(z.string()).min(1).max(3),
  usage_notes: z.array(z.string()),
});

export const WordRelationSchema = z.object({
  word: z.string(),
  part_of_speech: z.string(),
  differentiator: z.string().nullable().optional(),
});

export const WordFormSchema = z.object({
  word: z.string(),
  part_of_speech: z.string().nullable().optional(),
  ipa: z.string().nullable().optional(),
});

export const InflectionsSchema = z.object({
  past: z.string().nullable().optional(),
  past_participle: z.string().nullable().optional(),
  present_participle: z.string().nullable().optional(),
  plural: z.string().nullable().optional(),
  comparative: z.string().nullable().optional(),
  superlative: z.string().nullable().optional(),
});

export const GeneratedWordSchema = z.object({
  id: z.string(),
  word: z.string(),
  pos_tags: z.array(z.string()).min(1),
  senses: z.array(WordSenseSchema).min(1),
  synonyms: z.array(WordRelationSchema).max(4),
  antonyms: z.array(WordRelationSchema).max(4),
  inflections: InflectionsSchema.nullable(),
  word_family: z.array(WordFormSchema),
  pronunciation: PronunciationSchema,
  etymology: z.array(EtymologySchema),
  common_mistakes: z.array(z.string()).max(3),
  interesting_fact: z.string().nullable(),
  is_wotd: z.boolean(),
  past_wotd: z.boolean(),
  generation_date: z.string(),
});

export type GeneratedWord = z.infer<typeof GeneratedWordSchema>;
export type WordSense = z.infer<typeof WordSenseSchema>;
export type WordRelation = z.infer<typeof WordRelationSchema>;
export type WordForm = z.infer<typeof WordFormSchema>;
export type Inflections = z.infer<typeof InflectionsSchema>;
export type Pronunciation = z.infer<typeof PronunciationSchema>;
export type Etymology = z.infer<typeof EtymologySchema>;
