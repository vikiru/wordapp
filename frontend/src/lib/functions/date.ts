export const formatDate = (isoDate: string) =>
  new Date(isoDate).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  });

export const formatMonthLabel = (monthKey: string) =>
  new Date(`${monthKey}-01T00:00:00Z`).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    timeZone: 'UTC',
  });

export const shortDate = (iso: string) => {
  const parts = iso.split('-');
  const year = parts[0] || '0000';
  const month = parts[1] || '00';
  const day = parts[2] || '00';
  return `${month}.${day}.${year.slice(2)}`;
};
export const formatShortDate = (iso: string) =>
  new Date(`${iso}T00:00:00Z`).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  });
