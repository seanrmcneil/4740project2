#import this for parsing the Dictionary.xml file
import xml.etree.ElementTree as ET

tree3 = ET.parse('training-data.data')
root3 = tree3.getroot()

def get_training_answers():
	answers = []
	for child in root3:
		for sense in child:
			id = sense.attrib['id']
			name = id.split(".")[0]
			senseid = ""
			for items in sense.iter('answer'):
				senseid = str((items.attrib['senseid']))
			temp = str(id) + ',' + str(senseid)
			answers.append(temp)
	return answers

def compare_answers(output_file):
	with open(output_file) as f:
		count = 0
		correct = 0
		answers = get_training_answers()
		answers.append("")
		for line in f:
			if str(answers[count]) in str(line):
				correct = correct + 1
			count = count + 1

		print correct
		print len(answers)
		print correct/len(answers)

compare_answers("output_file11.txt")