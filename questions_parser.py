import sys
from parser import DocumentParser
from datetime import datetime
from datetime import date


class QuestionsParser(DocumentParser):

    KIND_QUESTIONS_SECTION = 'questions_start'
    KIND_QUESTION = 'question'
    KIND_QUESTION_PARTIAL = 'question partial'
    KIND_ANSWERS_SECTION = 'answers_start'
    KIND_ANSWER = 'answer'
    KIND_OTHER_HEADER = 'header'

    QUESTION_HEADER_PATTERN = r'^(?:\d+\.)?\s*(NOTICE OF\s*|URGENT\s*)?QUESTION(S)?.*'
    INTERROGATIVE = r'(?:how|when|what|if|why|where|which|whether|the)'
    MINISTER_TITLE = r'(Minister\s*(?:for|of)\s*[A-Za-z]*\s*(?:and\s*[A-Za-z ]*)?)'
    QUESTION_INTRO = r'To\s*ask\s*the\s*%s' % MINISTER_TITLE
    # QUESTION_INTRO = r'To\s*ask\s*the\s*(Minister\s*for.*)'
    QUESTION_INTRO_PARTIAL = r'^(\*\d+\.)?\s*(.*):\s*To\s*ask'
    QUESTION_START_PATTERN = r'^(\*\d+\.)?\s*(.*):\s*%s\s*(%s.*)+' % (QUESTION_INTRO, INTERROGATIVE)
    # QUESTION_START_PATTERN = r'^(\*\d+\.)?\s*(.*):\s*To\s*ask\s*the\s*(Minister\s*for.*)\s*((?:how|when|what|if|why|where|which|whether).*)'

    ANSWERS_HEADER_PATTERN = r'^ANSWERS'
    ANSWER_START_PATTERN = r'^(\*\d+\.)\s*(.*)'
    OTHER_HEADER_PATTERN = r'^\s*[0-9.]*\s*([A-Z-,\s]+)\s*$'

    HEADING_PATTERN = r'^\s*[0-9.]*\s*([A-Z-,\s]+)\s*$'

    BASE_PATTERNS = ()
    CUSTOM_PATTERNS = (
        (KIND_QUESTIONS_SECTION, QUESTION_HEADER_PATTERN),
        (KIND_ANSWERS_SECTION, ANSWERS_HEADER_PATTERN),

        (KIND_QUESTION, QUESTION_START_PATTERN),
        (KIND_QUESTION_PARTIAL, QUESTION_INTRO_PARTIAL),
        (KIND_ANSWER, ANSWER_START_PATTERN),
        (KIND_OTHER_HEADER, OTHER_HEADER_PATTERN)
    )

    NORMALIZATION = [
            (r'(To ask.*)\n\n', r'\1 ')
    ]

    def __init__(self, content):
        super(QuestionsParser, self).__init__(content)

    @classmethod
    def reconstruct_question(cls, current_line, remaining_lines):
        reconstructed = current_line
        while(len(remaining_lines) > 0):
            nextkind, nextline, nextmatch = remaining_lines.pop(0)
            if nextkind == cls.LINE:
                reconstructed = ' '.join([reconstructed, nextline])
            if nextkind in [cls.KIND_QUESTION_PARTIAL, cls.ANSWERS_HEADER_PATTERN, cls.KIND_OTHER_HEADER]:
                break
        print cls.scan_line(reconstructed)
        remaining_lines.insert(0, cls.scan_line(reconstructed))

    @classmethod
    def parse_qa(cls, kind, lines):
        thekind, line, match = None, None, None
        parsed = []
        valid = False
        num = 0
        timestamp = None

        while len(lines):
            thekind, line, match = lines.pop(0)
            num += 1

            if (thekind == cls.DATE):
                timestamp = date(int(match.group(4)),
                                 cls.MONTHS[match.group(3).lower()[:3]],
                                 int(match.group(2)))
                timestamp = datetime.combine(timestamp, datetime.min.time())

            if not valid and (thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                continue

            if thekind == kind:
                valid = True
                continue

            if valid and thekind == cls.KIND_QUESTION:  # start of question/answer
                qid = ''
                if match.group(1) is not None:
                    qid = match.group(1).replace('*', '').replace('.', '')
                else:
                    qid = 'urg'
                source = match.group(2)
                target = match.group(3)
                query = match.group(4)
                parsed_question = dict(ref=qid,
                                       timestamp_question=timestamp,
                                       timestamp_answer=None,
                                       source=source,
                                       target=target,
                                       question=query,
                                       answer=None)
                print parsed_question
                parsed.append(parsed_question)

            if valid and thekind == cls.KIND_QUESTION_PARTIAL:
                # new_line = line
                # while(len(lines) > 0):
                #     nextkind, nextline, nextmatch = lines.pop(0)
                #     if nextkind == cls.LINE:
                #         new_line = ' '.join([new_line, nextline])
                #     if nextkind in [cls.KIND_QUESTION_PARTIAL, cls.ANSWERS_HEADER_PATTERN, cls.KIND_OTHER_HEADER]:
                #         m = re.match(cls.QUESTION_START_PATTERN, new_line)
                #         print new_line
                #         print m.group(1)
                #         print m.group(2)
                #         print m.group(3)
                #         print m.group(4)
                #         lines.insert(0, (cls.KIND_QUESTION, new_line, m))
                #         break
                cls.reconstruct_question(line, lines)
                continue

            if valid and thekind == cls.KIND_ANSWER:
                qid = ''
                if match.group(1) is not None:
                    qid = match.group(1).replace('*', '').replace('.', '')
                else:
                    qid = 'urg'
                response = match.group(2)
                parsed_response = dict(ref=qid,
                                       timestamp_answer=timestamp,
                                       answer=response)
                print parsed_response
                parsed.append(parsed_response)

            # continued question/answer append
            if valid and thekind == cls.LINE:
                pass
                # print '{0}: {1} '.format(kind, str(line))

            if valid and (kind == cls.KIND_QUESTIONS_SECTION) and (thekind == cls.KIND_ANSWERS_SECTION):
                valid = False

            if valid and (kind == cls.KIND_ANSWERS_SECTION) and (thekind == cls.KIND_QUESTIONS_SECTION):
                # print 'IGNORE Kind: {0} - {1}'.format(thekind, line)
                valid = False
            # lines.insert(0, (thekind, line, match))
            # break
        return parsed

    @classmethod
    def parse_body(cls, lines):
        entries = []
        questions = cls.parse_qa(cls.KIND_QUESTIONS_SECTION, list(lines))
        # answers = parse_qa(cls.KIND_ANSWERS_SECTION, list(lines))
        return entries


def main(argv):
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = QuestionsParser(content)
        p.parse()
        print p.output()


if __name__ == '__main__':
    main(sys.argv)
