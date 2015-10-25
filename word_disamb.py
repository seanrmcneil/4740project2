#import this for parsing the Dictionary.xml file
import xml.etree.ElementTree as ET
tree = ET.parse('Dictionary.xml')
root = tree.getroot()

tree2 = ET.parse('test-data.data')
root2 = tree2.getroot()


tree3 = ET.parse('training-data.data')
root3 = tree3.getroot()

from collections import Counter
from nltk.corpus import wordnet as wn
#to download python stemming package, type this in command line:
#pip install stemming
from stemming.porter2 import stem
#pip install ordereddict
import collections
from ordereddict import OrderedDict

import random
#for testing purposes
from itertools import islice
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


VERB_WEIGHT = 1
NOUN_WEIGHT = 1
PREPOSITION_WEIGHT = 1
ADJECTIVE_WEIGHT = 1
OTHER_WEIGHT = 1

WORDNET_OR_NOT = {}
#sample sentence -- delete later

#uses Dictionary.xml to return all senses of the word returns a dictionary of senses with key: id number of the sense
#and value: the glossary definition of the word dictionaries are empty if the word is not in the dictionary
def get_dict_senses(word):
	sense_dict = {}
	item = {}
	final_name = ""
	for child in root:
		name = child.get('item')
		#name to the last -2 to not look for the pos
		if name == word:
			item = child.attrib
			final_name += name #Need this for writing to file
			for sense in child.iter("sense"):
				current_sense = sense.attrib
				sense_key = current_sense["id"]
				sense_value = current_sense["gloss"]
				sense_dict[sense_key] = sense_value
				WORDNET_OR_NOT[name] = current_sense['source']
	#can return the item later too if needed. ("word.pos")
	return sense_dict

def get_test_data():
	test_data = collections.OrderedDict()
	for child in root2:
		for sense in child:
			id = sense.attrib['id']
			name = id.split(".")[0]
			full_context = ""
			for context in sense.iter('context'):
				for head in context:
					head.text = name

			for context in sense.itertext():
				full_context = full_context + context
			test_data[id] = full_context

	return test_data



def get_training_data():
	training_data = collections.OrderedDict()
	for child in root3:
		for sense in child:
			id = sense.attrib['id']
			name = id.split(".")[0]
			full_context = ""
			for items in sense.iter('context'):
				for head in items:
					head.text = name
					head.set('updated','yes')
				for context in items.itertext():
					full_context = full_context + context

			training_data[id] = full_context

	return training_data




#returns the wordnet definitions of all of the synonyms of the sense
def get_wordnet(word):
	word_net_dict = {}
	for each_word in wn.synsets(word):

		word_net_dict[each_word] = each_word.definition()
	return word_net_dict

def wordnet_to_reg(target_dictionary,context_definition):
	context_word_set = context_definition.split(" ")
	best_def = {}
	for target_sense, target_definitions in target_dictionary.iteritems():
		target_word_set = target_definitions.split(" ")
		similar_words =  set(target_word_set).intersection(context_word_set)
		overlap = len(similar_words)
		best_def[target_sense] = overlap
	high_score = 0
	for item in best_def:
		if best_def[item] >= high_score:
			top_score = best_def[item] 
	finals = []
	for item in best_def:
		if best_def[item] == top_score:
			finals.append(item)
	return finals




#calculates the best sense of the target word compared to one other context word
#returns the id of the best sense of the target word and best sense of the context word as well as the score
def best_sense(target_word, context_word,target_dictionary):
	context_dictionary = get_wordnet(context_word)
	score = 0
	best_target_sense = {}
	best_context_sense = {}
	for target_sense, target_definitions in target_dictionary.iteritems():
		target_word_set = target_definitions.split(" ")
		target_word_set = [stem(x).lower() for x in target_word_set]
		for context_sense, context_definitions in context_dictionary.iteritems():
			context_word_set = context_definitions.split(" ")
			context_word_set = [stem(x).lower() for x in context_word_set]
			similar_words =  set(target_word_set).intersection(context_word_set)
			overlap = len(similar_words)
			consecutive_overlap = 0
			if overlap >= 2:
				for i in similar_words:
					target_index = target_word_set.index(i)
					context_index = context_word_set.index(i)
					if target_index < len(target_word_set)-1 and context_index < len(context_word_set)-1:
						if target_word_set[target_index+1] == context_word_set[context_index+1]:
							consecutive_overlap = consecutive_overlap +1
			temp_score = float(overlap + consecutive_overlap)/float(len(target_word))
			best_target_sense[target_sense] = temp_score
			new_number = 0
			new_number = semantic_similarity(target_sense,context_sense)
			best_target_sense[target_sense] += new_number
