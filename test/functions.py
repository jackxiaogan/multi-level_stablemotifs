#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Xiao Gan
#
# Created:     13/06/2016
# Copyright:   (c) Xiao Gan 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import re
##import numpy as np
import networkx as nx
##import matplotlib.pyplot as plt
import copy
import collections
##import time


def nodescan(functionlist,mode=0,subzero=0):
    # find how many original node there is, and how many states each has;
    # (Obsolete) subzero=1: substitute any 'N$0' state nodes with the negation of other node, e.g 'not N$1 and not N$2'
    # TBD: mode=1: show warning of node function errors/issues
    # TBD: replacesib=1: replace undetermined nodes whose sibling nodes are identified. Will not run if replacesib=0.
    # return a list of nodes,a list of states and a list of # states for the corresponding node

    nodelist=[]
    nodestates=[]
    nodestatenumber=[]
    nodehigheststate=[] #record the highest state given in the node name
    newfunctionlist=[]
    Flags=[]
    for words in functionlist:
        vnode = words.split("*",1)[0].strip()
        node = vnode.split("$",1)[0].strip()
        state = vnode.split("$",1)[1].strip()
        function = words.split("=",1)[1].strip()

        if node not in nodelist:
            nodelist.append(node)
            nodestates.append([state])
            nodestatenumber.append(1)
            nodehigheststate.append(state)
            Flags.append(0)
        else:
            # corresponding nodestatenumber +1
            x = nodelist.index(node)
            nodestates[x].append(state)
            nodestatenumber[x] += 1
            if nodehigheststate[x] < state:
                nodehigheststate[x] = state

    if mode==1:
        for i in range(0,len(nodelist)):
##            print i
##            print 'node=',nodelist[i]
##            print nodehigheststate[i]
##            print nodestatenumber[i]
            if int(nodehigheststate[i]) != (nodestatenumber[i]-1):
                print 'warning: node {} has number of states that does not match: max state {}, total states {}'.format(nodelist[i],nodehigheststate[i],nodestatenumber[i]-1)
##            print '------'

    return [nodelist, nodestates, nodestatenumber, nodehigheststate, newfunctionlist]


# test example:
##y =['N0$0* =(N1$0 AND N4$0) OR (N1$1 AND N4$0)', 'N0$1* =(N1$0 AND N4$1) OR (N1$1 AND N4$1) OR (N1$2 AND N4$0) OR (N1$2 AND N4$1)', 'N1$0* =(N3$0 AND N2$1) OR (N3$1 AND N2$0) OR (N3$2 AND N2$1)', 'N1$1* =(N3$0 AND N2$2) OR (N3$2 AND N2$0) OR (N3$2 AND N2$2)', 'N1$2* =(N3$0 AND N2$0) OR (N3$1 AND N2$1) OR (N3$1 AND N2$2)', 'N2$0* =(N1$0 AND N4$0) OR (N1$0 AND N4$1) OR (N1$2 AND N4$1)', 'N2$1* =(N1$2 AND N4$0)', 'N2$2* =(N1$1 AND N4$0) OR (N1$1 AND N4$1)', 'N3$0* =(N4$1 AND N2$1)', 'N3$1* =(N4$0 AND N2$0) OR (N4$0 AND N2$1) OR (N4$0 AND N2$2) OR (N4$1 AND N2$0)', 'N3$2* =(N4$1 AND N2$2)', 'N4$0* =(N2$0 AND N1$0) OR (N2$0 AND N1$1) OR (N2$1 AND N1$2) OR (N2$2 AND N1$0) OR (N2$2 AND N1$1)', 'N4$1* =(N2$0 AND N1$2) OR (N2$1 AND N1$0) OR (N2$1 AND N1$1) OR (N2$2 AND N1$2)']
##
##x = nodescan(y,mode=1)
##print x


def findinputs(list1,inc_normal=1,mode=1):
    # 'inc_normal' is an argument to control whether normal nodes are considered. Setting it=0 will return only inputs from composite nodes.
    # mode=1: normal mode; mode=0: return a list of composite nodes and a list of corresponding inputs
    composite_nodes=[]
    corresponding_inputs=[]
    nodes=[]
    for item in list1:
        if item.count('AND')>=1:
            composite_nodes.append(item)
            inputs = item.split("AND")
            inputs = [item.strip() for item in inputs]
            for item2 in inputs:
                if mode==1:
                    if item2 not in nodes:
                        nodes.append(item2)
                elif mode==0:
                    corresponding_inputs.append(inputs)
        else:
            if inc_normal:
                nodes.append(item)
    if mode==0:
        return [composite_nodes, corresponding_inputs]
    else:
        return list(set(nodes))




def findinputsstr(string,mode=1): # returns a list of input nodes for an implicant string (node names connected with 'AND').
    inputs=[]
    inputscount = string.count('AND')+1
    if inputscount>=2:
        inputs = string.split("AND")
        inputs = [ item.strip() for item in inputs]
    else:
        inputs.append(string)
    if mode==1:
        return list(set(inputs))
    if mode==0:
        return inputscount

# example
##print findinputsstr ('C$1 AND A$1 AND B$1')

def unrepeatednode(list):
    # From a list of nodes (may include composite nodes), return a list of virtual nodes that does not have other virtual nodes corresponding to the same original node
    Flag=0
    nodelist=[]
##    print nodelist
    repeated=[]
    for item in list:
    # select only virtual nodes; filters out compsite nodes
        if (item.count('AND')==0) and (item.count('$')==1):
            nodelist.append(item)
        elif (item.count('AND')==0) and (item.count('$')==0):
            print 'Error in nodelist'
            return
##    print nodelist
    for i in range (0,len(nodelist)):
        if nodelist[i] not in repeated:
##            print
##            print nodelist[i]
            node1 = nodelist[i].split('$')[0]
            state1 = nodelist[i].split('$')[1]
            Flag1=0
            for j in range (i+1,len(nodelist)):
##                print nodelist[j]
                if nodelist[j] not in repeated:
                    # see if same original node
                    node2 = nodelist[j].split('$')[0]
                    state2 = nodelist[j].split('$')[1]
                    if (node1==node2) and (state1!=state2):
                        repeated.append(nodelist[j])
                        Flag1=1
##                else:
##                    print 'Error: nodelist[j] in repeated',nodelist[j],repeated
            if Flag1==1:
                repeated.append(nodelist[i])
