import random

def get_ranking(preference):
    ranking =  [[-1 for i in range(len(preference[0]))] for j in range(len(preference[:]))]
    for row in range(0,len(preference[:])):
        for col in range(0,len(preference[0])):
            ranking[row][col]=preference[row].index(col) # the function index return the position of that element in the list
    return ranking

def gen_random_preference(M_SIZE = 4,W_SIZE=4):
    preference = [[-1 for i in range(W_SIZE)] for j in range(M_SIZE)]
    for i in range(0,M_SIZE):
        preference[i][0:W_SIZE]= random.sample([j for j in range(0,W_SIZE) ],W_SIZE)
    return preference

def deferred_acceptance(m_pref= gen_random_preference(4,4), w_pref= gen_random_preference(4,4)):
    print(m_pref)
    print(w_pref)

    m_SIZE = len(m_pref[:])
    w_SIZE = len(w_pref[:])
    m_ranking = get_ranking(m_pref)
    w_ranking = get_ranking(w_pref)
    m_engaged = [0 for i in range(m_SIZE)]
    m_head = [0 for i in range(m_SIZE)] # head points to the best possible partner of m at current stage
    w_tail = [m_SIZE for i in range(w_SIZE)] # tail points to the worst possible partner of w at current stage
    while sum(m_engaged)<m_SIZE:
        for man in range(0,m_SIZE):
            if m_engaged[man]==0:
                woman = m_pref[man][m_head[man]]
                if w_ranking[woman][man] < w_tail[woman]:
                    if w_tail[woman]!= m_SIZE: #take care of the initial case when the woman is engaged to no one
                        man_rejected= w_pref[woman][w_tail[woman]]
                        m_engaged[man_rejected] = 0
                        m_head[man_rejected] = m_head[man_rejected]+1
                        #print("woman rejects man_",man_rejected)
                        # woman rejects man_rejected
                        # man_rejected return unengaged
                        # and his best possible stable partner is updated to the one after woman

                    w_tail[woman] = w_ranking[woman][man]
                    #print(" man_", man, " is engaged to his best available partner woman_",woman)
                    # man is engaged to his best available partner woman
                    # woman's worst possible stable partner is updated to man i.e. w is engaged to man
                    m_engaged[man] =1

                else:
                    m_head[man] = m_head[man] + 1

    for man in range(0,m_SIZE):
        print("{0}| {1} ".format(man,m_pref[man][m_head[man]] ))
    return m_head
