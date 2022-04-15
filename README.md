# MKVToolNix Sequential Batch Mapper

## Notes:

 - This is useful for simple remuxes where each episode has the same basic variables.
 - My fork of this script allows you to map different titles to both the mkv and filename for each episode, and offset episode numbers by a predetermined amount.

## Dependencies:

-  [MKVToolNix](https://www.fosshub.com/MKVToolNix.html)

-  [Python 3](https://www.python.org/downloads/)

## Helpful tools: 
- [Advanced Renamer](https://www.advancedrenamer.com/) to batch rename files for step 2.

## Usage:

1. Clone this repository.

2. Make sure all your MKV files have the same name apart from the episode numbers. 

3. Open `mkvtoolnix-gui.exe`.

4. Insert all the media for your first episode of the batch.

5. Do your edits in the GUI, including naming the output file whatever you'd like.
- If you want to add different attachments for each episode, see the [relevant section](#attachments).

6. Go to `Menu Bar > Multiplexer > Create option file`, and save it as `options.json` in the same directory as the `mkv_merge_mapper.py` script. You can then close the GUI.

7. Open said `options.json` file with your text editor:

- Where there is an episode number, replace the number with the text `EPNUM` (S01E**01** -> S01E**EPNUM**)

- Do this for all the file paths in the `options.json` file.

- For more options on manipulating episode numbers, see [Episode Number Modifiers](#episode-number-modifiers)

8. Find the `mkvmerge.exe` executable within MKVToolNix and get its path (`Shift + Right-Click > Copy as path` from Windows File Explorer).

9. Edit `mkvconfig.json` and insert your path to `mkvmerge.exe` from step 8 into the quotes after the variable `mkv_merge_path`. You can optionally change other script variables, but I recommend you leave them unchanged.

- Note: You MUST replace every instance of a backslash `\` in mkvmerge's filepath with two backslashes `\\`.

10. Optional edits to `options.json`. See next sections.

11. Run `mkvtoolnix_merge_mapper.py`.
  
12. When prompted, enter the range of episode numbers you want to mux. Your files will be sequentially muxed into the set output directory (`mkvmerge_out` by default).

## Titles

Do this if you want to easily mux in episode titles without having to manually change them in each file.

1. Create `titles.txt` in the same directory as the options file and the script.
2. Write the desired titles for each episode in `titles.txt`, with each separate title on a new line. (The first line will be the first episode's title, the second line will be the second episode's title, and so on)
3. Run `mkvtoolnix_merge_mapper.py`.
4. When prompted on whether you want the title added to mkv or filename, type in `yes` or `y`.

Note:
You can now make the program use a separate list of titles in the mkv and filename. To do so, create a separate list of mkv titles named `mkvtitles.txt`.

## Episode Number Modifiers

Use this if you want the episode number in the script to be offset by a certain amount each time (eg. if you're muxing releases that use different episode numbers).

Put `MOD()` with the offset in the brackets after any instance of EPNUM that you want to change in the options file. 

For example, all my input files say "Episode 31", "Episode 32", but I want the episode numbers in my output file to be "Episode 01", "Episode 02", and so on. To do so, I would edit any instance of `EPNUM` that I would want to offset to `EPNUMMOD(-30)` in the options file.

If you want the episode numbers in the mkv title changed, just put `MOD()` with your offset number in the brackets anywhere in the title field.

## Attachments

If you want to attach different font files for each episode, you can create a folder for each episode, with the files for each episode in their respective folders.

(eg. if you have different fonts for episodes 1 and 2, make folders called `..\01` and `..\02`, with fonts for episode 1 in `..\01` and for episode 2 in `..\02`)

You should then add one of the folders as an attachment in mkvtoolnix before you export as `options.json`.

When editing `options.json`, you should replace the episode number in the folder name with `EPNUM`.

## License

Code licensed under GNU General Public License v3.0.
