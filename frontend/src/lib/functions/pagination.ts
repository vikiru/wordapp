export const ARCHIVE_CARDS_PER_PAGE = 12;

export type PageItem = number | 'ellipsis';

export const pageItems = (page: number, totalPages: number): PageItem[] => {
  const items: PageItem[] = [];
  let prev = 0;
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || Math.abs(i - page) <= 1) {
      if (prev && i - prev > 1) items.push('ellipsis');
      items.push(i);
      prev = i;
    }
  }
  return items;
};

export const clampPage = (page: number, totalPages: number) =>
  Number.isFinite(page) ? Math.min(totalPages, Math.max(1, Math.floor(page))) : 1;
