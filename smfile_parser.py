from collections import defaultdict
from os import makedirs, walk
from os.path import join, isdir, dirname, realpath
from re import sub
from shutil import copyfile
import argparse
import time

def format_file_name(f):    #formats file name to ASCII
    name = "".join(f.split('.')[:-1]).lower()   #lowercase; splits by period; removes extension
    formatted = sub('[^a-z0-9-_ ]', '', name)    #ignores special characters, except - and _
    return sub(' ', '_', formatted)  #replaces whitespace with _

def output_file(file_name, x, output_dir):  #outputs results to file text
    ofile = file_name + '.txt'

    with open(join(output_dir, ofile), 'w') as f:
        f.write('TITLE ' + x['title'] + '\n')
        f.write('BPM   ' + str(x['bpm']) + '\n')
        f.write('NOTES\n')
        for note in x['notes']:
            f.write(note + '\n')

#===================================================================================================

def convert_note(line):                                                      
    return sub('4', '1', sub('[MKLF]', '0', line))    #removes extra notes: M, K, L, F; removes 4 note

#===================================================================================================

# BPM       = beats/minute -> BPS = beats/second = BPM/60
# measure   = 4 beats = 4 * 1/4th notes     = 1 note
# 1/256    -> 256 * 1/256th notes           = 1 measure

def calculate_timing(measure, measure_index, bpm, offset):  #calculate time in seconds for each line
    measure_seconds = 4 * 60/bpm    #length of measure in seconds   
    note_256        = measure_seconds/256   #length of each 1/256th note in the measure in seconds
    measure_timing  = measure_seconds * measure_index   #accumulated time from previous measures
    fraction_256    = 256/len(measure)  #number of 1/256th notes per beat: 1/2nd = 128, 1/4th = 64, etc

    line_timing = [measure[i] + ' ' + str(i * note_256 * fraction_256 + measure_timing - offset) for i, is_set in enumerate(measure) if is_set != None]
    
    return line_timing

def parse_sm(sm_file, new_file, output_dir):
    step_dict = defaultdict(list)
    measure         = []
    measure_index   = 0

    flag            = False

    with open(sm_file, encoding='ascii', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            if not flag:
                if line.startswith('#TITLE:'):
                    step_dict['title']  = line.lstrip('#TILE').lstrip(':').rstrip(';')
                elif line.startswith('#BPMS:'):
                    if ',' in line:  # raises Exception if multiple BPMS detected
                        raise ValueError('Multiple BPMs detected')
                    step_dict['bpm']    = float(line.lstrip('#BPMS:.0').lstrip('=').rstrip(';'))
                elif line.startswith('#OFFSET:'):
                    step_dict['offset'] = float(line.lstrip('#OFSET:').rstrip(';'))
                elif line.startswith('#STOPS:') and line != "#STOPS:;":
                    raise ValueError('Stop detected')
                elif line.startswith('#NOTES:'):
                    flag     = True

            if flag:   #start of note processing
                if line and not line.startswith((' ', ',', ';', '#')):
                    line = convert_note(line)
                    if line[0].isdigit():
                        check = True if any((c in set('123456789')) for c in line) else False
                        if check:
                            measure.append(line)
                        else:
                            measure.append(None)
                elif line.startswith((',', ';')):
                    line_timing = calculate_timing(measure, measure_index, step_dict['bpm'], step_dict['offset'])
                    step_dict['notes'].extend(line_timing)
                    measure.clear()
                    measure_index += 1
                elif line.startswith('#NOTES:'):
                    measure_index = 0
                    next(f)
                    next(f)
                    step_dict['notes'].append('DIFFICULTY ' + next(f).lstrip(' ').rstrip(':\n'))
                
    return step_dict

#===================================================================================================

def parse(input_dir, output_dir):
    for root, dirs, files in walk(input_dir):
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
            makedirs(output_dir)
        parse(input_dir, output_dir)

    end_time = time.time()

    print("Elapsed time was %g seconds" % (end_time - start_time))
