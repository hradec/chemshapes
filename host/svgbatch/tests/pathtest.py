from mock import Mock, RunTests, TestCase

from svgbatch.path import Path, PathDataParser, ParseError, SvgLoopTracer


class PathDataTest(TestCase):

    def test_to_tuples_typical(self):
        data = [
            ' M 1, 2 L 3.0, 4.0 L 5, 6.0 Z ',
            'M 1, 2 L 3.0, 4.0 L 5, 6.0 Z',
            'M 1,2 L 3.0,4.0 L 5,6.0 Z',
            'M 1 2 L 3.0 4.0 L 5 6.0 Z',
            'M1, 2 L3.0, 4.0 L5, 6.0 Z',
            'M1,2 L3.0,4.0 L5,6.0 Z',
            'M1 2 L3.0 4.0 L5 6.0 Z',
            'M 1, 2L 3.0, 4.0L 5, 6.0Z',
            'M 1,2L 3.0,4.0L 5,6.0Z',
            'M 1 2L 3.0 4.0L 5 6.0Z',
            'M1, 2L3.0, 4.0L5, 6.0Z',
            'M1,2L3.0,4.0L5,6.0Z',
            'M1 2L3.0 4.0L5 6.0Z',
        ]
        expected = [ ('M', 1, 2), ('L', 3.0, 4.0), ('L', 5, 6.0), ('Z',)]
        for input in data:
            pathData = PathDataParser()
            actual = pathData.to_tuples(input)
            self.assertEquals(actual, expected, 'for %s' % (input,))


    def assert_to_tuples(self, data):
        for input, expected in data:
            pathData = PathDataParser()
            actual = pathData.to_tuples(input)
            self.assertEquals(actual, expected, 'for %r' % (input,))

            # test types of int/floats too. assertEquals doesn't
            for actual_cmd, exp_cmd in zip(actual, expected):
                for actual_param, exp_param in zip(actual_cmd, exp_cmd):
                    self.assertEquals(
                        type(actual_param),
                        type(exp_param),
                        'for %r' % (input,))


    def test_to_tuples_no_commands(self):
        self.assert_to_tuples([
            ('',            []),
            (' ',           []),
        ])


    def test_to_tuples_one_command_one_arg(self):
        self.assert_to_tuples([
            ('a',           [('a',)]),
            (' a ',         [('a',)]),
            ('a1',          [('a', 1)]),
            (' a 1 ',       [('a', 1)]),
            ('a-1',         [('a', -1)]),
            (' a -1 ',      [('a', -1)]),
            ('a1.0',        [('a', 1.0)]),
            (' a 1.0 ',     [('a', 1.0)]),
            ('a-1.0',       [('a', -1.0)]),
            (' a -1.0 ',    [('a', -1.0)]),
        ])

    def test_to_tuples_one_command_two_args(self):
        self.assert_to_tuples([
            ('a1 2',        [('a', 1, 2)]),
            ('a1,2',        [('a', 1, 2)]),
            (' a 1 2 ',     [('a', 1, 2)]),
            (' a 1,2 ',     [('a', 1, 2)]),
            (' a 1 , 2 ',   [('a', 1, 2)]),

            ('a-1 -2',      [('a', -1, -2)]),
            ('a-1,-2',      [('a', -1, -2)]),
            ('a-1-2',       [('a', -1, -2)]),
            (' a -1, -2 ',  [('a', -1, -2)]),
            (' a -1,-2 ',   [('a', -1, -2)]),
            (' a -1 -2 ',   [('a', -1, -2)]),
            (' a -1-2 ',    [('a', -1, -2)]),

            ('a1 -2',       [('a', 1, -2)]),
            ('a1,-2',       [('a', 1, -2)]),
            ('a1-2',        [('a', 1, -2)]),
            (' a 1, -2 ',   [('a', 1, -2)]),
            (' a 1,-2 ',    [('a', 1, -2)]),
            (' a 1 -2 ',    [('a', 1, -2)]),
            (' a 1-2 ',     [('a', 1, -2)]),

            ('a-1-2',       [('a', -1, -2)]),
            (' a -1 -2 ',   [('a', -1, -2)]),
            ('a-1,-2',      [('a', -1, -2)]),
            (' a -1 , -2 ', [('a', -1, -2)]),

            ('a1 -2.0',     [('a', 1, -2.0)]),
            ('a1,-2.0',     [('a', 1, -2.0)]),
            ('a1-2.0',      [('a', 1, -2.0)]),
            (' a 1, -2.0 ', [('a', 1, -2.0)]),
            (' a 1,-2.0 ',  [('a', 1, -2.0)]),
            (' a 1 -2.0 ',  [('a', 1, -2.0)]),
            (' a 1-2.0 ',   [('a', 1, -2.0)]),

            ('a-1.0-2.0',       [('a', -1.0, -2.0)]),
            (' a -1.0 -2.0 ',   [('a', -1.0, -2.0)]),
            (' a -1.0,-2.0 ',   [('a', -1.0, -2.0)]),
            (' a -1.0 , -2.0 ', [('a', -1.0, -2.0)]),
        ])

    def test_to_tuples_two_commands(self):
        self.assert_to_tuples([
            ('ab',          [('a',), ('b',)]),
            ('a b',         [('a',), ('b',)]),
            (' a b ',       [('a',), ('b',)]),
            ('a1b',         [('a', 1), ('b',)]),
            ('a-1b',        [('a', -1), ('b',)]),
            (' a 1 b ',     [('a', 1), ('b',)]),
            (' a -1 b ',    [('a', -1), ('b',)]),
            ('a1.0b',       [('a', 1.0), ('b',)]),
            ('a-1.0b',      [('a', -1.0), ('b',)]),
            (' a 1.0 b ',   [('a', 1.0), ('b',)]),
            (' a -1.0 b ',  [('a', -1.0), ('b',)]),
            ('ab2',         [('a',), ('b', 2)]),
            ('ab-2',        [('a',), ('b', -2)]),
            ('a b2',        [('a',), ('b', 2)]),
            ('a b-2',       [('a',), ('b', -2)]),
            ('a b 2',       [('a',), ('b', 2)]),
            (' a b 2 ',     [('a',), ('b', 2)]),
            ('ab2.0',       [('a',), ('b', 2.0)]),
            ('ab-2.0',      [('a',), ('b', -2.0)]),
            ('a b2.0',      [('a',), ('b', 2.0)]),
            ('a b 2.0',     [('a',), ('b', 2.0)]),
            ('a b -2.0',    [('a',), ('b', -2.0)]),
            (' a b 2.0 ',   [('a',), ('b', 2.0)]),
            ('a1b2',        [('a', 1), ('b', 2)]),
            ('a-1b-2',      [('a', -1), ('b', -2)]),
            ('a1 b2',       [('a', 1), ('b', 2)]),
            ('a-1 b-2',     [('a', -1), ('b', -2)]),
            (' a 1 b 2 ',   [('a', 1), ('b', 2)]),
            ('a1.0b2.0',    [('a', 1.0), ('b', 2.0)]),
            ('a-1.0b-2.0',  [('a', -1.0), ('b', -2.0)]),
            ('a1.0 b2.0',   [('a', 1.0), ('b', 2.0)]),
            (' a 1.0 b 2.0 ',   [('a', 1.0), ('b', 2.0)]),
            (' a -1.0 b -2.0 ',   [('a', -1.0), ('b', -2.0)]),
            ('a1,2b',       [('a', 1, 2), ('b',)]),
            ('a-1,-2b',     [('a', -1, -2), ('b',)]),
            ('a1 2b',       [('a', 1, 2), ('b',)]),
            ('a-1 -2b',     [('a', -1, -2), ('b',)]),
        ])

    def test_to_tuples_many_commands(self):
        self.assert_to_tuples([
            ('aaaaa',       [('a', ), ('a', ), ('a', ), ('a', ), ('a', ),]),
            ('abcde',       [('a', ), ('b', ), ('c', ), ('d', ), ('e', ),]),
            ('a a a a a',   [('a', ), ('a', ), ('a', ), ('a', ), ('a', ),]),
            ('a b c d e',   [('a', ), ('b', ), ('c', ), ('d', ), ('e', ),]),
            ('a1,2,3,4,5',  [('a', 1, 2, 3, 4, 5)]),
            ('a1 2 3 4 5',  [('a', 1, 2, 3, 4, 5)]),
        ])


    def test_to_tuples_bad(self):
        data = [
            ('0', "missing command at 0 in '0'"),
            (' 0', "missing command at 1 in ' 0'"),
            ('-', "missing command at 0 in '-'"),
            ('.', "missing command at 0 in '.'"),
            (',', "unexpected comma at 0 in ','"),
            (' ,', "unexpected comma at 1 in ' ,'"),
            ('M,', "unexpected comma at 1 in 'M,'"),
        ]
        for input, message in data:
            pathData = PathDataParser()
            self.assertRaisesWithMessage(ParseError, message,
                pathData.to_tuples, input)


