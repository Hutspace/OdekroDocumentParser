# -*- coding: utf-8 -*-

import sys
import re
from datetime import datetime
from datetime import date  
from parser import DocumentParser


class LoanParser(DocumentParser):
    SELECTION_MARKER = r".*(Loan Facility|Loan Agreement|Financial Agreement).*"
    ESCAPE_MARKERS = r".*(the date on which notice of the motion is given|Date:|Venue:|met on ).*"


    def __init__(self, content):
        super(LoanParser, self).__init__(content)

    @classmethod
    def filter_out_parties_to_agreement(self,line_content):
        line_content = line_content.replace(',',' ')
        all_parties1 = line_content.split('between',1)[-1]
        if len(all_parties1)>1:
            all_parties = all_parties1.split('and',1)
            party_1 = all_parties[0]
            if len(all_parties)>1:
                party_2 = all_parties[1].split('for an amount')[0].split('—',1)[0]
            else:
                party_2 = ''
                
            return (party_1 , party_2)
        else:
            return ( '', '' )


    @classmethod
    def filter_out_loan_purpose(self,line_content): 
        line_content = line_content.replace(',',' ')           
        loan_details = line_content.split('to finance',1)
        if len(loan_details)>1:
            return loan_details[1]
        else:
            #loan_details[0] 
            return ''

    @classmethod
    def filter_out_loan_purpose_via_party_2(self,line_content): 
        line_content = line_content.replace(',',' ')
        all_parties1 = line_content.split('between',1)[-1]
        if len(all_parties1)>1:
            all_parties = all_parties1.split('and',1)
            print all_parties 
            if len(all_parties)>1:
                purpose = all_parties[1].split('for an amount')[0].split('—',1)[1]
               #party_2 = all_parties[1].split('for an amount')[0].split('—',1)[0]
            else:
                purpose  = ''

            return purpose
        else:
            return ''

    @classmethod
    def filter_out_loan_amount(self,line_content):  
        line_content = line_content.replace(',',' ')          
        loan_details = line_content.split('amounting to',1)
        if len(loan_details)>1:
            amount = loan_details[1].split('between',1)[0]
            return amount
        else:  
            loan_details1 = line_content.split('an amount of',1)
            if len(loan_details1)>1:
                loan_details2  =loan_details1[1]
                amount = loan_details2.split('to finance',1)[0]         
            else:
                amount = ''
            #loan_details[0] 
            return amount


    @classmethod
    def parse_loan_summary(cls, lines):
        thekind, line, match = None, None, None
        loans = []
        valid = False

        party_1  = ''
        party_2 = ''
        purpose = ''
        amount = '';

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.strip()

            if (thekind == cls.BLANK ):
                continue

            matchObjectForLoan = re.match( cls.SELECTION_MARKER , line_content)
            matchObjectForEscapeMarkers = re.match( cls.ESCAPE_MARKERS , line_content)

            if matchObjectForEscapeMarkers:
                # START PARSING SECTION
                valid = False
                continue

            if matchObjectForLoan:
                # START PARSING SECTION
                valid = True
                pass


            if valid:

                if matchObjectForLoan:

                    all_parties = cls.filter_out_parties_to_agreement(line_content)
                    party_1 = all_parties[0]
                    party_2 = all_parties[1]


                    purpose = cls.filter_out_loan_purpose(line_content)
                    amount = cls.filter_out_loan_amount(line_content)

                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    continue

            else:
                # fallout
                continue


            if len(loans)==0:
                continue

        if party_1!='' and  party_2!='' and amount!='' and purpose!='':

            loans.append(dict(party_1=party_1,
                            party_2=party_2,
                            amount=amount,
                            purpose=purpose
                            ))

        return loans

    @classmethod
    def parse_body(cls, lines):
        entries = []
        loan_all = cls.parse_loan_summary( list(lines) )
        for loan in loan_all:

            if len(loan)>2:
                entries.append(loan)

        return entries


def main(argv):
    print 'Party 1 | Party 2 | Amount | Purpose '
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = LoanParser(content)
        p.parse()
        data = p.output()
        for row in data:
            print '%s|%s|%s|%s' % (row['party_1'],
                                      row['party_2'],
                                      row['amount'],
                                      row['purpose'])


if __name__ == "__main__":
    main(sys.argv)
