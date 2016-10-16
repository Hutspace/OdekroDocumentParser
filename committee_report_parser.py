# -*- coding: utf-8 -*- 

import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class CommitteeReportParser(DocumentParser):
    SELECTION_MARKER_POINT_1 = r"1\.0 [A-Z]*"     
    SELECTION_MARKER_INTRODUCTION = r"[0-9.]* INTRODUCTION"
    SELECTION_MARKER_BACKGROUND = r"[0-9.]* BACKGROUND" 
    SELECTION_MARKER_DELIBRATIONS = r"[0-9.]* DELIBRATIONS"    
    SELECTION_MARKER_OBJECTIVE = r"[0-9.]* (PROJECT)* OBJECTIVE"
    SELECTION_MARKER_SPECIFIC_PROVISIONS_OF_BILL = r"[0-9.]* PROVISIONS OF BILL"
    SELECTION_MARKER_RECOMMENDATIONS = r"[0-9.]* RECOMMENDATIONS"
    SELECTION_TERMS_AND_CONDITIONS = r"[0-9.]* TERMS AND CONDITIONS [A-Z]*"
    SELECTION_DESCRIPTION = r"[0-9.]* [A-Z]* DESCRIPTION"
    SELECTION_MARKER_CONCLUSION = r"[0-9.]* CONCLUSION [A-Z]*"
    SELECTION_MARKER_SUBMITTED_BY = 'Respectfully submitted'                    
    SELECTION_PAGE_NUMBERS = r"(Page)* [0-9]*"
    SELECTION_MARKER_COMMITTEE_OBSERVATIONS = r"([0-9.]* COMMITTEE OBSERVATIONS|[0-9.]* OBSERVATIONS)" 
    SELECTION_JUSTIFICATION=r"[0-9.]* JUSTIFICATION .*"


    SELECTION_MARKER_REFERENCE_DOCS = r"[0-9.]* REFERENCE (DOCS|DOCUMENTS)*"

    def __init__(self, content):
        super(CommitteeReportParser, self).__init__(content)


    @classmethod
    def parse_committee_report(cls, lines):
        thekind, line, match = None, None, None
        reports = []
        valid = False

        reference= background=objective = specific_provisions_of_bill=description= ''
        observations = recommendations= conclusion= ''
        submitted_by=delibrations = point_1 = introduction = justification = terms_and_conditions= ''


        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.encode("utf-8")
            line_content = line_content.strip()
            line_content = line_content.replace('$$','').replace('~~','').replace('¥¥','').replace('¥~¥','')

            #print line_content 

            if (thekind == cls.BLANK ):
                continue


            matchObjectForPointOne = re.match( cls.SELECTION_MARKER_POINT_1 , line_content)
            matchObjectForIntroduction = re.match( cls.SELECTION_MARKER_INTRODUCTION , line_content)          
            matchObjectForPageNumbers = re.match( cls.SELECTION_PAGE_NUMBERS , line_content)          
            matchObjectForBackground = re.match( cls.SELECTION_MARKER_BACKGROUND , line_content)          
            matchObjectForObjective = re.match( cls.SELECTION_MARKER_OBJECTIVE , line_content)          
            matchObjectForDelibrations = re.match( cls.SELECTION_MARKER_DELIBRATIONS , line_content)    
            matchObjectForReference = re.match( cls.SELECTION_MARKER_REFERENCE_DOCS , line_content)    
            matchObjectForJustification = re.match( cls.SELECTION_JUSTIFICATION , line_content) 
            matchObjectForTermsAndConditions = re.match( cls.SELECTION_TERMS_AND_CONDITIONS, line_content )   
            matchObjectForDescription = re.match( cls.SELECTION_DESCRIPTION, line_content )     
            matchObjectForObservations = re.match( cls.SELECTION_MARKER_COMMITTEE_OBSERVATIONS, line_content )     
            matchObjectForConclusion = re.match( cls.SELECTION_MARKER_CONCLUSION, line_content )     

            if matchObjectForIntroduction:
                valid = introduction_next =True 
                delibrations_next= reference_next = background_next=justification_next=objective_next=False
                terms_and_conditions_next= description_next=observations_next=conclusion_next= False
                # START PARSING SECTION
                continue
                    
            elif matchObjectForBackground:
                introduction_next=reference_next=delibrations_next=justification_next=objective_next=False 
                terms_and_conditions_next=description_next=observations_next=conclusion_next=False
                background_next =True 
                continue
            elif matchObjectForConclusion:
                introduction_next=reference_next=delibrations_next=justification_next=objective_next=False 
                terms_and_conditions_next=description_next=observations_next=background_next=False
                conclusion_next =True                 
                continue
            elif matchObjectForObjective:
                introduction_next=reference_next=background_next=delibrations_next=justification_next=objective_next=False  
                terms_and_conditions_next=description_next=observations_next=conclusion_next=False
                objective_next=True
                continue
            elif matchObjectForObservations:
                introduction_next=reference_next=background_next=delibrations_next=justification_next=objective_next=False  
                terms_and_conditions_next=description_next=objective_next=conclusion_next=False
                observations_next=True
                continue                
            elif matchObjectForDelibrations:
                introduction_next=reference_next=background_next=justification_next=objective_next=False
                terms_and_conditions_next=description_next=observations_next=conclusion_next=False
                delibrations_next=True     
                continue   
            elif matchObjectForReference:
                introduction_next=delibrations_next =background_next=justification_next=objective_next=False
                terms_and_conditions_next=description_next=observations_next=conclusion_next=False
                reference_next=True                     
                continue      
            elif matchObjectForTermsAndConditions:
                introduction_next=delibrations_next =background_next=justification_next=objective_next=reference_next=False
                description_next=observations_next=conclusion_next=False
                terms_and_conditions_next=True                     
                continue                      
            elif matchObjectForJustification:
                introduction_next=delibrations_next =background_next=reference_next=objective_next=False
                terms_and_conditions_next=description_next=observations_next=conclusion_next=False
                justification_next=True     
                continue
            elif matchObjectForDescription:
                introduction_next=delibrations_next =background_next=reference_next=objective_next=False
                terms_and_conditions_next=justification_next= observations_next=conclusion_next=False
                description_next=True          
                continue           
            else:
                # fallout
                pass

            if valid and introduction_next:
                introduction = "%s %s" % (introduction , line_content)   

            if valid and delibrations_next:
                delibrations = "%s %s" % (delibrations , line_content)  

            if valid and reference_next:
                reference = "%s %s" % (reference , line_content)    

            if valid and background_next:
                background = "%s %s" % (background , line_content)    

            if valid and justification_next:
                justification = "%s %s" % ( justification , line_content)

            if valid and objective_next:
                objective = "%s %s" % ( objective , line_content)

            if valid and terms_and_conditions_next:
                terms_and_conditions = "%s %s" % ( terms_and_conditions , line_content)

            if valid and description_next:
                description = "%s %s" % ( description , line_content )

            if valid and observations_next:
                observations = "%s %s" % ( observations , line_content )           

            if valid and conclusion_next:
                conclusion = "%s %s" % ( conclusion , line_content )           
                
                 
            
                    
        reports.append(dict(
            introduction=introduction,
            delibrations=delibrations,
            reference=reference,
            background=background,
            justification=justification,
            description=description,
            objective =objective,
            terms_and_conditions=terms_and_conditions,
            specific_provisions_of_bill=specific_provisions_of_bill,
            observations =observations,
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
