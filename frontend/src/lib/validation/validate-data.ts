/**
 * Build-time zod validation of the four static data artifacts (runs in
 * `pnpm build`; parse-only, fails the build on drift).
 */
import { readFileSync } from "node:fs";
import type { ZodType } from "zod";
import {
  ArchiveFileSchema,
  WotdFileSchema,
  WordsFileSchema,
  WordsTodayFileSchema,
} from "@/types/data-files";

const DATA_DIR = new URL("../../data/", import.meta.url);

function validateJsonFile(schema: ZodType, fileName: string): void {
  const raw = readFileSync(new URL(fileName, DATA_DIR), "utf8");
  const data: unknown = JSON.parse(raw);
  const result = schema.safeParse(data);
  if (!result.success) {
    const details = result.error.issues
      .map(
        (issue) =>
          `  - ${fileName}: ${issue.path.join(".") || "(root)"} — ${issue.message}`,
      )
      .join("\n");
    throw new Error(`Data validation failed:\n${details}`);
  }
}

export function validateAllData(): void {
  validateJsonFile(WordsFileSchema, "words.json");
  validateJsonFile(WordsTodayFileSchema, "words_today.json");
  validateJsonFile(WotdFileSchema, "wotd.json");
  validateJsonFile(ArchiveFileSchema, "archive.json");
}

// Build-only entrypoint: `tsx src/lib/validation/validate-data.ts` in `pnpm build`.
validateAllData();
console.log("Data validation: words.json, words_today.json, wotd.json, archive.json OK");