##    print repeated
    return [x for x in nodelist if x not in repeated]


# test examples
##y = ['B$1', 'B$0']
##x = unrepeatednode(y)
##print x

def containrep(list): # check if a list of input nodes contain at least two that refers to the same original node
    Flag=0
    nodes=[]
    states=[]
##    print list
    for index in range (len(list)):
        if list[index].count('AND')>=1:
            print "Error in containrep"
            return True
        else:
            node = list[index].split('$')[0]
            state = list[index].split('$')[1]
            if len(nodes)==0:
                nodes.append(node)
                states.append(state)
            else:
                for index2 in range (len(nodes)):
                    if node == nodes[index2]:
                        if state != states[index2]:
                            Flag=1
                            return True
                        # if same node and state, do nothing
                    else:
                        nodes.append(node)
                        states.append(state)

    if Flag==0:
        return False
    else:
        return "Flag=1"


def removedup(list1):    # keep only the smallest item(subset) in a list
    list2 = copy.copy(sorted(list1))
    discardlist =[]
    for i in range(0,len(list2)):
        item1=list2[i]
##        print 'item1:',item1
        for j in range(i+1,len(list2)):
            item2=list2[j]
##            print 'item2:',item2
            if item2 not in discardlist:
                item1s = set(item1)
                item2s = set(item2)
                if item1 == item2:
                    list1.remove(item2)
                    discardlist.append(item2)
##                    print 'remove item2 due to same:', item2

                else:
                    if item1s.issubset(item2s):
                        if item2 in list1:
                            list1.remove(item2)
                            discardlist.append(item2)
##                            print 'remove item2:', item2
                    elif item2s.issubset(item1s):
                        if item1 in list1:
                            list1.remove(item1)
                            discardlist.append(item1)
##                            print 'remove item1:', item1
##        print
##        print 'cyclelist:',list1

# test example:
##y = [['N6$0', 'N9$1'], ['N8$0', 'N6$0', 'N0$2', 'N1$1', 'N7$0', 'N8$0 AND N0$2', 'N3$1', 'N9$1', 'N5$1 AND N1$1', 'N1$1 AND N3$1', 'N5$1']]
##y = [[1,2,3],[1,3,4],[1,2,3,4],[1,2]]
##
##y = [['N0$1 AND N2$0', 'N1$2', 'N1$2 AND N0$1', 'N3$0', 'N0$1 AND N3$0', 'N4$0', 'N4$0 AND N3$0', 'N0$1', 'N2$0'], ['N4$1', 'N0$0'], ['N0$1 AND N3$0', 'N4$0 AND N3$0', 'N0$1 AND N2$0', 'N0$1', 'N4$0', 'N2$0', 'N1$2 AND N0$1', 'N1$2', 'N3$0']]
##
##removedup(y)
##
##print y



def removerep(cycles,mode=1):    # Mode1: keep only the cycles without repeated nodes in a list; Mode0: keep only cycles with all inputs of composite nodes present
    cycles1 = []
    for cycle in cycles:
        if mode==1:
            if not containrep(findinputs(cycle)):
                cycles1.append(cycle)
        elif mode==0:
            inputs = findinputs(cycle,0)
            Flag=0
            for item in inputs:
                if item not in cycle:
                    Flag=1
            if Flag==0:
                cycles1.append(cycle)

    return cycles1
# test
##cycles = [['N0$1 AND N3$0', 'N2$0', 'N1$2 AND N2$0', 'N3$0'], ['N0$1 AND N3$0', 'N2$0', 'N1$0 AND N2$0', 'N3$0'], ['N0$0 AND N3$0', 'N2$1', 'N1$1 AND N2$1', 'N3$0'], ['N1$1 AND N2$0', 'N3$1', 'N0$0 AND N3$1', 'N2$0'], ['N1$0', 'N0$0'], ['N1$2 AND N2$1', 'N3$1', 'N3$1 AND N0$1', 'N1$2'], ['N1$2 AND N2$1', 'N3$1', 'N0$1 AND N3$1', 'N2$1'], ['N0$1', 'N3$0 AND N0$1', 'N1$1'], ['N3$1', 'N0$1 AND N3$1', 'N2$1', 'N1$0 AND N2$1'], ['N1$1 AND N2$1', 'N3$0', 'N3$0 AND N0$1', 'N1$1']]
##print removerep(cycles,0)

def removenode(cycles,node):    # remove all cycles that contain cnode
    cycles1 = []
    for cycle in cycles:
        if node not in cycle:
            cycles1.append(cycle)
    return cycles1

def findcycle(cycles,node,input1=0,input2=0,mode=1):
    # return the cycles with a given node from a list of cycles. if input1 and input2 are given, it will return with cycles with input1 but without input2
    # mode=1 to find w/ input1 & w/o input2; mode=0 to find w/ both input1 and input2
    cycles1=[]
    for cycle in cycles:
        if node in cycle:
            if input1==0 and input2==0:
                cycles1.append(cycle)
            else:
                if input1 in findinputsstr(node):
                    if input1 in cycle:
                        cycles1.append(cycle)
                    else:
                        if mode==1:
                            if input1 in cycle and input2 not in cycle:
                                cycles1.append(cycle)
                        elif mode==0:
                            if input1 in cycle and input2 in cycle:
                                cycles1.append(cycle)

    return cycles1

def findcnode(cycles): # returns a list of cnodes in a list of cycles
    cnodes=[]
    for cycle in cycles:
        for node in cycle:
            if node.count('AND')>=1 and node not in cnodes:
                cnodes.append(node)
    return cnodes

def getinput(list1):
    nodelist=[]
    for node in list1:
        if node.count('AND')>=1:
            for node1 in node.split('AND'):
                if node1.strip() not in nodelist:
                    nodelist.append(node1.strip())
        elif node not in nodelist:
            nodelist.append(node)
    return nodelist

def checkreplist(list1,list2):
    # check if two lists of virtual nodes has repeated between lists
    for node1 in list1:
        for node2 in list2:
            if node1.split('$')[0] == node2.split('$')[0] and node1.split("$")[1] != node2.split("$")[1]:
                return True
    return False

def union(cycles1, cycles2, mode=1):
    # merge a list of cycles with another list of cycles, without merging those in the same list. Mode=1: Resulting cycles with repeated nodes are discarded.
