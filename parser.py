import xml.etree.ElementTree as ET
tree = ET.parse('Dictionary.xml')
root = tree.getroot()


#access dictionary to return the different sense of the word
#take in the word you are trying to find in the dictionary and the Dictionary.xml file
#returns 2 dicstionaries, the first is simply {'item' : 'word.pos'}
#the 2nd dicitonary is of the id number of the sense as key, and the glossary definition as the value
#dictionaries are empty if the word is not in the dictionary
def access_dictionary(word):
	sense_dict = {}
	item = {}
	for child in root:
		name = child.get('item')
		if name[:len(name)-2] == word:
			item = child.attrib
			for sense in child.iter("sense"):
				current_sense = sense.attrib
				sense_key = current_sense["id"]
				sense_value = current_sense["gloss"]
				sense_dict[sense_key] = sense_value
	return (item, sense_dict)

