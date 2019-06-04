import os

class Step:
    title   = "empty"
    BPM     = 0.0
    notes   = []

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

def get_file():                                                                                     #input name of file
    while True:                                                                                     #beware of foreign characters (ex. Japanese)
        n = input("Enter a .sm file: ")
        if n.endswith('.sm'):
            break
        print("Failed to open file.")
    return n

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
                    else:                                                                           #if line in measure has no notes
                        measure.append(0) 

            if line.startswith(','):
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
    n = '_'.join(n.split()).split('.')[0].lower() + '.txt'
    d = "".join(e for e in n if e not in '()[]@!?#$%^&*')

    with open(d, "w") as f:
        f.write("TITLE " + str(x.title) + "\n")
        f.write("BPM   " + str(x.BPM) + "\n")
        f.write("NOTES\n")
        for i in x.notes:
            f.write(str(i) + "\n")

    print("\nWrite successful.")

#=================================================================================================
#MAIN
while True:
    n = get_file()
    x = parse_sm(n)

    print("\nOptions")
    print("1...print info")
    print("2...write to file")
    print("3...quit")
    e = input("Select option: ")

    if(e=="1"):
        print("\nTitle: " + str(x.title))
        print("BPM:   "   + str(x.BPM))
        print("Notes:\n"  + str(x.notes) + "\n")

    if(e=="2"):
        output_file(n,x)

    if(e=="3"):
        break
