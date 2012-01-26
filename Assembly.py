from Bio.Sequencing import Ace
import Parse_Ace
import time
import math

class Assembly():
    
    def __init__(self):
        
        self.original_consensus = ""
        self.consensus = "" #string of consensus sequence
        self.consensus_name = ""
        self.reference = "" #string of reference sequence
        self.reference_name = ""
        
        # Some useful stats
        self.length_of_consensus = 0
        self.number_of_sequences = 0
        self.error_parameter = 0.75 # default value
        self.snp_parameter = 0.1 # default value
        self.coverage_thresh = 200
        self.snp_thresh = 2
        self.error_number = 0
        self.snp_number = 0
        self.gap_number = 0
        self.coverage = 0.0 # Average Coverage
        self.max_coverage = 0
        
    def open(self,snp_parameter,error_parameter,file):
        self.snp_parameter = snp_parameter
        self.error_parameter = error_parameter
        self.read(file)
        self.get_stats()
        
    def read(self,file):
        p = Parse_Ace.Parser(file)
        self.original_consensus = p.consensus
        self.consensus = p.consensus
        self.consensus_name = p.consensus_name
        self.number_of_sequences = p.number_sequences
        self.length_of_consensus = len(self.consensus)

        self.assembly = [None]*self.length_of_consensus # A,C,T,G,*,N,Coverage,New Position
        for i in range(0,self.length_of_consensus):
            self.assembly[i] = [0.0]*8
        self.assembly_stats = [None]*self.length_of_consensus # Gap, Error, SNP, Deleted
        for i in range(0,self.length_of_consensus):
            self.assembly_stats[i] = [False]*4
        
        for i in range(0,p.number_sequences):
            start,sequence = p.get_sequence(i)
            self.add_sequence(start,sequence)
        self.add_reference(p.reference,p.reference_name)
    
    def add_reference(self,reference,reference_name):
        self.reference = reference #string of reference sequence
        self.reference_name = reference_name
        assert len(self.consensus) == len(self.reference)
        
    #start is in position, not column
    def add_sequence(self,start,sequence):
        if start + len(sequence) - 1 > self.length_of_consensus:
            return 0
        if start < 1:
            return 0
        for i in range(0,len(sequence)):
            col_position = start - 1 + i
            if sequence[i] == 'A':
                self.assembly[col_position][0] += 1
            elif sequence[i] == 'C':
                self.assembly[col_position][1] += 1
            elif sequence[i] == 'T':
                self.assembly[col_position][2] += 1
            elif sequence[i] == 'G':
                self.assembly[col_position][3] += 1
            elif sequence[i] == '-' or sequence[i] == '*':
                self.assembly[col_position][4] += 1
            elif sequence[i] == 'N':
                self.assembly[col_position][5] += 1
            else:
                pass
            self.assembly[col_position][6] += 1 # add coverage
        self.number_of_sequences += 1
            
    def get_stats(self):
        for i in range(0,len(self.assembly)):
            # if gap, add first
            if self.assembly[i][6] == 0:
                self.assembly_stats[i][0] = 1
                self.gap_number += 1
                self.assembly[i][7] = i + 1 - self.error_number
            else:
                if self.assembly[i][6] > self.max_coverage and self.assembly_stats[i][3]==False:
                    self.max_coverage = self.assembly[i][6]
                if self.get_error(i) == True:
                    self.assembly_stats[i][1] = True
                    self.assembly_stats[i][3] = True
                    self.error_number += 1
                else:
                    self.assembly[i][7] = i + 1 - self.error_number
                if self.get_snp(i) == True:
                    self.assembly_stats[i][2] = True
                    self.snp_number += 1
    
    def get_snp(self,col_position):
        if self.snp_disagree(col_position) == True:
            return True
        elif (self.assembly[col_position][6] < self.coverage_thresh):
            if self.snp_threshold(col_position)==True:
                return True
        else:
            if self.snp_percent(col_position)==True:
                return True
        return False
    
    def snp_threshold(self,col_position):
        #if (self.assembly[col_position][6]<3):
        #    print "Low Coverage Warning"
        count = 0
        for i in range(0,4):
            if self.assembly[col_position][i] > self.snp_thresh:
                count += 1
        if count > 1:
            return True
        return False
    
    def snp_percent(self,col_position):
        count = 0
        for i in range(0,4):
            if self.assembly[col_position][i]/self.assembly[col_position][6] > self.snp_parameter:
                count += 1
        if count > 1:
            return True
        return False
    
    def snp_disagree(self,col_position):
        if (self.consensus[col_position]!=self.reference[col_position]):
            return True
        return False
        
    def get_error(self,col_position):
        if self.assembly[col_position][4]/self.assembly[col_position][6] > self.error_parameter:
            return True
        return False
    
    def get_shannon(self):
        x = []
        samples = []
        for i in range(0,len(self.assembly_stats)):
            if self.assembly_stats[i][3]==True:
                continue
            samples.append(self.get_shannon_single(self.assembly[i][0],
                                                   self.assembly[i][1],self.assembly[i][2],self.assembly[i][3],
                                                   self.assembly[i][4],self.assembly[i][6]))
            x.append(self.assembly[i][7])
        return x,samples
    
    
    def get_shannon_single(self,a,c,t,g,dash,coverage): 
        if (coverage==0):
            return 0
        
        S1_a = float(a)/(coverage)
        S1_t = float(t)/(coverage)
        S1_c = float(c)/(coverage)
        S1_g = float(g)/(coverage)
        S1_dash = float(dash)/(coverage)
        
        sum_a = 0
        if S1_a!=0:
            sum_a = S1_a*math.log(S1_a,5)
        sum_t = 0
        if S1_t!=0:
            sum_t = S1_t*math.log(S1_t,5)
        sum_c = 0
        if S1_c!=0:
            sum_c = S1_c*math.log(S1_c,5)
        sum_g = 0
        if S1_g!=0:
            sum_g = S1_g*math.log(S1_g,5)
        sum_dash = 0
        if S1_dash!=0:
            sum_dash = S1_dash*math.log(S1_dash,5)
    
        sum1 = sum_a + sum_t + sum_c + sum_g + sum_dash
        
        if sum1>0:
            print "Warning: Negative SE Value"
            sum1 = 0 
        
        return -sum1
    
    # does not actually delete from self.assembly, just marks for deletion
    def delete_column(self,col):
        self.assembly_stats[col][3] = True
        
    # gets the corresponding (non-deleting) column from a position after deletion
    def get_position_column(self,position):
        for i in range(0,len(self.assembly)):
            if self.assembly[i][7] == position:
                return i
        
    def change_column(self,column,change):
        self.consensus = self.consensus[0:column] + change + self.consensus[column + 1:len(self.consensus)]
        
    def previous_gap(self,start):
        if (self.gap_number == 0):
            return False
        i = None
        if (start == 0):
            i = self.length_of_consensus - 1
        else:
            i = start - 1
        while (i>-1):
            if (i==0):
                if self.assembly_stats[i][0] == True:
                    return i
                i = self.length_of_consensus - 1
            else:
                if self.assembly_stats[i][0] == True and self.assembly_stats[i-1][0]==False:
                    return i
                i += -1
        
    def next_gap(self,start):
        if (self.gap_number == 0):
            return False
        i = None
        if (start == self.length_of_consensus - 1):
            i = 0
        else:
            i = start + 1
        while (i<self.length_of_consensus):
            if (i==self.length_of_consensus - 1):
                if self.assembly_stats[i][0] == True and self.assembly_stats[i-1][0]==False:
                    return i
                i = 0
            else:
                if i==0:
                    if self.assembly_stats[i][0] == True:
                        return i
                else:
                    if self.assembly_stats[i][0] == True and self.assembly_stats[i-1][0]==False:
                        return i
                i += 1
                
    def previous_snp(self,start):
        if (self.snp_number == 0):
            return False
        i = None
        if (start == 0):
            i = self.length_of_consensus - 1
        else:
            i = start - 1
        while (i>-1):
            if self.assembly_stats[i][2] == True:
                return i
            if (i==0):
                i = self.length_of_consensus - 1
            else:
                i += -1
        
    def next_snp(self,start):
        if (self.snp_number == 0):
            return False
        i = None
        if (start == self.length_of_consensus - 1):
            i = 0
        else:
            i = start + 1
        while(i < self.length_of_consensus):
            if self.assembly_stats[i][2] == True:
                return i
            if (i==self.length_of_consensus - 1):
                i = 0
            else:
                i += 1