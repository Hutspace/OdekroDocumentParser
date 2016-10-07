import re
import sys


class DocumentParser(object):

    # Constants for various types of lines that might be found in the document
    BLANK = 'blank'
    TIME = 'time'
    DATE = 'date'
    HEADING = 'heading'
    LINE = 'line'
    PAGE_HEADER = 'page header'

    MONTHS = dict(jan=1, feb=2, mar=3, apr=4, may=5, jun=6, jul=7, aug=8, sep=9, oct=10, nov=11, dec=12)

    ORDINAL_WORDS = dict(first=1, second=2, third=3, fourth=4, fifth=5, sixth=6, seventh=7)

    PRINTED_BY_MARKER = 'printed by department of official report'
    SERIES_VOL_NO_PATTERN = r'^\s*([A-Z]+)\s+SERIES\s+VOL\.?\s*(\d+)\s*N(O|o|0)\.?\s*(\d+)\s*$'
    TITLES_TEMPLATE = '(Mr|Mrs|Ms|Miss|Papa|Alhaji|Madam|Dr|Prof|Chairman|Chairperson|Minister|An Hon Mem|Some Hon Mem|Minority|Majority|Nana)'
    TIME_TEMPLATE = '(\d\d?)(:|\.)(\d\d)\s*(am|a.\s*m|AM|A.\s*M|pm|PM|p.\s*m|P.\s*M|noon)\.?[\s\-]*'
    TIME_PATTERN = r'^\s*%s$' % TIME_TEMPLATE
    DATE_PATTERN = r'^\s*([A-Za-z]+\s*,\s*)?(\d+)\w{0,2}\s+(\w+),?\s+(\d+)\s*$'
    HEADING_PATTERN = r'^\s*[0-9.]*\s*([A-Za-z-,\s]+)\s*$'
    PAGE_HEADER_PATTERN = r'^\[(\d+)\]\s*$'

    HAS_HEADER = True
    NORMALIZATIONS = []

    HEADER_PATTERNS = None
    BASE_HEADER_PATTERNS = (
        (DATE, DATE_PATTERN),
    )
    CUSTOM_HEADER_PATTERNS = ()

    PATTERNS = None
    BASE_PATTERNS = (
        (HEADING, HEADING_PATTERN),
        (TIME, TIME_PATTERN),
        (PAGE_HEADER, PAGE_HEADER_PATTERN),
    )
    CUSTOM_PATTERNS = ()

    def __init__(self, content):
        self.content = content
        self.head = None
        self.entries = None

    @classmethod
    def setup_patterns(cls):
        cls.HEADER_PATTERNS = cls.BASE_HEADER_PATTERNS + cls.CUSTOM_HEADER_PATTERNS
        cls.PATTERNS = cls.BASE_PATTERNS + cls.CUSTOM_PATTERNS

    def parse(self):
        self.setup_patterns()
        lines = self.normalised_lines(self.content)
        lines = self.scan(lines)

        self.head = self.parse_head(lines)  # end_line
        self.entries = self.parse_body(lines)  # start_line

    def output(self):
        return self.entries

    @classmethod
    def scan_header_line(cls, line):
        for kind, pattern in cls.HEADER_PATTERNS:
            match = re.match(pattern, line)
            if match:
                return (kind, line, match)
        return None

    @classmethod
    def scan_line(cls, line):
        if not line.strip():
            return (cls.BLANK, '\n', None)
        for kind, pattern in cls.PATTERNS:
            match = re.match(pattern, line)
            if match:
                return (kind, line, match)
        return (cls.LINE, line.replace('\n', ' '), None)

    @classmethod
    def scan(cls, lines):
        if cls.HAS_HEADER:
            return [cls.scan_header_line(x) or cls.scan_line(x) for x in lines]
        return [cls.scan_line(x) for x in lines]

    @classmethod
    def parse_head(cls, lines):
        """
        Parse the document to extract the header information. Returns a dict.
        """
        return dict()

    @classmethod
    def parse_body(cls, lines):
        entries = []
        # parse body
        return entries

    @classmethod
    def preprocess(self, content):
        # hack to clear newlines and other chars we are seeing in some of the content
        content = '\n'.join([x.strip().decode('utf8', 'ignore') for x in content.splitlines()])
        content = ''.join(content.split(u'\xaf'))
        for s, r in [(u'\u2013', '-'), (u'\ufeff', ''),
                     (u'O\ufb01icial', 'Official'),
                     (u'Of\ufb01cial', 'Official'),
                     (u'\ufb01', 'fi'), (u'\ufb02', 'ff'),
                     (u'\u2019', "'"),
                     ('~', '-'),
                     ]:
            content = r.join(content.split(s))
        return content

    @classmethod
    def normalised_lines(cls, content):
        return cls.normalise_line_breaks(cls.preprocess(content)).split("\n")

    @classmethod
    def normalise_line_breaks(cls, content):
        # Each tuple is a (pattern, replacement) to apply to the string, in the
        # order listed here. Note that the re.M flag is applied so that ^ and $
        # DWIM.
        breaks = [
            # make whitespace consistent
            (r'\r', '\n'),  # convert any vertical whitespace to '\n'
            (r'[ \t]+', ' '),  # horizontal whitespace becomes single space
            (r' *\n *', '\n'),  # trim spaces from around newlines

            # Add breaks around the column numbers
            (r'\s*(\[\d+\])\s*', r"\n\n\1\n\n"),

            # Add breaks around anything that is all in CAPITALS
            # (r'^([^a-z]+?)$', r"\n\n\1\n\n"),
            # not sure why the '+?' can't just be '+' - if it is just '+' the
            # newline gets included too despite the re.M. Pah!

            # Add break before things that look like lists
            (r'^([ivx]+\))', r'\n\n\1'),

            # Add breaks around timestamps
            (r'^(%s)$' % cls.TIME_TEMPLATE, r"\n\n\1\n\n"),

            # Add a break before anything that looks like it might be a person's
            # name at the start of a speech
            (r'^(%s.+:)' % cls.TITLES_TEMPLATE, r'\n\n\1'),
        ]

        whitespace = [
            # Finally normalise the whitespace
            (r'(\S)\n(\S)', r'\1 \2'),  # wrap consecutive lines
            (r'\n\n+', "\n\n"),        # normalise line breaks
        ]

        normalizations = breaks + cls.NORMALIZATIONS + whitespace

        # apply all the transformations above
        for pattern, replacement in normalizations:
            content = re.sub(pattern, replacement, content, flags=re.M)

        return content.strip()


def main(argv):
    print "Extend this object."

if __name__ == "__main__":
    main(sys.argv)
