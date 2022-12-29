import networkx as nx
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from gensim.models import Word2Vec
from py2neo import *
from model.RandomWalker import RandomWalker
from service.community import CommunityService
from service.graph import GraphService
from service.neighbor import NeighborService

app = Flask(__name__)
CORS(app, resources=r'/*')  # 跨域
graph = Graph("bolt://localhost:7687", auth=("neo4j", "chinavis"))

# service
communityService = CommunityService(graphDevice=graph)
graphService = GraphService(graphDevice=graph)
neighborService = NeighborService(graphDevice=graph)

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

@app.route('/api/neighbors', methods=["GET", "POST"])
def get_neighbors():
    val = request.get_json()
    res = neighborService.getNeighborsByCommunity(val["communities"])
    if res != None:
        return  res
    else:
        return  "no neighbor data"

@app.route('/api/similarity', methods=["GET", "POST"])
def get_similarity():
    val = request.get_json()
    source = val["source"]
    target = val["target"]
    max = val["max"]
    res = communityService.getSimilarityCommunity(target,source,max)
    if res != None:
        return jsonify(res)
    else:
        return "no similarity data"

if __name__ == '__main__':
    app.run()

