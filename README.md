Set of programs for maximizing expectations in a KEP.

- Usage

      - Produce the database of different cycle configurations, as well as expressions for computing their expectations, as python programs; for 3- and 4-cycles:

        $ python expect.py 3 KEP_K3_DB.py

        $ python expect.py 4 KEP_K4_DB.py

        (NOTE: simplifying expressions for K>=4 might use too much space; we provide file KEP_K4_DB.py, which required about one day of computation in a machine with 24 GB.  Without simplifying it would take only a few minutes, but the file/expressions would be about two times larger.)
     
      - for solving a specific instance:
     
        $ python kep_max_expect.py 3 KEP_K3_DB DATA/small/50_01.input.gz
     
      - for solving all the instances in
          - J. P. Pedroso.
          - Maximizing expectation on vertex-disjoint cycle packing.
          - Lecture Notes in Computer Science, volume 8580, pages 32–46.
          - Springer International Publishing, 2014.
          - http://www.dcc.fc.up.pt/~jpp/publications/PDF/DCC-2013-05_KEP.pdf
     
        $ python run_experiment.py 3 KEP_K3_DB DATA results.txt
     
        where DATA must contain subdirectories 'small' and 'big', will all the instance files therein.
        Data is available from
             http://www.dcc.fc.up.pt/~jpp/code/KEP
        Notice that, due to multiple optimal solutions, evaluation of deterministic solutions in a stochastic setting (or the inverse) may not be consistent with the results in the paper.


- Files

      - DATA/mk_probabilities.sh -- script for preparing probabilities for KEP benchmark instances (complement data for Klimentova's instances); uses kep_io.py for reading/writing files.
     
      - DATA/kep_io.py -- instance read/write
     
      - expect.py -- prepare a database with all cycles of given size K
          - tested for K=3, K=4
          - for K=4 it uses a lot of memory (expressions in current database are NOT simplified)...
     
      - cycle_db.py -- interface class for constructing/using cycle database
     
      - gurobi_assign.py -- solve an assignment problem (not limiting cycle size) with gurobi
     
      - kep_max_expect.py -- main functions for optimizing expectation
          - requires the cycle database for working

          - usage: kep_max_expect.py K DBfile instance
            where:
             + K is the max cycle size
             + DBfile is the python program with cycle database hard coded
             + instance in Saidman generator's format
               (corresponding probability information file must exist)

      - run_experiment.py -- runs a full experiment using Klimentova/Pedroso's instances
          - usage: run_experiment.py K DBfile datadir results
            where:
             + K: max cycle size
             + DBfile: python program with cycle database hard coded
             + datadir: should contain 'small' and 'big' subdiretories with instances in Saidman generator's format and the corresponding probability information files
             + results: file where results are written
