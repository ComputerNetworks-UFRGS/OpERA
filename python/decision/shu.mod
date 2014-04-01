
param n;
# number of links
param l;
# number of rates
param u;
## SETS ##
# set of channels
set M := {1..n};
# set of cr links
set N := {1..l}; #CR Links
# set of rates supported per channel
set K := {1..u};

## DEPENDENT PARAMETERS ##
param Pi{m in M};
#Calculating the Bandwidth
param B {m in M};
#param R {m in M, i in N} := B[m] * log(1 + AWGN[m]/8)/log(2);
#param sinr {n in  N, k in K, q in  Q} := (2 ** (2 * qv[q]) - 1 ) *
# ( 1/3 *(1/QAM * Pe/4) ** 2);

## VARIABLES ##
var y {m in  M, k in K, i in N}, binary;
#var P {m in M, i in N};


param I {i in N, j in N};
param U{k in K};
param C{m in M}; 
param gama{m in M, k in K};
param Pmax { i in N};

### OJECTIVE ###
maximize bitrate: sum {m in M, i in N, k in K}( B[m] * U[k] * y[m, k, i]);

## CONSTRAINTS
s.t. cr_to_pr{m in M, i in N}: C[m] * sum { k in  K }( gama[m, k] * y[m,k,i] ), <= Pi[m];

s.t. power_suply { i in  N }: sum{m in  M}( C[m] * sum { k in K }( gama[m, k] * y[m,k,i] ) ), <= Pmax[i];

#s.t. cr_to_cr { m in M, (i,j) in N cross N : i != j }:  sum{k in K} (y[m,k,i]) + sum { k in K } ( y[m,k,j] ), <= 2- I[i,j];
s.t. cr_to_cr { m in M, (i,j) in N cross N : i != j }:  sum{k in K} (y[m,k,i]) + sum { k in K } ( y[m,k,j] ), <= 2- I[i,j];
s.t. one_transmission_per_cr { i in N} : sum {m in M, k in K}(y[m,k,i]), <=1;

s.t. one_channel {m in M} : sum {i in N, k in K}(y[m,k,i]), <=1;

#s.t. all_channels_must_be_used { m in M} : sum {i in N, k in K}(y[m,k,i]) >=1;
solve;

printf "ret=[";
for {i in N, m in M, k in K : y[m,k,i] == 1}{
	printf "[%d, %d],", i, m;
}
printf "]";
end;
