import numpy as np
# import pandas as pd
import random
# import copy
import matplotlib.pyplot as plt
# import csv

ENABLE_PRINT = 0
DETAILED_ENABLE_PRINT=0
#convert the preference matrix into ranking matrix
def get_ranking(preference):
    ranking = np.zeros(preference.shape,dtype=int)
    for row in range(0,len(preference[:,0])):
        for col in range(0,len(preference[0,:])):
            ranking[row,col]=list(preference[row,:]).index(col)
    return ranking


def phaseI_reduction(preference, leftmost, rightmost, ranking):
    ## leftmost and rightmost is updated here
    set_proposed_to=set() ## this set contains the players who has been proposed to and holds someone
    for person in range(0,len((preference[0,:]))):
        proposer = person
        while True:
            next_choice = preference[proposer,leftmost[proposer]]
            current = preference[next_choice,rightmost[next_choice]]

            while ranking[next_choice,proposer]> ranking[next_choice,current]:
                ## proposer proposed to his next choice but being rejected
                if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("player", proposer+1, "proposed to", next_choice+1, "; ", next_choice+1, "rejects", proposer+1 )
                leftmost[proposer] = leftmost[proposer] + 1 ##proposer's preference list got reduced by 1 from the left
                next_choice = preference[proposer, leftmost[proposer]]
                current = preference[next_choice, rightmost[next_choice]]

            ## proposer being accepted by his next choice and next choice rejected his current partner
            if current!= next_choice: ##if next choice currently holds somebody
                if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("player", proposer + 1, "proposed to", next_choice + 1,"; ",next_choice + 1, "rejects", current + 1, " and holds", proposer+1 )
                leftmost[current]=leftmost[current]+1
            else: ##if next choice currently holds no body
                if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("player", proposer + 1, "proposed to", next_choice+1, "; ", next_choice+1, "holds", proposer+1)

            rightmost[next_choice] = ranking[next_choice, proposer] ##next choice's preference's list got reduced, rightmost is proposer now

            if not (next_choice in set_proposed_to): ##if no one is rejected <=> next choice has not been proposed before proposer proposed
                break
            proposer = current ##the one who being rejected is the next proposer
        set_proposed_to.add(next_choice)

    soln_possible = not (proposer==next_choice)
    ##Claim1: if there is a player i who is rejected by all, then he must be the last proposer in the loop
    ##Proof: bc if someone who has not proposed anyone, then there must be at least 1 person besides player i who holds nobody
    ##This fact is used to decide whether the solution exists or not

    #if soln_possible:
    if ENABLE_PRINT:  print("The table after phase-I execution is:")
    if ENABLE_PRINT:  friendly_print_current_table(preference, leftmost, rightmost)
    return soln_possible, leftmost, rightmost

def get_all_unmatched(leftmost, rightmost):
    unmatched_players = []
    for person in range(0, len(leftmost)):
        if leftmost[person] != rightmost[person]:
            if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print(person + 1, "is unmatched")
            unmatched_players.append(person)
    return unmatched_players


def update_second2(person,preference, second, leftmost, rightmost, ranking):
    second[person]=leftmost[person]+1 #before updation, second is simply leftmost +1
    pos_in_list = second[person]
    while True:  # a sophisticated way to update the second choice, as some person between leftmost and rightmost might be dropped as well
        next_choice = preference[person, pos_in_list]
        pos_in_list += 1
        if ranking[next_choice, person] <= rightmost[next_choice]:  # check whether person is still in next_choice's reduced list <=> next_choice is still in his list
            second[person] = pos_in_list -1
            return next_choice, second


##Claim2: if a person whose reduced list contains only one person, he shall not appear in the cycle?
##Proof: Assume person i's list only contains one person j, -> j holds i's proposal after the reduction
# if there is l behind i in j's list, he must be deleted from i's list
# if there is k before i in j's list, then j's proposal must be accepted by someone a other than i, a's proposal must be accepted by someone b other than i,j,
#   b's proposal must be accepted by someone c other than a,i,j ... since there is only finite players, contradiction
#->i is the only person in j's reduced list -> i,j won't be found by find_unmatched and won't be someone's last choice or second choice

