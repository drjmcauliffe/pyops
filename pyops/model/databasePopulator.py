from pyops.edf import EDF
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from databaseCreator import Missions, MissionInstrumentID, Instruments, PIDs
from databaseCreator import FTSs, Actions, ActionObsIDS, ActionConstraints
from sqlalchemy.orm import load_only


def fill_edf(edf, instrument):
    result = session.query(MissionInstrumentID).options(
        load_only("mission_instrument_id")).filter_by(
        instrument_name=instrument, mission="BepiColombo").first()
    # Loading pids from EDF Dataframe
    df = edf.PIDS.Table
    for index, row in df.iterrows():
        session.add(PIDs(
            mission_instrument_id=result.mission_instrument_id,
            pid_number=row['PID number'],
            status=row['Status'], data_store_id=row["Data Store ID"]))
        session.commit()

    # Loading Actions from EDF Dataframe
    df = edf.ACTIONS.Table
    for index, row in df.iterrows():
        session.add(Actions(
            mission_instrument_id=result.mission_instrument_id,
            action=row["Action"], action_alias=row["Action_alias"],
            action_level=row["Action_level"], action_type=row["Action_type"],
            action_subsystem=row["Action_subsystem"],
            computed_parameters=row["Computed_parameters"],
            duration=row["Duration"], minimum_duration=row["Minimum_duration"],
            compression=row["Compression"], separation=row["Separation"],
            action_dataflow=row["Action_dataflow"],
            action_pid=row["Action_PID"], power_increase=row["Power_increase"],
            data_rate_increase=row["Data_rate_increase"],
            data_volume=row["Data_volume"],
            write_to_Z_record=row["Write_to_Z_record"],
            action_power_check=["Action_power_check"],
            action_data_rate_check=row["Action_data_rate_check"],
            update_at_start=row["Update_at_start"],
            update_when_ready=row["Update_when_ready"],
            run_type=row["Run_type"], run_start_time=row["Run_start_time"]))

        # Inserting observation ids
        if row["Obs_ID"] is not None:
            for ob_id in row["Obs_ID"].split():
                session.add(ActionObsIDS(
                    mission_instrument_id=result.mission_instrument_id,
                    action=row["Action"], observation_id=ob_id))

        # Inserting action constraints
        if row["Action_constraints"] is not None:
            for constraint in row["Action_constraints"].split():
                session.add(ActionConstraints(
                    mission_instrument_id=result.mission_instrument_id,
                    action=row["Action"], constraint_name=constraint))
        session.commit()

        # Missing: "Action_parameters", "Internal_variables","Power_profile",
        # "Data_rate_profile", "Run_actions"


# loading the engine
engine = create_engine('postgresql://planaspa:bepicolombo@localhost:5432/bepi')


session = Session(engine)


instruments = ["serena", "mertis", "more", "simbiosys", "isa", "bela",
               "mermag", "phebus", "antenna", "mixs_sixs", "mgns"]


session.add(Missions(mission_name="BepiColombo", other_information="Test"))
session.commit()


for instrument in instruments:
    session.add(MissionInstrumentID(
        mission="BepiColombo", instrument_name=instrument))
    session.commit()

for instrument in instruments:
    result = session.query(MissionInstrumentID).options(
        load_only("mission_instrument_id")).filter_by(
        instrument_name=instrument, mission="BepiColombo").first()
    session.add(Instruments(
        mission_instrument_id=result.mission_instrument_id,
        full_name=instrument + ' - Full Name'))
    session.commit()

edf = EDF('/lhome/planaspa/Documents/Bepi/BepiData/EDF/ssmm.edf')

# Loading ftss from EDF Dataframe
# With the new fix, ssmm.edf is not related with any instrument so
# mission_instrument_id shoule be changed!!!!!!!!
df = edf.FTS.Table
for index, row in df.iterrows():
    session.add(FTSs(
        mission_instrument_id=result.mission_instrument_id,
        data_store_id=row['Data Store ID'],
        status=row['Status'],
        data_volume=row["Data Volume"]))
    session.commit()

for instrument in instruments:
    edf = EDF('/lhome/planaspa/Documents/Bepi/BepiData/EDF/'
              + instrument + '.edf')
    fill_edf(edf, instrument)
