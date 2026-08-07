/**
 * Shared FlexSearch Document config for the pre-build step and any future
 * client that imports the emitted asset; both sides must construct the
 * index identically.
 */
import type { DocumentData, DocumentOptions } from "flexsearch";

export interface SearchHit extends DocumentData {
  id: string;
  word: string;
}

export const INDEX_VERSION = 1;

export const searchIndexOptions = {
  tokenize: "strict",
  document: {
    id: "id",
    index: ["word"],
    store: ["id", "word"],
  },
} satisfies DocumentOptions<SearchHit>;
