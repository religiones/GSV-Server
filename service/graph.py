import queue
import threading
import time
from distutils.util import strtobool
from py2neo import *

class graphThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

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
                "comboId": "combo-"+str(node["community"]),
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
                "comboId": "combo-"+str(node["community"]),
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
                "community": node["community"],
                "comboId": "combo-"+str(node["community"])
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

    def getMultipleGraphByCommunities(self, ids):
        # 最大线程数
        maxThread = 8
        graphs = []
        print("threading start")
        start = time.time()
        q = queue.Queue(maxsize=maxThread)
        for id in ids:
            t = graphThread(func=self.getGraphByCommunity, args=(str(id),), name="graphSearch")
            q.put(t)
            if q.qsize() == maxThread:
                joinThread = []
                while q.empty() != True:
                    t = q.get()
                    joinThread.append(t)
                    t.start()
                for t in joinThread:
                    t.join()
                    graph = t.get_result()
                    graph["id"] = t.args
                    graphs.append(graph)
        restThread = []
        while q.empty() != True:
            t = q.get()
            restThread.append(t)
            t.start()
        for t in restThread:
            t.join()
            graph = t.get_result()
            graph["id"] = t.args
            graphs.append(graph)
        end = time.time() - start
        print("graph thread cost: "+str(end))
        return graphs