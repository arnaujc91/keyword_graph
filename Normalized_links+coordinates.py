import networkx as nx
import pandas as pd
import sys
import re
import os
import json
from copy import deepcopy

keywords_extractor_path = os.path.expanduser('~/Cognostics/AVL_graphs/bin')
if not keywords_extractor_path in sys.path:
    sys.path.append(keywords_extractor_path)

keywords = ['cmd',
 'sap',
 'avl',
 'sales',
 'quote',
 'prism',
 'deletion flag',
 'zsh',
 'zbp',
 'zsp',
 'lead',
 'gam',
 'kam',
 'gso',
 'gam',
 'ast',
 'its',
 'pte',
 'customer',
 'account group',
 'pte',
 'its',
 'ast',
 'sd',
 'vmd',
 'opp',
 'vat',
 'fi',
 'vmd',
 'mmd',
 'sps',
 'sorg',
 'cocd',
 'df',
 'vat',
 'transaction',
 'zen',
 'kcb',
 'sfdc',
 'acc',
 'avi',
 'gac',
 'mac',
 'procalc',
 'crm',
 'management',
 'salesforce',
 'erp']

keywords = list(set(keywords))

meaningless = ['two']

for elemnt in meaningless:
    if elemnt in keywords:
        print(elemnt)
        keywords.remove(elemnt)

def clean_kw(keywords):
    # this function is used to remove keywords which are parts of other keywords.
    # So, let's say we have the keyword "crisis" and "financial crisis". It will
    # remove the word "crisis" from the KW.
    newlist = []
    for word in keywords:
        print(word)
        for j in range(len(keywords)):
            if word in keywords[j] and word != keywords[j]:
                newlist.append(word)
                break
    for word in newlist:
        keywords.remove(word)
    return keywords

def edges(document, keywords, k):
    # Extract the paragraphs
    Text_t = open(document)
    Text = Text_t.read()
    paragraphs = Text.splitlines()

    # Clean the paragraphs
    for paragraph in paragraphs:
        if paragraph == '':
            paragraphs.remove(paragraph)

    # Clean the KW
    keywords = clean_kw(keywords)

    # Create a dictionary with all the KW
    dictionary = {}
    for kw in keywords:
        dictionary['{}'.format(kw)] = []


    # Obtain two dictionaries:
    # 1. With th parargaphs and the KW contained in it
    # 2. With the KWs and which paragraphs contains that KW.
    # One method uses 'in' and the other uses regex.
    paragraphs_list = {}


    # 'In' method
    # for i in range(len(paragraphs)):
    #     List = []
    #     for keyword in keywords:
    #         if keyword in paragraphs[i]:
    #             List.append(keyword)
    #             dictionary[keyword].append(i)
    #     paragraphs_list['{}'.format(i)] = List


    # Regex Method
    for i in range(len(paragraphs)):
       List = []
       for keyword in keywords:
           if re.search(r'\b'+ '{}'.format(keyword) + 's?' + r'\b', paragraphs[i], re.IGNORECASE):
               List.append(keyword)
               dictionary[keyword].append(i)
       paragraphs_list['{}'.format(i)] = List


    # Find all relevant lines for each keyword. The number of line 'k' is arbitrary and must
    # be fixed by hand.
    keyword_range = {}
    for kw in keywords:
        keyword_range[kw] = []
        for i in dictionary[kw]:
            for a in range(i-k,i+1+k):
                keyword_range[kw].append(a)
        keyword_range[kw] = set(keyword_range[kw])

    # Give an integer value to each keyword.
    kw_integers_dict = {}
    i = 0
    for kw in keywords:
        i += 1
        kw_integers_dict["{}".format(kw)] = i


    # Now the only thing left is to see which keywords have an overlap in the lines where they are relevant.
    # If they have overlap, then that becomes a link.
    missing_kw = deepcopy(keywords)
    edges = []
    # We decide to use integers to label the nodes, thats why I introduce edges_int
    edges_int = []
    connected_kw = []
    for kw1 in keywords:
        for kw2 in missing_kw:
            # We will require some normalization to say that the words are actually connected. I will explain later.
            # We ask for the keywords to share some important lines for each keyword, and at the same time not
            # to be the same keyword.
            if (keyword_range[kw1]&keyword_range[kw2]) and not (set(kw1.split())&set(kw2.split())):
                   if (len(keyword_range[kw1] & keyword_range[kw2]) /(min(len(keyword_range[kw1]),
                                                                   len(keyword_range[kw2])))) > 0.3:
                       # Create the nodes for the graph.
                        edges.append((kw1,kw2))
                       # Create the nodes for the json file.
                        edges_int.append({"from": kw_integers_dict[kw1], "to": kw_integers_dict[kw2]})
                        # These two lines are here in order to select the Keywords that are connected to something.
                        # The rest of keywords will be deleted from the set "connected_kw"
                        if kw1 not in connected_kw: connected_kw.append(kw1)
                        if kw2 not in connected_kw: connected_kw.append(kw2)
        missing_kw.remove(kw1)

    # Create the graph with "networkx"
    KWG = nx.Graph()
    # Add nodes and edges to the graph
    KWG.add_nodes_from(connected_kw)
    KWG.add_edges_from(edges)
    # Obtain the coordinates of the nodes as a dictionary.
    coord = nx.spring_layout(KWG)
    # Create the nodes for the json file.
    nodes_int = []
    for kw in connected_kw:
        nodes_int.append({"id": kw_integers_dict[kw], "label": kw, "x": coord[kw][0], "y": coord[kw][1]
        , "group": 0, "type": 'concept', "description": "", "url": "", "documents": [], "external_documents": []})
    print(len(connected_kw))
    print(connected_kw)

    return {"edges": edges_int, "nodes": nodes_int}




with open('graph_coordinates_1_03.json', 'w') as stream:
    json.dump(edges('/Users/arnaujc/Cognostics/fwdavldokumente/CMD+IC.txt' , keywords, 1), stream)



with open('Andrej_keywords.json', 'w') as stream:
    json.dump(keywords, stream)

#print(edges('/Users/arnaujc/Cognostics/fwdavldokumente/CMD+IC.txt' , keywords, 3))