##Claim3: if a person whose reduced list contains more than one person, he must appear in the cycle?
##Proof: False. Duplicate the preference matrix in the paper with each number +6, and put the last six person at the end of the list of the first six person,
# and put the first six person at the end of the list of the last six person


##This fact means that we only need to initialize cycle once and loop to reduce the element of it


def seek_cycle2(preference, second,  first_unmatched, leftmost, rightmost, ranking):
    #tail= set()
    #print("I am in seek_cycle2")
    cycle =[]
    posn_in_cycle = 0
    person = first_unmatched
    if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("p_",posn_in_cycle+1,":",person+1)

    while not (person in cycle): ##loop until the first repeat
        cycle.append(person)
        posn_in_cycle+=1
        next_choice, second = update_second2(person,preference, second, leftmost, rightmost, ranking)
        if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("q_",posn_in_cycle,":",next_choice+1)
        person = preference[next_choice,rightmost[next_choice]]
        if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("p_",posn_in_cycle+1,":",person+1)
    #after this loop, person is the one who repeats first

    last_in_cycle= posn_in_cycle-1 #position of the last one in cycle in the "cycle" list
    #tail = set(cycle) #using the set object in Python, we don't need cycle_set
    while True: #this is used to find the head of the cycle and its position in the "cycle" list
        posn_in_cycle = posn_in_cycle - 1
        #tail = tail.remove(cycle[posn_in_cycle])
        if cycle[posn_in_cycle]==person: #loop until we get the person who repeat first
            first_in_cycle = posn_in_cycle
            break
    #print("!!!",first_in_cycle,last_in_cycle)
    #print("I am out of seek_cycle2 now")
    friendly_print_rotation(cycle, first_in_cycle, last_in_cycle, preference, leftmost, second)
    return first_in_cycle, last_in_cycle, cycle, second



def phaseII_reduction2(preference, first_in_cycle, last_in_cycle, second, leftmost, rightmost,  soln_possible, cycle):
    #print("I am in phase ii reduction2")
    #print("input is:")
    #print([ leftmost, rightmost, second])
    for rank in range(first_in_cycle, last_in_cycle+1):
        proposer = cycle[rank]
        leftmost[proposer] = second[proposer]
        second[proposer] = leftmost[proposer]+1 #it is mentioned that proper initialization is unnecessary
        next_choice = preference[proposer,leftmost[proposer]]
        if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print(proposer+1, "proposed to his second choice in the reduced list:", next_choice+1, ";", next_choice+1,"accepted ", proposer+1, "and rejected", preference[next_choice,rightmost[next_choice]]+1 )
        rightmost[next_choice] = get_ranking(preference)[next_choice,proposer]
    #print([leftmost, rightmost, second])
    #To check whether stable matching exists or not#
    rank = first_in_cycle
    while (rank <= last_in_cycle) and soln_possible:
        proposer = cycle[rank]
        soln_possible = leftmost[proposer] <= rightmost[proposer]
        rank+=1
    if not soln_possible:
        if ENABLE_PRINT: print("No stable matching exists!!!")
        return soln_possible, first_in_cycle, last_in_cycle, second.copy(), leftmost.copy(), rightmost.copy(),  cycle

    #A special step to handle the case of more than one cycle, seems not contained in the code in paper#
    for person in range(first_in_cycle, last_in_cycle):
        if leftmost[cycle[first_in_cycle]] != rightmost[cycle[first_in_cycle]]:
            to_print =np.array(cycle[first_in_cycle:last_in_cycle + 1])+1
            if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("E=",to_print, "is still unmatched")
            if ENABLE_PRINT: print("The table after rotation elimination is:")
            if ENABLE_PRINT:  friendly_print_current_table(preference, leftmost, rightmost)
            return soln_possible, first_in_cycle,  last_in_cycle,  second.copy(), leftmost.copy(), rightmost.copy(),  cycle
    to_print = np.array(cycle[first_in_cycle:last_in_cycle + 1]) + 1
    if ENABLE_PRINT and DETAILED_ENABLE_PRINT: print("E=",to_print, "is all  matched")
    first_in_cycle=0

    #print("I am out of phase II reduction2 now")
    if ENABLE_PRINT: print("The table after rotation elimination is:")
    if ENABLE_PRINT:  friendly_print_current_table(preference, leftmost, rightmost)
    return soln_possible, first_in_cycle, last_in_cycle, second.copy(), leftmost.copy(), rightmost.copy(),  cycle

