#import this for parsing the Dictionary.xml file
import xml.etree.ElementTree as ET
tree = ET.parse('Dictionary_wordnet.xml')
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
# import collections
# from ordereddict import OrderedDict

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
	#can return the item later too if needed. ("word.pos")
	return sense_dict

def get_test_data():
	test_dict = {}
	for child in root2:
		name = child.get('item')
		for word in child.iter('instance'):
			current = word.attrib
			id1= current['id']
			sentences = word[0].text
			split = sentences.split(".")
			test_dict[id1] = split;
	n_items = take(11, test_dict.iterkeys())
	#print n_items
	return test_dict


#returns the wordnet definitions of all of the synonyms of the sense
def get_wordnet(word):
	word_net_dict = {}
	for each_word in wn.synsets(word):

		word_net_dict[each_word] = each_word.definition()
	return word_net_dict


#calculates the best sense of the target word compared to one other context word
#returns the id of the best sense of the target word and best sense of the context word as well as the score
def best_sense(target_word, context_word,target_dictionary):
	context_dictionary = get_dict_senses(context_word)
	if not context_dictionary:
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

	return best_target_sense


#Using Wordnet's semenatic similarity program compares the similarity
#between two definitions
#For each word sense, match the semantic similarity of the definitions (aka call this on each word)
def semantic_similarity(word1_context_set, word2_context_set):
	total= 0
	for word1 in word1_context_set:
		for word2 in word2_context_set:
			nums = []
			nums.append(word1.path_similarity(word2))
			nums.append(word1.lch_similarity(word2))
			nums.append(word1.wup_similarity(word2))
			nums.append(word1.res_similarity(word2))
			nums.append(word1.lin_similarity(word2))
			nums.append(word1.jcn_similarity(word2))
			for item in nums:
				if item == None:
					pass
				else:
					total += item
	return total

#Takes a word and the sentence and returns the id number of the highest senses of the context words
#and target words for N words in front of and behind the word
def best_sense_entire_context(final_word,sentence,target_dictionary, N):
	sentence_array = sentence.split(" ")
	scoring = {}
	#i = sentence.index("<head>")
	for index,each_word in enumerate(sentence_array):
	#	if i - N < index  ||
		best = best_sense(final_word, each_word,target_dictionary);
		temp_scoring = Counter(best)
		scoring = temp_scoring + Counter(scoring)
	return scoring


if __name__ == '__main__':
	data = get_test_data()
	f=open('output_file5','w')
	f.write("Id,Prediction\n")
	for word in data:
		wordy = word.partition(".")
		word2 = wordy[2].partition(".")
		final_word = wordy[0] + "." + word2[0]
		target_dictionary = get_dict_senses(final_word)
		if not target_dictionary:
			target_dictionary = get_wordnet(target_word)
		scoring = {}
		for sentence in data[word]:
			sense =best_sense_entire_context(final_word, sentence, target_dictionary, 2) #Can change N here
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
		for index, val in enumerate(finals):
			top_matches += val + " "
		final_name = word + "," + top_matches + "\n"
		f.write(final_name)
	f.close()
