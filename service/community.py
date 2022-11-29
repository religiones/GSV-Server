from py2neo import *
import json
import os
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
