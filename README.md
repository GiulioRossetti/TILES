# TILES - Dynamic Community Discovery

[![Build Status](https://travis-ci.org/GiulioRossetti/TILES.svg?branch=master)](https://travis-ci.org/GiulioRossetti/TILES)
[![Coverage Status](https://coveralls.io/repos/github/GiulioRossetti/TILES/badge.svg?branch=master)](https://coveralls.io/github/GiulioRossetti/TILES?branch=master)
[![pyversions](https://img.shields.io/pypi/pyversions/TILES.svg)](https://badge.fury.io/py/TILES)
[![PyPI version](https://badge.fury.io/py/tiles.svg)](https://badge.fury.io/py/TILES)
[![Updates](https://pyup.io/repos/github/GiulioRossetti/TILES/shield.svg)](https://pyup.io/repos/github/GiulioRossetti/TILES/)
[![BCH compliance](https://bettercodehub.com/edge/badge/GiulioRossetti/TILES?branch=master)](https://bettercodehub.com/)
[![DOI](https://zenodo.org/badge/60351955.svg)](https://zenodo.org/badge/latestdoi/60351955)



Community discovery has emerged during the last decade as one of the most challenging problems in social network analysis. Many algorithms have been proposed to find communities on static networks, i.e. networks which do not change in time. However, social networks are dynamic realities (e.g. call graphs, online social networks): in such scenarios static community discovery fails to identify a partition of the graph that is semantically consistent with the temporal information expressed by the data. 
Tiles is an algorithm that extracts overlapping communities and tracks their evolution in time following an online iterative procedure. It operates following a domino effect strategy which dynamically recomputes nodes community memberships whenever a new interaction takes place. 

## Citation
If you use our algorithm please cite the following work:

>Giulio Rossetti, Luca Pappalardo, Dino Pedreschi, Fosca Giannotti (2016): 
>["Tiles: an online algorithm for community discovery in dynamic social networks"](http://link.springer.com/article/10.1007/s10994-016-5582-8). 
>In: Machine Learning Journal, 2016. [10.1007/s10994-016-5582-8](doi:10.1007/s10994-016-5582-8)

## Installation

In order to install the package just download (or clone) the current project and copy the demon folder in the root of your application.

Alternatively use pip:
```bash
sudo pip install tiles
```

## Implementation details

Two implementation of Tiles are available on this repository:
- Vanilla (TILES)
- Edge explicit removal (eTILES)

The former implementation is designed to cope with datasets for which edge vanishing events are not explicitly expressed: it implements an edge decay strategy (as detailed in the original paper). 
Conversely, the latter, implementation assume explict knowledge of edge vanishing events.

Both the implementations require as input an edgelist file (tab separated) with the following specs:

(TILES - Vanilla)
```
node_id0    node_id1    timestamp
```
(eTILES - Explicit removal)
```
action  node_id0    node_id1    timestamp
```
Where accepted actions are: edge removal (identified by -) and edge creation (identified by +). 
Timestamps are (seconds truncated) unix timestamps.
The input file should present interactions chronologically ordered from the oldest (first line) to the newest (last file line)

# Execution
Tiles is written in python and requires the following package to run:
- networkx

The algorithm can be used as standalone program as well as integrated in python scripts.

## Standalone

```bash

python tiles filename -o obs -p path -m TTL|Explicit [-t ttl]
```

where:
* filename: edgelist filename
* obs: number of days from a community observation to the subsequent one (default 7)
* mode: either to execute TILES or eTILES (explicit edge removal)
* ttl: edge time to live in days. (Optional. Default +inf, i.e. no edge removal)
* path: existing folder for the output files (optional)

The explicit removal version does not expose the ttl parameter.

## As python library
```python
import tiles as t
tl = t.TILES("filename.tsc", ttl=7, obs=30)
tl.execute()
```

or

```python
import tiles as t
tl = t.eTILES("filename.tsc", obs=30)
tl.execute()
```

# Execution Results
Tiles will output, for each observation window, a series of gzip files describing:

- current graph status
- current community partition
- community merged
- community splitted

Moreover an "extraction_status.txt" files will be generated containing detailed information on Tiles'execution.
