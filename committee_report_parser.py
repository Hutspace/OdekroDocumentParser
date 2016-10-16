import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class CommitteeReportParser(DocumentParser):
    SELECTION_MARKER_POINT_1 = '.0 INTRODUCTION'    
    SELECTION_MARKER_INTRODUCTION = '.0 INTRODUCTION'
    SELECTION_MARKER_REFERENCE_DOCS = (
        ".0 REFERENCE DOCS", ".0 REFERENCE DOCUMENTS",".0 REFERENCE"
        )
    SELECTION_MARKER_BACKGROUND = '.0 BACKGROUND'
    SELECTION_MARKER_DELIBRATIONS = '.0 DELIBRATIONS'    

    SELECTION_MARKER_OBJECTIVE = '.0 OBJECTIVE'
    SELECTION_MARKER_SPECIFIC_PROVISIONS_OF_BILL = '.0 PROVISIONS OF BILL'
    SELECTION_MARKER_COMMITTEE_OBSERVATIONS = (
        ".0 OBSERVATIONS",".0 COMMITTEE OBSERVATIONS",
        )
    SELECTION_MARKER_RECOMMENDATIONS = '.0 RECOMMENDATIONS'
    SELECTION_MARKER_CONCLUSION = '.0 CONCLUSION'
    SELECTION_MARKER_SUBMITTED_BY = 'Respectfully submitted'                    

    def __init__(self, content):
        super(OrderPaperParser, self).__init__(content)


    @classmethod
    def parse_committee_report(cls, lines):
        thekind, line, match = None, None, None
        reports = []
        valid = False

        reference_docs= background=objective_of_bill = specific_provisions_of_bill=''
        committee_observations =recommendations=conclusion=submitted_by=''
        delibrations = point_1 = ''


        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.encode("utf-8")
            line_content = line_content.strip()

            if (thekind == cls.BLANK ):
                continue

            if (line_content == cls.SELECTION_MARKER_POINT_1  or line_content ==cls.SELECTION_MARKER_INTRODUCTION ):
                # START PARSING SECTION
                valid = True
                continue


            if valid:
                print "lets start..... ) "
                """
                matchObjectForCommitteeName = re.match( cls.COMMITTEE_NAME_FORMAT , line_content)
                matchObjectForCommitteeDateTimeVenueAndAgenda = re.match( r"Date: *" , line_content)

                if matchObjectForCommitteeName:   
                    committee_name = line_content.split(' ',1)[0]
                """
                    
                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    continue
                                                    
            else:
                # fallout
                pass


            if len(reports)==0:
                continue 

        if submitted_by!='':
            reports.append(dict(
                reference_docs=reference_docs,
                background=background,
                objective_of_bill =objective_of_bill,
                specific_provisions_of_bill=specific_provisions_of_bill,
                committee_observations =committee_observations,
                recommendations=recommendations,
                conclusion=conclusion,
                submitted_by=submitted_by
                            ))

        return reports

    @classmethod
    def parse_body(cls, lines):
        entries = []
        ###committee name 
        report_all = cls.parse_committee_report( list(lines) )
        for report in report_all:
            entries.append(report)

        return entries


def main(argv):
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = CommitteeReportParser(content)
        p.parse()
        print p.output()


if __name__ == "__main__":
    main(sys.argv)
