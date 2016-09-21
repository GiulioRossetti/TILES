# TILES

Community discovery has emerged during the last decade as one of the most challenging problems in social network analysis. Many algorithms have been proposed to find communities on static networks, i.e. networks which do not change in time. However, social networks are dynamic realities (e.g. call graphs, online social networks): in such scenarios static community discovery fails to identify a partition of the graph that is semantically consistent with the temporal information expressed by the data. 
Tiles is an algorithm that extracts overlapping communities and tracks their evolution in time following an online iterative procedure. It operates following a domino effect strategy which dynamically recomputes nodes community memberships whenever a new interaction takes place. 

## Citation
If you use our algorithm please cite the following work:

>Giulio Rossetti, Luca Pappalardo, Dino Pedreschi, Fosca Giannotti (2016): 
>Tiles: an online algorithm for community discovery in dynamic social networks. 
>In: Machine Learning Journal, 2016. [10.1007/s10994-016-5582-8](doi:10.1007/s10994-016-5582-8)

## Implementation details

Two implementation of Tiles are available on this repository:
- Vanilla (Tiles.py)
- Edge explicit removal (TILES_explicit_removal.py)

The former implementation is designed to cope with datasets for which edge vanishing events are not explicitly expressed: it implements an edge decay strategy (as detailed in the original paper). 
Conversely, the latter, implementation assume explict knowledge of edge vanishing events.

Both the implementations require as input an edgelist file (tab separated) with the following specs:

(Vanilla)
```
node_id0    node_id1    timestamp
```
(Explicit removal)
```
action  node_id0    node_id1    timestamp
```
Where accepted actions are: edge removal (identified by -) and edge creation (identified by +). 
Timestamps are (seconds truncated) unix timestamps.
The input file should present interactions chronologically ordered from the oldest (first line) to the newest (last file line)

# Execution
Tiles is written in python and requires the following package to run:
- python 2.7.10
- networkx
- cStringIO
- date
- datetime
- Queue
- gzip

The algorithm can be used as standalone program as well as integrated in python scripts.

## Standalone

```bash

python Tiles.py filename -t ttl -o obs -p path 
```

where:
* filename: edgelist filename
* ttl: edge time to live (in days. Default +inf, i.e. no edge removal)
* obs: number of days from a community observation to the subsequent one (default 7)
* path: existing folder for the output files (optional)

The explicit removal version does not expose the ttl parameter.

## As python library
```bash
import Tiles as t
tl = t.TILES("filename.tsc", ttl=7, obs=30)
tl.execute()
```

# Execution Results
Tiles will output, for each observation window, a series of gzip files describing:

- current graph status
- current community partition
- community merged
- community splitted

Moreover an "extraction_status.txt" files will be generated containing detailed information on Tiles'execution.
