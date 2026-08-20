import type { BreadcrumbList, DefinedTerm, ItemList, WebSite, WithContext } from 'schema-dts';

import { slugify } from '@/lib/slugify';

const site = import.meta.env.SITE.replace(/\/$/, '');

const absolute = (path: string) => `${site}${path}`;

export const webSiteJsonLd = (): WithContext<WebSite> => ({
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Wordapp',
  description: 'Daily word enrichment',
  url: site,
  inLanguage: 'en',
});

export const breadcrumbJsonLd = (crumbs: { name: string; path: string }[]): WithContext<BreadcrumbList> => ({
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: crumbs.map((crumb, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    name: crumb.name,
    item: absolute(crumb.path),
  })),
});

export const wordPageJsonLd = (
  word: string,
  path: string,
  definition: string,
): WithContext<DefinedTerm | BreadcrumbList>[] => [
  {
    '@context': 'https://schema.org',
    '@type': 'DefinedTerm',
    name: word,
    url: absolute(path),
    description: definition,
  },
  {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: absolute('/') },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Glossary',
        item: absolute('/glossary/'),
      },
      { '@type': 'ListItem', position: 3, name: word, item: absolute(path) },
    ],
  },
];

export const dayListJsonLd = (words: string[], path: string): WithContext<ItemList> => ({
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: 'Generated words',
  url: absolute(path),
  numberOfItems: words.length,
  itemListElement: words.map((word, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    name: word,
    url: absolute(`/words/${slugify(word)}/`),
  })),
});
