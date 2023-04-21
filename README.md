# MKVToolNix Sequential Batch Mapper

## Notes:

 - This is useful for remuxes where each episode has the same basic input and output variables.
 - My fork of this script allows you to map different titles to both the mkv and filename for each episode, offset episode numbers by a predetermined amount, autocomplete filenames, automatically calculate the CRC of output files, and automatically mux in required fonts.
 - Only works on Windows for now.

## Dependencies:

-  [MKVToolNix](https://www.fosshub.com/MKVToolNix.html)

-  [Python 3](https://www.python.org/downloads/)

- `pip install FontCollector Colorama`

    - [FontCollector](https://github.com/moi15moi/FontCollector) is used for [automatic font muxing](#automatic-font-muxing)

## Helpful tools: 
- [Advanced Renamer](https://www.advancedrenamer.com/) to batch rename files.

## Usage:

1. Clone this repository.

2. Make sure all your MKV files have the same name apart from the episode numbers. 

    - Note: this can now be bypassed by using [filepath autocompletion](#autocomplete-filepath).

3. Open `mkvtoolnix-gui.exe`.

4. Insert all the media for your first episode of the batch.

5. Do your edits in the GUI, including naming the output file whatever you'd like.

    - If you want to add different attachments for each episode, see the [relevant section](#attachments).

6. Go to `Menu Bar > Multiplexer > Create option file`, and save it as `options.json` in the same directory as the `mkv_merge_mapper.py` script. You can then close the GUI.

7. Open said `options.json` file with your text editor:

    - Where there is an episode number, replace the number with the text `EPNUM` (S01E**01** -> S01E**EPNUM**)

    - Do this for all the file paths in the `options.json` file.

    - For more options on manipulating episode numbers, see [Episode Number Modifiers](#episode-number-modifiers)

8. Find the MKVToolNix folder and get its path. (`Shift + Right-Click > Copy as path` from Windows File Explorer).

    - Typically `C:\\Program Files\\MKVToolNix`.

9. Edit `mkvconfig.json` and insert the path to the MKVToolNix folder into the quotes after the variable `mkv_merge_path`. You can also change other script variables here.

    - Note: You MUST replace every instance of a backslash `\` in mkvmerge's filepath with two backslashes `\\`.

10. Optional edits to `options.json`. See following sections.

11. Run `mkvtoolnix_merge_mapper.py`.
  
12. When prompted, enter the range of episode numbers you want to mux. Your files will be sequentially muxed into the set output directory (`mkvmerge_out` by default).


## Titles

The script will put the episode title in filenames and automatically mux episode titles to the mkv header without having to manually change them in each file.

In order to do this, a `titles.txt` file must be in the working directory (alongside the options file and the script).

Write the desired titles for each episode in `titles.txt`, with each separate title on a new line. (The first line will be the first episode's title, the second line will be the second episode's title, and so on).

You can also include an `mkvtitles.txt` file in the working directory, which can be used to use separate titles for the filename and mkv header. If only `titles.txt` is present, its titles will be used in both the filenames and mkv header, and vice versa with `mkvtitles.txt`.

In the options file, any instance of `EPTITLE` or `MKVTITLE` will be replaced with the current episode's title, from either `titles.txt` or `mkvtitles.txt` respectively. For example, `Show - EPNUM - EPTITLE.mkv` will become `Show - 01 - dumb title.mkv`.

If the output filename doesn't have `EPTITLE` or `MKVTITLE` in it, and the filename title option is enabled, the title will be automatically placed after the episode number, using the separator specified in `mkvconfig.json`.

## Automatic font muxing
The script will automatically detect the fonts needed in included .ass files and will mux them into the output file. This feature also removes any unneeded fonts that may have been included in the input mkv files.

This feature requires [FontCollector](https://github.com/moi15moi/FontCollector) to be installed.

- Simply run `mkvtoolnix_merge_mapper.py`, and when prompted on whether you want to automatically mux fonts, input `yes` or `y`.
    - This preference can also be set in the `mkvconfig.json` file

- The script will only be able to mux fonts that are installed or that are in one of the input mkv files.

- I have introduced a feature where a log of FontCollector's activity is generated in the output directory, and all fonts from input mkvs will be copied to a `Fonts` folder. This should make it easier to spot and fix errors. It can be enabled in `mkvconfig.json`.

- **FontCollector is not perfect. Always QC your files!**

## Autocomplete filepath

The script will autocomplete the paths of specified files. Useful if the filenames you want to use have a CRC or episode name in them, which means they won't match the rule in your options file. (For example, if the releases you want to remux have filenames like `Show - 01 - dumb title.mkv`, `Show - 02 - different title.mkv`, the rule `Show - EPNUM.mkv` won't work.)

- Put three stars (`***`) wherever you want the script to autocomplete the filename. Using the example above, the rule `Show - EPNUM - ***` would match both of those filenames. This can also be used in folder names.

- Put two stars (`**`) if you want to specify an extension for the file. For example, let's say you have both `Show - 01 - dumb title.mkv` and `Show - 01 - dumb title.ass` in the same directory. In this case the rule `Show - EPNUM - **.mkv` would match the first file and `Show - EPNUM - **.ass` would match the second.

- As long as your rule gives enough information to single out one file, it will be accepted.

## Calculate CRC

The script will calculate a CRC32 hash for the file and insert it into the filename.

- Include `CRC` anywhere in the output filename. The script will calculate the CRC of the output file and replace  `CRC` with it.

- For example, if your output rule is `Show - EPNUM [CRC].mkv`, the output will be `Show - 01 [CF022A71]`.

## Episode Number Modifiers

The script will offset the episode numbers in the options file by a certain amount each time. Useful if you're muxing different releases that use different episode numbers.

- Put `MOD()` with the offset in the brackets after any instance of EPNUM that you want to change in the options file. 

    - For example, all my input files say "Episode 31", "Episode 32", but I want the episode numbers in my output file to be "Episode 01", "Episode 02", and so on. To do so, I would edit any instance of `EPNUM` that I would want to offset to `EPNUMMOD(-30)` in the options file.

- If you want the episode numbers in the mkv title changed, just put `MOD()` with your offset number in the brackets anywhere in the title field.

## Attachments

The script will mux different (specified) attachments for each episode. Can be used instead of the automatic font muxer.

- Create a separate folder for each episode, with the attachments for each episode in their respective folders.

    - For example, if you have different font attachments for episodes 1 and 2, make folders called `..\01` and `..\02`, with the attachments for episode 1 in `..\01` and those for episode 2 in `..\02`.

- Add a file from one of the folders as an attachment in mkvtoolnix before you export as `options.json`.

- When editing `options.json`:

    - Edit the aforementioned attachment's `attachment-mime-type` to be `batch/attachment`. 

    - `attachment-name` can be left as-is.

    - Replace the episode number in the folder name with `EPNUM`.

## License

Code licensed under GNU General Public License v3.0.
