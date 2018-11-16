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

```
conda install networkx plotly notebook nb_conda 
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
 can be of use
See //CitationGraph.py// for an example on how to use the script.


# R Google Scholar package

Maybe this can be of use in your project as well!

https://cran.r-project.org/web/packages/scholar/vignettes/scholar.html
