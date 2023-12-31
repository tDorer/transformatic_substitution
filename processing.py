import numpy as np
import random
import matplotlib.pyplot as plt

# Sorting algorithm
def create_next_permutation(perm):
    return perm[np.array([5,0,1,2,3,4])]
def reverse_permutation(perm):
    return perm[np.array([5,4,3,2,1,0])]
def calc_score(perm):
    group_scores = {"OH": 7, "NH2": 6, "C": 5, "Ha": 4, "F": 3, "CO": 2, "NO2": 1, "H": 0}
    score = 0
    for fact,group in enumerate(perm):
        score += group_scores[group]*(10**(5-fact))
    return score
def order(perm):
    perm = np.array(perm)
    permutations = [perm, reverse_permutation(perm)]
    scores = [calc_score(perm), calc_score(reverse_permutation(perm))]
    for i in range(5):
        perm = create_next_permutation(perm)
        permutations.append(perm)
        scores.append(calc_score(perm))
        rev_perm = reverse_permutation(perm)
        permutations.append(rev_perm)
        scores.append(calc_score(rev_perm))
    return permutations[np.argmax(scores)]


# Create random compound
def create_compound(substituents):
    groups = ["OH", "NH2", "C", "Ha", "F", "CO", "NO2"]
    indices = [0,1,2,3,4,5]
    index = random.sample(indices,substituents)
    group = random.sample(groups,substituents)
    compound = ["H", "H", "H", "H", "H", "H"]
    for i in range(substituents):
        compound[index[i]] = group[i]
    compound = order(compound)
    compound_str = ""
    for i in compound:
        compound_str += i
        compound_str += "."
    return compound_str[:-1]

#Create tokens for the encoder
def comp_tokenizer(compound):
    tokenization = {"H": 0, "OH": 1, "NH2": 2, "C": 3, "Ha": 4, "F": 5, "CO": 6, "NO2": 7}
    tokens = []
    compound = compound.split(".")
    for group in compound:
        tokens.append(tokenization[group])
    return tokens

# Create tokens for the decoder
def synth_tokenizer(steps, reagents):
    tokenization = {"": 0, "<start>": 1, "<end>": 2, "SENO2": 3, "RENH2": 4, "SEHa": 5, "REC": 6, "SNF": 7, "SAF": 8, "SNOH": 9, "SAHa": 10, "SAOH": 11, "OXNO2": 12, "SECO": 13, "REB": 14, "PO": 15, "UP": 16, "OXB": 17}
    input_steps = np.array([1,0,0,0,0,0,0,0,0])
    target_steps = np.zeros(9)
    synthesis = []
    steps = steps.split(".")
    reagents = reagents.split(".")
    for step,reagent in zip(steps,reagents):
        synthesis.append(step + reagent)
    progressing = True
    for i in range(len(synthesis)):
        input_steps[i+1] = tokenization[synthesis[i]]
        if progressing and synthesis[i] == "":
            progressing = False
            target_steps[i] = 2
        else:
            target_steps[i] = tokenization[synthesis[i]]
    if progressing:
        target_steps[8] = 2
    return input_steps, target_steps

# This is old code, it only uses steps, not the introduced groups
# def steps_tokenizer(steps):
#     tokenization = {"": 0, "<start>": 1, "<end>": 2, "SE": 3, "RE": 4, "SN": 5, "SA": 6, "OX": 7, "PO": 8, "UP": 9}
#     input_steps = np.array([1,0,0,0,0,0,0,0,0])
#     target_steps = np.zeros(9)
#     steps = steps.split(".")
#     progressing = True
#     for i in range(len(steps)):
#         input_steps[i+1] = tokenization[steps[i]]
#         if progressing and steps[i] == "":
#             progressing = False
#             target_steps[i] = 2
#         else:
#             target_steps[i] = tokenization[steps[i]]
#     if progressing:
#         target_steps[8] = 2
#     return input_steps, target_steps


# This function simply plots cross attention heads
def plot_attention_head(attention, in_tokens, translated_tokens=0):
    if in_tokens[0] == "<start>":
        in_tokens = in_tokens[1:]
    if translated_tokens == 0:
        translated_tokens = in_tokens
    elif translated_tokens[0] == "<start>":
        translated_tokens = translated_tokens[1:]
    fig,ax = plt.subplots(1,1, figsize=(10,10), dpi=160)
    ax = plt.gca()
    ax.matshow(attention)
    ax.set_xticks(range(len(in_tokens)))
    ax.set_yticks(range(len(translated_tokens)))

    labels = in_tokens
    ax.set_xticklabels(
        labels, rotation=90)

    labels = translated_tokens
    ax.set_yticklabels(labels)

#------------------------------------------------------------------------------------------------------------------------------------------------
# The following was used to create the database and creates random compound then checks whether they occur in the database and if not asks for the synthesis.

# Ask synthesis
def ask_synthesis(compound):
    print(f"Please enter the best synthesis strategy for the compound\n------------------------\n{compound}.\n------------------------\n")#Keywords for reactions:\nSE: electrophilic aromatic substitution\nSN: nucleophilic aromatic subsitution\nPO: protection of amine\nUP: unprotection of amine\nOX: oxidasation\nRE: reduction\nSA: diazotation with introduction of group (Sandmeyer's reaction)\nIf you don't know the synthesis, you could just hit \"end\" right at the beginning, empty sequences will not be saved.")
    sequence = []
    reactants = []
    for step in range(18):
        sequence.append(input("Which reaction is next? Please enter one of the keywords or \"end\"\n"))
        if sequence[-1] in ["SE", "SN", "SA", "RE", "OX"]:
            reactants.append(input("Which group do you want to create?\n"))
        else:
            reactants.append("")
        if sequence[-1] == "end":
            sequence[-1] = ""
            for i in range(18-step):
                sequence.append("")
                reactants.append("")
            break
    sequence_str = ""
    reactants_str = ""
    for i in range(18):
        sequence_str = sequence_str + sequence[i] + "."
        reactants_str = reactants_str + reactants[i] + "."
    return sequence_str[:-1], reactants_str[:-1]

# data = np.genfromtxt("data.csv", delimiter=',', dtype=str)
# # print(data[:5])
# cont = "yes"
# substituents = int(input("Compunds with how many substituents do you want to add?\nPlease enter 2 or 3.\n"))
# while cont!="no":
#     for i in range(100):
#         compound = create_compound(substituents)
#         if compound not in data[:,1]:
#             test = "no"
#             while test=="no":
#                 sequence, reactants = ask_synthesis(compound)
#                 test = input(f"To synthesise {compound} you propose the strategy {sequence} with the used reactants {reactants}.\nIs that correct? Please enter \"no\" if you want to repeat.")            
#             if sequence != ".................":
#                 data = np.vstack((data, np.array([str(int(data[-1,0])+1),compound, sequence, reactants])))
#                 print("Synthesis succesfully added.")
#                 break
#             else:
#                 print("No synthesis added.")
#                 break
#     cont = input("Do you want to try another one?\nEnter \"no\" if you want to stop.")
# np.savetxt("data.csv", data, delimiter=',', fmt='%s')
