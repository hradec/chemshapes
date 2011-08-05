import re

class LifParser(object):
    meta = re.compile(r'#(Life|D)')
    rule = re.compile(r'#([NR])')
    pattern = re.compile(r'#P (-?\d+) (-?\d+)')
    matchers = meta, rule, pattern
   
    @classmethod
    def match(cls, line):
        for matcher in cls.matchers:
            match = matcher.match(line)
            if match:
                return matcher, match.groups()
        return None, None

    @classmethod
    def parse_pattern(cls, lines):
        pattern = set()
        y = 0
        while lines and lines[0][0] != '#':
            line = lines.pop(0)
            x = 0
            for c in line:
                if c == '*':
                    pattern.add((x,y))
                x+=1
            y += 1
        return pattern

    @classmethod
    def parse(cls, filename):
        lines = [line.strip() for line in open(filename) if line.strip()]
        ruleset = None
        patterns = list()

        while lines:
            type, groups = cls.match(lines.pop(0))
            if type == cls.meta:
                pass
            elif type == cls.rule:
                ruleset = groups[0]
            elif type == cls.pattern:
                x, y = map(int, groups)
                pattern = cls.parse_pattern(lines)
                patterns.append((x,y,pattern))
        return ruleset, patterns
