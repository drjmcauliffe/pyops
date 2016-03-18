from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, create_engine
from sqlalchemy import event
from sqlalchemy.schema import DDL

Base = declarative_base()


class Missions(Base):
    __tablename__ = 'missions'
    # Here we define columns for the table mission
    # Notice that each column is also a normal Python instance attribute.
    mission_name = Column(String(50), primary_key=True)
    other_information = Column(String(250))


class EVFs(Base):
    __tablename__ = 'evfs'
    mission = Column(String(50), ForeignKey('missions.mission_name'),
                     primary_key=True)
    # This time data type could be change in the future
    time = Column(String(50), primary_key=True)
    event = Column(String(50), primary_key=True)
    experiment = Column(String(50), nullable=False)
    item = Column(String(50))
    count = Column(Integer)


class ERFs(Base):
    __tablename__ = 'erfs'
    mission = Column(String(50), ForeignKey('missions.mission_name'),
                     primary_key=True)
    event_name = Column(String(50))
    event_id = Column(Integer, primary_key=True)
    start_string = Column(String(50))
    stop_string = Column(String(50))


class ERFExpressions(Base):
    __tablename__ = 'erf_expressions'
    mission = Column(String(50), ForeignKey('missions.mission_name'),
                     primary_key=True)
    event_id = Column(Integer, primary_key=True)
    event = Column(String(50), primary_key=True)
    boolean_expression = Column(String(50))
    value = Column(String(50))


class MissionInstrumentID(Base):
    __tablename__ = 'mission_instrument_id'
    mission_instrument_id = Column(Integer, primary_key=True)
    mission = Column(String(50), ForeignKey('missions.mission_name'))
    instrument_name = Column(String(50), nullable=False)
    # explicit/composite unique constraint
    UniqueConstraint('mission', 'instrument_name')


class Instruments(Base):
    __tablename__ = 'instruments'
    mission_instrument_id = Column(
        Integer, ForeignKey('mission_instrument_id.mission_instrument_id'),
        primary_key=True)
    full_name = Column(String(50))
    other_information = Column(String(50))


class DataBuses(Base):
    __tablename__ = 'data_buses'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    data_bus = Column(String(50), primary_key=True)
    data_bus_rate_limit = Column(String(50))
    data_bus_warning = Column(String(50))


class DataStores(Base):
    __tablename__ = 'data_stores'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    label = Column(String(50), primary_key=True)
    memory_size = Column(String(50))
    packet_size = Column(String(50))
    priority = Column(Integer)
    identifier = Column(Integer)


class Areas(Base):
    __tablename__ = 'areas'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    area = Column(String(50), primary_key=True)
    area_orientation = Column(String(50))
    area_lighting_angle = Column(String(50))
    area_lighting_duration = Column(String(50))


class ITLIDs(Base):
    __tablename__ = 'itl_ids'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'))
    # This is converted into a serial data type in postgre
    itl_id = Column(Integer, primary_key=True)
    # This time data type could be change in the future
    time = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    experiment = Column(String(50))
    mode = Column(String(50))
    # explicit/composite unique constraint
    UniqueConstraint('mission_instrument_id', 'time', 'action')


class ITLParameters(Base):
    __tablename__ = 'itl_parameters'
    itl_id = Column(Integer, ForeignKey('itl_ids.itl_id'), primary_key=True)
    parameter_name = Column(String(50), primary_key=True)
    value = Column(String(50))
    unit = Column(String(50))


class FTSs(Base):
    __tablename__ = 'ftss'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    data_store_id = Column(Integer, primary_key=True)
    status = Column(String(50))
    data_volume = Column(String(50))


class Constraints(Base):
    __tablename__ = 'constraints'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    constraint_name = Column(String(50), primary_key=True)
    constraint_type = Column(String(50))
    severity = Column(Integer)
    constraint_group = Column(String(50))
    condition = Column(String(50))
    resource_constraint = Column(String(50))
    resource_mass_memory = Column(String(50))
    parameter_constraint = Column(String(50))
    condition_experiment = Column(String(50))
    expression = Column(String(50))


class PIDs(Base):
    __tablename__ = 'pids'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    pid_number = Column(Integer, primary_key=True)
    status = Column(String(50))
    data_store_id = Column(Integer)

