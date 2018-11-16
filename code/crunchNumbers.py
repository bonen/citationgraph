from CitationGraph import *
from pickle import dump, dumps
# from json import dump
from time import time

tstart = time()


def unnest(x):
	""" returns un-nested version of level 1 nested list x."""
	return [e for sublist in x for e in sublist]


def visualize_paper(paper_id):
	print('Metadata for {}'.format(mypaper.pmcid))
	for key, value in mypaper.metadata.items():
		print('{}: {}'.format(key, value))
# print('Example:\nPaper: {} cites {} articles.'.format(list(cited_papers.keys())[0],


def linked_authors(metadata, cited, this_PM_id, this_PMC_id):
	L_authors_by_level = []
	try:
		L_authors_by_level.append(metadata[this_PMC_id]['Author'])
	except KeyError:
		raise KeyError("referencing paper", this_PMC_id, "has no Author")
	L_authors_by_level.append([])
	this_cited = cited[this_PM_id]  # papers cited by the ids we provided
	this_cited_converted = list(pmc.convert(this_cited, 'pmcid').values())
	for cited_PMC_id in this_cited_converted:
		this_cited_metadata = Paper(cited_PMC_id).fetch_metadata(pmc)
		try:
			L_authors_by_level[1].extend(this_cited_metadata['Author'])
		except KeyError:
			print("paper", cited_PMC_id, "has no Author")
	return tuple(L_authors_by_level)

mail = 'joris.vanhoutven@uhasselt.be'  # your e-mail adres here
pmc = PMC(mail)  # create PubMed Central interface

# read in example list of pmc ids
# FP_input_ids = '../data/example_pmc_list.txt'
# FP_input_ids = '../data/example_pmc_list_short.txt'
# dirtype = 'data_2_ids'
dirtype = 'data_15_ids'
# FN_input_ids = 'epigenomics_2'
FN_input_ids = 'epigenomics_15'
FP_input_ids = '../'+dirtype+'/'+FN_input_ids+'.txt'
with open(FP_input_ids, 'r') as o:
	input_ids = o.read().strip().split('\n')

converted_ids = list(pmc.convert(input_ids, 'pmid').values())  # convert PubMed Central ids to PubMed IDs

# citing_papers = pmc.get_citations(converted_ids, how='citing')  # fetch papers citing the ids we provided
# print('Example:\nPaper: {} is cited by {} articles.'.format(list(citing_papers.keys())[0],
# 															len(citing_papers[list(citing_papers.keys())[0]])))
cited_papers = pmc.get_citations(converted_ids, how='cited_by')  # fetch papers cited by the ids we provided
# print('Example:\nPaper: {} cites {} articles.'.format(list(cited_papers.keys())[0],
# 													  len(cited_papers[list(citing_papers.keys())[0]])))

metadata = dict.fromkeys(converted_ids)
linkedAuthors = []
for PM_id, PMC_id in zip(converted_ids, input_ids):
	mypaper = Paper(PMC_id)  # create a representation of a paper
	metadata[PMC_id] = mypaper.fetch_metadata(pmc)  # pass pmc interface to fetch the paper's metadata
	# visualize_paper(paper_id)
	linkedAuthors.append(linked_authors(metadata, cited_papers, PM_id, PMC_id))
print(linkedAuthors)
# dumps(linkedAuthors, open('authors_'+FN_input_ids+'.pkl', 'wb'))
dump(linkedAuthors, open('authors_'+FN_input_ids+'.pkl', 'wb'))
print(time()-tstart)