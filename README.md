## SMFile_Parser
#### Stepmania File Parser for the [Stepmania Note Generator](https://github.com/cpuguy96/stepmania-note-generator) by cpuguy96 for [Stepmania](https://github.com/stepmania/stepmania/wiki/sm) by VR0. Used with [Stepmania File Writer](https://github.com/jhaco/SMTXT_Converter) by me

Batch processes all .sm files in current dir of smfile_parser.py and parses for:
- Title
- BPM
- Note Timings (in seconds)
- Note Placements (ex. 0001, 0201, etc)

Then writes data to their respective .txt output files for valid .sm files.\
Only supports files with static BPM for the purpose of training the note generator program.\
Is able to skip .sm files with varying BPM.\
Does not support 3/4th measures.\
Only reads the first difficulty listed.

#### links:

- [Stepmania .SM Formatting](https://github.com/stepmania/stepmania/wiki/sm)
- [Stepmania Note Colors](https://step-mania.fandom.com/wiki/Notes)
- [It's About Time: An Article on Beats and Measure Calculation](https://sites.uci.edu/camp2014/2014/05/19/its-about-time/)

---

#### changelog (top-new):
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

#### plans:
- ~~be able to convert the resultant .txt file back to a usable .sm file~~ [here](https://github.com/jhaco/SMTXT_Converter)
- be able to parse all difficulties included in the target .sm file
- be able to check .sm files for static BPM and only parse those

#### issues:
- some .sm files that should work does not, throwing a divide by zero exception
- a single file had been renamed incorrectly, unsure of what caused this
