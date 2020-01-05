## SMFile_Parser
###### Stepmania File Parser for the [Stepmania Note Generator](https://github.com/cpuguy96/stepmania-note-generator) by cpuguy96 for [Stepmania](https://github.com/stepmania/stepmania/wiki/sm) by VR0. Used with [Stepmania File Writer](https://github.com/jhaco/SMTXT_Converter). Currently supports files with static BPM to reduce complexity in training the note generator program, and only reads the first difficulty found in the file.

Parses all .sm files in the `parseIn` folder by default for the following information:
- Title
- Beats-per-Minute (BPM)
- Note Timings (in seconds)
- Note Placements (ex. 0001, 0201, etc)

Writes processed data to their respective .txt files for successfully parsed .sm files to the `parseOut` folder by default.

#### Usage:
- Copy the Stepmania song folders into the input folder and run the script. The default input folder is `parseIn`.
- Successfully parsed files will be generated in the output folder. The default output folder is `parseOut`.
- If different folders are used, specify them by appending `--input inputfolder` and/or `--output outputfolder`.
  * Example: `python smfile_parser.py --input inputfolder --output outputfolder`
###### If either arguments are not specified, the scripts uses the default folder where none is specified.
###### If the specified input folder is not found, the script will print an error and terminate.
###### If the specified output folder is not found, the script will automatically generate the missing folder.

#### Links:

- [Stepmania .SM Formatting](https://github.com/stepmania/stepmania/wiki/sm)
- [Stepmania Note Colors](https://step-mania.fandom.com/wiki/Notes)
- [It's About Time: An Article on Beats and Measure Calculation](https://sites.uci.edu/camp2014/2014/05/19/its-about-time/)

---

#### Changelog (top-new):
- added argparse functionality with leaner code implementations from cpuguy96
- refactored code for readability with changes from cpuguy96 for file management
- added a check for .sm files with static BPM and ignores files with changing BPM
- changed "#KEYSOUNDS" checks to "#NOTES", it's basically the same thing
- corrected from 1/192th notes to 1/256th notes
- added offset timings (if present) resulting in more accurate translations
- added an error message to print the offending file name
- included hold (2) and roll (3) note types
- changed from binary/decimal note notation to copying the numeric combination for each valid note from the .sm file
- fixed a bug where the Step.note and Step.types were not cleared if errors occured while parsing a previous file
- cleaned up code for readability
- added formatting to .ogg files found within the directory
- added example vanessa .sm, .txt and .ogg files
- fixed a bug where the parser skipped the last measure
- replaced holds with normal note for note placement
- added note placement for each note timing as a binary to decimal function, ignores mines
- fixed a bug where the Step lists were not cleared after each file, resulting in abnormally large and incorrect output files
- added exception handling to continue to the next file if the current one throws an error
- converted to a no-input, batch processing method for .sm files found within the directory
- added formatting to output .txt file names
- ignores non-ASCII (ex. Japanese) text in the title