##    i=0
    cycles3=[]
    for cycle1 in cycles1:
        for cycle2 in cycles2:
            if not checkreplist(getinput(cycle1),getinput(cycle2)):
                newcycle = list(set(cycle1+cycle2))
                if (newcycle not in cycles3):
                        cycles3.append(newcycle)
    return cycles3

def union2(cycles1, cycles2, mode=1):
    # merge a list of cycles with another list of cycles, without merging those in the same list. Mode=1: Resulting cycles with repeated nodes are discarded.
    cycles3=[]
    for cycle1 in cycles1:
        for cycle2 in cycles2:
            newcycle = list(set(cycle1+cycle2))
##            print cycle1,cycle2,newcycle
            if mode>=1:
                if (newcycle not in cycles3) and not containrep(findinputs(newcycle)):
                    cycles3.append(newcycle)
            elif mode==0:
                if newcycle not in cycles3:
                    cycles3.append(newcycle)
    return cycles3

def plus(cycles1,cycles2):
    # returns all the elements in cycle1 or cycles2
    cycles3=cycles1
    for cycle2 in cycles2:
        if cycle2 not in cycles3:
            cycles3.append(cycle2)
    return cycles3

def exclude(cycles1,cycles2):
    # returns the elements in cycle1 that are not elements of cycles2
    cycles3=[]
    for cycle1 in cycles1:
        if cycle1 not in cycles2:
            cycles3.append(cycle1)
    return cycles3

def intersection(cycles1,cycles2):
    # returns the elements in both cycle1 and cycles2
    cycles3=[]
    for cycle1 in cycles1:
        if cycle1 in cycles2:
            cycles3.append(cycle1)
    return cycles3

def candidate(cycles):  # return a list of SM candidates from a list of cycles
    cycles_a = copy.copy(cycles)
    a = removerep(cycles)
    SMcandidates = removerep(a,mode=0)
##    print SMcandidates

    cnodes=findcnode(cycles)
    inputs = ['']*len(cnodes)

    for cindex in range (len(cnodes)):# merge cycles that share the same composite node
        inputs[cindex] = findinputsstr(cnodes[cindex])

        candidates = findcycle(a,cnodes[cindex],input1=inputs[cindex][0])
##        print cnodes[cindex], inputs[cindex],candidates

        for inputindex in range (1,len(findinputsstr(cnodes[cindex]))):
##            print 'input:',inputs[cindex][inputindex]
            ab= candidates
            c = findcycle(cycles_a,cnodes[cindex],input1=inputs[cindex][inputindex])
##            print ab,c

            cycles1 = exclude(ab,c)
            cycles2 = exclude(c,ab)

            newcycles = union(cycles1,cycles2)# found the 'union' of the above cycles
            cycles3 = intersection(ab,c)
##            print 'cycle1:{}, cycle2:{},newcycles:{},cycles3:{}'.format(cycles1,cycles2,newcycles,cycles3)

            candidates = plus(cycles3,newcycles)# add cycles3, the cycles with both inputs A and B present

        for candidate in candidates:  # add the unions to the candidate pool
            if candidate not in SMcandidates:
                SMcandidates.append(candidate)
                cycles_a.append(candidate)

        # remove cycles with cnodes[cindex] that are not SM candidates (does not include all inputs for this cnode), add SM candidates
        a = removenode(a,cnodes[cindex])
        a = plus(a,SMcandidates)
##        print 'a=',a
##        print
##            else:
##                print "discarded"

    SMcandidates = removerep(SMcandidates,mode=0)
##    print 'SMcandidates:', SMcandidates
    # keep only the smallest SCCs
    removedup(SMcandidates)

    return SMcandidates

