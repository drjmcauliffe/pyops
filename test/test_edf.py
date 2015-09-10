from epys import EDF


def test_add_none_to_empty_fields():
    edf_test = EDF()

    test_dict = {'a': ['a'], 'b': [1, 3], 'c': [1]}
    output = edf_test._add_none_to_empty_fields(test_dict)
    assert output == {'a': ['a', None], 'b': [1, 3], 'c': [1, None]}

    test_dict = {'a': [], 'b': [], 'c': []}
    output = edf_test._add_none_to_empty_fields(test_dict)
    assert output == {'a': [], 'b': [], 'c': []}

    test_dict = {'a': [1, 2], 'b': [1, 3], 'c': [1, 'a']}
    output = edf_test._add_none_to_empty_fields(test_dict)
    assert output == {'a': [1, 2], 'b': [1, 3], 'c': [1, 'a']}


def test_how_many_brackets_following():
    edf_test = EDF()

    test_line = ['aa', 'bbadsf', '[asdf]', '[sdfs2]', 'asdfas', '[asfsddf]']
    output = edf_test._how_many_brackets_following(test_line)
    assert output == 0

    test_line = ['aa', 'bbadsf', '[asdf]', '[sdfs2]', 'asdfas', '[asfsddf]']
    output = edf_test._how_many_brackets_following(test_line[2:])
    assert output == 2

    test_line = ['aa', 'bbadsf', '[asdf]', '[sdfs2]', 'asdfas', '[asfsddf]']
    output = edf_test._how_many_brackets_following(test_line[5:])
    assert output == 1


def test_read_variables():
    edf_test = EDF()

    test_line = "Experiment: MERTIS 'MERTIS'".split()
    edf_test._read_variables(test_line)
    assert edf_test.experiment == "MERTIS 'MERTIS'"

    test_line = "Include: mertis.edf".split()
    edf_test._read_variables(test_line)
    output = False
    for files in edf_test.include_files:
        if 'mertis.edf' in files:
            output = True
    assert output is True

    test_line = "Include_file: bela.edf".split()
    edf_test._read_variables(test_line)
    output = False
    output2 = False
    for files in edf_test.include_files:
        if 'bela.edf' in files:
            output = True
        if 'mertis.edf' in files:
            output2 = True
    assert output is True and output2 is True

    test_line = "Random_variable: test".split()
    edf_test._read_variables(test_line)
    output = False
    for variable in edf_test.variables:
        if "Random_variable" in variable:
            if edf_test.variables["Random_variable"] == 'test':
                output = True
    assert output is True


def test_concatenate_lines():
    edf_test = EDF()

    test_content = ['#abc\\\n', 'abcd\\ #Comment\n', 'b\\\n', 'aa\n',
                    'bcd\\\n', 'aa\\\\\n', 'c\n']
    output = edf_test._concatenate_lines(test_content)
    assert output == ['#abc\\', 'abcd b aa', 'bcd aa\\\\', 'c']