def friendly_print_current_table(preference, leftmost, rightmost):
    for person in range(0,len(preference)):
        to_print = []
        for entry in range(leftmost[person],rightmost[person]+1):
            if get_ranking(preference)[preference[person, entry],person]<=rightmost[preference[person,entry]]:
                to_print.append(preference[person,entry])
        to_print=np.array(to_print)
        print(person+1,"|",to_print+1)

def friendly_print_rotation(cycle,first_in_cycle,last_in_cycle, preference,leftmost,second):
    print("The rotation exposed is:")
    print("E| H S")
    for person in range(first_in_cycle,last_in_cycle+1):
        print("{0}| {1} {2}".format(cycle[person]+1,preference[cycle[person],leftmost[cycle[person]]]+1,preference[cycle[person],second[cycle[person]]]+1))

def friendly_print_sol(partners):
    seen = []
    pairs=[]
    to_print = []
    for sol in partners:
        for people in range(0, len(sol)):
            if people not in seen:
                seen.append(people)
                pairs.append((people+1,sol[people]+1))
                seen.append(sol[people])
        to_print.append(pairs)
        pairs = []
        seen=[]
    return to_print


def Find_all_Irving_partner(preference):

    ranking = get_ranking(preference)
    leftmost = np.zeros(len(preference[0, :]), dtype=int) #leftmost indicates the position of the person who holds i's proposal
    second = np.zeros(len(preference[0, :]), dtype=int) + 1
    rightmost = np.zeros(len(preference[0, :]), dtype=int) + len(preference[0,:]) - 1 #rightmost indicates the position of the person whose proposal i holds
    partner = np.zeros(len(preference[0, :]), dtype=int)
    soln_possible = False
    first_unmatched = 1
    first_in_cycle = 0
    last_in_cycle = 0
    cycle=[]
    partners = []
    soln_found = False

    if ENABLE_PRINT: print("The preference lists are:")
    if ENABLE_PRINT: print(preference+1)


    soln_possible, leftmost, rightmost = phaseI_reduction(preference, leftmost, rightmost, ranking)
    if not soln_possible:
        if ENABLE_PRINT: print("No stable matching exists!!")
        return partners
    second = leftmost + 1



    seen = []
    queue =[]
    qlfmost =leftmost.copy()
    qrtmost = rightmost.copy()
    qsecond = second.copy()
    seen.append([qlfmost,qrtmost, qsecond])
    queue.append([qlfmost,qrtmost, qsecond])
    while queue:
        [qlfmost, qrtmost, qsecond] = queue.pop(0)

        unmatched = get_all_unmatched(qlfmost, qrtmost)
        if unmatched:
            # if ENABLE_PRINT: print("The tripple is:")
            # if ENABLE_PRINT: print([qlfmost, qrtmost, qsecond])
            # if ENABLE_PRINT: print("it is unmatched yet!")
            for person in unmatched:
                if ENABLE_PRINT: print("person is:", person+1)
                #print("before skcycle:",[qlfmost, qrtmost, qsecond])
                first_in_cycle, last_in_cycle, cycle, cursecond = seek_cycle2(preference, qsecond.copy(), person, qlfmost.copy(), qrtmost.copy(), ranking)
                #print("after skcycle:", [qlfmost, qrtmost, qsecond])
                soln_possible, first_in_cycle, last_in_cycle, cursecond,  curlfmost,  currtmost, cycle = phaseII_reduction2(preference, first_in_cycle, last_in_cycle, cursecond.copy(), qlfmost.copy(), qrtmost.copy(), soln_possible, cycle)
                #print("The tripple is:")
                #print([curlfmost, currtmost, cursecond])
                curtripple = [curlfmost, currtmost, cursecond]
                if not any(all((pref1==pref2).all() for pref1, pref2 in zip(curtripple,tripple)) for tripple in seen) and soln_possible:
                    # if ENABLE_PRINT: print("The new tripple is:")
                    # if ENABLE_PRINT: print([curlfmost, currtmost, cursecond])
                    # if ENABLE_PRINT: print("it is added to the queue")
                    seen.append([curlfmost, currtmost, cursecond])
                    queue.append([curlfmost, currtmost, cursecond])
                #print("after phase ii:", [qlfmost, qrtmost, qsecond])
        else:
            # if ENABLE_PRINT: print("The tripple is:")
            # if ENABLE_PRINT: print([qlfmost, qrtmost, qsecond])
            # if ENABLE_PRINT: print("it is matched already!")
            partner = np.zeros(len(preference[0, :]), dtype=int)
            for person in range(0, len(qlfmost)):
                partner[person] = preference[person, qlfmost[person]]
            if not any(partner.tolist() == p for p in partners):
                partners.append(partner.tolist())

            to_print = friendly_print_sol(partners)


    if ENABLE_PRINT: print("The solution is: ", to_print)
    return partners



