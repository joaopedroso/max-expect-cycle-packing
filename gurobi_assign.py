from gurobipy import *

def solve_assign(G):
    """solve_assign: solve an assignment problem
    Parameters:
        * G - underlying graph (in networkx format)
    Output:
        * objective value (number of assignments)
        * does not compute/return the corresponding arcs
    """
    model = Model("assignment")
    model.Params.OutputFlag = 0 # silent mode
    V = G.nodes()
    A = set(G.edges())
    x={}
    for (i,j) in A:
        x[i,j] = model.addVar(ub=1, name="x[%s,%s]"%(i,j))
    model.update()
    
    for i in V:
        model.addConstr(quicksum(x[j,i] for j in V if (j,i) in A) == \
                        quicksum(x[i,j] for j in V if (i,j) in A))

        if [j for j in V if (j,i) in A] != []:
            model.addConstr(quicksum(x[j,i] for j in V if (j,i) in A) <= 1)

    model.setObjective(quicksum(x[i,j] for (i,j) in A), GRB.MAXIMIZE)
    model.optimize()
    return model.ObjVal, None
    

def solve_assign_full(G):
    """solve_assign: solve an assignment problem
    Parameters:
        * G - underlying graph (in networkx format)
    Output:
        * objective value (number of assignments)
        * the corresponding arcs
    """
    model = Model("assignment")
    model.Params.OutputFlag = 0 # silent mode
    V = G.nodes()
    A = set(G.edges())
    x={}
    for (i,j) in A:
        x[i,j] = model.addVar(ub=1, name="x[%s,%s]"%(i,j))
    model.update()
    
    for i in V:
        model.addConstr(quicksum(x[j,i] for j in V if (j,i) in A) == \
                        quicksum(x[i,j] for j in V if (i,j) in A))

        if [j for j in V if (j,i) in A] != []:
            model.addConstr(quicksum(x[j,i] for j in V if (j,i) in A) <= 1)

    model.setObjective(quicksum(x[i,j] for (i,j) in A), GRB.MAXIMIZE)
    model.optimize()
    arcs = []
    for (i,j) in x:
        if x[i,j].X > EPS:
            assert x[i,j].X == 1., "x[%d,%d].X=%g" % (i,j,x[i,j].X)
            arcs.append( (i,j) )
    return model.ObjVal, arcs