# Trigger
pids_function = DDL(
    """
    CREATE OR REPLACE FUNCTION pids_data_store_id_check()
    RETURNS trigger AS $pids_data_store_id_check$
       DECLARE
           curs refcursor;
           dsid RECORD;
       BEGIN
          IF NEW.data_store_id IS NOT NULL THEN
            OPEN curs FOR SELECT data_store_id FROM ftss
            WHERE data_store_id = NEW.data_store_id ;
            FETCH curs INTO dsid;
            CLOSE curs;

            IF dsid is NULL THEN
               RAISE EXCEPTION 'data_store_id is not defined in ftss table ';
            END IF;
          END IF;
          RETURN NEW;
       END;
    $pids_data_store_id_check$ LANGUAGE plpgsql;
    """)
# event.listen(PIDs.__table__, 'after_create', pids_function)

pids_trigger = DDL(
    """
    CREATE TRIGGER pids_data_store_id_check
    BEFORE INSERT OR UPDATE ON pids
    FOR EACH ROW EXECUTE PROCEDURE pids_data_store_id_check();
    """)
# event.listen(PIDs.__table__, 'after_create', pids_trigger)


class Parameters(Base):
    __tablename__ = 'parameters'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    parameter = Column(String(50), primary_key=True)
    parameter_alias = Column(String(50))
    state_parameter = Column(String(50))
    parameter_action = Column(String(50))
    raw_type = Column(String(50))
    eng_type = Column(String(50))
    default_value = Column(String(50))
    unit = Column(String(50))
    raw_limits = Column(String(50))
    eng_limits = Column(String(50))
    resource = Column(String(50))
    value_alias = Column(String(50))
    nr_of_parameter_values = Column(Integer)


class FOVs(Base):
    __tablename__ = 'fovs'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    fov = Column(String(50), primary_key=True)
    fov_lookat = Column(String(50))
    fov_type = Column(String(50))
    fov_geometric_angles = Column(String(50))
    fov_geometric_pixels = Column(String(50))
    fov_sub_view = Column(String(50))
    fov_straylight_angles = Column(String(50))
    fov_straylight_duration = Column(String(50))
    fov_image_timing = Column(String(50))
    fov_pitch = Column(String(50))
    fov_yaw = Column(String(50))


class Actions(Base):
    __tablename__ = 'actions'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    action = Column(String(500), primary_key=True)
    action_alias = Column(String(500))
    action_level = Column(String(500))
    action_type = Column(String(500))
    action_subsystem = Column(String(500))
    computed_parameters = Column(String(500))
    duration = Column(String(500))
    minimum_duration = Column(String(500))
    compression = Column(Integer)
    separation = Column(String(500))
    action_dataflow = Column(String(500))
    action_pid = Column(Integer)
    power_increase = Column(String(500))
    data_rate_increase = Column(String(500))
    data_volume = Column(String(500))
    write_to_Z_record = Column(String(500))
    action_power_check = Column(String(500))
    action_data_rate_check = Column(String(500))
    update_at_start = Column(String())
    update_when_ready = Column(String())
    run_type = Column(String(500))
    run_start_time = Column(String(500))
    ForeignKeyConstraint(['mission_instrument_id', 'action_pid'],
                         ['pids.mission_instrument_id', 'pids.pid_number'])

# Trigger
actions_function = DDL(
    """
    CREATE OR REPLACE FUNCTION actions_action_pid_check()
    RETURNS trigger AS $actions_action_pid_check$
       DECLARE
           curs refcursor;
           pid RECORD;
       BEGIN
          IF NEW.action_pid IS NOT NULL THEN
            OPEN curs FOR SELECT pid_number FROM pids
            WHERE pid_number = NEW.action_pid ;
            FETCH curs INTO pid;
            CLOSE curs;

            IF pid is NULL THEN
               RAISE EXCEPTION 'action_pid is not defined in pids table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $actions_action_pid_check$ LANGUAGE plpgsql;
    """)
event.listen(Actions.__table__, 'after_create', actions_function)

actions_trigger = DDL(
    """
    CREATE TRIGGER actions_action_pid_check
    BEFORE INSERT OR UPDATE ON actions
    FOR EACH ROW EXECUTE PROCEDURE actions_action_pid_check();
    """)
event.listen(Actions.__table__, 'after_create', actions_trigger)


class Parametervalues(Base):
    __tablename__ = 'parameter_values'
    mission_instrument_id = Column(Integer, nullable=False)
    parameter = Column(String(50), nullable=False)
    parameter_value = Column(String(50), nullable=False)
    parameter_uas = Column(String(50))
    parameter_uwr = Column(String(50))
    parameter_value_composite_id = Column(Integer, primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'parameter'],
                         ['parameters.mission_instrument_id',
                          'parameters.parameter'])
    UniqueConstraint('mission_instrument_id', 'parameter', 'parameter_value')


