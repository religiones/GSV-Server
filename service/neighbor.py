from py2neo import *

class NeighborService:
    def __init__(self, graphDevice):
        if graphDevice == None:
            self.graphDevice = Graph("bolt://localhost:7687", auth=("neo4j", "chinavis"))
        else:
            self.graphDevice = graphDevice

    def getNeighborsByCommunity(self, communities):
        neighbor_sql = "match (n) where n.id in ["
        for community in communities:
            neighbor_sql += str(community)+","
        neighbor_sql = neighbor_sql.strip(',')+"]"+" return n.community, count(*)"
        neighbor_res = self.graphDevice.run(neighbor_sql)
        for community in neighbor_res:
            print(community)
        return "111"