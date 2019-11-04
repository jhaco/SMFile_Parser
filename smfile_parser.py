from os import listdir, makedirs
from os.path import isfile, join, isdir
from shutil import copyfile
import re


class Step:
    def __init__(self):
        self.title = "empty"
        self.BPM = 0.0
        self.notes = []
        self.types = []
        self.offset = 0.0


def get_file_names(mypath):                                                                         #lists all files in specified directory
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]


def get_folder_names(mypath):
    return [f for f in listdir(mypath) if isdir(join(mypath, f))]

#=================================================================================================


def convert_note(line):
    x = line.replace("M", "0").replace("4", "1").replace("K", "0").replace("L", "0").replace("F", "0")
    return x


def format(src):
    split_by_period = src.lower().split(".")[:-1]
    name = ""
    for part in split_by_period:
        name += part
    formatted = re.sub("[^a-z0-9-_ ]", "", name)
    return re.sub(" ", "_", formatted)

#=================================================================================================

#BPM = beats/minute -> BPS = beats/second = BPM/60
#measure = 4 beats = 4 1/4th notes = 1
#1/256 >  1 measure = 256 1/256nd notes

def get_timing(measure, m_i, bpm, offset):                                                                  #gets time
    time            = []                                                                            #seconds per beat = 60/bpm
    measure_seconds = 4 * 60/bpm                                                                    #measure in seconds = 4 x seconds per beat
    note_256        = measure_seconds/256                                                           #time of notes in seconds
    sum             = measure_seconds * m_i                                                         #sum of measures before in seconds
    X_256           = 256/len(measure)                                                              #number of 1/256th notes between 1/Xth notes

    for i in range(len(measure)):
        if measure[i] == 1:
            time.append(i * note_256 * X_256 + sum - offset)

    return time

#=================================================================================================

def parse_sm(n):                                                                                    #parse .sm for BPM and measure + notes
    x       = Step()                                                                                #Step class x
    m_i     = 0                                                                                     #number of measure
    measure = []
    chars   = set('123456789')                                                                      #set of digits, not including 0
    flag    = False

    with open(n, 'r', encoding='ascii', errors='ignore') as f:                                      #ignores non-ASCII text (ex. Japanese)      
        for line in f:                                                                              #reads by line
           
            if line.startswith('#TITLE:'):                                                          #title
                x.title = line.lstrip('#TITLE').lstrip(':').rstrip(';\n')

            if line.startswith('#BPMS:'):                                                           #BPM
                if "," in line:
                    print('Multiple bpms detected')
                    raise Exception
                x.BPM   = float(line.lstrip('#BPMS:0.0').lstrip('0').lstrip('=').rstrip(';\n'))

            if line.startswith('#OFFSET:'):
                x.offset = float(line.lstrip('#OFFSET').lstrip(':').rstrip(';\n'))

            if line.startswith('#NOTES:'):                                                          #checks if the last hashtag property is read
                flag = True

            #=====================================================================================

            if flag:
                if line[0].isdigit():                                                                   #notes
                    check = False
                    if any((c in chars) for c in line):                                             #if line in measure has notes
                        check = True
                    if check:
                        measure.append(1)
                        x.types.append(convert_note(line.rstrip('\n')))
                    else:                                                                           #if line in measure has no notes
                        measure.append(0)

                if line.startswith(','):
                    time = get_timing(measure, m_i, x.BPM, x.offset)
                    x.notes.extend(time)                                                                #adds list of timestamps to x.notes
                    measure.clear()
                    m_i += 1

                if line.startswith(';'):                                                                #stops parsing after first difficulty set finished
                    time = get_timing(measure, m_i, x.BPM, x.offset)
                    x.notes.extend(time)                                                                #adds list of timestamps to x.notes
                    measure.clear()
                    break

    return x

#=================================================================================================

def output_file(new_file_name,x):                                                                               #outputs to .txt
    d = new_file_name + '.txt'

    with open(join("outputs/", d), "w") as f: # TODO: might change to store in different folders from oggs
        f.write("TITLE " + str(x.title) + "\n")
        f.write("BPM   " + str(x.BPM) + "\n")
        f.write("NOTES\n")
        for i in range(len(x.notes)):
            f.write(str(x.types[i]) + " " + str(x.notes[i]) + "\n")

    #print("Write successful: " + d)

#=================================================================================================


def main():
    # create input and output directories if they don't exist already
    makedirs("inputs", exist_ok=True)
    makedirs("outputs", exist_ok=True)
    # Parsing by searching through folders
    for folder_name in get_folder_names(join("inputs/")):
        folder_path = join("inputs/", folder_name)
        file_names = get_file_names(folder_path)
        ogg_name = None
        sm_name = None
        for file in file_names:
            # TODO: right now just checking first ogg and sm. want to check for exact name match first, then latest
            if file.endswith(".ogg"):
                ogg_name = file
            elif file.endswith(".sm"):
                sm_name = file
            if ogg_name is not None and sm_name is not None:  # end if found sm and ogg files
                break
        # check to see if found both ogg and sm files
        if ogg_name is None or sm_name is None:
            print("Folder %s is missing sm or ogg file!" % folder_name)
            continue
        # begin parsing the ogg file
        new_file_name = format(sm_name) # using sm file name to rename both the sm file and ogg files
        try:
            sm_data = parse_sm(join(folder_path, sm_name))
            output_file(new_file_name, sm_data) # write sm file data to text
        except Exception:
            print("Write failed: " + sm_name)
            continue # failed to parse sm file so skipping entire folder

        # if passed parsing sm file, rename ogg file too
        copyfile(join(folder_path, ogg_name), join("outputs/", new_file_name + ".ogg"))

    # parse by file names in inputs/ folder. requires ogg and sm files to be the same name
    file_names = get_file_names(join("inputs/"))
    sm_file_names = [file for file in file_names if file.endswith('.sm')]
    ogg_file_names = [file for file in file_names if file.endswith('.ogg')]
    # formats ogg names for comparision
    formatted_ogg_file_dict = dict(zip([format(ogg_name) for ogg_name in ogg_file_names], range(len(ogg_file_names))))
    for sm_name in sm_file_names:
        new_file_name = format(sm_name) # using sm file name to rename both the sm file and ogg files
        if new_file_name in formatted_ogg_file_dict: # check to see if ogg named same as sm file
            try:
                sm_data = parse_sm(join("inputs/", sm_name))
                output_file(new_file_name, sm_data)  # write sm file data to text
            except Exception:
                print("Write failed: " + sm_name)
                continue  # failed to parse sm file so skipping sm file

            # if passed parsing sm file, rename ogg file too
            copyfile(join("inputs/", ogg_file_names[formatted_ogg_file_dict[new_file_name]]), join("outputs/", new_file_name + ".ogg"))


if __name__ == '__main__':
    main()