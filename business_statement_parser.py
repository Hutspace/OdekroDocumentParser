import sys
import re
from datetime import datetime
from datetime import date  
from parser import DocumentParser


class BusinessStatementParser(DocumentParser):
    NORMALIZATIONS = [
            (r'([0-9]*)\s*(st|ST|nd|ND|rd|RD|th|TH)\n', r'\1\2\s')
    ]
    SELECTION_MARKER = 'No. of Question(s)'
    MINISTER_AND_ROMAN_NUMERAL_FORMAT = r"(i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii)[.] Minister"
    CLOSING_MARKER = r"Total Number of Questions"
    

    def __init__(self, content):
        super(BusinessStatementParser, self).__init__(content)



    @classmethod
    def questions_asked(cls, lines):
        thekind, line, match = None, None, None
        questions_info = []
        valid = False

        total_questions  = ''
        questions = []

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.strip()

            if (thekind == cls.BLANK ):
                continue

            if (line_content == cls.SELECTION_MARKER):
                # START PARSING SECTION
                valid = True
                continue

            if valid:

                matchObjectForMinisterQuestioned = re.match( cls.MINISTER_AND_ROMAN_NUMERAL_FORMAT , line_content)

                if matchObjectForMinisterQuestioned:
                    all_questions_asked = line_content.split('.')

                    cnt_all_qnts_asked = len(all_questions_asked)
                    last_qtn_asked = cnt_all_qnts_asked - 1 
                    x=1
                    while x < cnt_all_qnts_asked:

                        string_in_qtn =  all_questions_asked[x]

                        if last_qtn_asked==x:
                            string_in_qtn_line_content = string_in_qtn
                            string_in_qtn = string_in_qtn_line_content.split('Total')[0] 
                            total_questions = string_in_qtn_line_content.split('Total')[1].rsplit(' ')[-1] 

                        x=x+1
                        for ch in ['xii','xi','ix','x','viii','vii','vi','iv','v','iii','ii']:
                            if ch in string_in_qtn:
                                string_in_qtn=string_in_qtn.replace(ch,'')

                        string_in_qtn = string_in_qtn.strip()

                        minister_no_of_qtns =  string_in_qtn.rsplit(' ',1)[-1]
                        minister_title =  string_in_qtn.rsplit(' ',1)[0].replace(',','')    
                        
                        questions.append(dict(
                            minister_title= minister_title,
                            minister_no_of_qtns=minister_no_of_qtns                            
                            ))
                        


                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    continue

            else:
                # fallout
                pass


            if len(questions_info)==0:
                continue


        if len(questions)>0:
            questions_info.append(dict(
                question_details=questions,
                total_questions=total_questions
                ))        

        return questions_info

    @classmethod
    def parse_body(cls, lines):
        entries = []
        all_questions = cls.questions_asked( list(lines) )
        for questions in all_questions:
            entries.append(questions)

        return entries


def main(argv):

    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = BusinessStatementParser(content)
        p.parse()
        data = p.output()
        for row in data:
            print "Total questions : %s" % (row['total_questions'])
            len_of_question_details = len(row['question_details'])
            print "minister_title|number of questions"
            x=y=0
            while y<len(row['question_details']):
                print "%s|%s" % ( row['question_details'][y]['minister_title'] , row['question_details'][y]['minister_no_of_qtns'])
                y=y+1 


if __name__ == "__main__":
    main(sys.argv)
