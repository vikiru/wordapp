import { z } from "zod";

/**
 * Word domain contract mirroring `packages/data/src/data/models/word.py`
 * (names, optionality, nullability, list bounds). snake_case field names are
 * the JSON wire format; TS naming applies to schema/type names only.
 */

export const PronunciationSchema = z.object({
  ipa: z.string().optional(),
  phonetic: z.string().optional(),
});

export const EtymologySchema = z.object({
  origin_language: z.string().optional(),
  original_word: z.string().optional(),
  first_recorded: z.string().optional(),
  explanation: z.string().optional(),
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
  differentiator: z.string().optional(),
});

export const WordFormSchema = z.object({
  word: z.string(),
  part_of_speech: z.string().optional(),
  ipa: z.string().optional(),
});

export const InflectionsSchema = z.object({
  past: z.string().optional(),
  past_participle: z.string().optional(),
  present_participle: z.string().optional(),
  plural: z.string().optional(),
  comparative: z.string().optional(),
  superlative: z.string().optional(),
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
  generation_date: z.string(),
});

export type GeneratedWord = z.infer<typeof GeneratedWordSchema>;
export type WordSense = z.infer<typeof WordSenseSchema>;
export type WordRelation = z.infer<typeof WordRelationSchema>;
export type WordForm = z.infer<typeof WordFormSchema>;
export type Inflections = z.infer<typeof InflectionsSchema>;
export type Pronunciation = z.infer<typeof PronunciationSchema>;
export type Etymology = z.infer<typeof EtymologySchema>;
