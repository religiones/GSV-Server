import networkx as nx
import numpy as np
from gensim.models import Word2Vec
from py2neo import *
import json
import os

from model.RandomWalker import RandomWalker

path = os.getcwd()  #获取当前路径

class CommunityService:
    def __init__(self, graphDevice):
        if graphDevice == None:
            self.graphDevice = Graph("bolt://localhost:7687", auth=("neo4j", "chinavis"))
        else:
            self.graphDevice = graphDevice

    "get all community"
    def getAllCommunity(self):
        with open(path+"\dbData\community_node.json",'r', encoding='utf-8') as fp:
            data = json.load(fp)
            return data

    "get graph embedding"
    def get_graph_embedding(self, id):
        num_walks = 80  # 序列数量
        walk_length = 10  # 序列长度
        workers = 4
        node_sql = "match (n) where n.community="+id+" return n.id"
        edge_sql = "match (n)-[r]->(m) where n.community="+id+" and m.community="+id+" return n.id,m.id"
        res_node = self.graphDevice.run(node_sql).to_ndarray()
        res_edge = self.graphDevice.run(edge_sql).to_ndarray()
        node_list = []
        for node in res_node:
            node_list.append((node[0]))
        edge_list = [tuple(y) for y in res_edge]
        # create graph
        G = nx.DiGraph()
        G.add_edges_from(edge_list)
        G.add_nodes_from(node_list)
        # RandomWaker产生序列
        rw = RandomWalker(G, p=1, q=1, use_rejection_sampling=0)
        rw.preprocess_transition_probs()
        sentences = rw.simulate_walks(num_walks=num_walks, walk_length=walk_length, workers=workers, verbose=1)
        model = Word2Vec(sentences=sentences,
                         vector_size=128,
                         min_count=5,
                         sg=1,
                         hs=0,
                         workers=workers,
                         window=5,
                         epochs=3)
        embedding_list = []
        for word in G.nodes():
            embedding_list.append(model.wv[word].tolist())
        return {"embedding": embedding_list, "community_id": id}

    "get similarity community"
    def getSimilarityCommunity(self, target, source, max):

        return None