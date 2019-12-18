import os
from os.path import isfile, join, isdir, dirname, realpath
from shutil import copyfile
import re
import time

def make_folder(dir):                                                       #generate input/output folders. Place song folders in input.
    if not isdir(join(dir, "input")):
        os.makedirs(join(dir, "input"))
    if not isdir(join(dir, "output")):
        os.makedirs(join(dir, "output"))

def get_file_name(path):                                                    #gets file name
    return [f for f in os.listdir(path) if isfile(join(path, f))]

def get_folder_name(path):                                                  #gets folder name
    return [f for f in os.listdir(path) if isdir(join(path, f))]               

def format_file_name(f):                                                    #formats file name to ASCII
    name = "".join(f.split('.')[:-1]).lower()                               #lowercase; splits by period; keeps extension
    formatted = re.sub('[^a-z0-9-_ ]', '', name)                            #ignores special characters, except - and _
    return re.sub(' ', '_', formatted)                                      #replaces whitespace with _

def output_file(file_name, x):                                              #outputs results from Step() to file text
    ofile = file_name + '.txt'

    with open(join(output_dir, ofile), 'w') as f:
        f.write('TITLE ' + str(x.title) + '\n')
        f.write('BPM   ' + str(x.BPM) + '\n')
        f.write('NOTES\n')
        for i in range(len(x.notes)):
            f.write(str(x.types[i]) + " " + str(x.notes[i]) + '\n')

#===================================================================================================

class Step:                                                                 #Step
    def __init__(self):                                                     #constructor/instanced Step variable
        self.title  = 'empty'
        self.BPM    = 0.0
        self.notes  = []
        self.types  = []
        self.offset = 0.0
        #self.difficulty = "easy"

#===================================================================================================

def convert_note(line):                                                      
    convert = re.sub('[MKLF]', '0', line)                                   #removes extra notes: M, K, L, F
    return re.sub('4', '1', convert)                                        #removes 4 note

#===================================================================================================

# BPM       = beats/minute -> BPS = beats/second = BPM/60
# measure   = 4 beats = 4 * 1/4th notes     = 1 note
# 1/256    -> 256 * 1/256th notes           = 1 measure

def calculate_timing(measure, measure_index, bpm, offset):                  #calculate time in seconds for each line
    time            = []
    measure_seconds = 4 * 60/bpm                                            #length of measure in seconds   
    note_256        = measure_seconds/256                                   #length of each 1/256th note in the measure in seconds
    sum             = measure_seconds * measure_index                       #accumulated time from previous measures
    fraction_256    = 256/len(measure)                                      #number of 1/256th notes per beat: 1/2nd = 128, 1/4th = 64, etc

    for i in range(len(measure)):
        if measure[i]==1:
            time.append(i * note_256 * fraction_256 + sum - offset)

    return time

def parse_sm(sm_file):
    x               = Step()
    measure         = []
    measure_index   = 0

    chars           = set('123456789')
    flag            = False

    with open(sm_file, encoding='ascii', errors='ignore') as f:
        for line in f:
            if line.startswith('#TITLE:'):
                x.title  = line.lstrip('#TITLE').lstrip(':').rstrip(';\n')
            if line.startswith('#BPMS:'):
                if ',' in line:                                             #raises Exception if multiple BPMS detected
                    raise Exception
                x.BPM    = float(line.lstrip('#BPMS:0.0').lstrip('0').lstrip('=').rstrip(';\n'))
            if line.startswith('#OFFSET:'):
                x.offset = float(line.lstrip('#OFFSET').lstrip(':').rstrip(';\n'))
            if line.startswith('#NOTES:'):
                flag     = True

            #start of note processing

            if flag:
                if line[0].isdigit():
                    check = False
                    if any((c in chars) for c in line):
                        check = True
                    if check:
                        measure.append(1)
                        x.types.append(convert_note(line.rstrip('\n')))
                    else:
                        measure.append(0)
                if line.startswith(','):
                    time = calculate_timing(measure, measure_index, x.BPM, x.offset)
                    x.notes.extend(time)
                    measure.clear()
                    measure_index += 1

                if line.startswith(';'):
                    time = calculate_timing(measure, measure_index, x.BPM, x.offset)
                    x.notes.extend(time)
                    measure.clear()
                    break

    return x

#===================================================================================================

def parse_by_folder(input_dir, output_dir):
    for folder in get_folder_name(input_dir):                                                      #parses song folders                          
        input_path = join(input_dir, folder)
        file_names = get_file_name(input_path)
        
        ogg = None
        sm  = None
        for file in file_names:
            if file.endswith('.ogg'):
                ogg = file
            elif file.endswith('.sm'):
                sm  = file
            if ogg is not None and sm is not None:
                break

        if ogg is None or sm is None:
            print('Folder %s is missing .sm or .ogg file!' % folder)
            continue

        new_file = format_file_name(sm)
        try:
            sm_data = parse_sm(join(input_path, sm))
            output_file(new_file, sm_data)
            copyfile(join(input_path, ogg), join(output_dir, new_file + '.ogg'))
        except Exception:
            print('Write failed: ' + sm)    

def parse_by_file(input_dir, output_dir):                                                        #parses loose .sm and .ogg files
    file_names = get_file_name(input_dir)
    sm_files  = [file for file in file_names if file.endswith('.sm')]
    ogg_files = [file for file in file_names if file.endswith('.ogg')]

    format_ogg_dict = dict(zip([format_file_name(ogg) for ogg in ogg_files], range(len(ogg_files))))

    for sm in sm_files:
        new_file = format_file_name(sm)
        if new_file in format_ogg_dict:
            try:
                sm_data = parse_sm(join(input_dir, sm))
                output_file(new_file, sm_data)
            except Exception:
                print('Write failed: ' + sm)
                continue

            copyfile(join(input_dir, ogg_files[format_ogg_dict[new_file]]), join(output_dir, new_file + '.ogg'))

#===================================================================================================

if __name__ == '__main__':
    dir = dirname(realpath(__file__))
    start_time = time.time()

    make_folder(dir)
    input_dir  = join(dir, 'input')
    output_dir = join(dir, 'output')

    parse_by_folder(input_dir, output_dir)
    parse_by_file(input_dir, output_dir)

    end_time = time.time()

    print("Elapsed time was %g seconds" % (end_time - start_time))