# test example
##cycles = [['N0$1 AND N3$0', 'N2$0', 'N1$2 AND N2$0', 'N3$0'], ['N0$1 AND N3$0', 'N2$0', 'N1$0 AND N2$0', 'N3$0'], ['N0$0 AND N3$0', 'N2$1', 'N1$1 AND N2$1', 'N3$0'], ['N1$1 AND N2$0', 'N3$1', 'N0$0 AND N3$1', 'N2$0'], ['N1$0', 'N0$0'], ['N1$2 AND N2$1', 'N3$1', 'N3$1 AND N0$1', 'N1$2'], ['N1$2 AND N2$1', 'N3$1', 'N0$1 AND N3$1', 'N2$1'], ['N0$1', 'N3$0 AND N0$1', 'N1$1'], ['N3$1', 'N0$1 AND N3$1', 'N2$1', 'N1$0 AND N2$1'], ['N1$1 AND N2$1', 'N3$0', 'N3$0 AND N0$1', 'N1$1']]
##cycles = [['N1$1 AND N3$2', 'N7$0', 'N9$1', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2', 'N3$2', 'N3$2 AND N2$0', 'N1$1'], ['N1$1 AND N3$2', 'N7$0', 'N9$1', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2', 'N3$2'], ['N1$1 AND N3$2', 'N7$0', 'N2$0', 'N6$0', 'N9$1', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2', 'N3$2', 'N3$2 AND N2$0', 'N1$1'], ['N1$1 AND N3$2', 'N7$0', 'N2$0', 'N6$0', 'N9$1', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2', 'N3$2'], ['N1$1 AND N3$2', 'N7$0', 'N2$0', 'N3$2 AND N2$0', 'N1$1'], ['N1$0 AND N3$2', 'N7$2', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2', 'N8$2 AND N0$1', 'N3$2'], ['N1$0 AND N3$2', 'N7$2', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2', 'N8$2 AND N0$2', 'N3$2'], ['N1$0 AND N3$2', 'N7$2', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2', 'N8$2 AND N0$1', 'N3$2'], ['N1$0 AND N3$2', 'N7$2', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2', 'N8$2 AND N0$2', 'N3$2'], ['N5$0 AND N1$2', 'N8$2', 'N8$2 AND N0$1', 'N3$2', 'N3$2 AND N2$1', 'N1$2'], ['N5$0 AND N1$2', 'N8$2', 'N8$2 AND N0$2', 'N3$2', 'N3$2 AND N2$1', 'N1$2'], ['N8$2 AND N0$0', 'N3$0', 'N9$0 AND N3$0', 'N0$0'], ['N8$2 AND N0$0', 'N3$0', 'N1$0', 'N5$1 AND N1$0', 'N8$2'], ['N8$2 AND N0$0', 'N3$0', 'N1$0', 'N1$0 AND N3$0', 'N7$2', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2'], ['N8$2 AND N0$0', 'N3$0', 'N1$0', 'N1$0 AND N3$0', 'N7$2', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2'], ['N8$2 AND N0$0', 'N3$0', 'N1$1 AND N3$0', 'N7$1', 'N6$1 AND N7$1', 'N9$0', 'N9$0 AND N3$0', 'N0$0'], ['N8$2 AND N0$0', 'N3$0', 'N1$1 AND N3$0', 'N7$1', 'N2$1', 'N2$1 AND N9$0', 'N6$1', 'N6$1 AND N7$1', 'N9$0', 'N9$0 AND N3$0', 'N0$0'], ['N8$2 AND N0$0', 'N3$0', 'N1$0 AND N3$0', 'N7$2', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2'], ['N8$2 AND N0$0', 'N3$0', 'N1$0 AND N3$0', 'N7$2', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$0', 'N8$2'], ['N0$0', 'N8$0 AND N0$0', 'N3$0', 'N9$0 AND N3$0'], ['N0$0', 'N8$0 AND N0$0', 'N3$0', 'N1$1 AND N3$0', 'N7$1', 'N6$1 AND N7$1', 'N9$0', 'N9$0 AND N3$0'], ['N0$0', 'N8$0 AND N0$0', 'N3$0', 'N1$1 AND N3$0', 'N7$1', 'N2$1', 'N2$1 AND N9$0', 'N6$1', 'N6$1 AND N7$1', 'N9$0', 'N9$0 AND N3$0'], ['N9$0', 'N2$1 AND N9$0', 'N6$1', 'N6$1 AND N7$1'], ['N5$0 AND N1$0', 'N8$0', 'N8$0 AND N0$2', 'N3$1', 'N1$0 AND N3$1', 'N7$1', 'N2$1', 'N2$1 AND N9$0', 'N6$1', 'N5$0'], ['N5$0 AND N1$0', 'N8$0', 'N8$0 AND N0$1', 'N3$1', 'N1$0 AND N3$1', 'N7$1', 'N2$1', 'N2$1 AND N9$0', 'N6$1', 'N5$0'], ['N5$0 AND N1$0', 'N8$0', 'N8$0 AND N0$0', 'N3$0', 'N1$0'], ['N1$1 AND N3$1', 'N7$0', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$2', 'N3$1'], ['N1$1 AND N3$1', 'N7$0', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$2', 'N3$1', 'N1$1'], ['N1$1 AND N3$1', 'N7$0', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$1', 'N3$1'], ['N1$1 AND N3$1', 'N7$0', 'N9$1', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$1', 'N3$1', 'N1$1'], ['N1$1 AND N3$1', 'N7$0', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$2', 'N3$1'], ['N1$1 AND N3$1', 'N7$0', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$2', 'N3$1', 'N1$1'], ['N1$1 AND N3$1', 'N7$0', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$1', 'N3$1'], ['N1$1 AND N3$1', 'N7$0', 'N2$0', 'N6$0', 'N5$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$1', 'N3$1', 'N1$1'], ['N3$2', 'N1$2 AND N3$2', 'N7$0', 'N9$1', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2'], ['N3$2', 'N1$2 AND N3$2', 'N7$0', 'N2$0', 'N6$0', 'N9$1', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2'], ['N3$2', 'N3$2 AND N2$1', 'N1$2', 'N1$2 AND N3$2', 'N7$0', 'N9$1', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2'], ['N3$2', 'N9$1 AND N3$2', 'N0$2', 'N8$2 AND N0$2'], ['N3$1', 'N1$1', 'N5$0 AND N1$1', 'N8$1'], ['N3$1', 'N1$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$2'], ['N3$1', 'N1$1', 'N5$1 AND N1$1', 'N8$0', 'N8$0 AND N0$1'], ['N3$1', 'N0$2', 'N8$0 AND N0$2'], ['N6$0', 'N5$1', 'N5$1 AND N1$2', 'N8$0', 'N8$0 AND N0$0', 'N3$0', 'N1$2 AND N3$0', 'N7$2', 'N9$1'], ['N6$0', 'N5$1', 'N5$1 AND N1$2', 'N8$0', 'N8$0 AND N0$0', 'N3$0', 'N1$2 AND N3$0', 'N7$2', 'N2$0'], ['N6$0', 'N9$1']]
##
##cycles = [['N0$0 AND N2$0', 'N3$0', 'N3$0 AND N2$0', 'N1$1', 'N4$1 AND N1$1', 'N2$0'], ['N0$0 AND N2$0', 'N3$0', 'N3$0 AND N2$0', 'N1$1', 'N4$1 AND N1$1', 'N2$0', 'N2$0 AND N3$0', 'N0$0'], ['N0$0 AND N2$0', 'N3$0', 'N3$0 AND N2$0', 'N1$1', 'N4$0 AND N1$1', 'N2$0'], ['N0$0 AND N2$0', 'N3$0', 'N3$0 AND N2$0', 'N1$1', 'N4$0 AND N1$1', 'N2$0', 'N2$0 AND N3$0', 'N0$0'], ['N0$0 AND N2$0', 'N3$0', 'N2$0 AND N3$0', 'N0$0'], ['N2$0 AND N3$1', 'N0$1', 'N0$1 AND N2$0', 'N3$1', 'N3$1 AND N2$0', 'N1$0', 'N4$2 AND N1$0', 'N2$0'], ['N2$0 AND N3$1', 'N0$1', 'N0$1 AND N2$0', 'N3$1'], ['N4$1 AND N1$0', 'N2$1', 'N3$0 AND N2$1', 'N1$0'], ['N4$1 AND N1$0', 'N2$1', 'N0$1 AND N2$1', 'N3$0', 'N3$0 AND N2$1', 'N1$0'], ['N4$1 AND N1$0', 'N2$1', 'N2$1 AND N3$0', 'N0$1', 'N0$1 AND N2$1', 'N3$0', 'N3$0 AND N2$1', 'N1$0'], ['N4$0 AND N1$1', 'N2$0', 'N3$0 AND N2$0', 'N1$1'], ['N4$0 AND N1$1', 'N2$0', 'N4$0'], ['N1$1', 'N4$1 AND N1$1', 'N2$0', 'N3$0 AND N2$0'], ['N1$1', 'N4$2 AND N1$1', 'N2$1', 'N2$1 AND N3$1'], ['N2$1', 'N4$2', 'N4$2 AND N1$1'], ['N2$1 AND N3$1', 'N0$0', 'N0$0 AND N2$1', 'N3$1'], ['N3$1', 'N3$1 AND N2$0', 'N1$0', 'N4$2 AND N1$0', 'N2$0', 'N0$1 AND N2$0'], ['N0$1 AND N2$1', 'N3$0', 'N2$1 AND N3$0', 'N0$1'], ['N2$2 AND N3$0', 'N1$0', 'N4$0 AND N1$0', 'N2$2'], ['N2$2 AND N3$0', 'N1$0', 'N4$0 AND N1$0', 'N2$2', 'N3$0'], ['N2$0', 'N3$1 AND N2$0', 'N1$0', 'N4$2 AND N1$0']]
##
##cycles =[['N1$1', 'N4$2 AND N1$1', 'N2$1', 'N2$1 AND N3$1'],
##['N2$1', 'N4$2', 'N4$2 AND N1$1'],
##['N2$1 AND N3$1', 'N0$0', 'N0$0 AND N2$1', 'N3$1']]