#	if best_target_sense == {}:
#		print target_word
#		print context_word
	return best_target_sense


#Using Wordnet's semenatic similarity program compares the similarity
#between two definitions
#For each word sense, match the semantic similarity of the definitions (aka call this on each word)
def semantic_similarity(word1, word2):
	total= 0
	nums = []
	nums.append(word1.path_similarity(word1))
			#nums.append(word1.lch_similarity(word2))
	nums.append(word1.wup_similarity(word2))
			#nums.append(word1.res_similarity(word2))
		#	nums.append(word1.lin_similarity(word2))
		#	nums.append(word1.jcn_similarity(word2))
	for item in nums:
		if item == None:
			pass
		else:
			total += item
	return total

#Takes a word and the sentence and returns the id number of the highest senses of the context words
#and target words for N words in front of and behind the word
def best_sense_entire_context(final_word,sentence,target_dictionary, N):
	context_1 = get_wordnet(final_word.partition(".")[0])
	sentence_array = sentence.split(" ")
	while "," in sentence_array:
		sentence_array.remove(",")
	while "-" in sentence_array:
		sentence_array.remove("-")
	while "." in sentence_array:
		sentence_array.remove(".")
	while " " in sentence_array:
		sentence_array.remove(" ")
	while "" in sentence_array:
		sentence_array.remove("")
	while "and" in sentence_array:
		sentence_array.remove("and")
	while "of" in sentence_array:
		sentence_array.remove("of")
	while "a" in sentence_array:
		sentence_array.remove("a")
	while "it" in sentence_array:
		sentence_array.remove("it")
	for word in sentence_array:
		if not get_dict_senses(word + ".v") and not get_dict_senses(word + ".n") and not get_dict_senses(word + ".a"):
			while word in sentence_array:
				sentence_array.remove(word)
	scoring = {}
	i = sentence_array.index(final_word.partition(".")[0])
	for index,each_word in enumerate(sentence_array):
		if i - N < index  and i + N > index: #If it is in between the two	
			best = best_sense(final_word, each_word,target_dictionary);
			temp_scoring = Counter(best)
			scoring = temp_scoring + Counter(scoring)
	if scoring == {}:
		print "SCORING IS 0"
		print final_word
		print sentence
	


	return scoring


if __name__ == '__main__':
	#data = get_test_data()
	data = get_training_data()
	f=open('output_file11.txt','w')
	f.write("Id,Prediction\n")
	for word in data:
		wordy = word.partition(".")
		word2 = wordy[2].partition(".")
		final_word = wordy[0] + "." + word2[0]
		target_dictionary = get_wordnet(wordy[0])
		scoring = {}
		sense =best_sense_entire_context(final_word, data[word], target_dictionary, 1) #Can change N here
		for item in sense:
			if item in scoring:
				scoring[item] = scoring[item] + sense[item]
			else:
				scoring[item] = sense[item]
		top_score = -1
		finals = []
		for item in scoring:
			if scoring[item] >= top_score:
				top_score = scoring[item] 
		for item in scoring:
			if scoring[item] == top_score:
				finals.append(item)
		top_matches = ""
		from_wordnet = []
		for item in finals:
			from_wordnet = from_wordnet + wordnet_to_reg(get_dict_senses(final_word), target_dictionary[item])
		if len(from_wordnet) > 1:
			top_matches += random.choice(from_wordnet)
		else:
			top_matches += from_wordnet[0]
		final_name = word + "," + top_matches + "\n"
		f.write(final_name)
	f.close()
	print "done"
