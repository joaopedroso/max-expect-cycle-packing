"""
kep_max_expect.py:  optimization of KEP instance based on the cycle model

functions:
    - normalize: change a cycle representation so that the first vertex has the lowest label
    - all_cycles: recursive function for cycle enumeration
    - get_all_cycles: wrapper for all_cycles
    - kep_solve_expect: solve the cycle formulation weighting cycle with their expectation value

Copyright (c) by Joao Pedro PEDROSO, 2012
"""


def normalize(cycle):
    cmin = min(cycle)
    while cycle[0] != cmin:
        v = cycle.pop(0)
        cycle.append(v)


def all_cycles(cycles, path, node, tovisit, adj, K):
    for i in adj[node]:
        if i in path:
            j = path.index(i)
            cycle = path[j:]+[node]
            normalize(cycle)
            cycles.add(tuple(cycle))

        if i in tovisit:
            if K-1 > 0:
                all_cycles(cycles, path+[node], i, tovisit-set([i]), adj, K-1)
    return cycles


def get_all_cycles(adj,K):
    """get_all_cycles(adj,K):
    Parameters:
        - adj: adjacency list describing the graph
        - K: maximum cycle size
    Returns:
        cycles list, each cycle represented as a vertex tuple
    """  
    tovisit = set(adj.keys())
    visited = set()
    cycles = set()
    for i in tovisit:
        tmpvisit = set(tovisit)
        tmpvisit.remove(i)
        first = i
        all_cycles(cycles,[],first,tmpvisit,adj,K)
    return cycles


EPS = 1.e-4
import time
import networkx as nx
from networkx.algorithms import isomorphism
from gurobipy import *
def kep_solve_expect(DB, adj, cycles, p):
    model = Model("expectation")
    model.Params.OutputFlag = 0 # silent mode
    x={}
    cmap, nmap, on_cyc = {}, {}, {}
    for i in adj:
        on_cyc[i] = set()
    n = 1
    for c in cycles:
        cmap[c] = n
        nmap[n] = c
        for i in c:
            on_cyc[i].add(n)
        x[n] = model.addVar(vtype="B", name="x(%s)"%(n))
        n += 1
    model.update()

    for i in on_cyc:
        cs = on_cyc[i]
        if len(cs) > 1:
            model.addConstr(quicksum(x[j] for j in cs) <= 1, "cycles(%s)"%i)

    E = {}
    for c in cycles:
        # make graph for current cycle
        arcs = []
        for i in adj:
            for j in adj[i]:
                if i in c and j in c:
                    arcs.append((i,j))
        G = nx.DiGraph()
        G.add_edges_from(arcs)
        # E[c] = expectVA(G,p)   ### for calculating expectations in runtime; check expectVA.py
        E[c] = DB.expect(G,p)  ### for using expectations' expressions stored in a database

    model.setObjective(quicksum(E[c] * x[cmap[c]] for c in cycles), GRB.MAXIMIZE)
    model.optimize()
    # model.write("tmp.lp")
    sol = []
    for j in x:
        if x[j].X > EPS:
            sol.append(nmap[j])
    return sorted(sol), model.ObjVal



def eval_sol_expect(DB, adj, sol, p):
    """eval_sol_expect: evaluate expectation for a solution under known probabilities of failure
    Parameters:
        - adj:
        - sol:
    Returns:
        expectation value
    """
    E = 0
    for c in sol:
        # make graph for current cycle
        arcs = []
        for i in adj:
            for j in adj[i]:
                if i in c and j in c:
                    arcs.append((i,j))
        G = nx.DiGraph()
        G.add_edges_from(arcs)
        E += DB.expect(G,p)

    return E



if __name__ == "__main__":
    import sys
    from kep_io import read_prob
    try:
        K = int(sys.argv[1])
        dbfile = sys.argv[2]
        instance = sys.argv[3]
    except:
        print "usage: %s K DBfile instance" % sys.argv[0]
        print "    where - K is the max cycle size"
        print "          - DBfile is the python program with cycle database hard coded"
        print "          - instance in Saidman generator's format"
        print "            (corresponding probability information file must exist)"
        exit(0)

    adj, w, p = read_prob(instance)
    dbfile = dbfile.replace(".py", "")
    exec("from %s import DB" % dbfile)	# import database -- may take a long time...
    print("loaded %s" % dbfile)

    # prepare problem: enumerate cyles
    cycles = get_all_cycles(adj,K)
    print len(cycles), "cycles, enumeration time:", time.clock(), "s"

    # deterministic model on same graph, for comparison with stochastic 
    q = {}
    for i in adj:
        q[i] = 0.
        for j in adj[i]:
            q[i,j] = 0.

    # solve models
    solS, objS = kep_solve_expect(DB, adj, cycles, p)	# stochastic
    solD, objD = kep_solve_expect(DB, adj, cycles, q)	# deterministic

    # obtain cross-evaluation of the solutions
    objSinD = eval_sol_expect(DB, adj, solS, q)
    objDinS = eval_sol_expect(DB, adj, solD, p)

    print 'solution to stochastic model:', solS, objS
    print '         evaluated in a deterministic reality:', objSinD
    print 'solution to deterministic model:', solD, objD
    print '         evaluated in a stochastic reality:', objDinS
