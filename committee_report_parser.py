# -*- coding: utf-8 -*- 

import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class CommitteeReportParser(DocumentParser):
    SELECTION_MARKER_POINT_1 = r"1\.0 [A-Z]*"     

    SELECTION_MARKER_INTRODUCTION = r"[0-9.]* INTRODUCTION"
    SELECTION_MARKER_BACKGROUND = r"([0-9.]* BACKGROUND [A-Z]*|[0-9.]* BACKGROUND)" 
    SELECTION_MARKER_DELIBRATIONS = r"[0-9.]* DELIBRATIONS"    
    SELECTION_MARKER_OBJECTIVE = r"[0-9.]* (PROJECT)* OBJECTIVE"
    SELECTION_MARKER_SPECIFIC_PROVISIONS_OF_BILL = r"[0-9.]* PROVISIONS OF BILL"
    SELECTION_MARKER_RECOMMENDATIONS = r"[0-9.]* RECOMMENDATIONS"
    SELECTION_TERMS_AND_CONDITIONS = r"[0-9.]* TERMS AND CONDITIONS [A-Z]*"
    SELECTION_DESCRIPTION = r"[0-9.]* [A-Z]* DESCRIPTION"
    SELECTION_MARKER_CONCLUSION = r"([0-9.]* CONCLUSION [A-Z]*|[0-9.]* CONCLUSION|[0-9.]* CONCLUSSIONS|[0-9.]* CONCLUSIONS)"
    SELECTION_MARKER_SUBMITTED_BY = r"Respectfully submitted"                    
    SELECTION_PAGE_NUMBERS = r"(Page [0-9]*|[0-9]{4}|[0-9]{1}|(July|January|June||September|Novermber|December|April|August|October|March|May|Februay) [0-9]{1})"
    SELECTION_MARKER_COMMITTEE_OBSERVATIONS = r"([0-9.]* COMMITTEE OBSERVATIONS|[0-9.]* OBSERVATIONS|[0-9.]* KEY OBSERVATIONS)" 
    SELECTION_JUSTIFICATION=r"([0-9.]* JUSTIFICATION [A-Z ]*|[0-9.]* JUSTIFICATION)"

    SELECTION_MARKER_REFERENCE_DOCS = r"[0-9.]* REFERENCE (DOCS|DOCUMENTS)*"

    def __init__(self, content):
        super(CommitteeReportParser, self).__init__(content)

    @classmethod
    def reg_check_on_selection_marker(cls,passed_selection_marker,line_content):
        return re.match( passed_selection_marker, line_content)

    @classmethod    
    def sanitize_line_content(cls,line_content):
        line_content = line_content.strip()
        line_content = line_content.replace('$$','').replace('~~','').replace('¥¥','').replace('¥~¥','').replace("...","")
        line_content = line_content.replace('--','').replace('\\','').replace(';','')
        line_content = line_content.replace('\xe80','').replace('\xa2','').replace('\xe2','').replace('\x80','')
        line_content = line_content.replace(',','').replace('--','').replace('==','').replace('::','').replace('__','')
        line_content = line_content.replace('.:.','')
        line_content = line_content.strip()
        return line_content 

    @classmethod        
    def truth_value_for_section(cls,matchObjectForDescription,delibrations_next):
        if matchObjectForDescription:
            delibrations_next=True    
            return  (delibrations_next,True)
                     
        else:
            return  (delibrations_next,False)        
           
    
    @classmethod
    def parse_committee_report(cls, lines):
        thekind, line, match = None, None, None
        reports = []
        valid = False

        reference= background=objective = specific_provisions_of_bill=description= submitted_by=''
        observations = recommendations= conclusion= ''
        submitted_by=delibrations  = introduction = justification = terms_and_conditions= ''
        point_1 =''
        

        valid = introduction_next =False 
        delibrations_next= reference_next = background_next=justification_next=objective_next=False
        terms_and_conditions_next= description_next=observations_next=conclusion_next= submitted_by_next=False
               

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.encode("utf-8")
            line_content = cls.sanitize_line_content(line_content)


            #print line_content 

            if (thekind == cls.BLANK ):
                continue

            matchObjectForPoint1 = cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_POINT_1 , line_content)
            

            matchObjectForIntroduction = cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_INTRODUCTION , line_content)          
            matchObjectForPageNumbers = cls.reg_check_on_selection_marker( cls.SELECTION_PAGE_NUMBERS , line_content)          
            matchObjectForBackground = cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_BACKGROUND , line_content)          
            matchObjectForObjective = cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_OBJECTIVE , line_content)          
            matchObjectForDelibrations = cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_DELIBRATIONS , line_content)    
            matchObjectForReference = cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_REFERENCE_DOCS , line_content)    
            matchObjectForJustification = cls.reg_check_on_selection_marker( cls.SELECTION_JUSTIFICATION , line_content) 
            matchObjectForTermsAndConditions = cls.reg_check_on_selection_marker( cls.SELECTION_TERMS_AND_CONDITIONS, line_content )   
            matchObjectForDescription = cls.reg_check_on_selection_marker( cls.SELECTION_DESCRIPTION, line_content )     
            matchObjectForObservations = cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_COMMITTEE_OBSERVATIONS, line_content )     
            matchObjectForConclusion =  cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_CONCLUSION ,line_content)
            matchObjectForSubmittedBy =  cls.reg_check_on_selection_marker( cls.SELECTION_MARKER_SUBMITTED_BY ,line_content)

            if matchObjectForIntroduction:
                introduction_next,valid = cls.truth_value_for_section(matchObjectForIntroduction,introduction_next)

                delibrations_next= reference_next = background_next=justification_next=objective_next=False
                terms_and_conditions_next= description_next=observations_next=conclusion_next= submitted_by_next=False                                                                                                                  
                continue
            elif matchObjectForDescription:
                description_next,valid = cls.truth_value_for_section(matchObjectForDescription,description_next)
                delibrations_next= reference_next = background_next=justification_next=objective_next=False
                terms_and_conditions_next= introduction_next=observations_next=conclusion_next= submitted_by_next=False                                                                                                                     
                continue                      
            elif matchObjectForBackground:
                background_next,valid = cls.truth_value_for_section(matchObjectForBackground,background_next)
                delibrations_next= reference_next = description_next=justification_next=objective_next=False
                terms_and_conditions_next= introduction_next=observations_next=conclusion_next= submitted_by_next=False                                                                                                                                                   
                continue
            elif matchObjectForConclusion:
                conclusion_next,valid = cls.truth_value_for_section(matchObjectForConclusion,conclusion_next)
                delibrations_next= reference_next = description_next=justification_next=objective_next=False
                terms_and_conditions_next= introduction_next=observations_next=background_next= submitted_by_next=False                                                                                                                                                                 
                continue
            elif matchObjectForObjective:
                objective_next,valid = cls.truth_value_for_section(matchObjectForObjective,objective_next)
                delibrations_next= reference_next = description_next=justification_next=conclusion_next=False
                terms_and_conditions_next= introduction_next=observations_next=background_next= submitted_by_next=False                                                                                                                                                                  
                continue
            elif matchObjectForObservations:
                observations_next,valid = cls.truth_value_for_section(matchObjectForObservations,observations_next)                
                delibrations_next= reference_next = description_next=justification_next=conclusion_next=False
                terms_and_conditions_next= introduction_next=objective_next=background_next= submitted_by_next=False                                                                                                                                                                                    
                continue                
            elif matchObjectForDelibrations:
                delibrations_next,valid = cls.truth_value_for_section(matchObjectForDelibrations,delibrations_next)                                
                observations_next= reference_next = description_next=justification_next=conclusion_next=False
                terms_and_conditions_next= introduction_next=objective_next=background_next= submitted_by_next=False                                                                                                                                                                                    
                continue   
            elif matchObjectForReference:
                reference_next,valid = cls.truth_value_for_section(matchObjectForReference,reference_next)                                
                delibrations_next= observations_next = description_next=justification_next=conclusion_next=False
                terms_and_conditions_next= introduction_next=objective_next=background_next= submitted_by_next=False                                                                                                                                                                                    
                continue      
            elif matchObjectForTermsAndConditions:
                terms_and_conditions_next,valid = cls.truth_value_for_section(matchObjectForTermsAndConditions,terms_and_conditions_next)                                 
                delibrations_next= reference_next = description_next=justification_next=conclusion_next=False
                observations_next= introduction_next=objective_next=background_next= submitted_by_next=False                                                                                                                                                                                    
                continue                      
            elif matchObjectForJustification:
                justification_next,valid = cls.truth_value_for_section(matchObjectForJustification,justification_next)                                
                delibrations_next= reference_next = description_next=terms_and_conditions_next=conclusion_next=False
                observations_next= introduction_next=objective_next=background_next= submitted_by_next=False                                                                                                                                                                                                 
                continue
            elif matchObjectForDescription:
                description_next,valid = cls.truth_value_for_section(matchObjectForDescription,description_next)                                
                delibrations_next= reference_next = observations_next=justification_next=conclusion_next=False
                terms_and_conditions_next= introduction_next=objective_next=background_next= submitted_by_next=False                                                                                                                                                                                   
                continue           
            elif matchObjectForSubmittedBy:
                submitted_by_next,valid = cls.truth_value_for_section(matchObjectForSubmittedBy,submitted_by_next)                                
                delibrations_next= reference_next = description_next=justification_next=conclusion_next=False
                terms_and_conditions_next= introduction_next=objective_next=background_next= observations_next=False                                                                                 
                continue 
            elif matchObjectForPageNumbers:
                continue        
            else:
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

            if valid and submitted_by_next:
                submitted_by = "%s %s" % ( submitted_by , line_content ) 

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
            submitted_by=submitted_by,
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


