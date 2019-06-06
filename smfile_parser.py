from os import listdir, rename
from os.path import isfile, join

class Step():
    title   = "empty"
    BPM     = 0.0
    notes   = []
    types   = []

def get_file_names(mypath):                                                                         #lists all files in specified directory
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

#=================================================================================================

def convert_note(line):
    x = line.replace("M", "0").replace("2", "1").replace("3", "1").replace("4", "1").replace("K", "0").replace("L", "0").replace("F", "0")
    return x

def format(src):
    dst = '_'.join(src.split()).split('.')[0].lower()
    return "".join(e for e in dst if e not in '()[]@!?#$%^&*')

#=================================================================================================

#BPM = beats/minute -> BPS = beats/second = BPM/60
#measure = 4 beats = 4 1/4th notes = 1
#1/192 >  1 measure = 192 1/192nd notes

def get_timing(measure, m_i, bpm):                                                                  #gets time
    time            = []                                                                            #seconds per beat = 60/bpm
    measure_seconds = 4 * 60/bpm                                                                    #measure in seconds = 4 x seconds per beat
    note_192        = measure_seconds/192                                                           #time of notes in seconds
    sum             = measure_seconds * m_i                                                         #sum of measures before in seconds
    X_192           = 192/len(measure)                                                              #number of 1/192th notes between 1/Xth notes

    for i in range(len(measure)):
        if measure[i] == 1:
            time.append(i * note_192 * X_192 + sum)

    return time

#=================================================================================================

def parse_sm(n):                                                                                    #parse .sm for BPM and measure + notes
    x       = Step()                                                                                #Step class x
    m_i     = 0                                                                                     #number of measure
    measure = []
    chars   = set('123456789')                                                                      #set of digits, not including 0
    flag    = False
    bide    = {
        "0001": "01", "0110": "06", "1011": "11",
        "0010": "02", "0111": "07", "1100": "12",
        "0011": "03", "1000": "08", "1101": "13",
        "0100": "04", "1001": "09", "1110": "14",
        "0101": "05", "1010": "10", "1111": "15"
    }

    with open(n, 'r', encoding='ascii', errors='ignore') as f:                                      #ignores non-ASCII text (ex. Japanese)      
        for line in f:                                                                              #reads by line
           
            if line.startswith('#TITLE:'):                                                          #title
                x.title = line.lstrip('#TITLE').lstrip(':').rstrip(';\n')

            if line.startswith('#BPMS:'):                                                           #BPM
                x.BPM   = float(line.lstrip('#BPMS:0.0').lstrip('0').lstrip('=').rstrip(';\n'))

            if line.startswith('#KEYSOUNDS:') or line.startswith('#ATTACKS:'):                      #checks if the last hashtag property is read
                flag = True

            #=====================================================================================

            if line[0].isdigit():                                                                   #notes
                if flag:
                    check = False
                    if any((c in chars) for c in line):                                             #if line in measure has notes
                        check = True
                    if check:                        
                        measure.append(1)
                        x.types.append(bide[convert_note(line.rstrip('\n'))])                                                            
                    else:                                                                           #if line in measure has no notes
                        measure.append(0) 

            if line.startswith(',') or line.startswith(';'):
                time = get_timing(measure, m_i, x.BPM)
                x.notes.extend(time)                                                                #adds list of timestamps to x.notes
                measure.clear()
                m_i += 1

            if line.startswith(';'):                                                                #stops parsing after first difficulty set finished
                if flag:
                    break

    return x

#=================================================================================================

def output_file(n,x):                                                                               #outputs to .txt
    d = format(n) + '.txt'

    with open(d, "w") as f:
        f.write("TITLE " + str(x.title) + "\n")
        f.write("BPM   " + str(x.BPM) + "\n")
        f.write("NOTES\n")
        for i in range(len(x.notes)):
            f.write(str(x.types[i]) + " " + str(x.notes[i]) + "\n")

    print("Write successful: " + d)

#=================================================================================================
#MAIN
for f in get_file_names("./"):
    if f.endswith(".sm"):
        try:
            x = parse_sm(f)
            output_file(f,x)
        except Exception:
            pass
        x.notes.clear()
        x.types.clear()
    if f.endswith(".ogg"):
        try:
            n = format(f) + '.ogg'
            rename(f, n)
        except Exception:
            pass
