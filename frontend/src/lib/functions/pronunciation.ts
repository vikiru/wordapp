export const formatIpa = (ipa?: string | null) => {
  if (!ipa) return undefined;
  const core = ipa.trim().replace(/^\/+|\/+$/g, '');
  return core ? `/${core}/` : undefined;
};
