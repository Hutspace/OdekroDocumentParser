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
    DATE_MARKER = r".* WEEK ENDING"    
    MINISTER_AND_ROMAN_NUMERAL_FORMAT = r"(i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii)[.] Minister"
    CLOSING_MARKER = r"Total Number of Questions"
    

    def __init__(self, content):
        super(BusinessStatementParser, self).__init__(content)


    @classmethod
    def format_question_date(cls, question_date):
        qd_1 = question_date.strip().split('WEEK ENDING')[1]
        qd_2 = qd_1.split(',')[1]   
        qd_3 = qd_2.strip().split('-')
        date_full_1 = qd_3[0].replace('TH','').replace('ST','').replace('ND','').replace('RD','').replace('\\s','')
        qd_4 = date_full_1.split(' ')
        date_full_1 = "%s-%s-%s" % ( qd_4[0], qd_4[1][:3] , qd_4[2] )
        date_as_timestamp = datetime.strptime( date_full_1 , "%d-%b-%Y" ).strftime("%Y-%m-%d") 
        dt_format = date_as_timestamp.split("-")
        string_to_use_as_timestamp = "datetime.datetime(%s, %s, %s )"  % ( dt_format[0] , dt_format[1],dt_format[2] )                  
        return string_to_use_as_timestamp

    @classmethod
    def questions_asked(cls, lines):
        thekind, line, match = None, None, None
        questions_info = []
        valid = False

        total_questions  = ''
        question_date = ''
        questions = []

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.strip()

            if (thekind == cls.BLANK ):
                continue

            matchObjectForDate = re.match( cls.DATE_MARKER , line_content)
            if matchObjectForDate:
                question_date = cls.format_question_date(  line_content )



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
                question_date=question_date
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
            len_of_question_details = len(row['question_details'])
            print "Question date | Minister title | Number of questions"
            x=y=0
            while y<len(row['question_details']):
                print "%s|%s|%s" % ( 
                    row['question_date'] ,                   
                    row['question_details'][y]['minister_title'] , 
                    row['question_details'][y]['minister_no_of_qtns'] ,
                    )
                y=y+1 


if __name__ == "__main__":
    main(sys.argv)