class Modes(Base):
    __tablename__ = 'modes'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    mode = Column(String(50), primary_key=True)
    mode_class = Column(String(50))
    internal_clock = Column(String(50))
    norminal_power = Column(String(50))
    power_parameter = Column(String(50))
    nominal_data_rate = Column(String(50))
    data_rate_parameter = Column(String(50))
    mode_aux_data_rate = Column(String(50))
    equivalent_power = Column(String(50))
    equivalent_data_rate = Column(String(50))

# Trigger
modes_function1 = DDL(
    """
    CREATE OR REPLACE FUNCTION modes_power_parameter_check()
    RETURNS trigger AS $modes_power_parameter_check$
       DECLARE
           curs refcursor;
           parameter RECORD;
       BEGIN
          IF NEW.power_parameter IS NOT NULL THEN
            OPEN curs FOR SELECT parameter FROM parameters
            WHERE parameter = NEW.power_parameter ;
            FETCH curs INTO parameter;
            CLOSE curs;

            IF parameter is NULL THEN
               RAISE EXCEPTION 'Parameter is not defined in parameters table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $modes_power_parameter_check$ LANGUAGE plpgsql;
    """)
event.listen(Modes.__table__, 'after_create', modes_function1)

modes_trigger1 = DDL(
    """
    CREATE TRIGGER modes_power_parameter_check
    BEFORE INSERT OR UPDATE ON modes
    FOR EACH ROW EXECUTE PROCEDURE modes_power_parameter_check();
    """)
event.listen(Modes.__table__, 'after_create', modes_trigger1)

# Trigger
modes_function2 = DDL(
    """
    CREATE OR REPLACE FUNCTION modes_data_rate_parameter_check()
    RETURNS trigger AS $modes_data_rate_parameter_check$
       DECLARE
           curs refcursor;
           parameter RECORD;
       BEGIN
          IF NEW.data_rate_parameter IS NOT NULL THEN
            OPEN curs FOR SELECT parameter FROM parameters
            WHERE parameter = NEW.data_rate_parameter ;
            FETCH curs INTO parameter;
            CLOSE curs;

            IF parameter is NULL THEN
               RAISE EXCEPTION 'Parameter is not defined in parameters table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $modes_data_rate_parameter_check$ LANGUAGE plpgsql;
    """)
event.listen(Modes.__table__, 'after_create', modes_function2)

modes_trigger2 = DDL(
    """
    CREATE TRIGGER modes_data_rate_parameter_check
    BEFORE INSERT OR UPDATE ON modes
    FOR EACH ROW EXECUTE PROCEDURE modes_data_rate_parameter_check();
    """)
event.listen(Modes.__table__, 'after_create', modes_trigger2)


class FOVAlgorithm(Base):
    __tablename__ = 'fov_algorithms'
    mission_instrument_id = Column(Integer, primary_key=True)
    fov = Column(String(50), primary_key=True)
    algorithm_id = Column(String(50))
    argument = Column(String(50))
    ForeignKeyConstraint(['mission_instrument_id', 'fov'],
                         ['fovs.mission_instrument_id', 'fovs.fov'])


class FOVActives(Base):
    __tablename__ = 'fov_actives'
    mission_instrument_id = Column(Integer, primary_key=True)
    fov = Column(String(50), primary_key=True)
    mode_ms = Column(String(50))
    label = Column(String(50))
    ForeignKeyConstraint(['mission_instrument_id', 'fov'],
                         ['fovs.mission_instrument_id', 'fovs.fov'])


class FOVImaging(Base):
    __tablename__ = 'fov_imaging'
    mission_instrument_id = Column(Integer, primary_key=True)
    fov = Column(String(50), primary_key=True)
    ms_action = Column(String(50))
    label = Column(String(50))
    ForeignKeyConstraint(['mission_instrument_id', 'fov'],
                         ['fovs.mission_instrument_id', 'fovs.fov'])


class ParameterRun(Base):
    __tablename__ = 'parameter_run'
    parameter_value_composite_id = Column(
        Integer, ForeignKey('parameter_values.parameter_value_composite_id'),
        primary_key=True)
    parameter = Column(String(50), primary_key=True)
    action = Column(String(50), primary_key=True)