##cycles = ['N4$0', 'N1$2 AND N4$0', 'N2$1', 'N2$1 AND N1$2']
##['N4$0', 'N1$2 AND N4$0', 'N2$1', 'N3$1 AND N2$1', 'N1$2', 'N2$1 AND N1$2']
##['N2$1', 'N3$1 AND N2$1', 'N1$2', 'N1$2 AND N4$0']
##
##x = candidate(cycles)
##print x

##x = findcycle(a,'N2$1 AND N3$1',input1=inputs[cindex][0])
##print x

def siblingnode(nodex, nodelist, nodestates):
##    print vnode, nodelist,nodestates
    # returns all sibling nodes of a node from a nodelist
    sibling_nodelist =[]
    if nodex.count('AND')>=1:
        vnodes = nodex.split("AND")
    else:
        vnodes= [nodex]
    for vnode in vnodes:
        node = vnode.split("$",1)[0].strip()
        state = vnode.split("$",1)[1].strip()
        for state1 in nodestates[nodelist.index(node)]:
            if state1 != state:
                vnode1 = node + '$' + state1
                sibling_nodelist.append(vnode1)
##    print sibling_nodelist
    return sibling_nodelist

#test:

##y = [['N0', 'N1', 'N2', 'N3', 'N4', 'N5'], [['0', '1'], ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1', '2'], ['0', '1']]]
##y = [['N0', 'N1', 'N2'], [['0', '1'], ['0', '1'], ['0', '1']]]
##nodex = 'N0$1 AND N1$1'
##
##x = siblingnode(nodex,y[0],y[1])
##
##print x
def checkrep(nextnode,path):
    if len(path)>= 2:
##        print 'nextnode:',nextnode
        if ('AND' not in nextnode):
            for node in getinput(path):
                if nextnode.split("$")[0] == node.split("$")[0] and nextnode.split("$")[1] != node.split("$")[1]:
                    return True
        else:
            nodes = nextnode.split("AND")
            for node1 in nodes:
##                print 'node1:',node1
                for node in getinput(path):
                    if (node1.strip()).split("$")[0] == node.split("$")[0] and (node1.strip()).split("$")[1] != node.split("$")[1]:
##                        print node, 'removing'
                        return True
    return False

def simple_cycles_SM(G,lengthlimit=30,timelimit=0, nodelist=[], nodestates=[]):
    # copied from nx.simple_cycles(G). finds cycles that does not have repeated nodes.
    # TBD: setting upper bound of cycles

    def _unblock(thisnode,blocked,B):
        stack=set([thisnode])
        while stack:
            node=stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

##    start_time = time.time()
    # Johnson's algorithm requires some ordering of the nodes.
    # We assign the arbitrary ordering given by the strongly connected comps
    # There is no need to track the ordering as each node removed as processed.
    subG = type(G)(G.edges_iter()) # save the actual graph so we can mutate it here
                              # We only take the edges because we do not want to
                              # copy edge and node attributes here.
    sccs = list(nx.strongly_connected_components(subG))
    while sccs:
        scc=sccs.pop()
        # order of scc determines ordering of nodes
        startnode = scc.pop()
        # Processing node runs "circuit" routine from recursive version
        path=[startnode]
        blocked = set() # vertex: blocked from search?
        closed = set() # nodes involved in a cycle
        blocked.add(startnode)
##        for item in siblingnode(startnode,nodelist, nodestates):
##            print 'block siblingnode: ',item
##            blocked.add(item)
        B=collections.defaultdict(set) # graph portions that yield no elementary circuit
        stack=[ (startnode,list(subG[startnode])) ]  # subG gives component nbrs
##        print startnode,stack
        while stack:
            thisnode,nbrs = stack[-1]
##            print 'thisnode:',thisnode,nbrs
            # filter out nodes in nbrs that are repeated
            if nbrs:
                nextnode = nbrs.pop()
##                if startnode == 'N0$1':
##                    print thisnode,nbrs,":",nextnode,blocked,B,path,stack,startnode
##                print 'nextnode:{},blocked:{}'.format(nextnode,blocked),len(blocked)
##                print 'path:',path,'nextnode:',nextnode
##                print 'stack:', stack
#                    print thisnode,nbrs,":",nextnode,blocked,B,path,stack,startnode
#                    f=raw_input("pause")
                if nextnode == startnode:
                    yield path[:]
                    closed.update(path)
##                    print "Found a cycle",path,closed
                elif nextnode not in blocked:
                    path.append(nextnode)
##                    print 'path:',path,findinputs(path)
                    if len(path)>=lengthlimit or checkrep(nextnode,path[:-1:]):
##                    if containrep(findinputs(path)) or len(path)>=lengthlimit:
##                        stack.append( (nextnode,[]))
##                        continue
##                    # Done but to be checked: block all nodes that contain repeated nodestates with nextnode
##                        print 'remove: {}'.format(nextnode)
                        closed.update(path)
                        path.remove(nextnode)
                    else:
                        stack.append( (nextnode,list(subG[nextnode])) )
                        closed.discard(nextnode)
                        blocked.add(nextnode)
