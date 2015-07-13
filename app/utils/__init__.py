from os import environ, path

timelog_path = path.join(environ.get('HOME'), '.gtimelog', 'timelog.txt')

if not path.exists(timelog_path):
    # Use the dummy data in working directory
    timelog_path = path.join(path.realpath(path.pardir), 'working', 'timelog.txt')