# Trigger
parameter_run_function1 = DDL(
    """
    CREATE OR REPLACE FUNCTION parameter_run_parameter_check()
    RETURNS trigger AS $parameter_run_parameter_check$
       DECLARE
           curs refcursor;
           parameter RECORD;
       BEGIN
          IF NEW.parameter IS NOT NULL THEN
            OPEN curs FOR SELECT parameter FROM parameters
            WHERE parameter = NEW.parameter ;
            FETCH curs INTO parameter;
            CLOSE curs;

            IF parameter is NULL THEN
               RAISE EXCEPTION 'Parameter is not defined in parameters table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $parameter_run_parameter_check$ LANGUAGE plpgsql;
    """)
event.listen(ParameterRun.__table__, 'after_create', parameter_run_function1)

parameter_run_trigger1 = DDL(
    """
    CREATE TRIGGER parameter_run_parameter_check
    BEFORE INSERT OR UPDATE ON parameter_run
    FOR EACH ROW EXECUTE PROCEDURE parameter_run_parameter_check();
    """)
event.listen(ParameterRun.__table__, 'after_create', parameter_run_trigger1)

parameter_run_function2 = DDL(
    """
    CREATE OR REPLACE FUNCTION parameter_run_action_check()
    RETURNS trigger AS $parameter_run_action_check$
       DECLARE
           curs refcursor;
           action RECORD;
       BEGIN
          IF NEW.action IS NOT NULL THEN
            OPEN curs FOR SELECT action FROM actions
            WHERE action = NEW.action ;
            FETCH curs INTO action;
            CLOSE curs;

            IF action is NULL THEN
               RAISE EXCEPTION 'Action is not defined in actions table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $parameter_run_action_check$ LANGUAGE plpgsql;
    """)
event.listen(ParameterRun.__table__, 'after_create', parameter_run_function2)

parameter_run_trigger2 = DDL(
    """
    CREATE TRIGGER parameter_run_action_check
    BEFORE INSERT OR UPDATE ON parameter_run
    FOR EACH ROW EXECUTE PROCEDURE parameter_run_action_check();
    """)
event.listen(ParameterRun.__table__, 'after_create', parameter_run_trigger2)


class Modules(Base):
    __tablename__ = 'modules'
    mission_instrument_id = Column(
        Integer, ForeignKey('instruments.mission_instrument_id'),
        primary_key=True)
    module = Column(String(50), primary_key=True)
    module_level = Column(String(50))
    module_dataflow = Column(String(50))
    module_pid = Column(Integer)
    module_aux_pid = Column(Integer)
    nr_of_module_states = Column(Integer)
    ForeignKeyConstraint(['mission_instrument_id', 'module_pid'],
                         ['pids.mission_instrument_id', 'pids.pid_number'])
    ForeignKeyConstraint(['mission_instrument_id', 'module_aux_pid'],
                         ['pids.mission_instrument_id', 'pids.pid_number'])


class PIDEnableFlags(Base):
    __tablename__ = 'pid_enable_flags'
    mission_instrument_id = Column(Integer, primary_key=True)
    mode = Column(String(50), primary_key=True)
    enable = Column(String(50))
    pid_number = Column(Integer, primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'mode'],
                         ['modes.mission_instrument_id'], 'modes.mode')
    ForeignKeyConstraint(['mission_instrument_id', 'pid_number'],
                         ['pids.mission_instrument_id'], 'pids.pid_number')


class ActionPowerProfiles(Base):
    __tablename__ = 'action_power_profiles'
    mission_instrument_id = Column(Integer, primary_key=True)
    action = Column(String(50), primary_key=True)
    # This time should use another data type in the future
    relative_time = Column(String(50), primary_key=True)
    power = Column(String(50))
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])


class ActionDataRateProfiles(Base):
    __tablename__ = 'action_data_rate_profiles'
    mission_instrument_id = Column(Integer, primary_key=True)
    action = Column(String(50), primary_key=True)
    # This time should use another data type in the future
    relative_time = Column(String(50), primary_key=True)
    data_rate = Column(String(50))
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])


class ActionObsIDS(Base):
    __tablename__ = 'action_obs_ids'
    mission_instrument_id = Column(Integer, primary_key=True)
    action = Column(String(50), primary_key=True)
    observation_id = Column(Integer, primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])


class ActionConstraints(Base):
    __tablename__ = 'action_constraints'
    mission_instrument_id = Column(Integer, primary_key=True)
    action = Column(String(50), primary_key=True)
    constraint_name = Column(String(50), primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])
    ForeignKeyConstraint(['mission_instrument_id', 'Constraint'],
                         ['constraints.mission_instrument_id',
                          'constraints.constraint_name '])


