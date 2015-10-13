from sqlalchemy.orm import Session, load_only
from sqlalchemy import create_engine
from databaseCreator import Missions, MissionInstrumentID, PIDs, Actions
import os
import sys
import argparse


def parser():
    """This function generates input parser and explains the user how to
    use our program from the command line.

    Returns:
        dictionary: Input arguments
    """
    parser = argparse.ArgumentParser(
        description='Creates EPS files from the database.')
    parser.add_argument('-out', dest='out', nargs=1, required=True,
                        help='output directory for the files.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    return vars(parser.parse_args())


def mission_builder(mission_dir):
    if not os.path.exists(mission_dir):
        os.mkdir(mission_dir)
    if not os.path.exists(os.path.join(mission_dir, "EDF")):
        os.mkdir(os.path.join(mission_dir, "EDF"))
    if not os.path.exists(os.path.join(mission_dir, "ITL")):
        os.mkdir(os.path.join(mission_dir, "ITL"))
    if not os.path.exists(os.path.join(mission_dir, "EVF")):
        os.mkdir(os.path.join(mission_dir, "EVF"))
    if not os.path.exists(os.path.join(mission_dir, "ERF")):
        os.mkdir(os.path.join(mission_dir, "ERF"))


def create_edf(session, mission_dir, instrument):
    edf_dir = os.path.join(mission_dir, "EDF")
    edf = os.path.join(edf_dir, instrument.instrument_name + '.edf')

    with open(edf, 'w') as f:
        output_pids(f, session, instrument.mission_instrument_id)
        output_actions(f, session, instrument.mission_instrument_id)


def output_pids(f, session, instrument_id):

    f.write("\n# PID allocation\n\n")

    results = session.query(PIDs).filter_by(
        mission_instrument_id=instrument_id).all()
    for result in results:
        pid = result.pid_number
        if pid is not None:
            pid = " " + str(pid) + " "

        status = result.status
        if status is not None:
            status = " " + status + " "

        data_store_id = result.data_store_id
        if data_store_id is not None:
            data_store_id = " " + str(data_store_id) + " "

        f.write("\tPID:" + pid + status + data_store_id + "\n")


def output_actions(f, session, instrument_id):

    f.write("\n# Actions\n")

    results = session.query(Actions).filter_by(
        mission_instrument_id=instrument_id).all()

    # Lambda function to upper case the first character of a string
    up_case = lambda s: s[:1].upper() + s[1:] if s else None

    for result in results:
        f.write("\n")
        out = ["\t" + up_case(column.name) + ": " +
               str(getattr(result, column.name)) + "\n"
               for column in Actions.__table__.columns
               if getattr(result, column.name) is not None and
               column.name is not "mission_instrument_id"]

        for line in out:
            f.write(line)


if __name__ == '__main__':
    parser = parser()
    outputDir = parser['out'][0]

    # loading the engine
    engine = create_engine(
        'postgresql://planaspa:bepicolombo@localhost:5432/bepi')

    session = Session(engine)

    result = session.query(Missions).options(load_only("mission_name")).all()
    for mission in result:
        mission_dir = os.path.join(outputDir, mission.mission_name)
        mission_builder(mission_dir)

        # Finding out the instruments related to that mission
        instruments = session.query(MissionInstrumentID).filter_by(
            mission=mission.mission_name).all()
        for instrument in instruments:
            create_edf(session, mission_dir, instrument)
