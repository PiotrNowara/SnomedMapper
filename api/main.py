
from typing import List, Union
from fastapi import FastAPI, Query, HTTPException
from SPARQLWrapper import SPARQLWrapper, JSON

import json
from pydantic import BaseModel

app = FastAPI()

sparql = SPARQLWrapper("http://localhost:7200/repositories/SNOMED")
sparql.setReturnFormat(JSON)

class SnomedMatch:
    def __init__(self, mapsFrom, mapsToLabel, mapsToIri, score):
        self.mapsFrom = mapsFrom
        self.mapsToLabel = mapsToLabel
        self.mapsToIri = mapsToIri
        self.score = score
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    
class MapsFrom(BaseModel):
    labels: List[str]

@app.get("/snomed/map")
def map_snomed(label: str):
    sparql.setQuery(create_snomed_query(label))
    print("Label to map: {}\nQuery: {}".format(label, sparql.queryString))
    try:
        sparql_result = sparql.queryAndConvert()
        res_data = sparql_result["results"]["bindings"]
        if res_data:
            return SnomedMatch(label, res_data[0]["label"]["value"],
                                res_data[0]["iri"]["value"],
                                res_data[0]["score"]["value"])
        else:
            return SnomedMatch(label, "N/A", "N/A", "N/A")
    except Exception as e:
        print(e)


@app.post("/map_to_snomed/")
def map_to_snomed(mapsFrom: MapsFrom):
    print(len(mapsFrom.labels))
    response = []
    for label in mapsFrom.labels:
        sparql.setQuery(create_snomed_query(label))
        print("Label to map: {}\nQuery: {}".format(label, sparql.queryString))
        try:
            sparql_result = sparql.queryAndConvert()

            res_data = sparql_result["results"]["bindings"]
            if res_data:
                response.append(SnomedMatch(label, res_data[0]["label"]["value"],
                                res_data[0]["iri"]["value"],
                                res_data[0]["score"]["value"]))
            else:
                response.append(SnomedMatch(label, "N/A", "N/A", "N/A"))
        except Exception as e:
            print(e)
    return response


def create_snomed_query(mapsFromLabel) -> str:
    return """
PREFIX : <http://www.ontotext.com/graphdb/similarity/>
PREFIX similarity: <http://www.ontotext.com/graphdb/similarity/instance/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?iri ?score ?label ?prefLabel
WHERE {
?search a similarity:rdfsLabel;
        :searchTerm \"""" + mapsFromLabel + """\";
           :documentResult ?result .
?result :value ?iri;
:score ?score.
?iri rdfs:label ?label;
     <http://www.w3.org/2004/02/skos/core#prefLabel> ?prefLabel.
     
}
ORDER BY desc(?score)
LIMIT 1
"""

def create_query(template, params: List) -> str:
    s = template.format(*params)
    print(s)
    return s
