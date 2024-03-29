from flask import Flask, request, jsonify
from flask_cors import CORS
from py2neo import *
from service.community import CommunityService
from service.graph import GraphService
from service.neighbor import NeighborService

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
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
    res = graphService.getGraphByCommunity(str(val["community"]))
    if res != None:
        return res
    else:
        return "no graph data"

@app.route('/api/graphs', methods=["GET", "POST"])
def get_graphs():
    val = request.get_json()
    res = graphService.getMultipleGraphByCommunities(val["communities"])
    if res != None:
        return jsonify(res)
    else:
        return "no graphs data"

@app.route('/api/neighbors', methods=["GET", "POST"])
def get_neighbors():
    val = request.get_json()
    res = neighborService.getNeighborsByCommunity(str(val["communities"]))
    if res != None:
        return res
    else:
        return "no neighbor data"

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

@app.route('/api/graphEmbedding', methods=["GET", "POST"])
def get_graphEmbedding():
    val = request.get_json()
    res = communityService.get_graph_embedding(str(val["community"]),"dict")
    if res != None:
        return res
    else:
        return  "no embedding data"

@app.route('/api/similarityNodes', methods=["GET", "POST"])
def get_similarityNodes():
    val = request.get_json()
    print(val["modelCfg"])
    print(val["nodes"])
    res = communityService.getSimilarityNodes(str(val["nodes"]), str(val["community"]), val["graph"], val["k"], val["modelCfg"])
    if res != None:
        return jsonify(res)
    else:
        return "no similarity nodes data"

if __name__ == '__main__':
    app.run()

