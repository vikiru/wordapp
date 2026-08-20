export type Accent = 'us' | 'uk' | 'au';

export interface SpeakOptions {
  accent?: Accent;
  rate?: number;
}

const ACCENT_LANGS: Record<Accent, string> = {
  us: 'en-US',
  uk: 'en-GB',
  au: 'en-AU',
};

const DEFAULT_ACCENT: Accent = 'us';

const DEFAULT_RATE = 0.9;

export const isSupported = () =>
  typeof window !== 'undefined' &&
  typeof window.speechSynthesis.speak === 'function' &&
  typeof window.speechSynthesis.getVoices === 'function';

export const hasVoices = (): boolean => isSupported() && loadVoices().length > 0;

let cachedVoices: SpeechSynthesisVoice[] = [];

const normalizeLang = (lang: string) => lang.toLowerCase().replace('_', '-');

const loadVoices = (): SpeechSynthesisVoice[] => {
  if (isSupported()) {
    cachedVoices = window.speechSynthesis.getVoices();
  }
  return cachedVoices;
};

if (isSupported()) {
  loadVoices();
  window.speechSynthesis.addEventListener('voiceschanged', () => {
    loadVoices();
  });
}

const getVoice = (accent: Accent): SpeechSynthesisVoice | null => {
  const voices = loadVoices();
  const lang = ACCENT_LANGS[accent];
  const exact = voices.find((voice) => normalizeLang(voice.lang) === lang);
  if (exact) return exact;
  const english = voices.find((voice) => normalizeLang(voice.lang).startsWith('en'));
  return english ?? voices[0] ?? null;
};

export const speak = (text: string, options: SpeakOptions = {}): SpeechSynthesisUtterance | null => {
  if (!isSupported() || !text) return null;
  const synth = window.speechSynthesis;
  if (synth.speaking) synth.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  const accent = options.accent ?? DEFAULT_ACCENT;
  const voice = getVoice(accent);
  if (voice) {
    utterance.voice = voice;
    utterance.lang = voice.lang;
  } else {
    utterance.lang = ACCENT_LANGS[accent];
  }
  utterance.rate = options.rate ?? DEFAULT_RATE;
  synth.speak(utterance);
  return utterance;
};

export const stop = (): void => {
  if (isSupported()) window.speechSynthesis.cancel();
};