def gen_random_preference(SIZE = 4):
    preference = np.zeros((SIZE,SIZE), dtype=int)
    for i in range(0,SIZE):
        preference[i,0:SIZE-1]= random.sample([j for j in range(0,SIZE) if j != i ],SIZE-1)
        preference[i,SIZE-1] = i
    return preference




if __name__== '__main__':



    while True:
        try:
            inp = input("Type in Y to see an example, anything else to skip")
            if inp =="Y":
                example = np.array([[1,4,3,5,6,7,2,0],[2,5,0,6,7,4,3,1],[3,6,1,7,4,5,0,2],[0,7,2,4,5,6,1,3],[5,0,7,1,2,3,6,4],[6,1,4,2,3,0,7,5],[7,2,5,3,0,1,4,6],[4,3,6,0,1,2,5,7]])

                ENABLE_PRINT = 1
                Find_all_Irving_partner(example)
            else:
                break
        except:
            print("Invalid input")

    while True:
        try:
            inp = input("Type in Y to try your own problem, anything else to skip")
            if inp =="Y":
                problem = input("Please type in your preference table, e.g. [[2,3,4,1],[1,3,4,2],[2,4,1,3],[1,3,2,4]]:")
                preferences = np.array(eval(problem))-1
                ENABLE_PRINT = 1
                Find_all_Irving_partner(preferences)
            else:
                break
        except:
            print("Invalid input")


    while True:
        try:
            ENABLE_PRINT =0
            examples = dict()
            counters=[]
            inp = input("Type in Y to try gen random samples and see the distribution of number of solutions, anything else to skip")
            if inp == "Y":
                hsize = int(int(input("Please specify the size of problem:"))/2)
                samples = int(input("Please specify the sample size:"))
                for half_size in range(hsize,hsize+1):
                    for i in range(0,samples+1):
                        preference = gen_random_preference(2*half_size)
                        pref_as_key = preference.tolist()
                        for i in range(0, len(preference)):
                            pref_as_key[i] = tuple(pref_as_key[i])
                        if tuple(pref_as_key) not in examples.keys():
                            examples[tuple(pref_as_key)] = Find_all_Irving_partner(preference)
                        else:
                            i = i-1
                            continue
                for pref_as_key in examples.keys():
                    counters.append(len(examples[pref_as_key]))
                plt.hist(counters)
                plt.show()
            else:
                break
        except:
             print("Invalid input")

