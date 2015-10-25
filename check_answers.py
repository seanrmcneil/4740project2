#import this for parsing the Dictionary.xml file
import xml.etree.ElementTree as ET

tree3 = ET.parse('training-data.data')
root3 = tree3.getroot()

def get_training_answers():
	answers = ["Id,Prediction"]
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
		correct = 0
		answers = get_training_answers()

		line1 = []
		for line in f:
			line1.append(line)

		for i in xrange(0, len(answers)):
			if answers[i] in line1[i]:
				correct = correct +1

		print correct
		print float(correct)/float(len(answers))


compare_answers("output_file11.txt")