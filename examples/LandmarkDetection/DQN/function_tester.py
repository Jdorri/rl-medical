import numpy as np


test_dic = {'0':[([1,1,1,1],1,1,False),([2,2,2,2],2,2,False),([3,2,2,2],2,3,False),([4,2,2,2],2,4,False),([5,2,2,2],2,5,False),([6,3,3,3],3,6,True)]}


def return_n_future_steps(episode, index, n):
    '''
    Given the episode number and the index of a step taken will return the
    next n-1 (s,a,r)
    '''
    steps_to_end = len(test_dic[episode]) - index+1
    n_index = index+n

    if steps_to_end >= n:
        ns, na, nrs, nisOver = zip(*test_dic[episode][index+1:n_index+1])
        ns, na, nisOver = ns[-1], na[-1], nisOver[-1]
        return ns, na, list(nrs), nisOver

    else:
        while steps_to_end < n:
            print(n)
            n -= 1
        return return_n_future_steps(episode, index, n)


# episode = np.asarray([e for e in ['0','0','0','0','0']], dtype='float32')
# step_index = np.asarray([e for e in [0,3,2,1,3,6]], dtype='int8')
# print(step_index)
# print(episode)
# print(return_n_future_steps(episode, step_index, 3))

test_dic_2 = {'r':'red', 'b': 'blue', 'g':'green'}
keys = ['r', 'b', 'g']


a = [[1,2,3,4,5,6],[1,2],[1,2,3,4,54]]
b = np.asarray(a)
print(b)
