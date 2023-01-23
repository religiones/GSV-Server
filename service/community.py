import queue
import threading
import time
import networkx as nx
import numpy as np
from gensim.models import Word2Vec
from py2neo import *
import json
import os

from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors

from model.RandomWalker import RandomWalker
path = os.getcwd()  #获取当前路径

class similarityThread(threading.Thread):
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
    def get_graph_embedding(self, id, embeddingType):
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
        if embeddingType == "list":
            embedding_list = []
            for word in G.nodes():
                embedding_list.append(model.wv[word].tolist())
            return {"embedding": embedding_list, "id": id}
        else:
            embedding = {}
            for word in G.nodes():
                embedding[word] = model.wv[word].tolist()
            return embedding

    "get graph embedding to 2D"
    def getGraphEmbeddingTo2D(self, graphEmbedding):
        modelTSNE = TSNE(n_components=2, init='pca', random_state=0, n_iter=3000)
        nodePos = modelTSNE.fit_transform((graphEmbedding)).tolist()
        return nodePos

    "get similarity community"
    def getSimilarityCommunity(self, target, source, max):
        # 最大线程数
        maxThread = 8
        embeddings = []
        print("threading start")
        start = time.time()
        # 创建队列,队列大小限制线程个数
        q = queue.Queue(maxsize=maxThread)
        # 多线程查询数据库
        for id in source:
            t= similarityThread(func=self.get_graph_embedding,args=(id,"list",),name='graphEmbedding')
            q.put(t)
            # 队列队满
            if q.qsize() == maxThread:
                # 记录线程
                # 从队列中取线程 直至队列为空
                joinThread = []
                while q.empty() != True:
                    t = q.get()
                    joinThread.append(t)
                    t.start()
                # 终止所有线程
                for t in joinThread:
                    t.join()
                    embeddings.append(t.get_result())
        # 清空剩余线程
        restThread = []
        while q.empty() != True:
            t = q.get()
            restThread.append(t)
            t.start()
        for t in restThread:
            t.join()
            embeddings.append(t.get_result())
        end = time.time() - start
        print("similarity thread cost: "+str(end))

        targetEmbedding = None
        embeddingList = []
        for embedding in embeddings:
            embeddingMatrix = np.array(embedding["embedding"]).flatten().tolist()
            # 填充0使纬度一致
            embeddingPad = np.pad(embeddingMatrix,(0,(max*128)-len(embeddingMatrix)),'constant').tolist()
            embeddingList.append(embeddingPad)
            if embedding["id"] == target:
                targetEmbedding = embeddingPad

        neigh = NearestNeighbors(n_neighbors=len(embeddingList)).fit(np.array(embeddingList))
        distance, indices = neigh.kneighbors(np.array([targetEmbedding]))
        return {"distance":distance.flatten().tolist(), "rank": indices.flatten().tolist()}