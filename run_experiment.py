import sys
import time
from kep_io import read_prob
from kep_max_expect import get_all_cycles, kep_solve_expect, eval_sol_expect
try:
    K = int(sys.argv[1])
    dbfile = sys.argv[2]
    datadir = sys.argv[3]
    results = sys.argv[4]
except:
    print "usage: %s K DBfile datadir results" % sys.argv[0]
    print "    where - K: max cycle size"
    print "          - DBfile: python program with cycle database hard coded"
    print "          - datadir: should contain 'small' and 'big' subdiretories with"
    print "            instances in Saidman generator's format and the"
    print "            corresponding probability information files"
    print "          - results: file where results are written"
    exit(0)


def run(inst):
    adj, w, p = read_prob(inst)
    
    # prepare problem: enumerate cyles
    cycles = get_all_cycles(adj,K)
     
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

    return len(cycles), objS, objD, objSinD, objDinS

def mean(x):
    return float(sum(x))/len(x) if len(x) > 0 else float('nan')

from math import sqrt
def mean_stddev(v):
    n = len(v)
    if n == 0:
        return float('nan'), float('nan')
    mean = sum(v)/n
    var = sum((x - mean)**2 for x in v)/n
    return mean, sqrt(var)


dbfile = dbfile.replace(".py", "")
exec("from %s import DB" % dbfile)
print("loaded %s" % dbfile)

f = open(results, "a")
# test small and big instances
for (SIZES, sname, snumber) in [
    ([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], "small", 50),
    ([70, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000], "big", 10)
    ]:
    print >>f, "%s instances" % sname
    print >>f, ("%s\t"+"%12s\t"*9) % ("size", "|C|",
                                      "objDet", "objDetInStoch", "missedDet", "(sdddev)",
                                      "objStoch", "objStochInDet", "missedStoch", "(stddev)")
    for size in SIZES:
        C, objS, objD, objSinD, objDinS = [], [], [], [], []
        missedS, missedD = [], []
        for rnd in range(1,1+snumber):
            filename = datadir + "/%s/%d_%02d.input.gz" % (sname, size, rnd)
            C_, objS_, objD_, objSinD_, objDinS_ = run(filename)
            print ("%s\t"+"%12g\t"*5) % (filename, C_, objS_, objD_, objSinD_, objDinS_); sys.stdout.flush()
            C.append(C_)
            objS.append(objS_)
            objD.append(objD_)
            objSinD.append(objSinD_)
            objDinS.append(objDinS_)
            missedD.append(0. if objS_ == 0 else 100.*(objS_ - objDinS_)/objS_)
            missedS.append(0. if objD_ == 0 else 100.*(objD_ - objSinD_)/objD_)
     
        mD, sD = mean_stddev(missedD)
        mS, sS = mean_stddev(missedS)
        print >>f, ("%d\t"+"%12g\t"*9) % (size, mean(C),
                                          mean(objD), mean(objDinS), mD, sD,
                                          mean(objS), mean(objSinD), mS, sS
                                          )
        f.flush()
    print >>f, ""
               
