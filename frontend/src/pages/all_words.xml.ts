import rss from '@astrojs/rss';
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

import { slugify } from '@/lib/slugify';

export const GET: APIRoute = async (context) => {
  const site = context.site ?? new URL(import.meta.env.SITE);
  const words = (await getCollection('words')).sort((a, b) =>
    b.data.generation_date.localeCompare(a.data.generation_date),
  );
  const lastBuildDate = words[0] ? new Date(words[0].data.generation_date) : new Date();
  return rss({
    title: 'Wordapp — All Words',
    description:
      'A scholarly dictionary grown one word at a time. Archive of all generated words with definitions, pronunciation, and etymology.',
    site,
    items: words.map((entry) => ({
      title: entry.data.word,
      link: `/words/${slugify(entry.data.word)}/`,
      pubDate: new Date(entry.data.generation_date),
      description: entry.data.senses.map((s) => `${s.part_of_speech}: ${s.definition}`).join('; '),
      // Each pos_tag becomes a separate <category> element
      categories: entry.data.pos_tags,
      guid: `${entry.data.word}-${entry.data.generation_date}`,
    })),
    customData: [
      '<language>en</language>',
      `<lastBuildDate>${lastBuildDate.toUTCString()}</lastBuildDate>`,
      '<ttl>43200</ttl>',
    ].join('\n'),
  });
};