##                    for item in siblingnode(nextnode,nodelist, nodestates):
##                        print 'block siblingnode: ',item
##                        blocked.add(item)
                    continue
            # done with nextnode... look for more neighbors
            if not nbrs:  # no more nbrs
                if thisnode in closed:
                    _unblock(thisnode,blocked,B)
                else:
                    for nbr in subG[thisnode]:
                        if thisnode not in B[nbr]:
                            B[nbr].add(thisnode)
                stack.pop()
#                assert path[-1]==thisnode
                path.pop()
        # done processing this node
        subG.remove_node(startnode)
        H=subG.subgraph(scc)  # make smaller to avoid work in SCC routine
        sccs.extend(list(nx.strongly_connected_components(H)))

# test example
##G = nx.DiGraph([('A$0', 'A$1'),('B$0', 'A$1'), ('A$1', 'B$1'), ('B$1', 'A$0'), ('B$1', 'A$1'), ('A$1', 'A$1'), ('B$1', 'B$0')])

##G = nx.DiGraph([('N4$0','N3$1'), ('N3$1','N3$1 AND N2$1'), ('N3$1 AND N2$1','N1$2'), ('N1$2','N1$2 AND N4$0'), ('N1$2 AND N4$0','N2$1'), ('N2$1', 'N2$1 AND N1$2'),('N2$1 AND N1$2','N4$0')])
##    print ExpandedG.nodes()
##    # drawing the graph
##    pos=nx.spring_layout(ExpandedG)
##    nx.draw(ExpandedG, with_labels = True)
##    plt.show()print list(simple_cycles_SM(G))
##print list(simple_cycles_SM(G))


## print list(nx.simple_cycles(G))
##['N4$0', 'N3$1', 'N3$1 AND N2$1', 'N1$2', 'N1$2 AND N4$0', 'N2$1', 'N2$1 AND N1$2']
##pos=nx.spring_layout(G)
##nx.draw(G, with_labels = True)
##plt.show()

def simple_cycles(G):
    def _unblock(thisnode,blocked,B):
        stack=set([thisnode])
        while stack:
            node=stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

    # Johnson's algorithm requires some ordering of the nodes.
    # We assign the arbitrary ordering given by the strongly connected comps
    # There is no need to track the ordering as each node removed as processed.
    subG = type(G)(G.edges_iter()) # save the actual graph so we can mutate it here
                              # We only take the edges because we do not want to
                              # copy edge and node attributes here.
    sccs = list(nx.strongly_connected_components(subG))
    while sccs:
        scc=sccs.pop()
        # order of scc determines ordering of nodes
        startnode = scc.pop()
        # Processing node runs "circuit" routine from recursive version
        path=[startnode]
        blocked = set() # vertex: blocked from search?
        closed = set() # nodes involved in a cycle
        blocked.add(startnode)
        B=collections.defaultdict(set) # graph portions that yield no elementary circuit
        stack=[ (startnode,list(subG[startnode])) ]  # subG gives component nbrs
        while stack:
            thisnode,nbrs = stack[-1]
            if nbrs:
                nextnode = nbrs.pop()
##                if startnode == 'N0$1':
##                    print thisnode,nbrs,":",nextnode,blocked,B,path,stack,startnode
#                    f=raw_input("pause")
                if nextnode == startnode:
                    yield path[:]
                    closed.update(path)
##                    if startnode == 'N0$1':
##                        print "Found a cycle",path,closed
                elif nextnode not in blocked:
                    path.append(nextnode)
                    stack.append( (nextnode,list(subG[nextnode])) )
                    closed.discard(nextnode)
                    blocked.add(nextnode)
                    continue
            # done with nextnode... look for more neighbors
            if not nbrs:  # no more nbrs
                if thisnode in closed:
                    _unblock(thisnode,blocked,B)
                else:
                    for nbr in subG[thisnode]:
                        if thisnode not in B[nbr]:
                            B[nbr].add(thisnode)
                stack.pop()
#                assert path[-1]==thisnode
                path.pop()
        # done processing this node
        subG.remove_node(startnode)
        H=subG.subgraph(scc)  # make smaller to avoid work in SCC routine
        sccs.extend(list(nx.strongly_connected_components(H)))


def findoscillation(ExpandedG, stablemotifs):  # return a list of oscillation candidates from the expanded graph

# conditions:
# (1) the SCC must contain at least 2 virtual nodes of every normal/orginal node
# (2) if the SCC contains a composite node, all its input nodes must also be part of the SCC
# (3)* (not sure if true for multi-level) the oscillating component must not contain stable motifs without composite nodes
    oscillations =[]
    SCCs=[]
    newSCCs=[]
    for item in list(nx.strongly_connected_components(ExpandedG)):
        # filter out single nodes
        if len(item)>1:
            newSCCs.append(list(item))

##    SCCs=temp
    # filter out non-source SCC
    for item1 in newSCCs:
        Flag0=0
        for item2 in newSCCs:
            if item2 != item1:
                if nx.has_path(ExpandedG,list(item2)[0],list(item1)[0]):
                    Flag0=1
        if Flag0 ==0:
            SCCs.append(list(item1))


##    print SCCs

    while SCCs != []:
##        print
##        print 'SCCs:',SCCs
        obj = SCCs.pop(0) # pop up an SCC (list of nodes)
##        print 'obj=',obj
        ExpandedG1 = nx.DiGraph(ExpandedG.subgraph(obj))
##        print 'nodes:', nx.nodes(ExpandedG1), type(ExpandedG1)
##        print 'edges:', nx.edges(ExpandedG1)
        compositenodelist =findinputs(obj,inc_normal=0,mode=0)
        temp=[]
        for item in compositenodelist[1]:
            if item not in temp:
                temp.append(item)
        compositenodelist[1] = temp

##        print 'compositenodelist:',compositenodelist
        # find all composite nodes in obj that do not have all their input nodes in this SCC; remove these composite nodes; remove this SCC, and add sub-SCCs within this SCC
##        print
        Flag1=0
        # check if the SCC satisfies (2): If so, proceed to 3; if not, remove these composite nodes; remove this SCC, and add sub-SCCs within this SCC to stack
        for i in range(0,len(compositenodelist[0])):
            for input in compositenodelist[1][i]:
