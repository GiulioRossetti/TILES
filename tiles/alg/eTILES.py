# -*- coding: utf-8 -*-
"""
    Created on 20/09/2016
    @author: Giulio Rossetti
"""
import networkx as nx
import gzip
import datetime
import time
from .TILES import TILES


import sys
if sys.version_info > (2, 7):
    from io import StringIO
else:
    from cStringIO import StringIO

__author__ = "Giulio Rossetti"
__contact__ = "giulio.rossetti@gmail.com"
__website__ = "about.giuliorossetti.net"
__license__ = "BSD"


class eTILES(TILES):
    """
        TILES
        Algorithm for evolutionary community discovery
        ***Explicit removal***
    """

    def __init__(self, filename=None, g=nx.Graph(), obs=7, path="", start=None, end=None):
        """
            Constructor
            :param g: networkx graph
            :param obs: observation window (days)
            :param path: Path where generate the results and find the edge file
            :param start: starting date
            :param end: ending date
        """
        super(self.__class__, self).__init__(filename, g, 0,obs, path, start, end)

    def execute(self):
        """
            Execute TILES algorithm
        """
        self.status.write(u"Started! (%s) \n\n" % str(time.asctime(time.localtime(time.time()))))
        self.status.flush()

        with open("%s" % self.filename, 'r') as f:
            first_line = f.readline()

        actual_time = datetime.datetime.fromtimestamp(float(first_line.rstrip().split("\t")[3]))
        last_break = actual_time
        f.close()

        count = 0

        #################################################
        #                   Main Cycle                  #
        #################################################

        f = open("%s/%s" % (self.base, self.filename))
        for l in f:
            l = l.rstrip().split("\t")
            self.added += 1
            e = {}
            action = l[0]
            u = int(l[1])
            v = int(l[2])
            dt = datetime.datetime.fromtimestamp(float(l[3]))

            e['weight'] = 1
            e["u"] = u
            e["v"] = v

            #############################################
            #               Observations                #
            #############################################

            gap = dt - last_break
            dif = gap.days

            if dif >= self.obs:
                last_break = dt

                print("New slice. Starting Day: %s" % dt)

                self.status.write(u"Saving Slice %s: Starting %s ending %s - (%s)\n" %
                                  (self.actual_slice, actual_time, dt,
                                   str(time.asctime(time.localtime(time.time())))))

                self.status.write(u"Edge Added: %d\tEdge removed: %d\n" % (self.added, self.removed))
                self.added = 0
                self.removed = 0

                actual_time = dt
                self.status.flush()

                self.splits = gzip.open("%s/%s/splitting-%d.gz" % (self.base, self.path, self.actual_slice), "wt", 3)
                self.splits.write(self.spl.getvalue())
                self.splits.flush()
                self.splits.close()
                self.spl = StringIO()

                self.print_communities()
                self.status.write(
                    u"\nStarted Slice %s (%s)\n" % (self.actual_slice, str(datetime.datetime.now().time())))

            if u == v:
                continue

            # Check if edge removal is required
            if action == '-':
                self.remove_edge(e)
                continue

            if not self.g.has_node(u):
                self.g.add_node(u)
                self.g.node[u]['c_coms'] = {}

            if not self.g.has_node(v):
                self.g.add_node(v)
                self.g.node[v]['c_coms'] = {}

            if self.g.has_edge(u, v):
                w = self.g.edge[u][v]["weight"]
                self.g.edge[u][v]["weight"] = w + e['weight']
                continue
            else:
                self.g.add_edge(u, v)
                self.g.edge[u][v]["weight"] = e['weight']

            u_n = self.g.neighbors(u)
            v_n = self.g.neighbors(v)

            #############################################
            #               Evolution                   #
            #############################################

            # new community of peripheral nodes (new nodes)
            if len(u_n) > 1 and len(v_n) > 1:
                common_neighbors = set(u_n) & set(v_n)
                self.common_neighbors_analysis(u, v, common_neighbors)

            count += 1

        #  Last writing
        self.status.write(u"Slice %s: Starting %s ending %s - (%s)\n" %
                          (self.actual_slice, actual_time, actual_time,
                           str(time.asctime(time.localtime(time.time())))))
        self.status.write(u"Edge Added: %d\tEdge removed: %d\n" % (self.added, self.removed))
        self.added = 0
        self.removed = 0

        self.print_communities()
        self.status.write(u"Finished! (%s)" % str(time.asctime(time.localtime(time.time()))))
        self.status.flush()
        self.status.close()

    def remove_edge(self, e):
        """
            Edge removal procedure
            :param actual_time: timestamp of the last inserted edge
            :param qr: Priority Queue containing the edges to be removed ordered by their timestamps
        """

        coms_to_change = {}

        self.removed += 1
        u = e["u"]
        v = e["v"]

        if self.g.has_edge(u, v):

            # u and v shared communities
            if len(self.g.neighbors(u)) > 1 and len(self.g.neighbors(v)) > 1:
                coms = set(self.g.node[u]['c_coms'].keys()) & set(self.g.node[v]['c_coms'].keys())

                for c in coms:
                    if c not in coms_to_change:
                        cn = set(self.g.neighbors(u)) & set(self.g.neighbors(v))
                        coms_to_change[c] = [u, v]
                        coms_to_change[c].extend(list(cn))
                    else:
                        cn = set(self.g.neighbors(u)) & set(self.g.neighbors(v))
                        coms_to_change[c].extend(list(cn))
                        coms_to_change[c].extend([u, v])
                        ctc = set(coms_to_change[c])
                        coms_to_change[c] = list(ctc)
            else:
                if len(self.g.neighbors(u)) < 2:
                    coms_u = self.g.node[u]['c_coms'].keys()
                    for cid in coms_u:
                        self.remove_from_community(u, cid)

                if len(self.g.neighbors(v)) < 2:
                    coms_v = self.g.node[v]['c_coms'].keys()
                    for cid in coms_v:
                        self.remove_from_community(v, cid)

            self.g.remove_edge(u, v)

        # update of shared communities
        self.update_shared_coms(coms_to_change)
