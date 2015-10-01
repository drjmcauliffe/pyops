from pyops import EDF
import os


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


def test_load_edf_file():
    this_dir, this_filename = os.path.split(__file__)
    parent_dir = os.path.abspath(os.path.join(this_dir, os.pardir))
    test_file = os.path.join(parent_dir, "test/data/test.edf")

    edf = EDF(test_file)

    assert edf.experiment == 'SSMM "MassMemory"'

    for key in edf.GLOBAL_PROPERTIES:
        if key == 'Global_actions':
            assert edf.GLOBAL_PROPERTIES[key] == \
                'COPY_DV UPDATE_FTS_TABLE ALLOCATE_PID'
        else:
            assert edf.GLOBAL_PROPERTIES[key] is None

    assert len(edf.DATA_STORES.Table) == 28
    assert edf.DATA_STORES.Table.loc[2]['Memory size'] == '1 [Gbits]'

    assert len(edf.PIDS.Table) == 6
    assert edf.PIDS.Table.loc[3]['Data Store ID'] == '30'

    assert len(edf.FTS.Table) == 8
    assert edf.FTS.Table.loc[6]['Data Volume'] == '150'

    assert len(edf.FOVS.Table) == 2
    assert edf.FOVS.Table.loc[1]['FOV_type'] == 'RECTANGULAR'

    assert len(edf.MODES.Table) == 5
    assert edf.MODES.Table.loc[3]['Nominal_power'] == '0 [Watts]'

    assert len(edf.MODULES.Table) == 4
    assert edf.MODULES.Table.loc[2]['Module_level'] is None

    assert len(edf.MODULES.Module_states_Table) == 10
    assert edf.MODULES.Module_states_Table.loc[5]['MS_data_rate_parameter'] ==\
        'VIHI_DATA_RATE'

    assert len(edf.PARAMETERS.Table) == 11
    assert edf.PARAMETERS.Table.loc[7]['Eng_type'] == 'REAL'

    assert len(edf.PARAMETERS.Parameter_values_Table) == 6
    assert edf.PARAMETERS.Parameter_values_Table.loc[3]['Parameter_value'] == \
        'FTS_ENABLE_FLAG - 1 ENABLE'

    assert len(edf.ACTIONS.Table) == 3
    assert edf.ACTIONS.Table.loc[1]['Duration'] is None
