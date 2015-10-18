#import this for parsing the Dictionary.xml file
import xml.etree.ElementTree as ET
tree = ET.parse('Dictionary.xml')
root = tree.getroot()


#import word net
import nltk
from nltk.corpus import wordnet as wn


#to download python stemming package, type this in command line:
#pip install stemming
from stemming.porter2 import stem
#run with stem(word)

VERB_WEIGHT = 1
NOUN_WEIGHT = 1
PREPOSITION_WEIGHT = 1
ADJECTIVE_WEIGHT = 1
OTHER_WEIGHT = 1

#sample sentence -- delete later
sentence = "this is activate oops add appear after now"

#uses Dictionary.xml to return all senses of the word
#returns a dictionary of senses with key: id number of the sense
#and value: the glossary definition of the word
#dictionaries are empty if the word is not in the dictionary
def get_dict_senses(word):
	sense_dict = {}
	item = {}
	for child in root:
		name = child.get('item')
		#name to the last -2 to not look for the pos
		if name[:len(name)-2] == word:
			item = child.attrib
			for sense in child.iter("sense"):
				current_sense = sense.attrib
				sense_key = current_sense["id"]
				sense_value = current_sense["gloss"]
				sense_dict[sense_key] = sense_value
	#can return the item later too if needed. ("word.pos")
	return (sense_dict)

#calculates the best sense of the target word compared to one other context word
#returns the id of the best sense of the target word and best sense of the context word as well as the score
def best_sense(target_word, context_word):
	score = 0
	#incase the word is not in the dictionary add here
	best_target_sense = "null"
	best_context_sense = "null"
	
	for target_sense, target_definitions in get_dict_senses(target_word).iteritems():
		target_word_set = target_definitions.split(" ")
		for context_sense, context_definitions in get_dict_senses(context_word).iteritems():
			context_word_set = context_definitions.split(" ")
			similar_words =  set(target_word_set).intersection(context_word_set)
			overlap = len(similar_words)
			if overlap >= score:
				best_target_sense = target_sense
				best_context_sense = context_sense
				score = overlap
	return (best_target_sense, best_context_sense, score)

#best_sense("add", "activate")

#Takes a word and the sentence and returns the id number of the highest senses of the context words
#and target words for N words in front of and behind the word
def best_sense_entire_context(word,sentence,N):
	sentence_array = sentence.split(" ")
	target_index = sentence_array.index(word)
	context_words = sentence_array[target_index - N: target_index + 1 + N]
	#remove the target word from the context word set
	context_words.remove(word)

	for each_word in context_words:
		return best_sense(word, each_word)

#test
#best_sense_entire_context("add", sentence, 1)

#returns the wordnet definitions of all of the synonyms of the sense
def get_wordnet(word):
	word_net_dict = {}
	for each_word in wn.synsets(word):
		word_net_dict[each_word] = each_word.definition()
	return word_net_dict



#Yo Molly-- I didn't implement score_matching_words() quite the way you wrote here because I don't think
#that we need to keep track of the number of overlaps for each one, we just need to remember the one with the
#most overlaps. But I could be wrong so I left the function in here. It will be easier to calculate with
#what I did do though either way :)

#Takes a word and the sentence it is in and counts the number of similar words in each
#of the word's different senses, in N words in front of and behind the word
#Returns an array/ dictionary for each word sense's score
def score_matching_words(word,sentence,N):
	pass

#Takes a word and a sentence and returns a dictionary of each word N words away in either direction
#and their weight depending on their part of speech
#Will be used in scoring later to give word matches more or less points based on their part
#of speech
def part_of_speech_tagging(word,sentence,N):

	pass



#Using Wordnet's semenatic similarity program (thanks wikipedia) compares the similarity
#between the words and other words N away from this word in the sentence
def semantic_similarity(word,sentence,N):
	pass



#In the problem set it said if we use wordnet we might have to find a way to fit its definitions
#with the ones given in the class dictionary, so this is a function we'll have to do later
#to match them
def wordnet_to_class_dictionary(class_defs,wordnet_defs,word):
	pass


