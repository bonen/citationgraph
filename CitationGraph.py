#!/usr/bin/env python3

from time import sleep

import requests

from bs4 import BeautifulSoup as BS


class Paper():
	
	''' Paper in PubMed Central '''
	
	def __init__(self, pmcid):
		
		self.pmcid = pmcid
		
		
	def fetch_metadata(self, pmc):
		
		''' Query PubMed Central for a summary of metadata information for this paper.
		
		Arguments:
		----------
		pmc
		- type: PMC object
		- description: PubMed Central interface
		
		Returns:
		--------
		dict that is also stored as a new attribute 'metadata'
		- keys: metadata tag names (eg: Author, Title, ...)
		- values: information associated with the tag for this paper
			if a tag only has one value, it is stored as a string
			if a tag has multiple values, they are stored as a list of strings
		
		'''
		
		soup = pmc._get_metadata(self.pmcid)
		self.metadata = {}
		
		for item in soup.find_all('item'):
			
			tag = item['name']
			value = item.string
			
			if tag in self.metadata.keys():
				if type(self.metadata[tag]) != list:
					stored_value = self.metadata[tag]
					del self.metadata[tag]
					self.metadata.setdefault(tag, []).append(stored_value)	
				self.metadata.setdefault(tag, []).append(value)
			else:
				self.metadata[tag] = value
				
		
		return self.metadata



class PMC():
	
	''' PubMed Central interface '''
	
	def __init__(self, mail):
		
		self.tool = 'CitationGraph'
		self.mail = mail
		
		self._chunk_size = 200
		self._sleep_time = 1
		
		
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
		
		for i in range(0, len(ids), self._chunk_size):
			chunk = ids[i:i+self._chunk_size]
			query = '{}{}&tool={}&email={}'.format(service_root, ','.join(chunk), self.tool, self.mail)

			r = requests.get(query)
			soup = BS(r.text, 'lxml')
			records = soup.find_all('record')
			for record in records:
				query_id = record['requested-id']
				result_id = record[to_idtype]
				results[query_id] = result_id
			sleep(self._sleep_time)
			
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
			raise ValueError('Wrong or missing argument for \'how\', please choose between: \'citing\', \'cited_by\'')
			
		results = {}
		
		for i in range(0, len(ids), self._chunk_size):
			chunk = ids[i:i+self._chunk_size]
			query = '{}{}&tool={}&email={}'.format(service_root, '&id='.join(chunk), self.tool, self.mail)
			
			r = requests.get(query)

			soup = BS(r.text, 'lxml')
			for linkset in soup.find_all('linkset'):
				cited_id = linkset.find('idlist').find('id').contents[0]
				citing_ids = [link.contents[0] for link in linkset.find('linksetdb').find_all('id')]
				results[cited_id] = citing_ids
			sleep(self._sleep_time)
			
		return results
		
		
	def _get_metadata(self, pmcid):
		
		''' Get summary of the metadata from PubMed Central for a single PubMed Central id.
		
		Documentation: https://www.ncbi.nlm.nih.gov/pmc/tools/get-metadata/
		
		Arguments:
		----------
		pmcid:
		- type: string
		- description: a single PubMed Central identifier
		
		Returns:
		--------
		PMC server response
		- type: bs4.BeautifulSoup object
		- description: a summary of the paper's metadata
		
		'''
		
		if pmcid.startswith('PMC'):
			pmcid = pmcid[3:]
			
		service_root = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id='
		query = '{}{}&tool={}&email={}'.format(service_root, pmcid, self.tool, self.mail)
		r = requests.get(query)
		soup = BS(r.text, 'lxml')
		
		sleep(self._sleep_time/5)
		
		return soup

		
if __name__ == '__main__':
	
	mail = 'ex.ample@university.be' # your e-mail adres here
	
	ids = ['PMC4364064', 'PMC5811185']
	pmc = PMC(mail) # create PubMed Central interface
	
	converted_ids = list(pmc.convert(ids, 'pmid').values()) # convert PubMed Central ids to PubMed IDs
	
	print(pmc.get_citations(converted_ids, how='citing')) # fetch papers citing the ids we provided
	print(pmc.get_citations(converted_ids, how='cited_by')) # fetch papers cited by the ids we provided
	mypaper = Paper(ids[0])