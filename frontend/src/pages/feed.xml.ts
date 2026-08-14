import rss from '@astrojs/rss';
import type { APIRoute } from 'astro';
import { getCollection, type CollectionEntry } from 'astro:content';

import { slugify } from '@/lib/slugify';

export const GET: APIRoute = async (context) => {
  const site = context.site ?? new URL(import.meta.env.SITE);
  const words: CollectionEntry<'words'>[] = await getCollection('words');
  const sortedWords = words.toSorted((a, b) => b.data.generation_date.localeCompare(a.data.generation_date));
  const latest = sortedWords.slice(0, 10);
  const lastBuildDate = latest[0] ? new Date(latest[0].data.generation_date) : new Date();
  return rss({
    title: 'Wordapp',
    description:
      'A scholarly dictionary grown one word at a time. New words daily with definitions, pronunciation, and etymology.',
    site,
    items: latest.map((entry) => ({
      title: entry.data.word,
      link: `/words/${slugify(entry.data.word)}/`,
      pubDate: new Date(entry.data.generation_date),
      description: entry.data.senses[0]?.definition ?? '',
      categories: entry.data.pos_tags,
    })),
    customData: [
      '<language>en</language>',
      `<lastBuildDate>${lastBuildDate.toUTCString()}</lastBuildDate>`,
      '<ttl>1440</ttl>',
    ].join('\n'),
  });
};