class ActionParameters(Base):
    __tablename__ = 'action_parameters'
    mission_instrument_id = Column(Integer, primary_key=True)
    action = Column(String(50), primary_key=True)
    parameter = Column(String(50), primary_key=True)
    value = Column(String(50))
    unit = Column(String(50))
    fixed = Column(String(50))
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])
    ForeignKeyConstraint(['mission_instrument_id', 'parameter'],
                         ['parameters.mission_instrument_id',
                          'parameters.parameter'])


class ActionInternalVariables(Base):
    __tablename__ = 'action_internal_variables'
    mission_instrument_id = Column(Integer, primary_key=True)
    action = Column(String(50), primary_key=True)
    variable_name = Column(String(50), primary_key=True)
    variable_value = Column(String(50))
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])


class RunActions(Base):
    __tablename__ = 'run_actions'
    mission_instrument_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    # This time should use another data type instead of string in the future...
    delta_time = Column(String(50))
    run_action = Column(String(50), nullable=False)
    run_action_comoposed_id = Column(Integer, primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])
    UniqueConstraint('mission_instrument_id', 'action', 'run_action')


class ModuleStateModes(Base):
    __tablename__ = 'module_state_modes'
    mission_instrument_id = Column(Integer, primary_key=True)
    mode = Column(String(50), primary_key=True)
    module_states = Column(String(50), primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'mode'],
                         ['modes.mission_instrument_id', 'modes.mode'])


class ModeTransitions(Base):
    __tablename__ = 'mode_transitions'
    mission_instrument_id = Column(Integer, primary_key=True)
    mode = Column(String(50), primary_key=True)
    transition = Column(String(50), primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'mode'],
                         ['modes.mission_instrument_id', 'modes.mode'])
    ForeignKeyConstraint(['mission_instrument_id', 'transition'],
                         ['actions.mission_instrument_id', 'actions.action'])


class ModeActions(Base):
    __tablename__ = 'mode_actions'
    mission_instrument_id = Column(Integer, primary_key=True)
    mode = Column(String(50), primary_key=True)
    action = Column(String(50), primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'mode'],
                         ['modes.mission_instrument_id', 'modes.mode'])
    ForeignKeyConstraint(['mission_instrument_id', 'action'],
                         ['actions.mission_instrument_id', 'actions.action'])


class ModeConstraints(Base):
    __tablename__ = 'mode_constraints'
    mission_instrument_id = Column(Integer, primary_key=True)
    mode = Column(String(50), primary_key=True)
    constraint_name = Column(String(50), primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'mode'],
                         ['modes.mission_instrument_id', 'modes.mode'])
    ForeignKeyConstraint(['mission_instrument_id', 'constraint'],
                         ['actions.mission_instrument_id',
                          'constraints.Constraint'])


class SubModules(Base):
    __tablename__ = 'sub_modules'
    mission_instrument_id = Column(Integer, primary_key=True)
    module = Column(String(50), primary_key=True)
    submodule = Column(String(50), primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'module'],
                         ['modules.mission_instrument_id', 'modules.module'])
    ForeignKeyConstraint(['mission_instrument_id', 'submodule'],
                         ['modules.mission_instrument_id', 'modules.module'])


class ModuleStateIDS(Base):
    __tablename__ = 'module_state_ids'
    mission_instrument_id = Column(Integer, nullable=False)
    module = Column(String(50), nullable=False)
    module_state = Column(String(50), nullable=False)
    module_state_id = Column(Integer, primary_key=True)
    ForeignKeyConstraint(['mission_instrument_id', 'module'],
                         ['modules.mission_instrument_id', 'modules.module'])
    UniqueConstraint('mission_instrument_id', 'module', 'module_state')


class RunActionParameters(Base):
    __tablename__ = 'run_action_parameters'
    run_action_comoposed_id = Column(
        Integer, ForeignKey('run_actions.run_action_comoposed_id'),
        primary_key=True)
    parameter = Column(String(50), primary_key=True)
    value = Column(String(50))
    unit = Column(String(50))


class ModuleStates(Base):
    __tablename__ = 'module_states'
    module_state_id = Column(
        Integer, ForeignKey('module_state_ids.module_state_id'),
        primary_key=True)
    ms_pid = Column(Integer)
    ms_aux_pid = Column(Integer)
    ms_power = Column(String(50))
    ms_power_parameter = Column(String(50))
    ms_data_rate = Column(String(50))
    ms_data_rate_parameter = Column(String(50))
    ms_pitch = Column(String(50))
    ms_yaw = Column(String(50))

