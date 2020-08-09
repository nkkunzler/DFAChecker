def main():
	print("Mode Types\n")
	print("0 -> Create DFA")
	print("1 -> Run DFA")
	print("2 -> DFA Union")
	mode = int(input("\nEnter Mode: "))

	if mode == 0: # Create DFA
		createDFA()
	elif mode == 1: # Load/Validate DFA
		results = loadDFA("DFA File Name: ")
		# return (fileName, states, alphabet, stateMap, startState)
		validateWords(results[3], results[4], results[0])
	elif mode == 2: # Union DFA
		unionDFA()

def unionDFA():
	# return (fileName, states, alphabet, stateMap, startState)
	m1 = loadDFA("DFA 1 File Name: ")
	m2 = loadDFA("DFA 2 File Name: ")

	fileName = m1[0] + "_" + m2[0] + "_union"
	f = open(fileName, "w+")

	if m1[2] != m2[2]:
		print("Unequal alphabets not able to Union")
		exit(1)
	
	alphabetStr = m1[2]
	alphabet = alphabetStr.split(":")

	m1StateMap = m1[3]
	m1StartState = m1StateMap[m1[4]]

	m2StateMap = m2[3]
	m2StartState = m2StateMap[m2[4]]

	unionStateMap = {}
	startState = (m1[4], m2[4])
	acceptStates = ""

	# Creating the new states
	unionKeys = []	
	for m1State in m1[1]:
		for m2State in m2[1]:		
			isAccept = False
			if m1StateMap[m1State].isAccept() or m2StateMap[m2State].isAccept():
				isAccept = True
				acceptStates += str((m1State, m2State)) + ":"
			unionKeys.append((m1State, m2State))
			unionStateMap.update({(m1State, m2State):State(str((m1State, m2State)), isAccept)})
	

	# Getting all the states after the union operation
	DFAStates = ""
	for key in unionKeys:
		DFAStates += str(key) + ":"
	DFAStates = DFAStates.strip(":")

	f.write(DFAStates + "\n")
	f.write(alphabetStr + "\n")

	# Creating a new stateMap to represent the union of DFA 1 and DFA 2
	m1CurrState, m2CurrState = m1StartState, m2StartState
	for key in unionKeys: # key is tuple of (m1State, m2State)
		f.write(str(key) + "\n")
		for char in alphabet:
			m1NewState = m1StateMap[key[0]].getState(char)
			m2NewState = m2StateMap[key[1]].getState(char)
			unionStateMap[key].addTransition(char, (m1NewState, m2NewState))
			f.write(char + ":" + str((m1NewState, m2NewState)) + "\n")
		f.write("-\n")
	
	f.write("\n" + str(startState) + "\n")
	f.write(acceptStates.strip(":") + "\n")

	f.write("\n\n##### Everything Below Not Included #####\n\n")
	f.write(strTransitionFunction(unionStateMap, unionKeys, alphabet) + "\n")

	# Simplify the DFA
	simplifyDFA(unionStateMap, unionKeys, startState, alphabet,f)

	f.close()

	print("DFA Saved As: " + fileName)

'''
Simplify DFA by removing unreachable states
'''
def simplifyDFA(stateMap, states, startState, alphabet, f):
	statesSeen = []
	simplifyDFAHelper(stateMap, stateMap[startState], alphabet, statesSeen)

	simplifiedStateMap = {}
	newStates = []
	for state in states:
		if str(state) in statesSeen:
			newStates.append(state)
			simplifiedStateMap.update({state : stateMap[state]})
	f.write("\n ---- Simplified DFA ---- \n")
	f.write(strTransitionFunction(simplifiedStateMap, newStates, alphabet))		
def simplifyDFAHelper(stateMap, currState, alphabet, statesSeen):
	if currState.getName() in statesSeen:
		return

	statesSeen.append(currState.getName())
	for char in alphabet:
		simplifyDFAHelper(stateMap, stateMap[currState.getState(char)], alphabet, statesSeen)
		

'''
ALL CODE BELOW IS DEALING WITH LOADING A DFA
'''

'''
Loads all information needed to represent a DFA from a 
file
'''
def loadDFA(prompt):
	fileName = input("\n" + prompt)
	f = open(fileName, "r")

	states = f.readline().strip("\n\r").split(":")		
	alphabetStr = f.readline().strip("\n\r")
	alphabet = alphabetStr.split(":")
	stateMap = {}
	
	while True:
		line = f.readline().strip("\n\r")
		if not line:
			break
		stateName = line
		stateObj = State(stateName, False)
		stateMap.update({stateName:stateObj})

		while True:
			transition = f.readline().strip("\n\r")
			if "-" in transition:
				break
			transitionList = transition.split(":")
			stateObj.addTransition(transitionList[0], transitionList[1])

	startState = f.readline().strip("\n\r")
	acceptStates = f.readline().strip("\n\r").split(":")
	for state in acceptStates:
		stateMap[state].updateAccept(True)
	f.close()

	return (fileName, states, alphabetStr, stateMap, startState)


