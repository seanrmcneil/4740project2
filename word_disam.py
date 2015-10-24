#import this for parsing the Dictionary.xml file
import xml.etree.ElementTree as ET
tree = ET.parse('Dictionary.xml')
root = tree.getroot()

tree2 = ET.parse('test-data.data')
root2 = tree2.getroot()

tree3 = ET.parse('training-data.data')
training_root = tree3.getroot()

from collections import Counter
from nltk.corpus import wordnet as wn
#to download python stemming package, type this in command line:
#pip install stemming
from stemming.porter2 import stem
#pip install ordereddict
import collections
from ordereddict import OrderedDict

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
sentence = "this is activate running add appear after now"

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
	return [final_name,sense_dict]

def get_test_data2():
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
	for child in training_root:
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



def get_test_data():
	test_dict = collections.OrderedDict()
	for child in root2:
		name = child.get('item')
		for word in child.iter('instance'):
			current = word.attrib
			id1= current['id']
			sentences = word[0].text
			split = sentences.split(".")
			test_dict[id1] = split;
	#n_items = take(11, test_dict.iterkeys())
	#print n_items
	return test_dict



#returns the wordnet definitions of all of the synonyms of the sense
def get_wordnet(word):
	word_net_dict = {}
	for each_word in wn.synsets(word):

		word_net_dict[each_word] = each_word.definition()
	return word_net_dict

#test
#get_wordnet("running")


#Total score: (Number of overlaps in stememd definitions) + (Weighted score for each overlap based on part of speech) + (Similarity of words in 
	#definition using wordnet's similarity function)

#calculates the best sense of the target word compared to one other context word
#returns the id of the best sense of the target word and best sense of the context word as well as the score
def best_sense(target_word, context_word):
	score = 0
	#incase the word is not in the dictionary add here
	best_target_sense = {}
	best_context_sense = {}
	name = ""
	#get the sense of the words from Dictioonary.xml
	targ = get_dict_senses(target_word)
	target_dictionary = targ[1]
	context_dictionary = get_dict_senses(context_word)[1]
	#if the word is not in Dictionary.xml, get it from Wordnet
	if not target_dictionary:
		target_dictionary = get_wordnet(target_word)
		name += target_word
	else:
		name += targ[0]
	if not context_dictionary:
		context_dictionary = get_wordnet(context_word)
	#for each of the definitions of senses, split to array and compare words to each of the definitions of sense
	# of the context word
	for target_sense, target_definitions in target_dictionary.iteritems():
		target_word_set = target_definitions.split(" ")
		target_word_set = [stem(x).lower() for x in target_word_set]
		for context_sense, context_definitions in context_dictionary.iteritems():
			#CHECKS FOR OVERLAPS IN THE TWO DEFINITIONS GIVEN THE STEMMED DEFINITIONS
			context_word_set = context_definitions.split(" ")
			context_word_set = [stem(x).lower() for x in context_word_set]
			similar_words =  set(target_word_set).intersection(context_word_set)
			overlap = len(similar_words)

			#FOR EACH WORD IN OVERLAP WANT TO GO THROUGH AND WEIGH DIFFERENTLY TO ADD TO SCORE


			#GO THROUGH AND CHECK SEMANTIC SIMILARITY OF ALL WORDS IN EACH DEFINITION
			#semantic_similarity(target_word_set,context_word_set)

			#if there is consecutive overlap, give additional weight to the score
			consecutive_overlap = 0
			if overlap >= 2:
				for i in similar_words:
					target_index = target_word_set.index(i)
					context_index = context_word_set.index(i)
					if target_index < len(target_word_set)-1 and context_index < len(context_word_set)-1:
						if target_word_set[target_index+1] == context_word_set[context_index+1]:
							consecutive_overlap = consecutive_overlap +1


			#We should divide the temporary score by the number of words in the definition
			#may want to change how much having a consecutive overlap is weighted
			temp_score = float(overlap + consecutive_overlap)/float(len(target_word))

			# if there are multiple best senses, add them to the array of best senses
			if temp_score == score:
				best_target_sense[target_sense] = temp_score
				best_context_sense[context_sense] = temp_score

			if temp_score > score:
				best_target_sense = {}
				best_context_sense = {}
				best_target_sense[target_sense] = temp_score
				best_context_sense[context_sense] = temp_score
				score = temp_score

	return (best_target_sense, best_context_sense,name,target_dictionary)


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

# def part_of_speech_weighting(word1_context_set):
# 	total =0
# 	for word1 in word1_context_set:
# 		x = word1.pos.nn 
# 		print x



#test
#print best_sense("add", "running")

#Takes a word and the sentence and returns the id number of the highest senses of the context words
#and target words for N words in front of and behind the word
def best_sense_entire_context(word,sentence, f):
	sentence_array = sentence.split(" ")
	# target_index = sentence_array.index(word)
	# context_words = sentence_array[target_index - N: target_index + 1 + N]
	# #remove the target word from the context word set
	# context_words = target_index
	# context_words.remove(word) #Want to later make sure we remove the specific incidence in case it comes up twice
	wordy = word.partition(".")
	word2 = wordy[2].partition(".")
	final_word = wordy[0] + "." + word2[0]
	scoring = {}

	for each_word in sentence_array:
		best = best_sense(final_word, each_word);
		temp_scoring = Counter(best[0])
		scoring = temp_scoring + Counter(scoring)
		name = best[2]
	if not scoring:
		targ = get_dict_senses(target_word)
		dicty = {}
		for item in targ:
			dicty[item] = 1
		return dicty
	else:
		return scoring


if __name__ == '__main__':
	data = get_test_data()
	f=open('output_file2','w')
	f.write("Id,Prediction\n")
	for word in data:

		scoring = {}
		short_word = word.partition(".")[0]
		for sentence in data[word]:
			if short_word in sentence:
				sense =best_sense_entire_context(word, sentence, f) #Can change N here
				for item in sense:
					if item in scoring:
						scoring[item] = scoring[item] + sense[item]
					else:
						scoring[item] = sense[item]
		top_score = 0
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
