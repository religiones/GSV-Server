from distutils.util import strtobool
from py2neo import *

class GraphService:
    def __init__(self, graphDevice):
        if graphDevice == None:
            self.graphDevice = Graph("bolt://localhost:7687", auth=("neo4j", "chinavis"))
        else:
            self.graphDevice = graphDevice

    def nodeTypeSelect(self, node):
        if "Domain" in node["id"]:
            return {
                "id": node["id"],
                "name": node["name"],
                "type": "Domain",
                "community": node["community"],
                "properties": {
                    "porn": strtobool(node["porn"]),
                    "gambling": strtobool(node["gambling"]),
                    "fraud": strtobool(node["fraud"]),
                    "drug": strtobool(node["drug"]),
                    "gun": strtobool(node["gun"]),
                    "hacker": strtobool(node["hacker"]),
                    "trading": strtobool(node["trading"]),
                    "pay": strtobool(node["pay"]),
                    "other": strtobool(node["other"])
                }
            }
        elif "IP" in node["id"]:
            return {
                "id": node["id"],
                "name": node["name"],
                "type": "IP",
                "community": node["community"],
                "properties": {
                    "ipc_id": node["ipc_id"],
                    "ipc": node["ipc"]
                }
            }
        else:
            return {
                "id": node["id"],
                "name": node["name"],
                "type": "Cert",
                "community": node["community"]
            }

    def getGraphByCommunity(self, id):
        node_sql = "match (n) where n.community ="+id+" return n"
        edge_sql = "match (n)-[r]-(m) where n.community="+id+" and m.community="+id+" return n.id,m.id"
        res_node = self.graphDevice.run(node_sql)
        res_edge = self.graphDevice.run(edge_sql)
        node_list = []
        edge_list = []
        for node in res_node:
            node = node.values()[0]
            node_list.append(self.nodeTypeSelect(node))
        for edge in res_edge:
            edge_list.append({"source": edge["n.id"], "target": edge["m.id"]})
        return {"nodes": node_list, "edges": edge_list}