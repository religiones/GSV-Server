from distutils.util import strtobool
from py2neo import *

class GraphService:
    def __init__(self, graphDevice):
        if graphDevice == None:
            self.graphDevice = Graph("bolt://localhost:7687", auth=("neo4j", "chinavis"))
        else:
            self.graphDevice = graphDevice

    def nodeTypeSelect(self, node):
        colorArray = ['#f49c84','#099EDA','#FEE301','#ABB7BD','#F4801F','#D6C223',
                '#D75D73','#E0592B', '#58B7B3', '#68bb8c','#3F3B6C']
        if "Domain" in node["id"]:
            return {
                "id": node["id"],
                "name": node["name"],
                "nodeType": "Domain",
                "style": {
                    "fill": "#6ECCAF",
                    "lineWidth": 1,
                    # "opacity": 0.6
                },
                "community": node["community"],
                "donutAttrs": {
                    "porn": strtobool(node["porn"]),
                    "gambling": strtobool(node["gambling"]),
                    "fraud": strtobool(node["fraud"]),
                    "drug": strtobool(node["drug"]),
                    "gun": strtobool(node["gun"]),
                    "hacker": strtobool(node["hacker"]),
                    "trading": strtobool(node["trading"]),
                    "pay": strtobool(node["pay"]),
                    "other": strtobool(node["other"])
                },
                "donutColorMap": {
                    "porn": colorArray[0],
                    "gambling": colorArray[1],
                    "fraud": colorArray[2],
                    "drug": colorArray[3],
                    "gun": colorArray[4],
                    "hacker": colorArray[5],
                    "trading": colorArray[6],
                    "pay": colorArray[7],
                    "other": colorArray[8]
                }
            }
        elif "IP" in node["id"]:
            return {
                "id": node["id"],
                "name": node["name"],
                "nodeType": "IP",
                "style": {
                    "fill": "#FF6D28",
                    "lineWidth": 1,
                    # "opacity": 0.6
                },
                "community": node["community"],
                "attrs": {
                    "ipc_id": node["ipc_id"],
                    "ipc": node["ipc"]
                }
            }
        else:
            return {
                "id": node["id"],
                "name": node["name"],
                "nodeType": "Cert",
                "style": {
                    "fill": "#5C2E7E",
                    "lineWidth": 1,
                    # "opacity": 0.6
                },
                "community": node["community"]
            }

    def getGraphByCommunity(self, id):
        node_sql = "match (n) where n.community ="+id+" return n"
        edge_sql = "match (n)-[r]->(m) where n.community="+id+" and m.community="+id+" return n.id,m.id"
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