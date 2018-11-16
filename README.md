''Citationgraph''

* Installation

Install conda from https://conda.io/docs/user-guide/install/index.html if you haven’t installed it already.

Make a new conda environment that uses python 3.5 with the required dependencies using:


```
conda env create --file citation_graph_env.yml
```

You can activate this environment with:

```
activate citationgraph
```

or 

```
source activate citationgraph
```

depending on your OS.


* Dependencies

** python 3
***  beautifulsoup4
*** requests
*** lxml
*** unidecode

* Usage

The included python script can be used to convert paper's IDs (from PubMed, PubMed Central & DOIs) and fetch the following information for a given ID:

# Papers citing and cited by our paper of interest
# Article metadata available through NCBI's esummary

See //CitationGraph.py// for an example on how to use the script.