class SvgLoopTracerTest(TestCase):

    def test_to_loops_bad_command(self):
        tracer = SvgLoopTracer()
        self.assertRaisesWithMessage(
            ParseError,
            'unsupported svg path command: X',
            tracer.to_loops, ('X',),
        )


    def test_parse_incomplete_path(self):
        tracer = SvgLoopTracer()
        self.assertRaisesWithMessage(
            ParseError,
            'loop needs 3 or more verts',
            tracer.to_loops, [('M', 1, 2), ('Z')],
        )
        self.assertRaisesWithMessage(
            ParseError,
            'loop needs 3 or more verts',
            tracer.to_loops, [('M', 1, 2), ('L', 3, 4), ('Z')]
        )
        self.assertRaisesWithMessage(
            ParseError,
            'loop needs 3 or more verts',
            tracer.to_loops, [('M', 1, 2), ('L', 3, 4), ('L', 1, 2), ('Z')],
        )

    def test_to_loops_duplicated_final_point_stripped(self):
        tracer = SvgLoopTracer()
        actual = tracer.to_loops(
            [('M', 1, 2), ('L', 3, 4), ('L', 5, 6), ('L', 1, 2), ('Z')])
        expected = [ [(1, -2), (3, -4), (5, -6)], ]
        self.assertEquals(actual, expected)


    def test_parse_not_z_terminated(self):
        self.fail()

    def test_parse_relative(self):
        self.fail()

    def test_parse_horizontal(self):
        self.fail()

    def test_parse_vertical(self):
        self.fail()

    def test_parse_repeated_implicit_commands(self):
        self.fail()


if __name__=='__main__':
    RunTests(PathDataTest, SvgLoopTracerTest)

