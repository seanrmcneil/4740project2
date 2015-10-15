#Molly and Sean words disambiguation

VERB_WEIGHT = 1
NOUN_WEIGHT = 1
PREPOSITION_WEIGHT = 1
ADJECTIVE_WEIGHT = 1
OTHER_WEIGHT = 1


#Takes a word and the sentence it is in and counts the number of similar words in each
#of the word's different senses, in N words in front of and behind the word
#Returns an array/ dictionary for each word sense's score
def score_matching_words(word,sentence,N):
	pass



#Takes a word and a sentence and returns a dictionary of each word N words away in either direction
#and their weight depending on their part of speecy
#Will be used in scoring later to give word matches more or less points based on their part
#of speech
def part_of_speech_tagging(word,sentence,N):
	pass



#Stems each word N words away from the given word in the sentence and checks for matches
def stemming(word,sentence,N):
	pass



#Using Wordnet's semenatic similarity program (thanks wikipedia) compares the similarity
#between the words and other words N away from thsi word in the sentence
def semantic_similarity(word,sentence,N):
	pass



#In the problem set it said if we use wordnet we might have to find a way to fit its definitions
#with the ones given in the class dictionary, so this is a function we'll have to do later
#to match them
def wordnet_to_class_dictionary(class_defs,wordnet_defs,word):
	pass