'''
Reads a file of words and checks if they are valid or not based
off of a given DFA
'''
def validateWords(stateMap, startState, DFAFileName):
	fileName = input("Word File: ")
	wordFile = open(fileName, "r")

	resultFile = open(DFAFileName + "_" + fileName + "_result", "w+")

	for line in wordFile.readlines():
		word = line.strip("\n\r")
		if not word:
			resultFile.write("\": ")
		else:
			resultFile.write(word + ": ")
		if validWord(startState, stateMap, word):
			resultFile.write("\n")
		else:
			resultFile.write("X\n")
	print("Results Saved As: " + DFAFileName + "_" + fileName + "_result") 
	wordFile.close()
	resultFile.close()


'''
Returns whether a given word is valid for the given DFA
'''
def validWord(startState, stateMap, word):
	state = stateMap[startState]
	for transition in word:
		state = stateMap[state.getState(str(transition))]
	return state.isAccept()


'''
EVERYTHING BELOW IS TO CREATE DFA FILE
'''

'''
Creates a DFA
'''
def createDFA():
	fileName = input("\nSave File Name: ")
	
	f = open(fileName, "w+")

	print()

	states = getStates(f)
	alphabet = getAlphabet(f)
	stateMap = getTransitionFunction(f, states, alphabet)
	getStartState(f)
	getAcceptStates(stateMap, f)

	# Everything following #### is comments and not included
	f.write("\n\n########## Everything Below Not Included ##########\n\n")
	f.write(strTransitionFunction(stateMap, states, alphabet)+"\n")
	f.close()

	print("DFA Saved As: " + fileName)

'''
Prompts for all states in DFA
'''
def getStates(f):
	stateStr = input("Q (States): ")
	stateStr = stateStr.replace(",",":")
	f.write(stateStr + "\n")	
	return stateStr.split(":")

'''
Prompts for DFA alphabet
'''
def getAlphabet(f):
	alphabetStr = input("E (Alphabet): ")
	alphabetStr = alphabetStr.replace(",", ":")
	f.write(alphabetStr + "\n")
	return alphabetStr.split(":")

'''
Prompts and creates transition function
'''
def getTransitionFunction(f, states, alphabet):
	stateMap = {}
	print("& (Transition Function): ")
	for stateStr in states:
		print("\nState: " + stateStr)
		f.write(stateStr + "\n")
		stateObj = State(stateStr, False)
		stateMap[stateStr] = stateObj

		for alphabetChar in alphabet:
			toState = input(alphabetChar + " -> ")
			stateObj.addTransition(alphabetChar, toState)
			f.write(alphabetChar + ":" + toState + "\n")
		f.write("-\n")
	f.write("\n")
	return stateMap

'''
Creates a string representation of the transition function
for easy reading
'''
def strTransitionFunction(stateMap, states, alphabet):
	spaceLen = len(str(states[0])) + 1
	out = " " * int(spaceLen * 1.5)
	for char in alphabet:
		out += char + (" " * (spaceLen // 2)) + " |" + (" " * (spaceLen // 2))
	out += "\n" + " " * spaceLen + ("-" * (spaceLen + 2) * len(alphabet)) + "\n"

	for state in states:
		out += str(state) + " | " + stateMap[state].toString(alphabet) 
		if stateMap[state].isAccept():
			out += " -> Accept State"
		out += "\n"
	return out

'''
Prompts for the start state
'''
def getStartState(f):
	startState = input("\nq0 (Start State): ")
	f.write(startState + "\n")

'''
Prompts for all the accept states
'''
def getAcceptStates(stateMap, f):
	acceptStateStr = input("F (Accept States): ")
	acceptState = acceptStateStr.replace(",",":").split(":")
	for accept in acceptState:
		stateMap[accept].updateAccept(True)
	f.write(acceptStateStr.replace(",",":") + "\n")

'''
Class that represents a State within a DFA
'''
class State:
	
	def __init__(self, name, accept):
		self.name = name
		self.accept = accept
		self.transitionDict = {}
	
	def addTransition(self, transition, toState):
		if transition not in self.transitionDict:
			self.transitionDict.update({transition : toState})
	
	def updateAccept(self, accept):
		self.accept = accept	

	def isAccept(self):
		return self.accept

	def getName(self):
		return self.name
	
	def getState(self, transition):
		return self.transitionDict[transition]
	
	def toString(self, alphabet):
		out = ""
		for strChar in alphabet:
			if strChar not in self.transitionDict:
				out += "- |"
			else:
				out += str(self.transitionDict[strChar]) + " | "
		return out

main()
