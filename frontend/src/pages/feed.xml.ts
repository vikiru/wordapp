import { getCollection } from 'astro:content';
import rss from '@astrojs/rss';
import type { APIRoute } from 'astro';
import { slugify } from '@/lib/slugify';

export const GET: APIRoute = async (context) => {
  const site = context.site ?? new URL(import.meta.env.SITE);
  const words = (await getCollection('words'))
    .sort((a, b) => b.data.generation_date.localeCompare(a.data.generation_date))
    .slice(0, 30);
  const lastBuildDate = words[0] ? new Date(words[0].data.generation_date) : new Date();
  return rss({
    title: 'Wordapp',
    description:
      'A scholarly dictionary grown one word at a time. New words daily with definitions, pronunciation, and etymology.',
    site,
    items: words.map((entry) => ({
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
      `<image><url>${new URL('/og.png', site)}</url><title>Wordapp</title><link>${site}</link></image>`,
    ].join('\n'),
  });
};
