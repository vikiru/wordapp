/**
 * Build-time FlexSearch index generation (runs in `pnpm build` before
 * `astro build`; emits public/search-index.json, always regenerated).
 * Indexes only the word field; entries store id + word so results can
 * link to detail pages without any runtime data access.
 */
import { readFileSync, writeFileSync } from 'node:fs';

import { Document } from 'flexsearch';

import { INDEX_VERSION, type SearchHit, searchIndexOptions } from '@/features/search/config';
import { ArchiveFileSchema, WordsFileSchema } from '@/lib/validation/schemas/data-files';
import type { GeneratedWord } from '@/types/word';

const DATA_DIR = new URL('../../data/', import.meta.url);
const OUT_FILE = new URL('search-index.json', DATA_DIR);

function readWordFile(fileName: string): GeneratedWord[] {
  const raw = readFileSync(new URL(fileName, DATA_DIR), 'utf8');
  const parsed = WordsFileSchema.safeParse(JSON.parse(raw));
  if (!parsed.success) {
    throw new Error(`Failed to parse ${fileName}: ${parsed.error.message}`);
  }
  return parsed.data;
}

function readArchiveDays(): GeneratedWord[] {
  const raw = readFileSync(new URL('archive.json', DATA_DIR), 'utf8');
  const parsed = ArchiveFileSchema.safeParse(JSON.parse(raw));
  if (!parsed.success) {
    throw new Error(`Failed to parse archive.json: ${parsed.error.message}`);
  }
  return Object.values(parsed.data).flat();
}

function buildSearchHits(): SearchHit[] {
  const byId = new Map<string, GeneratedWord>();
  for (const word of [...readWordFile('words.json'), ...readArchiveDays()]) {
    if (!byId.has(word.id)) {
      byId.set(word.id, word);
    }
  }
  return [...byId.values()].map((word) => ({ id: word.id, word: word.word }));
}

export function buildSearchIndex(): void {
  const hits = buildSearchHits();
  const index = new Document<SearchHit>(searchIndexOptions);
  for (const hit of hits) {
    index.add(hit);
  }
  const chunks: Record<string, string> = {};
  index.export((key, data) => {
    chunks[key] = data;
  });
  const asset = JSON.stringify({ version: INDEX_VERSION, docs: hits, chunks });
  writeFileSync(OUT_FILE, asset);
  const sizeKb = (asset.length / 1024).toFixed(1);
  console.log(`Search index: ${hits.length} words -> src/data/search-index.json (${sizeKb} KB)`);
}

// Build-only entrypoint: `tsx src/features/search/build-index.ts` in `pnpm build`.
buildSearchIndex();
