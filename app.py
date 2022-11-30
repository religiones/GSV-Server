import networkx as nx
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from gensim.models import Word2Vec
from py2neo import *
from model.RandomWalker import RandomWalker
from service.community import CommunityService
from service.graph import GraphService

app = Flask(__name__)
CORS(app, resources=r'/*')  # 跨域
graph = Graph("bolt://localhost:7687", auth=("neo4j", "chinavis"))

num_walks = 80    # 序列数量
walk_length = 10  # 序列长度
workers = 4
# service
communityService = CommunityService(graphDevice=graph)
graphService = GraphService(graphDevice=graph)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/api/test', methods=["GET", "POST"])
def test():
    return {"res": "connected!"}

@app.route('/api/community', methods=["GET", "POST"])
def get_community():
    communitylist = communityService.getAllCommunity()
    if communitylist != None:
        return jsonify(communitylist)
    else:
        return "no community data"

@app.route('/api/graph', methods=["GET", "POST"])
def get_graph():
    val = request.get_json()
    res = graphService.getGraphByCommunity(val["community"])
    if res != None:
        return res
    else:
        return "no graph data"

@app.route('/api/getGraphEmbedding', methods=["GET", "POST"])
def get_graph_embedding():
    node_sql = "match (n) where n.community=1782816 return n.id"
    edge_sql = "match (n)-[r]-(m) where n.community=1782816 and m.community=1782816 return n.id,m.id"
    res_node = graph.run(node_sql).to_ndarray()
    res_edge = graph.run(edge_sql).to_ndarray()
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
        embedding_list.append(model.wv[word])
    embedding_list = np.array(embedding_list).flatten().tolist()
    embedding_list_pad = np.pad(embedding_list, (0, 55936 - len(embedding_list)), 'constant').tolist()
    # nodes_json = {"nodes":G.nodes(),"edges":G.edges(),"community_id":"1782816"}
    return {"embedding":embedding_list_pad,"community_id":"1782816"}

if __name__ == '__main__':
    app.run()

