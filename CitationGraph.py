#!/usr/bin/env python3

from time import sleep

import requests

from bs4 import BeautifulSoup as BS


class PMC():
	
	def __init__(self, mail):
		
		self.tool = 'CitationGraph'
		self.mail = mail


	def convert(self, ids, to_idtype):
		
		''' Query Pubmed's ID Converter API to convert ids.
		Breaks list of ids in batches of (up to) 200 queries every second.
			(max 3 requests per second allowed without API key,
			more info at https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/).
		API service should be able to autodect format of ids passed.
		
		Documentation: https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/
		
		Arguments:
		----------
		ids:
		- type: list of string(s)
		- description: list of identifiers to convert
		to_idtype:
		- type: string
		- description: one of "pmcid", "pmid", "mid", and "doi"
		
		Returns:
		--------
		dict of converted ids
		- keys: queried ids (strings)
		- values: converted ids (strings)
		
		'''
		
		service_root = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids='
		results = {}
		
		for i in range(0, len(ids), 200):
			chunk = ids[i:i+200]
			query = '{}{}&tool={}&email={}'.format(service_root, ','.join(chunk), self.tool, self.mail)

			r = requests.get(query)
			soup = BS(r.text, 'lxml')
			records = soup.find_all('record')
			for record in records:
				query_id = record['requested-id']
				result_id = record[to_idtype]
				results[query_id] = result_id
			sleep(1)
			
		return results


	def get_citations(self, ids, how):
		
		''' Query PMC with PubMed IDs to retrieve a list of PubMed IDs citing the queried IDs.
		Breaks list of ids in batches of (up to) 200 queries every second.
		
		Documentation: https://www.ncbi.nlm.nih.gov/pmc/tools/cites-citedby/
		
		Arguments:
		----------
		ids:
		- type: list of string(s)
		- description: list of PubMed identifiers to find citing papers for
		how:
		- type: string, either 'citing' or 'cited_by'
		- description:
			if 'citing': returns all PubMed IDs of papers citing the queried ids in PMC
			if 'cited_by': returns all PubMed IDs of papers cited by the queried ids in PMC
		
		Returns:
		--------
		dict of citing papers
		- keys: queried PubMed identifiers (strings)
		- values: list of strings, with each string a PubMed identifiers citing the PubMed ID in the associated key
		
		'''
		
		if how == 'citing':
			service_root = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id='
		elif how == 'cited_by':
			service_root = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_refs&id='
		else:
			raise ValueError('Please choose either:\n-citing\ncited_by')
			
		results = {}
		
		for i in range(0, len(ids), 200):
			chunk = ids[i:i+200]
			query = '{}{}&tool={}&email={}'.format(service_root, '&id='.join(chunk), self.tool, self.mail)
			
			r = requests.get(query)

			soup = BS(r.text, 'lxml')
			for linkset in soup.find_all('linkset'):
				cited_id = linkset.find('idlist').find('id').contents[0]
				citing_ids = [link.contents for link in linkset.find('linksetdb').find_all('id')]
				results[cited_id] = citing_ids
			sleep(1)
			
		return results
		
		
if __name__ == '__main__':
	
	mail = 'nicolas.deneuter@uantwerpen.be'
	
	pmc = PMC(mail)
	
	converted_ids = list(pmc.convert(['PMC4364064', 'PMC5811185'], 'pmid').values())
	
	print(pmc.get_citations(converted_ids, how='citing'))
	print(pmc.get_citations(converted_ids, how='cited_by'))