##                print 'input:',input,i,compositenodelist[1]
                if input not in obj:
                    # remove these composite nodes; remove this SCC, and add sub-SCCs within this SCC
##                    print 'removing composite node: ', compositenodelist[0][i]
                    ExpandedG1.remove_node(compositenodelist[0][i])
##                    print 'nodes:', nx.nodes(ExpandedG1)
##                    print 'edges:', nx.edges(ExpandedG1)
                    newSCCs=[]
                    for item in list(nx.strongly_connected_components(ExpandedG1)):
                        # filter out single nodes
                        if len(item)>1:
                            newSCCs.append(item)
                    SCCs += newSCCs

##                    print list(nx.strongly_connected_components(ExpandedG1))
##                    print 'added SCCs'
##                    print 'SCCs:', SCCs
                    Flag1=1
                    break
            if Flag1==1:
                break

        if Flag1==0:
        #3. check if the SCC contains at least 2 virtual nodes of every normal/orginal node: if so, proceed to 4; if not, remove the corresponding virtual nodes, then add sub-SCCs within this SCC
            unrepeated = unrepeatednode(obj)
##            print unrepeated
            if unrepeated != []:
##                print 'removing unrepeated nodes: ', unrepeated
                for item in unrepeated:
                    ExpandedG1.remove_node(item)
                Flag1=1
                newSCCs=[]
                for item in list(nx.strongly_connected_components(ExpandedG1)):
                    # filter out single nodes
                    if len(item)>1:
                        newSCCs.append(item)
                SCCs += newSCCs

        # 4 & 5. check if the SCC contains a stable motif without a composite node, if so, remove the stable motif, then go to 1; if not, the SCC is an oscillating candidate
        # suspected: incorrect in Multi-level? Jorge has made changes to this section in his dissertation
##        if Flag1==0:
##            simpleSM=[]
##            for sm in stablemotifs:
##                Flag2=0
##                # filter sm s.t. only sms w/o composite node
##                for item in sm:
####                    print item
##                    if item.count('AND')==1:
##                        Flag2=1
##                        break
##                if Flag2==0:
##                    simpleSM.append(sm)
####            print simpleSM
##
##            for sm in simpleSM:
####                print sm,obj
##                if set(sm) & set(obj) == set(sm):
##                # if the SCC contains a stable motif without a composite node, remove the stable motif
##                    Flag1=1
##                    for item in sm:
##                        if item in ExpandedG1:
##                            ExpandedG1.remove_node(item)
##                    newSCCs=[]
##                    for item in list(nx.strongly_connected_components(ExpandedG1)):
##                        # filter out single nodes
##                        if len(item)>1:
##                            newSCCs.append(item)
##                    SCCs += newSCCs

        if Flag1==0:
            oscillations.append(obj)
##        print
    return oscillations

# test examples:
##y = ['A$0* = B$0 OR (C$1 AND B$1)', 'A$1* = B$1 AND C$0', 'A$2* = B$2', 'B$0* = C$0 OR A$0', 'B$1* = C$1 AND A$1', 'B$2* = C$1 AND A$2', 'C$0* = A$0', 'C$1* = A$1 OR A$2']

##z = list(nx.strongly_connected_components(ExpandedG))
##x = findoscillation(y)

##print x


def findstablenodes(SM,mode=1): # from a single SM candidate or oscillating motif, find all nodes in it, with corresponding values.
    # Returns a list of two lists: 1. stablenodes; 2. values
    # if input is 'None' or '[]', i.e. no Stable Motif, return 'None'
    # if input is an oscillation , the value for oscillating nodes will be '@'
    if SM== 'None':
        return 'None'
##    print len(SM)
    nodes=[]
    states=[]
    stablenodes=[]
    values=[]
    Error=0
##    count1=0
##    count2=0
    for i in range (0,len(SM)):
##        print
##        print 'i={}, count={}'.format(i,count1+count2)
        x = findinputsstr(SM[i])
##        print 'x=',x
        # finding all nodes and values from a set of input nodes
        for j in range (0,len(x)):
##            print 'x[{}]= {}'.format(j,x[j])
            node1 = x[j].split("$")[0].strip()
            state1 = x[j].split("$")[1].strip()
            if node1 not in nodes:
                nodes.append(node1)
                states.append(state1)
                a = node1
                a += '$'
                a += state1
                stablenodes.append(a)
                values.append(1)
##                count1 += 1

            else:       # if the same node but different state, then enter as oscillation
                for k in range (0, len(nodes)):
                    if node1 == nodes[k]:
                        if state1 != states[k]:
                            # oscillation
                            a = node1
                            a += '$'
                            a += state1
                            if a not in stablenodes:
##                                count2 += 1
                                nodes.append(node1) # not sure if right here
                                states.append(state1)
##                                print node1,state1,states[k]
                                stablenodes.append(a)
                                values.append('@')
                                y= nodes[k] + '$' + str(states[k])
                                values[stablenodes.index(y)]='@'
##        print stablenodes,values

    if mode==0:
        return [nodes,states,Error]
    else:
##        print 'stablenodes:',stablenodes,values
        return [stablenodes,values]

#TBD: The result will include all virtual nodes of the same original node. e.g if the stable motif contains A$1, then A$0, A$2, etc.will all gets 0



# test

