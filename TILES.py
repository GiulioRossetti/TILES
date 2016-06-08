"""
    Created on 11/feb/2015
    @author: Giulio Rossetti
"""
import networkx as nx
import gzip
from Queue import PriorityQueue
import datetime
import time
from cStringIO import StringIO

__author__ = "Giulio Rossetti"
__contact__ = "giulio.rossetti@gmail.com"
__website__ = "about.giuliorossetti.net"
__license__ = "BSD"


class TILES(object):
    """
        TILES
        Algorithm for evolutionary community discovery
        ***Mongodb version***
    """

    def __init__(self, filename=None, g=nx.Graph(), ttl=float('inf'), obs=7, path="", start=None, end=None):
        """
            Constructor
            :param con: mongod connection
            :param g: networkx graph
            :param ttl: edge time to live (days)
            :param obs: observation window (days)
            :param path: Path where generate the results and find the edge file
            :param start: starting date
            :param end: ending date
        """
        self.communities = {}
        self.path = path
        self.ttl = ttl
        self.cid = 0
        self.actual_slice = 0
        self.g = g
        self.splits = None
        self.spl = StringIO()
        self.status = open("%s/extraction_status.txt" % path, "w")
        self.removed = 0
        self.added = 0
        self.filename = filename
        self.start = start
        self.end = end
        self.obs = obs

    def execute(self):
        """
            Execute TILES algorithm
        """
        self.status.write("Started! (%s) \n\n" % str(time.asctime(time.localtime(time.time()))))
        self.status.flush()

        qr = PriorityQueue()
        f = open(self.filename)
        actual_time = datetime.datetime.fromtimestamp(float(f.next().split(",")[2]))
        last_break = actual_time
        f.close()

        count = 0

        #################################################
        #                   Main Cycle                  #
        #################################################

        f = open(self.filename)
        for l in f:
            l = l.split(",")
            self.added += 1
            e = {}
            u = int(l[0])
            v = int(l[1])
            dt = datetime.datetime.fromtimestamp(float(l[2]))

            e['weight'] = 1
            e["u"] = l[0]
            e["v"] = l[1]
            # month = dt.month

            #############################################
            #               Observations                #
            #############################################

            gap = dt - last_break
            dif = gap.days

            if dif == self.obs:
                last_break = dt

                print "New slice. Starting Day: %s" % dt

                self.status.write("Saving Slice %s: Starting %s ending %s - (%s)\n" %
                                  (self.actual_slice, actual_time, dt,
                                   str(time.asctime(time.localtime(time.time())))))

                self.status.write("Edge Added: %d\tEdge removed: %d\n" % (self.added, self.removed))
                self.added = 0
                self.removed = 0

                actual_time = dt
                self.status.flush()

                self.splits = gzip.open("%s/splitting-%d.gz" % (self.path, self.actual_slice), "w", 3)
                self.splits.write(self.spl.getvalue())
                self.splits.flush()
                self.splits.close()
                self.spl = StringIO()

                self.__print_communities()
                self.status.write(
                    "\nStarted Slice %s (%s)\n" % (self.actual_slice, str(datetime.datetime.now().time())))

            if u == v:
                continue

            # Check if edge removal is required
            if self.ttl != float('inf'):
                qr.put((dt, e))
                self.__remove(dt, qr)

            if not self.g.has_node(u):
                self.g.add_node(u)
                self.g.node[u]['c_coms'] = {}  # central

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
                self.__common_neighbors_analysis(u, v, common_neighbors)

            count += 1

        #  Last writing
        self.status.write("Slice %s: Starting %s ending %s - (%s)\n" %
                          (self.actual_slice, actual_time, actual_time,
                           str(time.asctime(time.localtime(time.time())))))
        self.status.write("Edge Added: %d\tEdge removed: %d\n" % (self.added, self.removed))
        self.added = 0
        self.removed = 0

        self.__print_communities()
        self.status.write("Finished! (%s)" % str(time.asctime(time.localtime(time.time()))))
        self.status.flush()
        self.status.close()

    @property
    def __new_community_id(self):
        """
            Return a new community identifier
            :return: new community id
        """
        self.cid += 1
        self.communities[self.cid] = {}
        return self.cid

    def __remove(self, actual_time, qr):
        """
            Edge removal procedure
            :param actual_time: timestamp of the last inserted edge
            :param qr: Priority Queue containing the edges to be removed ordered by their timestamps
        """

        coms_to_change = {}
        at = actual_time

        # main cycle on the removal queue
        if not qr.empty():

            t = qr.get()
            timestamp = t[0]
            e = t[1]

            delta = at - timestamp
            displacement = delta.days

            if displacement < self.ttl:
                qr.put((timestamp, e))

            else:
                while self.ttl <= displacement:

                    self.removed += 1
                    u = e["u"]
                    v = e["v"]

                    if self.g.has_edge(u, v):

                        w = self.g.edge[u][v]["weight"]

                        # decreasing link weight if greater than one
                        # (multiple occurrence of the edge: remove only the oldest)
                        if w > 1:
                            self.g.edge[u][v]["weight"] = w - 1
                            qr.put((at, e))

                        else:
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
                                        self.__remove_from_community(u, cid)

                                if len(self.g.neighbors(v)) < 2:
                                    coms_v = self.g.node[v]['c_coms'].keys()
                                    for cid in coms_v:
                                        self.__remove_from_community(v, cid)

                            self.g.remove_edge(u, v)

                    if not qr.empty():
                        t = qr.get()

                        timestamp = t[0]
                        delta = at - timestamp
                        displacement = delta.days

                        e = t[1]

        # update of shared communities
        for c in coms_to_change:

            c_nodes = self.communities[c].keys()

            if len(c_nodes) > 3:

                sub_c = self.g.subgraph(c_nodes)
                c_components = nx.number_connected_components(sub_c)

                # unbroken community
                if c_components == 1:
                    to_mod = sub_c.subgraph(coms_to_change[c])
                    self.__modify_after_removal(to_mod, c)

                # broken community: bigger one maintains the id, the others obtain a new one
                else:
                    new_ids = []

                    first = True
                    components = nx.connected_components(sub_c)
                    for com in components:
                        if first:
                            if len(com) < 3:
                                self.__destroy_community(c)
                            else:
                                to_mod = list(set(com) & set(coms_to_change[c]))
                                sub_c = self.g.subgraph(to_mod)
                                self.__modify_after_removal(sub_c, c)
                            first = False

                        else:
                            if len(com) > 3:
                                # update the memberships: remove the old ones and add the new one
                                to_mod = list(set(com) & set(coms_to_change[c]))
                                sub_c = self.g.subgraph(to_mod)

                                central = self.__centrality_test(sub_c).keys()
                                if len(central) >= 3:
                                    actual_id = self.__new_community_id
                                    new_ids.append(actual_id)
                                    for n in central:
                                        self.__add_to_community(n, actual_id)

                    # splits
                    if len(new_ids) > 0 and self.actual_slice > 0:
                        self.spl.write("%s\t%s\n" % (c, str(new_ids)))
            else:
                self.__destroy_community(c)

    def __modify_after_removal(self, sub_c, c):
        """
            Maintain the clustering coefficient invariant after the edge removal phase
            :param sub_c: sub-community to evaluate
            :param c: community id
        """
        central = self.__centrality_test(sub_c).keys()

        # in case of previous splits, update for the actual nodes
        remove_node = set(self.communities[c].keys()) - set(sub_c.nodes())

        for rm in remove_node:
            self.__remove_from_community(rm, c)

        if len(central) < 3:
            self.__destroy_community(c)
        else:
            not_central = set(sub_c.nodes()) - set(central)
            for n in not_central:
                self.__remove_from_community(n, c)

    def __common_neighbors_analysis(self, u, v, common_neighbors):
        """
            General case in which both the nodes are already present in the net.
            :param u: a node
            :param v: a node
            :param common_neighbors: common neighbors of the two nodes
        """

        # no shared neighbors
        if len(common_neighbors) < 1:
            return

        else:

            shared_coms = set(self.g.node[v]['c_coms'].keys()) & set(self.g.node[u]['c_coms'].keys())
            only_u = set(self.g.node[u]['c_coms'].keys()) - set(self.g.node[v]['c_coms'].keys())
            only_v = set(self.g.node[v]['c_coms'].keys()) - set(self.g.node[u]['c_coms'].keys())

            # community propagation: a community is propagated iff at least two of [u, v, z] are central
            propagated = False

            for z in common_neighbors:
                for c in self.g.node[z]['c_coms'].keys():
                    if c in only_v:
                        self.__add_to_community(u, c)
                        propagated = True

                    if c in only_u:
                        self.__add_to_community(v, c)
                        propagated = True

                for c in shared_coms:
                    if c not in self.g.node[z]['c_coms']:
                        self.__add_to_community(z, c)
                        propagated = True

            else:
                if not propagated:
                    # new community
                    actual_cid = self.__new_community_id
                    self.__add_to_community(u, actual_cid)
                    self.__add_to_community(v, actual_cid)

                    for z in common_neighbors:
                        self.__add_to_community(z, actual_cid)

    def __print_communities(self):
        """
            Print the actual communities
        """

        out_file_coms = gzip.open("%s/strong-communities-%d.gz" % (self.path, self.actual_slice), "w", 3)
        com_string = StringIO()

        nodes_to_coms = {}
        merge = {}
        coms_to_remove = []
        drop_c = []

        self.status.write("Writing Communities (%s)\n" % str(time.asctime(time.localtime(time.time()))))
        self.status.flush()
        for idc, comk in self.communities.iteritems():

            com = comk.keys()

            if self.communities[idc] is not None:
                if len(com) > 2:
                    key = tuple(sorted(com))

                    # Collision check and merge index build (maintaining the lowest id)
                    if key not in nodes_to_coms:
                        nodes_to_coms[key] = idc
                    else:
                        old_id = nodes_to_coms[key]
                        drop = idc
                        if idc < old_id:
                            drop = old_id
                            nodes_to_coms[key] = idc

                        # merged to remove
                        coms_to_remove.append(drop)
                        if not nodes_to_coms[key] in merge:
                            merge[nodes_to_coms[key]] = [idc]
                        else:
                            merge[nodes_to_coms[key]].append(idc)
                else:
                    drop_c.append(idc)
            else:
                drop_c.append(idc)

        write_count = 0
        for k, idk in nodes_to_coms.iteritems():
            write_count += 1
            if write_count % 50000 == 0:
                out_file_coms.write(com_string.getvalue())
                out_file_coms.flush()
                com_string = StringIO()
                write_count = 0
            com_string.write("%d\t%s\n" % (idk, str(list(k))))

        for dc in drop_c:
            self.__destroy_community(dc)

        out_file_coms.write(com_string.getvalue())
        out_file_coms.flush()
        out_file_coms.close()

        # write the graph
        self.status.write("Writing actual graph status (%s)\n" % str(time.asctime(time.localtime(time.time()))))
        self.status.flush()
        out_file_graph = gzip.open("%s/graph-%d.gz" % (self.path, self.actual_slice), "w", 3)
        g_string = StringIO()
        for e in self.g.edges():
            g_string.write("%d\t%s\t%d\n" % (e[0], e[1], self.g.edge[e[0]][e[1]]['weight']))

        out_file_graph.write(g_string.getvalue())
        out_file_graph.flush()
        out_file_graph.close()

        # Write merge status
        self.status.write("Writing merging file (%s)\n" % str(time.asctime(time.localtime(time.time()))))
        self.status.flush()
        out_file_merge = gzip.open("%s/merging-%d.gz" % (self.path, self.actual_slice), "w", 3)
        m_string = StringIO()
        for comid, c_val in merge.iteritems():
            # maintain minimum community after merge
            c_val.append(comid)
            k = min(c_val)
            c_val.remove(k)
            m_string.write("%d\t%s\n" % (k, str(c_val)))
        out_file_merge.write(m_string.getvalue())
        out_file_merge.flush()
        out_file_merge.close()

        # Community Cleaning
        m = 0
        for c in coms_to_remove:
            self.__destroy_community(c)
            m += 1

        self.status.write("Merged communities: %d (%s)\n" % (m, str(time.asctime(time.localtime(time.time())))))

        self.actual_slice += 1
        self.status.write("Total Communities %d (%s)\n" % (len(self.communities.keys()),
                                                           str(time.asctime(time.localtime(time.time())))))
        self.status.flush()

    def __destroy_community(self, cid):
        for n in self.communities[cid].keys():
            self.__remove_from_community(n, cid)
        self.communities.pop(cid, None)

    def __add_to_community(self, node, cid):
        self.g.node[node]['c_coms'][cid] = None
        self.communities[cid][node] = None

    def __remove_from_community(self, node, cid):
        if cid in self.g.node[node]['c_coms']:
            self.g.node[node]['c_coms'].pop(cid, None)
            if node in self.communities[cid]:
                self.communities[cid].pop(node, None)

    def __centrality_test(self, subgraph):
        central = {}

        for u in subgraph.nodes():
            if u not in central:
                cflag = False
                neighbors_u = set(self.g.neighbors(u))
                if len(neighbors_u) > 1:
                    for v in neighbors_u:
                        if u > v:
                            if cflag:
                                break
                            else:
                                neighbors_v = set(self.g.neighbors(v))
                                cn = neighbors_v & neighbors_v
                                if len(cn) > 0:
                                    central[u] = None
                                    central[v] = None
                                    for n in cn:
                                        central[n] = None
                                    cflag = True
        return central


if __name__ == "__main__":
    import argparse

    print "------------------------------------"
    print "              TILES                 "
    print "------------------------------------"
    print "Author: ", __author__
    print "Email:  ", __contact__
    print "WWW:    ", __website__
    print "------------------------------------\n"

    parser = argparse.ArgumentParser()

    parser.add_argument('filename', type=str, help='filename')
    parser.add_argument('-t', '--ttl', type=float, help='ttl', default=float('inf'))
    parser.add_argument('-o', '--obs', type=int, help='obs', default=7)
    parser.add_argument('-p', '--path', type=str, help='path', default="")

    args = parser.parse_args()
    an = TILES(args.network_file, filename=args.filename, ttl=args.ttl, obs=args.obs, path=args.path)
