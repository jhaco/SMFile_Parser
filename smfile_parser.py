from collections import defaultdict
from os import makedirs, walk
from os.path import dirname, isdir, join, realpath
from re import sub
from shutil import copyfile
import argparse
import time

def format_file_name(f):    #formats file name to ASCII
    name = "".join(f.split('.')[:-1]).lower()   #lowercase; splits by period; removes extension
    formatted = sub('[^a-z0-9-_ ]', '', name)    #ignores special characters, except - and _
    return sub(' ', '_', formatted)  #replaces whitespace with _

def get_data(sm_file):
    data = defaultdict(list)
    flag = False

    with open(sm_file, encoding='ascii', errors='ignore') as f:
        for line in f:
            if not flag:
                if line.startswith('#TITLE:'):
                    data['title'] = line
                elif line.startswith('#BPMS:'):
                    if ',' in line:
                        raise ValueError('Multiple BPMs detected')
                    data['bpm'] = line
                elif line.startswith('#OFFSET:'):
                    data['offset'] = line
                elif line.startswith('#STOPS') and line.rstrip('\n') != '#STOPS:;':
                    raise ValueError('Stop detected')
                elif line.startswith('#NOTES:'):
                    flag = True
            if flag:
                if not (line.startswith(' ') or line.startswith('/') or line.startswith('\n') or line.startswith('#')):
                    data['notes'].append(sub('4', '1', sub('[MKLF]', '0', line)).rstrip('\n'))
                if line.startswith('#NOTES:'):
                    next(f)
                    next(f)
                    data['notes'].append('DIFFICULTY ' + next(f).lstrip(' ').rstrip(':\n'))

    return data

def clean_data(data):
    data['title']  = data['title'].lstrip('#TILE').lstrip(':').rstrip(';\n')
    data['bpm']    = float(data['bpm'].lstrip('#BPMS:.0').lstrip('=').rstrip(';\n'))
    data['offset'] = float(data['offset'].lstrip('#OFSET:').rstrip(';\n'))

def calculate_timing(measure, position, bpm, offset):
    mlength    = 4 * 60/bpm    #length of measure in seconds   
    notelength = mlength/256   #length of each 1/256th note in the measure in seconds
    mtime      = mlength * position   #accumulated time from previous measures
    beatlength = 256/len(measure)  #number of 1/256th notes per beat: 1/2nd = 128, 1/4th = 64, etc

    timing = [measure[i] + ' ' + str(i * notelength * beatlength + mtime - offset) for i, is_set in enumerate(measure) if is_set != None]
    
    return timing

def generate_timing(data):
    measure = []
    notes = []
    position = 0

    for line in data['notes']:
        if line[0].isdigit():
            check = True if any((c in set('123456789')) for c in line) else False
            if check:
                measure.append(line)
            else:
                measure.append(None)
        elif line.startswith(',') or line.startswith(';'):
            timing = calculate_timing(measure, position, data['bpm'], data['offset'])
            notes.extend(timing)
            measure.clear()
            position += 1
        elif line.startswith('DIFFICULTY'):
            notes.append(line)
            position = 0
    
    data['notes'] = notes

def output_file(file_name, data, output_dir):  #outputs results to file text
    ofile = file_name + '.txt'

    with open(join(output_dir, ofile), 'w') as f:
        f.write('TITLE ' + data['title'] + '\n')
        f.write('BPM   ' + str(data['bpm']) + '\n')
        f.write('NOTES\n')
        for note in data['notes']:
            f.write(note + '\n')

def parse(input_dir, output_dir):
    for root, dirs, files in walk(input_dir):
        sm_files = [file for file in files if file.endswith('.sm')]
        ogg_files = [file for file in files if file.endswith('.ogg')]

        format_ogg_dict = dict(zip([format_file_name(ogg) for ogg in ogg_files], range(len(ogg_files))))

        for sm_file in sm_files:
            new_file = format_file_name(sm_file)
            if new_file in format_ogg_dict:
                try:
                    sm_data = get_data(join(root, sm_file))
                    clean_data(sm_data)
                    generate_timing(sm_data)
                    # write sm text data to output dir
                    output_file(new_file, sm_data, output_dir)
                    # move and rename .ogg file to output dir
                    copyfile(join(root, ogg_files[format_ogg_dict[new_file]]), join(output_dir, new_file + '.ogg'))
                except Exception as ex:
                    print('Write failed for %s: %r' % (sm_file, ex))    

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
