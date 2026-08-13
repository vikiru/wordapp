import { Document } from 'flexsearch';

import searchIndex from '@/data/search-index.json';
import { type SearchHit, searchIndexOptions } from '@/lib/search/config';

export const searchIndexClient = new Document<SearchHit>(searchIndexOptions);
for (const [key, data] of Object.entries(searchIndex.chunks)) {
  searchIndexClient.import(key, data);
}
