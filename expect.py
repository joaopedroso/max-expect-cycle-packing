import sys
from time import clock
import networkx as nx
from networkx.algorithms import isomorphism
from gurobi_assign import solve_assign
from sympy import symbols, factor # simplify


def expectV(G):
    """expectV(G): compute expression for calculating the expectation under node failure
    Parameters:
        * G - underlying graph (in networkx format)
    Returns:
        function for calculating expectation, taking probabilities as parameter
    """
    V = G.nodes()
    A = G.edges()
    g = lambda l: reduce(lambda z, x: z + [y + [x] for y in z], l, [[]])
    S = g(V)
    s = ""
    for R in S:
        if len(R) < 2:
            continue
        Q = set(V) - set(R)
        # print "\t***", R, Q
        RA = []
        for (i,j) in list(A):
            if i in R and j in R:
                RA.append((i,j))
        # print "\t\tremaining graph:", RA
        if len(RA) < 2:
            continue
        Gl = nx.DiGraph(RA)
        z, arcs = solve_assign(Gl)
        # print z, arcs
        if z > 0.5:
            s += " + %s" % int(z+.5)
            for i in R:
                s += "*(1-p%d)" % i
            for i in Q:
                s += "*p%d" % i
    # print "simplified expression:", factor(s)
    return str(factor(s))




def expectA(G):
    """expectA(G): compute expression for calculating the expectation under arc failure
    Parameters, returns: as expectV
    """
    V = G.nodes()
    A = G.edges()
    g = lambda l: reduce(lambda z, x: z + [y + [x] for y in z], l, [[]])
    S = g(A)
    s = ""
    for R in S:
        if len(R) < 2:
            continue
        Q = set(A) - set(R)
        RA = list(R)
        # print "\t\tremaining graph:", RA
        Gl = nx.DiGraph(RA)
        z, arcs = solve_assign(Gl)
        # print "assignment solution:"
        # print z, arcs
        if z > 0.5:
            s += " + %s" % int(z+.5)
            for i in R:
                s += "*(1-p_%d_%d)" % i
            for i in Q:
                s += "*p_%d_%d" % i
    # print "simplified expression:", factor(s)
    return str(factor(s))



zDB = {}
def expectVA(G):
    """expectVA(G): compute expression for calculating the expectation under node and arc failure
    Parameters, returns: as expectV
    """
    V = G.nodes()
    A = G.edges()
    init = clock()
    print "processing", A, "%5g" % (clock() - init)
    g = lambda l: reduce(lambda z, x: z + [y + [x] for y in z], l, [[]])
    S = g(V + A)
    s = ""
    for R in S:
        if len(R) < 4:
            continue
        RA = [(i,j) for (i,j) in A if i in R and j in R and (i,j) in R]
        lenRA = len(RA)
        if lenRA < 2:
            continue
        elif lenRA == 2:
            if RA[0][0] != RA[1][1] or RA[0][1] != RA[1][0]:
                continue
            z = 2
        elif lenRA == 3:
            (i0,j0) = RA[0]
            (i1,j1) = RA[1]
            (i2,j2) = RA[2]
            if (i0 == j1 and j0 == i1)  or  (i0 == j2 and j0 == i2)  or  (i1 == j2 and j1 == i2):
                z = 2
            elif (j0 == i1 and j1 == i2 and j2 == i0) or (j0 == i2 and j2 == i1 and j1 == i0):
                z = 3
            else:
                continue
        else:
            key = frozenset(RA)
            if zDB.has_key(key):
                z = zDB[key]
            else:
                Gl = nx.DiGraph(RA)
                z, arcs = solve_assign(Gl)
                zDB[key] = z

        # print z, arcs
        if z > 0.5:
            s += " + %s" % int(z+.5)
            for i in R: 
                if type(i)==type(1):
                    s += "*(1-p%d)" % i
                else: # i is an arc
                    s += "*(1-p_%d_%d)" % i
            for i in set(V+A) - set(R):	# Q, quitting vertices/arcs
                if type(i)==type(1):
                    s += "*p%d" % i
                else: # i is an arc
                    s += "*p_%d_%d" % i
    return str(factor(s)) # uses too much memory... probably not usable for preparing database for K>4...



