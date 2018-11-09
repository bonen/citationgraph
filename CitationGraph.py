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
		Breaks list of ids in batches of (up to) 200 queries every second (= max allowed per request).
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
		- keys: query ids (strings)
		- values: converted ids (strings)
		
		'''
		
		base_query = '?ids='
		results = {}
		
		for i in range(0, len(ids), 200):
			chunk = ids[i:i+200]
			query = '{}{}{}&tool={}&email={}'.format(self.service_root, base_query, ','.join(chunk), self.tool, self.mail)

			r = requests.get(query)
			soup = BS(r.text, "lxml")
			records = soup.find_all('record')
			for record in records:
				query_id = record['requested-id']
				result_id = record[to_idtype]
				results[query_id] = result_id
			sleep(1)
			
		return results
	

class EUtils():
	
	def __init__(self):
		
		self.service_root = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

if __name__ == '__main__':
	
	converter = PubmedIDConverter()
	print(converter.convert(['21876726', '21876725', '30202444'], 'doi'))