const INFLECTION_SUFFIXES = ['s', 'es', 'd', 'ed', 'ing'] as const;

const buildVariants = (word: string): Set<string> => {
  const variants = new Set<string>([word]);
  for (const suffix of INFLECTION_SUFFIXES) {
    variants.add(word + suffix);
  }

  if (/[^aeiou]y$/i.test(word)) {
    variants.add(`${word.slice(0, -1)}ies`);
  }
  return variants;
};

export const highlightParts = (sentence: string, word: string): { text: string; match: boolean }[] => {
  if (!word) {
    return [{ text: sentence, match: false }];
  }
  const variants = buildVariants(word);
  const lowerVariants = new Set([...variants].map((v) => v.toLowerCase()));
  const pattern = [...variants].map((v) => v.replace(/[.*+?^${}()|[\]\\]/g, String.raw`\$&`)).join('|');
  return sentence.split(new RegExp(`(\\b(?:${pattern})\\b)`, 'ig')).map((part) => ({
    text: part,
    match: part.length > 0 && lowerVariants.has(part.toLowerCase()),
  }));
};