def add_graph(Gs, N, arcs):
    """add_graph: check if given graph is isomorphic to another in list, if not add it
    Parameters:
        * Gs - graph database
        * N - number of nodes in the new graph
        * arcs - list of arcs
    Output: True if new graph was added, False if not
    """
    Gn = nx.DiGraph()
    Gn.add_nodes_from(range(1,N+1))
    Gn.add_edges_from(arcs)

    for G in Gs:
        DiGM = isomorphism.DiGraphMatcher(G,Gn)
        if DiGM.is_isomorphic():
            return False
    Gs.append(Gn)
    print "added", Gn.edges(), len(Gs), "graphs"
    return True
        


def mk_graphs(Gs, N, node, arcs):
    """mk_graphs: make a database of non-isomorphic graphs with given number of nodes
    Parameters:
        * Gs - list with current graph database
        * N - number of vertices
        * node - vertex currently being considered as source (from-vertex)
        * arcs - current list of arcs
    Output:
        * list with all non-isomorphic graphs from the initial base
    """
    # modify coming graph by adding all possible arcs from 'node'
    for i in range(N):
        j = i+1
        if j != node and (node,j) not in arcs:
            if add_graph(Gs, N, arcs | set([(node,j)])):
                mk_graphs(Gs, N, node, arcs | set([(node,j)]))
    if node != N:
        mk_graphs(Gs, N, node+1, arcs)
    return Gs



# code for calculating expectations with arc and node failure -- math simplification through sympy
if __name__ == "__main__":
    from cycle_db import cycle_db

    try:
        K = int(sys.argv[1])	# max cycle len to consider
        dbname = sys.argv[2]	# where to store the python code generated
    except:
        print "usage: %s K DBfilename" % sys.argv[0]
        print "    where K is the max cycle size"
        print "          DBfilename is the .py file for saving the cycle/expectation database"
        exit(0)
    
    
    f = open(dbname,"w")
    print >>f, "import networkx as nx"
    print >>f, "from cycle_db import cycle_db, string_to_function"
    print >>f, "DB = cycle_db()"
    print >>f, ""
            
    for N in range(2, K+1):
        arcs = set([(N,1)])
        for i in range(N-1):
            arcs.add((i+1,i+2))
     
        G = nx.DiGraph()
        G.add_nodes_from(range(1,N+1))
        G.add_edges_from(arcs)
        print "base arcs:", G.edges()
        Gs = mk_graphs([G], N, 1, arcs)
        print "\n\nRESULT:", len(Gs), "graphs"

        # nodes: [1, 2]
        # arcs: [(1, 2), (2, 1)]
        arcs = [(1, 2), (2, 1)]
        G = nx.DiGraph()
        G.add_edges_from(arcs)
        
        for G in Gs:
            print "nodes:", G.nodes()
            print "arcs:", G.edges()

            # # graph
            # fname = "GINFO/g_" + "%s_" % N + "-".join("%s%s"%(i,j) for (i,j) in G.edges()) + ".tex"
            # f = open(fname,"w")
            # print >>f, latex_graph(G)
            # f.close()

            # print "tackling failure on vertices...",; sys.stdout.flush()
            # v = expectV(G)
            # expr = string_to_function(s)

             
            # print "tackling failure on arcs...",; sys.stdout.flush()
            # a = expectA(G)

            print "tackling failure on both vertices and arcs..."; sys.stdout.flush()
            va = expectVA(G)
            print >>f, "G = nx.DiGraph()"
            print >>f, "G.add_edges_from(%s)" % G.edges()
            print >>f, "DB.add(G, string_to_function('%s'))" % va
            print >>f, ""
            f.flush()

            print "done"

        print "finished all graphs for N=%d" % N

