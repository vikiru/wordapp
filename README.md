<h1 align="center">Wordapp <br> An AI-powered Word of the Day App </h1>

<div align="center" id="badges">
  <a href="https://github.com/vikiru/wordapp/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-aqua" alt="MIT License Badge"/>
  </a>
  <a href="https://github.com/vikiru/wordapp/releases">
    <img src="https://img.shields.io/github/v/release/vikiru/wordapp" alt="Release"/>
  </a>
  <a href="https://github.com/vikiru/wordapp/issues?q=is%3Aissue+is%3Aclosed">
    <img src="https://img.shields.io/github/issues-closed/vikiru/wordapp" alt="Closed Issues"/>
  </a>
  <a href="https://github.com/vikiru/wordapp/pulls?q=is%3Apr+is%3Aclosed">
    <img src="https://img.shields.io/github/issues-pr-closed/vikiru/wordapp?label=closed%20prs" alt="Closed PRs"/>
  </a>
</div>

---

**Wordapp** is an AI-powered Word of the Day web app which presents a curated collection of high quality words that have a certain flair and elegance, potentially allowing someone to enrich their grammar.

Starting from an initial word set ([english-words](https://github.com/mwiens91/english-words-py) / web-2) of around 235,970 words, words are filtered by various conditions such as a [Zipf-frequency window](https://en.wikipedia.org/wiki/Zipf%27s_law) (roughly how often the word is used — excluding both rare and overly common words), [WordNet synset](https://en.wikipedia.org/wiki/WordNet#Structure) validity (part of speech, hypernyms, taxonomy), word length, and suffix/derivation rules, while excluding profanity, named individuals and places, clinical or technical jargon, culturally-specific terms, and an explicit blocklist (archaic, low-flair, and occupation/politics/religion/currency words). A small curated whitelist bypasses the filters. 

The curated collection of words is then assessed daily and a selection of 10 words is chosen at random, passed onto Gemini AI which will generate word metadata according to a given [prompt](packages/generate/src/generate/prompts/prompt.py) and finally, this metadata is saved to a database so it can be fetched later by the front end as a pre-build step.

## 📖 Table of Contents

- [📖 Table of Contents](#-table-of-contents)
- [🌟 Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📝 Prerequisites](#-prerequisites)
- [⚡ Setup Instructions](#-setup-instructions)
- [📜 Available Scripts](#-available-scripts)
- [✨ Acknowledgments](#-acknowledgments)
- [©️ License](#️-license)

## 🌟 Features

- **Curated collection of words** that can be adapted and improved at any time
- **Random word generation** — 10 new words a day, powered by Gemini AI
- **RSS feeds** — two feeds: `/feed.xml` (today's words) and `/all_words.xml` (the full archive)
- **Glossary** of all words present
- **Archive** of words, showing when they were generated
- **Words of the day** — a set of daily words with one main word of the day, selected randomly / based on some conditions

## 🛠️ Tech Stack

- Frontend: [Astro](https://astro.build/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Starwind UI](https://github.com/starwind-ui/starwind-ui), [FlexSearch](https://github.com/nextapps-de/flexsearch), [Lucide Icons](https://lucide.dev/), [@fontsource](https://fontsource.org/), [astro-seo](https://github.com/jonasmerlin/astro-seo)

- Data & AI Engine: [Python](https://www.python.org/), [uv](https://docs.astral.sh/uv/), [poethepoet](https://github.com/nat-n/poethepoet), [Beanie](https://beanie-odm.dev/), [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/), [Google GenAI SDK](https://ai.google.dev/gemini-api/docs) (Gemini), [loguru](https://github.com/Delgan/loguru), [python-dotenv](https://github.com/theskumar/python-dotenv), [orjson](https://github.com/ijl/orjson)

- Validation: [zod](https://zod.dev/), [Pydantic](https://docs.pydantic.dev/), [msgspec](https://github.com/jcrist/msgspec)

- Database & Hosting: [MongoDB Atlas](https://www.mongodb.com/atlas), [Cloudflare Pages](https://pages.cloudflare.com/)

- Linting & Formatting: [oxlint](https://oxc.rs/docs/guide/usage/linter/oxlint.html), [Biome](https://biomejs.dev/), [oxfmt](https://oxc.rs/docs/guide/usage/formatter.html), [Prettier](https://prettier.io/), [prettier-plugin-astro](https://github.com/withastro/prettier-plugin-astro), [Ruff](https://docs.astral.sh/ruff/)

- Dev Tools: [pnpm](https://pnpm.io/), [lefthook](https://github.com/evilmartians/lefthook), [commitlint](https://commitlint.js.org/), [Knip](https://github.com/webpro-nl/knip), [semantic-release](https://github.com/semantic-release/semantic-release)

## 📝 Prerequisites

Ensure that the following prerequisites are installed on your system by following the [Setup Instructions](#-setup-instructions):

- [Node.js](https://nodejs.org/) [≥ 22.12]
- [pnpm](https://pnpm.io/)
- [Python](https://www.python.org/) [3.13]
- [uv](https://docs.astral.sh/uv/) (Python environment/package manager)
- Google Gemini API Key (via [Google AI Studio](https://aistudio.google.com/))
- A [MongoDB Atlas](https://www.mongodb.com/atlas) cluster (persistence/export pipeline)

## ⚡ Setup Instructions

1. Clone this repository to your local machine.

```bash
git clone https://github.com/vikiru/wordapp.git
cd wordapp
```

2. Install frontend dependencies.

```bash
pnpm install
```

3. Set up the Python workspace, install dependencies, and set up the environment file.

```bash
cd packages
uv sync
cp .env.sample .env
```

4. Add your API keys to `packages/.env`.

```bash
GEMINI_API_KEY=
MONGODB_URI=
```

5. Download the [Open English WordNet](https://en-word.net/) corpus.

```bash
uv run poe download-wordnet
```

6. Run the data pipeline stages in order.

   - Extract and filter candidate words from WordNet (one-time).

   ```bash
   uv run poe curate
   ```

   - Generate 10 random words using Gemini AI ([gemini-3.1-flash-lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite)).

   ```bash
   uv run poe generate
   ```

   - Save the generated data to the MongoDB database.

   ```bash
   uv run poe save-to-db
   ```

   - Export the MongoDB data to the frontend JSON files.

   ```bash
   uv run poe fetch
   ```

7. Run the frontend prebuild steps (validate the data and build the search index).

```bash
pnpm --filter frontend prebuild
```

8. Start the development server from the repository root.

```bash
pnpm dev
```

The application will be running and available at the following URL:

```bash
http://localhost:4321
```

Alternatively, build and preview the production version.

```bash
pnpm build
pnpm preview
```

## 📜 Available Scripts

1. Start the development server.

```bash
pnpm dev
```

2. Build the production version of the application.

```bash
pnpm build
```

3. Preview the production build.

```bash
pnpm preview
```

4. Lint files using [oxlint](https://oxc.rs/docs/guide/usage/linter/oxlint.html), [Biome](https://biomejs.dev/), and [Ruff](https://docs.astral.sh/ruff/).

```bash
pnpm lint
```

5. Format files using [oxfmt](https://oxc.rs/docs/guide/usage/formatter.html), [Biome](https://biomejs.dev/), [Prettier](https://prettier.io/), and [Ruff](https://docs.astral.sh/ruff/).

```bash
pnpm format
```

1. Run TypeScript type checks.

```bash
pnpm typecheck
```

7. Check unused dependencies and files with [Knip](https://github.com/webpro-nl/knip).

```bash
pnpm unused
```

## ✨ Acknowledgments

- [Astro](https://astro.build/)
- [Astro Docs](https://docs.astro.build/)
- [prettier-plugin-astro](https://github.com/withastro/prettier-plugin-astro)
- [Tailwind CSS](https://tailwindcss.com/)
- [Starwind UI](https://github.com/starwind-ui/starwind-ui)
- [zod](https://zod.dev/)
- [Google Gemini](https://ai.google.dev/gemini-api/docs)
- [WordNet](https://wordnet.princeton.edu/)
- [WN Docs](https://wn.readthedocs.io/)
- [english-words](https://github.com/mwiens91/english-words-py)
- [wordfreq](https://github.com/rspeer/wordfreq)
- [simplemma](https://github.com/adbar/simplemma)
- [wn](https://github.com/goodmami/wn)
- [pycountry](https://github.com/flyingcircusio/pycountry)
- [glin-profanity](https://github.com/GLINCKER/glin-profanity)
- [Beanie](https://beanie-odm.dev/)
- [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/)
- [Pydantic](https://docs.pydantic.dev/)
- [msgspec](https://github.com/jcrist/msgspec)
- [orjson](https://github.com/ijl/orjson)
- [loguru](https://github.com/Delgan/loguru)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [Shields Badges](https://github.com/badges/shields)
- [Semantic Release](https://github.com/semantic-release/semantic-release)
- [Favicon Generator](https://favicon.io/favicon-generator/)

## ©️ License

The contents of this repository are licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

[MIT](LICENSE) &copy; 2025-present Visakan Kirubakaran.