##obj = [['N0$0* =N0$0', 'N0$1* =N0$1', 'N1$0* = 0', 'N1$1* = 1'], [['N0$1'], ['N1$1']]]
##obj = [['N0$0* =(N8$0 AND N2$1) OR (N8$0 AND N2$2)', 'N0$1* =(N8$0 AND N2$0) OR (N8$1 AND N2$0) OR (N8$1 AND N2$1) OR (N8$1 AND N2$2) OR (N8$2 AND N2$1) OR (N8$2 AND N2$2)', 'N0$2* =(N8$2 AND N2$0)', 'N1$0* =(N6$1 AND N9$1)', 'N1$1* =(N6$0 AND N9$0) OR (N6$1 AND N9$0) OR (N6$2 AND N9$2)', 'N1$2* =(N6$0 AND N9$1) OR (N6$0 AND N9$2) OR (N6$1 AND N9$2) OR (N6$2 AND N9$0) OR (N6$2 AND N9$1)', 'N2$0* =(N8$0 AND N3$0) OR (N8$0 AND N3$2) OR (N8$1 AND N3$0) OR (N8$1 AND N3$1) OR (N8$2 AND N3$2)', 'N2$1* =(N8$0 AND N3$1) OR (N8$1 AND N3$2)', 'N2$2* =(N8$2 AND N3$0) OR (N8$2 AND N3$1)', 'N3$0* =(N6$0 AND N0$0)', 'N3$1* =(N6$1 AND N0$0) OR (N6$1 AND N0$1) OR (N6$2 AND N0$1) OR (N6$2 AND N0$2)', 'N3$2* =(N6$0 AND N0$1) OR (N6$0 AND N0$2) OR (N6$1 AND N0$2) OR (N6$2 AND N0$0)', 'N4$0* =(N5$1 AND N7$0) OR (N5$1 AND N7$2) OR (N5$2 AND N7$2)', 'N4$1* =(N5$0 AND N7$0) OR (N5$0 AND N7$1) OR (N5$0 AND N7$2) OR (N5$1 AND N7$1) OR (N5$2 AND N7$0) OR (N5$2 AND N7$1)', 'N5$0* =(N2$1 AND N3$2)', 'N5$1* =(N2$0 AND N3$1) OR (N2$1 AND N3$0) OR (N2$1 AND N3$1) OR (N2$2 AND N3$2)', 'N5$2* =(N2$0 AND N3$0) OR (N2$0 AND N3$2) OR (N2$2 AND N3$0) OR (N2$2 AND N3$1)', 'N6$0* =(N3$0 AND N5$1) OR (N3$1 AND N5$0) OR (N3$2 AND N5$0) OR (N3$2 AND N5$1)', 'N6$1* =(N3$0 AND N5$0) OR (N3$1 AND N5$2)', 'N6$2* =(N3$0 AND N5$2) OR (N3$1 AND N5$1) OR (N3$2 AND N5$2)', 'N7$0* =(N3$0 AND N1$2) OR (N3$2 AND N1$0) OR (N3$2 AND N1$1)', 'N7$1* =(N3$0 AND N1$1)', 'N7$2* =(N3$0 AND N1$0) OR (N3$1 AND N1$0) OR (N3$1 AND N1$1) OR (N3$1 AND N1$2) OR (N3$2 AND N1$2)', 'N8$0* =(N4$0 AND N1$0) OR (N4$0 AND N1$1) OR (N4$1 AND N1$0) OR (N4$1 AND N1$2)', 'N8$1* =(N4$1 AND N1$1)', 'N8$2* =(N4$0 AND N1$2)', 'N9$0* =(N3$0 AND N4$0) OR (N3$1 AND N4$1) OR (N3$2 AND N4$0) OR (N3$2 AND N4$1)', 'N9$1* =(N3$0 AND N4$1)', 'N9$2* =(N3$1 AND N4$0)'], [['N5$1 AND N7$2', 'N4$0', 'N3$0 AND N4$0', 'N9$0', 'N6$1 AND N9$0', 'N1$1', 'N4$0 AND N1$1', 'N3$2 AND N1$1', 'N7$0', 'N5$2 AND N7$0', 'N4$1', 'N4$1 AND N1$1', 'N8$1', 'N3$0 AND N4$1', 'N9$1', 'N6$1 AND N9$1', 'N1$0', 'N8$0', 'N8$0 AND N2$2', 'N0$0', 'N6$1 AND N0$0', 'N3$1', 'N8$1 AND N3$1', 'N3$1 AND N4$1', 'N3$1 AND N4$0', 'N9$2', 'N8$0 AND N3$1', 'N2$0 AND N3$1', 'N5$1', 'N3$1 AND N5$1', 'N3$2 AND N5$1', 'N6$0', 'N6$0 AND N9$0', 'N6$0 AND N9$1', 'N6$0 AND N9$2', 'N6$0 AND N0$0', 'N3$0', 'N3$0 AND N1$1', 'N7$1', 'N8$1 AND N3$0', 'N3$0 AND N5$1', 'N8$0 AND N3$0', 'N6$0 AND N0$2', 'N3$2', 'N8$1 AND N3$2', 'N2$1', 'N2$1 AND N3$1', 'N2$1 AND N3$0', 'N8$0 AND N2$1', 'N2$1 AND N3$2', 'N5$0', 'N3$2 AND N5$0', 'N3$1 AND N5$0', 'N3$0 AND N5$0', 'N8$0 AND N3$2', 'N2$0', 'N2$0 AND N3$0', 'N2$0 AND N3$2', 'N5$2', 'N3$1 AND N5$2', 'N6$1', 'N6$1 AND N9$2', 'N3$0 AND N5$2', 'N3$2 AND N5$2', 'N6$2', 'N6$2 AND N9$2', 'N6$2 AND N0$0', 'N6$2 AND N9$0', 'N6$2 AND N9$1', 'N1$2', 'N4$0 AND N1$2', 'N8$2', 'N8$2 AND N3$2', 'N8$2 AND N3$0', 'N8$2 AND N3$1', 'N2$2', 'N2$2 AND N3$1', 'N2$2 AND N3$0', 'N2$2 AND N3$2', 'N8$2 AND N2$2', 'N8$2 AND N2$1', 'N3$0 AND N1$2', 'N4$1 AND N1$2', 'N8$0 AND N2$0', 'N0$1', 'N6$0 AND N0$1', 'N6$2 AND N0$1', 'N6$1 AND N0$1', 'N8$2 AND N2$0', 'N0$2', 'N6$2 AND N0$2', 'N6$1 AND N0$2', 'N3$2 AND N1$2', 'N3$0 AND N1$0', 'N7$2', 'N5$2 AND N7$2', 'N3$2 AND N1$0', 'N5$1 AND N7$0']]]

##print obj[1][len(obj[1])-1]
##stablenodes = findstablenodes(obj[1][len(obj[1])-1])

##x = ['B$2 AND C$2','B$0', 'C$1','B$1','B$0 AND B$1','B$2']
##
##stablenodes = findstablenodes(x)
##print stablenodes


##SMcandidates = candidate(cycles)
##
##
##print "SM candidates in the expanded network:"
##for item in SMcandidates:
##    print item

##SMcandidates = candidate(cycles)


##print "SM candidates in the expanded network:"
##for item in SMcandidates:
##    print item
