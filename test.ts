import fs from "node:fs";
import { words } from "popular-english-words";
import { profanity } from "@2toad/profanity";
import stopwords from "stopwords";
import { nouns } from "nouns";
import countryList from "country-list";
import LanguageList from "language-list";
import wordListPath from "word-list";
import { lemmatizer } from "lemmatizer";
import nlp from "compromise";
import natural from "natural";
// TODO: cleanup this file. Find a proper source of english words matching what I want. Find npm pkgs/ideas to filter out words
// TODO: decide between compromise/natural for POS tagging, filter out words not needed. Determine total word count.
// TODO: determine if python is better. Currently, src/data has the result of POS tagging on 274k words.

const language = "EN";
const defaultCategory = "N";
const defaultCategoryCapitalized = "NNP";
const lexicon = new natural.Lexicon(
	language,
	defaultCategory,
	defaultCategoryCapitalized,
);
const ruleSet = new natural.RuleSet(language);
const tagger = new natural.BrillPOSTagger(lexicon, ruleSet);

const wordArray = fs.readFileSync(wordListPath, "utf8").split("\n");
const chunkSize = 1000;
let currentChunk = 0;
const taggedWords = [];
while (currentChunk <= wordArray.length - chunkSize) {
	const str = wordArray.slice(currentChunk, currentChunk + chunkSize);
	const result = tagger.tag(str);
	if (result.taggedWords.length > 0) {
		taggedWords.push(...result.taggedWords);
	}
	currentChunk += chunkSize;
	console.log(currentChunk);
}
console.log(taggedWords.length);

const POSTagMap = new Map();
for (const word of taggedWords) {
	const token = word.token;
	const tag = word.tag;
	if (!POSTagMap.has(tag)) {
		POSTagMap.set(tag, [token]);
	}
	POSTagMap.set(tag, [...POSTagMap.get(tag), token]);
	console.log(word);
}

for (const tag of POSTagMap.keys()) {
	fs.writeFileSync(
		`./src/data/${tag}.json`,
		JSON.stringify(POSTagMap.get(tag)),
	);
	console.log(tag);
}
// fs.writeFileSync("./src/data/taggedWords.json", JSON.stringify(taggedWords));

//
// const rawExcludedWordsJson = fs.readFileSync(
// 	"./src/data/excludedWords.json",
// 	"utf-8",
// );
// const excludedWordsSet = new Set(JSON.parse(rawExcludedWordsJson));
//
// const languagesInstance = new LanguageList();
// const languageNamesSet = new Set(
// 	languagesInstance.getData().map((lang) => lang.language.toLowerCase()),
// );
//
// const countryNamesSet = new Set(
// 	countryList.getNames().map((name) => name.toLowerCase()),
// );
//
// const stopwordsEngSet = new Set(stopwords.english);
// const nounsSet = new Set(nouns.map((noun) => noun.toLowerCase()));
//
// const rootWords = new Set();
// for (const word of wordArray) {
// 	try {
// 		const lemmatizedForm = lemmatizer(word);
// 		rootWords.add(lemmatizedForm);
// 	} catch (error) {}
// }
// console.log(`Initial word list length: ${wordArray.length}`);
// console.log(`Root word list length: ${rootWords.size}`);
//
// const filteredWords = Array.from(rootWords).filter((word) => {
// 	const lowerCaseWord = word.toLowerCase();
//
// 	if (!/^[a-z]+$/.test(lowerCaseWord)) {
// 		return false;
// 	}
// 	if (lowerCaseWord.includes(" ")) {
// 		return false;
// 	}
//
// 	if (excludedWordsSet.has(lowerCaseWord)) {
// 		return false;
// 	}
// 	if (profanity.exists(lowerCaseWord)) {
// 		return false;
// 	}
// 	if (stopwordsEngSet.has(lowerCaseWord)) {
// 		return false;
// 	}
// 	if (nounsSet.has(lowerCaseWord)) {
// 		return false;
// 	}
// 	if (countryNamesSet.has(lowerCaseWord)) {
// 		return false;
// 	}
// 	if (languageNamesSet.has(lowerCaseWord)) {
// 		return false;
// 	}
//
// 	return true;
// });
//
// console.log(`Filtered word list length: ${filteredWords.length}`);
//
// // for (const word of filteredWords) {
// // 	try {
// // 		const lemmatizedForm = lemmatizer(word);
// // 		rootWords.add(lemmatizedForm);
// // 	} catch (error) {}
// // }
// // console.log(`Root word list length: ${rootWords.size}`);
// //
// // const rootWordsJson = JSON.stringify(Array.from(rootWords));
// // fs.writeFileSync("./src/data/wordList.json", JSON.stringify(filteredWords));
