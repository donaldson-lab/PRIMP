from Bio.Sequencing import Ace
import re

class Parser:
    
    def __init__(self,ace_file):    
        self.ace_file = ace_file
        self.records = Ace.read(open(ace_file, 'r'))
        assert len(self.records.contigs)==1
        self.contig = self.records.contigs[0]
        self.consensus = self.contig.sequence
        self.consensus_name = self.contig.name
        self.number_sequences = len(self.contig.reads)
        self.reference = ""
        self.reference_name = ""
    
    def get_sequence(self,index):
        start = 0
        sequence = ""
        text = self.contig.reads[index].rd.name
        # Find Reference
        match = re.search("ref",text)
        if match or len(self.contig.reads[index].rd.sequence)==len(self.contig.sequence):
            self.reference = self.contig.reads[index].rd.sequence
            self.reference_name = text
            return -1,"REFERENCE"
	###
        start = self.contig.af[index].padded_start           
        sequence = self.contig.reads[index].rd.sequence
        return start,sequence
