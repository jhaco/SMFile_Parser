import os
from os.path import isfile, join, isdir, dirname, realpath
from shutil import copyfile
from collections import defaultdict
import re
import time
import argparse

def format_file_name(f):    #formats file name to ASCII
    name = "".join(f.split('.')[:-1]).lower()   #lowercase; splits by period; keeps extension
    formatted = re.sub('[^a-z0-9-_ ]', '', name)    #ignores special characters, except - and _
    return re.sub(' ', '_', formatted)  #replaces whitespace with _

def output_file(file_name, x, output_dir):  #outputs results to file text
    ofile = file_name + '.txt'

    with open(join(output_dir, ofile), 'w') as f:
        f.write('TITLE ' + str(x['title']) + '\n')
        f.write('BPM   ' + str(x['BPM']) + '\n')
        f.write('NOTES\n')
        for note_type, note in zip(x['types'], x['notes']):
            f.write(str(note_type) + " " + str(note) + '\n')

#===================================================================================================

def convert_note(line):                                                      
    convert = re.sub('[MKLF]', '0', line)   #removes extra notes: M, K, L, F
    return re.sub('4', '1', convert)    #removes 4 note

#===================================================================================================

# BPM       = beats/minute -> BPS = beats/second = BPM/60
# measure   = 4 beats = 4 * 1/4th notes     = 1 note
# 1/256    -> 256 * 1/256th notes           = 1 measure

def calculate_timing(measure, measure_index, bpm, offset):  #calculate time in seconds for each line
    measure_seconds = 4 * 60/bpm    #length of measure in seconds   
    note_256        = measure_seconds/256   #length of each 1/256th note in the measure in seconds
    measure_timing  = measure_seconds * measure_index   #accumulated time from previous measures
    fraction_256    = 256/len(measure)  #number of 1/256th notes per beat: 1/2nd = 128, 1/4th = 64, etc

    line_timing = [str(i * note_256 * fraction_256 + measure_timing - offset) for i, is_set in enumerate(measure) if is_set]
    
    return line_timing

def parse_sm(sm_file, new_file, output_dir):
    step_dict = defaultdict(list)
    measure         = []
    measure_index   = 0

    flag            = False

    with open(sm_file, encoding='ascii', errors='ignore') as f:
        for line in f:
            if not flag:
                if line.startswith('#TITLE:'):
                    step_dict['title']  = line.lstrip('#TITLE').lstrip(':').rstrip(';\n')
                elif line.startswith('#BPMS:'):
                    if ',' in line:  # raises Exception if multiple BPMS detected
                        raise ValueError('Multiple BPMs detected')
                    step_dict['BPM']    = float(line.lstrip('#BPMS:0.0').lstrip('0').lstrip('=').rstrip(';\n'))
                elif line.startswith('#OFFSET:'):
                    step_dict['offset'] = float(line.lstrip('#OFFSET').lstrip(':').rstrip(';\n'))
                elif line.startswith('#STOPS:') and line.rstrip('\n') != "#STOPS:;":
                    raise ValueError('Stop detected')

                elif line.startswith('#NOTES:'):
                    flag     = True
                    next(f)
                    next(f)
                    step_dict['types'].append("")
                    step_dict['notes'].append("")
                    step_dict['types'].append("DIFFICULTY ")
                    step_dict['notes'].append(next(f).lstrip(' ').rstrip(':\n'))

            else:   #start of note processing
                if line[0].isdigit():
                    check = True if any((c in set('123456789')) for c in line) else False
                    if check:
                        measure.append(True)
                        step_dict['types'].append(convert_note(line.rstrip('\n')))
                    else:
                        measure.append(False)
                elif line.startswith(',') or line.startswith(';'):
                    line_timing = calculate_timing(measure, measure_index, step_dict['BPM'], step_dict['offset'])
                    step_dict['notes'].extend(line_timing)
                    measure.clear()
                    if line.startswith(';'):
                        output_file(new_file, step_dict, output_dir)
                    measure_index += 1
                elif line.startswith('#NOTES:'):
                    measure_index = 0
                    #step_dict['types'].clear()
                    #step_dict['notes'].clear()
                    next(f)
                    next(f)
                    step_dict['types'].append("")
                    step_dict['notes'].append("")
                    step_dict['types'].append("DIFFICULTY ")
                    step_dict['notes'].append(next(f).lstrip(' ').rstrip(':\n'))
    return step_dict

#===================================================================================================

def parse(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        sm_files = [file for file in files if file.endswith('.sm')]
        ogg_files = [file for file in files if file.endswith('.ogg')]

        format_ogg_dict = dict(zip([format_file_name(ogg) for ogg in ogg_files], range(len(ogg_files))))

        for sm_file in sm_files:
            new_file = format_file_name(sm_file)
            if new_file in format_ogg_dict:
                try:
                    sm_data = parse_sm(join(root, sm_file), new_file, output_dir)
                    # write sm text data to output dir
                    output_file(new_file, sm_data, output_dir)
                    # move and rename .ogg file to output dir
                    copyfile(join(root, ogg_files[format_ogg_dict[new_file]]), join(output_dir, new_file + '.ogg'))
                except Exception as ex:
                    print('Write failed for %s: %r' % (sm_file, ex))    

#===================================================================================================

if __name__ == '__main__':
    start_time = time.time()

    dir = dirname(realpath(__file__))
    parser = argparse.ArgumentParser(description='Parser')
    parser.add_argument('--input', default='parseIn', help='Provide an input folder (default: parseIn)')
    parser.add_argument('--output', default='parseOut', help='Provide an output folder (default: parseOut)')

    args = parser.parse_args()
    input_dir  = join(dir, args.input)
    output_dir = join(dir, args.output)

    if not isdir(input_dir):
        print("Invalid input directory argument.")
    else:
        if not isdir(output_dir):
            print("Output directory missing: " + args.output + " \nGenerated specified output folder.")
            os.makedirs(output_dir)
        parse(input_dir, output_dir)

    end_time = time.time()

    print("Elapsed time was %g seconds" % (end_time - start_time))