# Trigger
module_states_function1 = DDL(
    """
    CREATE OR REPLACE FUNCTION module_states_ms_pid_check()
    RETURNS trigger AS $module_states_ms_pid_check$
       DECLARE
           curs refcursor;
           pid RECORD;
       BEGIN
          IF NEW.ms_pid IS NOT NULL THEN
            OPEN curs FOR SELECT pid_number FROM pids
            WHERE pid_number = NEW.ms_pid ;
            FETCH curs INTO pid;
            CLOSE curs;

            IF pid is NULL THEN
               RAISE EXCEPTION 'ms_pid is not defined in pids table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $module_states_ms_pid_check$ LANGUAGE plpgsql;
    """)
event.listen(ModuleStates.__table__, 'after_create', module_states_function1)

module_states_trigger1 = DDL(
    """
    CREATE TRIGGER module_states_ms_pid_check
    BEFORE INSERT OR UPDATE ON module_states
    FOR EACH ROW EXECUTE PROCEDURE module_states_ms_pid_check();
    """)
event.listen(ModuleStates.__table__, 'after_create', module_states_trigger1)

# Trigger
module_states_function2 = DDL(
    """
    CREATE OR REPLACE FUNCTION module_states_ms_aux_pid_check()
    RETURNS trigger AS $module_states_ms_aux_pid_check$
       DECLARE
           curs refcursor;
           pid RECORD;
       BEGIN
          IF NEW.ms_aux_pid IS NOT NULL THEN
            OPEN curs FOR SELECT pid_number FROM pids
            WHERE pid_number = NEW.ms_aux_pid ;
            FETCH curs INTO pid;
            CLOSE curs;

            IF pid is NULL THEN
               RAISE EXCEPTION 'ms_pid is not defined in pids table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $module_states_ms_aux_pid_check$ LANGUAGE plpgsql;
    """)
event.listen(ModuleStates.__table__, 'after_create', module_states_function2)

module_states_trigger2 = DDL(
    """
    CREATE TRIGGER module_states_ms_aux_pid_check
    BEFORE INSERT OR UPDATE ON module_states
    FOR EACH ROW EXECUTE PROCEDURE module_states_ms_aux_pid_check();
    """)
event.listen(ModuleStates.__table__, 'after_create', module_states_trigger2)


class RepeatActionModuleStates(Base):
    __tablename__ = 'repeat_action_module_states'
    module_state_id = Column(
        Integer, ForeignKey('module_state_ids.module_state_id'),
        primary_key=True)
    repeat_action = Column(String(50), primary_key=True)
    parameter = Column(String(50), primary_key=True)


class MSConstraints(Base):
    __tablename__ = 'ms_constraints'
    module_state_id = Column(
        Integer, ForeignKey('module_states.module_state_id'),
        primary_key=True)
    constraint_name = Column(String(50), primary_key=True)

# Trigger
ms_constraints_function = DDL(
    """
    CREATE OR REPLACE FUNCTION ms_constraints_constraint_check()
    RETURNS trigger AS $ms_constraints_constraint_check$
       DECLARE
           curs refcursor;
           constr RECORD;
       BEGIN
          IF NEW.constraint_name IS NOT NULL THEN
            OPEN curs FOR SELECT constraint_name FROM constraints
            WHERE constraint_name = NEW.constraint_name ;
            FETCH curs INTO constr;
            CLOSE curs;

            IF constr is NULL THEN
               RAISE EXCEPTION 'Constraint is not defined in constraints table ';
            END IF;
          END IF;
        RETURN NEW;
       END;
    $ms_constraints_constraint_check$ LANGUAGE plpgsql;
    """)
event.listen(MSConstraints.__table__, 'after_create', ms_constraints_function)

ms_constraints_trigger = DDL(
    """
    CREATE TRIGGER ms_constraints_constraint_check
    BEFORE INSERT OR UPDATE ON ms_constraints
    FOR EACH ROW EXECUTE PROCEDURE ms_constraints_constraint_check();
    """)
event.listen(MSConstraints.__table__, 'after_create', ms_constraints_trigger)

# Create an engine that stores data in the local directory's
# bepi.db file.
# dialect+driver://username:password@host:port/database
engine = create_engine('postgresql://planaspa:bepicolombo@localhost:5432/bepi')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
