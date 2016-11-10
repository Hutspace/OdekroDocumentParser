import sys
import re
from datetime import datetime
from datetime import date  
from parser import DocumentParser


class LoanParser(DocumentParser):
    SELECTION_MARKER = r".*(Loan Facility|Loan Agreement|Financial Agreement).*"

    def __init__(self, content):
        super(LoanParser, self).__init__(content)


    @classmethod
    def parse_loan_summary(cls, lines):
        thekind, line, match = None, None, None
        loans = []
        valid = False

        party_1  = ''
        party_2 = ''
        activity = ''
        amount = '';6

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.strip()

            if (thekind == cls.BLANK ):
                continue

            matchObjectForLoan = re.match( cls.SELECTION_MARKER , line_content)

            if matchObjectForLoan:
                # START PARSING SECTION
                valid = True
                pass
            #else:
            #    valid = False    
            #    continue


            if valid:
                #matchObjectForCommitteeName = re.match( cls.COMMITTEE_NAME_FORMAT , line_content)
                #matchObjectForCommitteeDateTimeVenueAndAgenda = re.match( r"Date: *" , line_content)

                if matchObjectForLoan:
                    loan_details = line_content.split(' ')
                    print loan_details



                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    continue

            else:
                # fallout
                pass


            if len(loans)==0:
                continue

        if party_1!='' and  party_2!='':
            loans.append(dict(party_1=party_1,
                            party_2=party_2,
                            amount=amount,
                            activity=activity
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
    print 'Party 1 | Party 2 | Amount | Activity '
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = LoanParser(content)
        p.parse()
        data = p.output()
        for row in data:
            print '%s|%s|%s|%s|%s' % (row['party_1'],
                                      row['party_2'],
                                      row['amount'],
                                      row['activity'])


if __name__ == "__main__":
    main(sys.argv)
