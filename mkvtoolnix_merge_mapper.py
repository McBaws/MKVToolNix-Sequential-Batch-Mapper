import json
from json import JSONDecoder
import os
from os.path import exists
import subprocess
import zlib
import shutil
import datetime
import difflib
import platform

#set up config variables
config_filename = 'mkvconfig.json'

#default config
default_config = {
"mkv_toolnix_path":"C:\\Program Files\\MKVToolNix",

"out_folder":"mkvmerge_out",
"ep_var_name":"EPNUM",

"options_filename":"options.json",
"titles_filename":"titles.txt",
"mkvtitles_filename":"mkvtitles.txt",

"CRC_buffer":8192,

"auto_font_q":"",
"font_collector_log":"yes",
"font_match_guess":"yes",

"titles_filename_q":"",
"titles_mux_q":"",
"titles_mux_ep_q":"",

"skip_mux":""
}

#checks if a config file exists
if exists(config_filename):
    #loads config file as json
    with open(config_filename) as json_file:
        config_filedata = json.load(json_file)
    #makes config into a dictionary
    config = dict(default_config)
    #replaces any changed default values with those from the config file
    config.update(config_filedata)
else:
    print('Config file was not found. Using defaults.')
    config = dict(default_config)
    #looks up and assigns config values

auto_font_q = config['auto_font_q']
font_collector_log = config['font_collector_log']
font_match_guess = config["font_match_guess"]

titles_mux_q = config['titles_mux_q']
titles_filename_q = config['titles_filename_q']
titles_mux_ep_q = config['titles_mux_ep_q']

options_filename = config['options_filename']
titles_filename = config['titles_filename']
mkvtitles_filename = config['mkvtitles_filename']
ep_var_name = config['ep_var_name']
out_folder = config['out_folder']
CRC_buffer = config["CRC_buffer"]

mkv_toolnix_path = config['mkv_toolnix_path']
mkv_merge_path = mkv_toolnix_path + "\\mkvmerge.exe"
mkv_extract_path = mkv_toolnix_path + "\\mkvextract.exe"
mkv_propedit_path = mkv_toolnix_path + "\\mkvpropedit.exe"
mkv_info_path = mkv_toolnix_path + "\\mkvinfo.exe"

skip_mux = config["skip_mux"]

#checks if crucial files exist
if not exists(mkv_merge_path):
    print('\nmkvmerge was not found at given path')
    input('<press enter>')
    quit()

if not exists(options_filename):
    print('\noptions file was not found')
    input('<press enter>')
    quit()

if font_collector_log.lower() == "yes" or font_collector_log.lower() == "y" or font_collector_log.lower() == "true":
    font_collector_log = True
else:
    font_collector_log = False

if font_match_guess.lower() == "yes" or font_match_guess.lower() == "y" or font_match_guess.lower() == "true":
    font_match_guess = True
else:
    font_match_guess = False

if skip_mux.lower() == "yes" or skip_mux.lower() == "y" or skip_mux.lower() == "true":
    skip_mux = True
else:
    skip_mux = False

if not auto_font_q:
    print('\nWould you like to mux fonts automatically?')
    auto_font_q = input()
    if auto_font_q.lower() == "yes" or auto_font_q.lower() == "y":
        print("I'll take that as a yes.")
        auto_font_q = True
    else:
        print("I'll take that as a no.")
        auto_font_q = False
else:
    if auto_font_q.lower() == "yes" or auto_font_q.lower() == "y":
        print("\nMuxing fonts automatically.")
        auto_font_q = True
    else:
        print("\nNot muxing fonts automatically.")
        auto_font_q = False

#checks if a text file containing titles exists
mkvtitles_found = False
titles_found = False
if not exists(mkvtitles_filename) and not exists(titles_filename):
    print("\n\nCould not find " + titles_filename + " or " + mkvtitles_filename + ".")
    print("Will continue without including titles.")
    titles_mux_q = False
    titles_mux_ep_q = False
    titles_filename_q = False
if exists(titles_filename):
    with open(titles_filename) as titles:
        titles_data = [line.strip() for line in titles]
    titles_found = True
if exists(mkvtitles_filename):
    with open(mkvtitles_filename) as mkvtitles:
        mkvtitles_data = [line.strip() for line in mkvtitles]
    mkvtitles_found = True

if titles_found:
    if not titles_filename_q:
        print('\n\nWould you like to add titles to filename?')
        titles_filename_q = input()
        if titles_filename_q.lower() == "yes" or titles_filename_q.lower() == "y":
            print("I'll take that as a yes.")
            titles_filename_q = True
        else:
            print("I'll take that as a no.")
            titles_filename_q = False
    else:
        if titles_filename_q.lower() == "yes" or titles_filename_q.lower() == "y":
            print("\nAdding titles to filename.")
            titles_filename_q = True
        else:
            print("\nNot adding titles to filename.")
            titles_filename_q = False

if titles_found or mkvtitles_found:
    if not titles_mux_q:
        print('\n\nWould you like to mux titles to mkv?')
        titles_mux_q = input()
        if titles_mux_q.lower() == "yes" or titles_mux_q.lower() == "y":
            print("I'll take that as a yes.")
            titles_mux_q = True
        else:
            print("I'll take that as a no.")
            titles_mux_q = False
    else:
        if titles_mux_q.lower() == "yes" or titles_mux_q.lower() == "y":
            print("\nMuxing titles to mkv.")
            titles_mux_q = True
        else:
            print("\nNot muxing titles to mkv.")
            titles_mux_q = False

    if titles_mux_q == True:
        if not titles_mux_ep_q:
            print('\n\nWould you like to add episode number to mkv title?')
            titles_mux_ep_q = input()
            if titles_mux_ep_q.lower() == "yes" or titles_mux_ep_q.lower() == "y":
                print("I'll take that as a yes.")
                titles_mux_ep_q = True
            else:
                print("I'll take that as a no.")
                titles_mux_ep_q = False
        else:
            if titles_mux_ep_q.lower() == "yes" or titles_mux_ep_q.lower() == "y":
                print("\nAdding episode number to mkv title.")
                titles_mux_ep_q = True
            else:
                print("\nNot adding episode number to mkv title.")
                titles_mux_ep_q = False



#asks for range of episodes to mux
print('\n\nStart Episode:')
start_episode = input()

print('\nEnd Episode:')
end_episode = input()
print("")

#loads options file
with open(options_filename) as json_file:
    options_data = json.load(json_file)

ep_num = int(start_episode)

first_ep = True

while ep_num < int(end_episode)+1:
    options_data_temp = []
    options_data_temp += options_data

    #reads titles for given episode
    if titles_filename_q == True or titles_mux_q == True:
        if titles_found:
            title = titles_data[ep_num - 1]
        if mkvtitles_found:
            mkvtitle = mkvtitles_data[ep_num - 1]
        else:
            mkvtitle = title
        title_muxed = False

    #appends a 0 to numbers under 10
    if ep_num < 10:
        ep_string = '0' + str(ep_num)
    else:
        ep_string = str(ep_num)

    #searches for episode variable and places the title after its last occurence
    if titles_filename_q == True:
        for i, v in enumerate(options_data_temp):
            if options_data_temp[i - 1] == '--output':
                full_path = v
                if ep_var_name + "MOD(" in v:
                    if v.rindex(ep_var_name + "MOD(") != v.index(ep_var_name + "MOD("):
                        ep_num_pos = v.rindex(ep_var_name + "MOD(")
                        c_brack_pos = v.find(")", ep_num_pos) + 1
                        options_data_temp[i] = full_path[:c_brack_pos] + " - " + title + full_path[c_brack_pos:]
                    elif v.rindex(ep_var_name) != v.index(ep_var_name + "MOD("):
                        title_pos = v.rindex(ep_var_name) + len(ep_var_name)
                        options_data_temp[i] = full_path[:title_pos] + " - " + title + full_path[title_pos:]
                    else:
                        ep_num_pos = v.index(ep_var_name + "MOD(")
                        c_brack_pos = v.find(")", ep_num_pos) + 1
                        options_data_temp[i] = full_path[:c_brack_pos] + " - " + title + full_path[c_brack_pos:]
                elif ep_var_name in v:
                    if v.rindex(ep_var_name) != v.index(ep_var_name):
                        title_pos = v.rindex(ep_var_name) + len(ep_var_name)
                        options_data_temp[i] = full_path[:title_pos] + " - " + title + full_path[title_pos:]
                    else:
                        title_pos = v.index(ep_var_name) + len(ep_var_name)
                        options_data_temp[i] = full_path[:title_pos] + " - " + title + full_path[title_pos:]

    for i, v in enumerate(options_data_temp):

        #replaces episode variable with modified episode number
        if ep_var_name + "MOD(" in v:
            ep_num_pos = v.index(ep_var_name + "MOD(")
            o_brack_pos = ep_num_pos + len(ep_var_name) + 3
            c_brack_pos = v.find(")", ep_num_pos)
            entire_ep_var = v[ep_num_pos:c_brack_pos+1]
            try:
                modder = int(v[o_brack_pos+1:c_brack_pos])
            except:
                print("make sure episode number modifier is a number")
            new_ep_num = ep_num + modder
            if new_ep_num < 0:
                raise Exception("episode number modifier returns negative number")
            if new_ep_num < 10:
                new_ep_string = "0" + str(new_ep_num)
            else:
                new_ep_string = str(new_ep_num)
            options_data_temp[i] = options_data_temp[i].replace(entire_ep_var, new_ep_string, 1)

        #replaces episode variable with episode number
        if v.find(ep_var_name):
            options_data_temp[i] = options_data_temp[i].replace(ep_var_name, ep_string, 1)

        if v == '--output':
            full_path = options_data_temp[i + 1]
            pos = options_data_temp[i + 1].rindex("\\") + 1
            if out_folder:
                options_data_temp[i + 1] = full_path[:pos] + out_folder + "\\" + full_path[pos:]
            else:
                options_data_temp[i + 1] = full_path
            
        if v == '--title':
            if titles_mux_q == True:
                if titles_mux_ep_q == True:
                    if "MOD(" in options_data_temp[i + 1]:
                        ep_num_pos = options_data_temp[i + 1].index("MOD(")
                        o_brack_pos = ep_num_pos + 3
                        c_brack_pos = options_data_temp[i + 1].find(")", ep_num_pos)
                        try:
                            modder = int(options_data_temp[i + 1][o_brack_pos+1:c_brack_pos])
                        except:
                            print("make sure mktitle episode number modifier is a number")
                        new_ep_num = ep_num + modder
                        if new_ep_num < 0:
                            raise Exception("mkvtitle episode number modifier returns negative number")
                        if new_ep_num < 10:
                            new_ep_string = "0" + str(new_ep_num)
                        else:
                            new_ep_string = str(new_ep_num)
                        options_data_temp[i + 1] = "Episode " + new_ep_string + ": " + mkvtitle
                    else:
                        options_data_temp[i + 1] = "Episode " + ep_string + ": " + mkvtitle
                else:
                    options_data_temp[i + 1] = mkvtitle
                title_muxed = True

        if "***" in v:
            completion_pos = []
            #gets indexes where "***" appears
            for x in range(len(v)):
                if v.startswith("***", x):
                    completion_pos.append(x)
            for x in completion_pos:
                #updates v
                v = options_data_temp[i]
                #finds first occurrence of "***"
                x = v.index("***")
                #the folder the file to be completed is in
                completion_dir = v[:v[:x].rindex("\\")]
                #the beginning of the file to be completed
                completion_substr = v[v[:x].rindex("\\")+1:x]
                #all the files in that directory, ie possible matches
                completion_possible = os.listdir(completion_dir)
                completion_result = []
                #finds all the matches given the beginning of the file
                for y in completion_possible:
                    if y.startswith(completion_substr):
                        completion_result.append(y)
                #if there is more than one match or no matches, raise error
                if len(completion_result) > 1:
                    print("Usage of '***' unclear.", len(completion_result), "matching paths found:")
                    print(completion_result)
                    input('<press any key to exit>')
                    quit()
                if len(completion_result) == 0:
                    print("\nUsage of '***' unclear. No matching paths found for:")
                    print(v[:x+3])
                    input('<press any key to exit>')
                    quit()
                #get path with matched filename
                completion_path = os.path.join(completion_dir, completion_result[0])
                #replace options data with matched filename
                options_data_temp[i] = completion_path + v[x+3:]

        if "**" in v:
            v = options_data_temp[i]
            #finds index of "**"
            x = v.index("**")
            #the folder the file to be completed is in
            completion_dir = v[:v[:x].rindex("\\")]
            #the beginning of the file to be completed
            completion_substr = v[v[:x].rindex("\\")+1:x]
            #the file's extension
            completion_ext = os.path.splitext(v)[1]
            #all the files in that directory, ie possible matches
            completion_possible = os.listdir(completion_dir)
            completion_result = []
            #finds all the matches given the beginning of the file
            for y in completion_possible:
                if y.startswith(completion_substr) and y.endswith(completion_ext):
                    completion_result.append(y)
            #if there is more than one match or no matches, raise error
            if len(completion_result) > 1:
                print("Usage of '**' unclear.", len(completion_result), "matching paths found:")
                print(completion_result)
                input('<press any key to exit>')
                quit()
            if len(completion_result) == 0:
                print("\nUsage of '**' unclear. No matching paths found for:")
                print(v[:x+2])
                input('<press any key to exit>')
                quit()
            #get path with matched filename
            completion_path = os.path.join(completion_dir, completion_result[0])
            #replace options data with matched filename
            options_data_temp[i] = completion_path

    #check if CRC in output filename
    for i, v in enumerate(options_data_temp):
        if v == '--output':
            if "CRC" in options_data_temp[i + 1]:
                CRC_calc = True
            else:
                CRC_calc = False
            output_file = options_data_temp[i + 1]

    #add all attachments in folder 
    for i, v in enumerate(options_data_temp):  
        if v == "inode/directory":
            attachment_dir = options_data_temp[i+2]
            for root, dirs, files in os.walk(attachment_dir):
                for file in files:
                    options_data_temp.append("--attach-file")
                    options_data_temp.append(os.path.join(root, file))

    #remove folder attachments
    for i, v in reversed(list(enumerate(options_data_temp))):  
        if v == "inode/directory":
            options_data_temp.pop(i+2)
            options_data_temp.pop(i+1)
            options_data_temp.pop(i)
            options_data_temp.pop(i-1)
            options_data_temp.pop(i-2)
            options_data_temp.pop(i-3)

    if titles_mux_q == True:
        if title_muxed == False:
            options_data_temp.append('--title')
            if titles_mux_ep_q == True:
                options_data_temp.append("Episode " + str(ep_num) + ": " + mkvtitle)
            else:
                options_data_temp.append(mkvtitle)
            title_muxed = True
    
    print('Starting Episode (' + str(ep_num) + '/' + str(int(end_episode)) + ') ---------------')
    if not skip_mux:
        subprocess.call([mkv_merge_path] + options_data_temp)

    if auto_font_q:
        print("\nAutomatically muxing required fonts...")

        print("Extracting subtitle files...")
        #output mkvinfo for output file to a temp directory, then read it
        temp_dir = os.path.dirname(output_file) + "\\temp"
        if exists(temp_dir):
            shutil.rmtree(temp_dir)
        mkvinfo_output_file = temp_dir + "\\mkvinfo.txt"
        subprocess.call([mkv_info_path] + [output_file] + ["--redirect-output"] + [mkvinfo_output_file], stdout=subprocess.DEVNULL)
        with open(mkvinfo_output_file) as mkvinfo:
            mkvinfo_data = [line.strip() for line in mkvinfo]

        #get track ids of all ass files
        trackid = []
        for i, v in enumerate(mkvinfo_data):
            if v == "|  + Codec ID: S_TEXT/ASS":
                for x in range(0,1000):
                    if "Track number" in mkvinfo_data[i-x]:
                        trackid.append(int(mkvinfo_data[i-x][-2:-1]))
                        break

        #extract all subtitle files from output mkv
        extract_args = ["tracks"]
        for i in range(0, len(trackid)):
            extract_args.append(str(trackid[i]) + ":" + temp_dir + "\\extracted sub " + str(trackid[i]) + ".ass")
        subprocess.call([mkv_extract_path] + [output_file] + extract_args)

        #get attachment ids and names of all fonts
        cur_aid = 0
        aid = []
        for i, v in enumerate(mkvinfo_data):
            if v == "| + Attached":
                cur_aid+=1
            if "application/x-truetype-font" in v or "application/vnd.ms-opentype" in v or "application/x-font-ttf" in v or "application/x-font" in v or "application/font-sfnt" in v or "font/collection" in v or "font/otf" in v or "font/ttf" in v or "font/sfnt" in v:
                aid.append([cur_aid, mkvinfo_data[i-1][mkvinfo_data[i-1].index("name:")+6:]])

        #extract all fonts from output mkv
        print("\nExtracting fonts from output file...", end="")
        extract_args = ["attachments"]
        for i in range(0, len(aid)):
            extract_args.append(str(aid[i][0]) + ":" + temp_dir + "\\" + aid[i][1])
        subprocess.call([mkv_extract_path] + [output_file] + extract_args, stdout=subprocess.DEVNULL)
        print("   Done.")

        if font_collector_log:
            print("Copying extracted fonts to folder...", end="")
            extract_args = ["attachments"]
            for i in range(0, len(aid)):
                extract_args.append(str(aid[i][0]) + ":" + os.path.dirname(output_file) + "\\Fonts\\" + aid[i][1])
            subprocess.call([mkv_extract_path] + [output_file] + extract_args, stdout=subprocess.DEVNULL)
            print("   Done.")

        #delete all fonts from output mkv
        print("Removing fonts from output file...", end="")
        subprocess.call([mkv_propedit_path] + [output_file] + ["--delete-attachment", "mime-type:application/x-truetype-font", "--delete-attachment", "mime-type:application/vnd.ms-opentype", "--delete-attachment", "mime-type:application/x-font-ttf", "--delete-attachment", "mime-type:application/x-font", "--delete-attachment", "mime-type:application/font-sfnt", "--delete-attachment", "mime-type:font/collection", "--delete-attachment", "mime-type:font/otf", "--delete-attachment", "mime-type:font/sfnt", "--delete-attachment", "mime-type:font/ttf"], stdout=subprocess.DEVNULL)
        print("   Done.")

        #fontCollector
        #detect all ass files in folder, then copy all needed fonts
        attachment_dir = temp_dir + "\\collected"
        log_font_dir = temp_dir + "\\log"
        os.mkdir(attachment_dir)
        os.mkdir(log_font_dir)
        fontcollector_args = []
        print("\nFinding necessary fonts...")
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".ass"):
                    fontcollector_args.append(os.path.join(root, file))
        subprocess.call(["fontcollector", "-o", attachment_dir, "-mkvpropedit", mkv_propedit_path, "--additional-fonts", temp_dir, "--input"] + fontcollector_args)

        #do the same but log
        cur_ep_font_log = []
        if font_collector_log:
            print("\nLogging...")
            if first_ep:
                log_path = os.path.dirname(output_file) + "\\Fonts\\!fontcollector - " + datetime.datetime.now().strftime("%Y.%m.%d %H-%M-%S") + ".log"
                with open(log_path, "w") as log:
                    log.write("Episode " + ep_string + ":\n")
            else:
                with open(log_path, "a") as log:
                    log.write("Episode " + ep_string + ":\n")
            
            with open(log_path, "a") as log:
                with subprocess.Popen(["fontcollector", "-o", attachment_dir, "-mkvpropedit", mkv_propedit_path, "--additional-fonts", temp_dir, "--input"] + fontcollector_args, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True) as p:
                    for line in p.stdout:
                        log.write(line)
                        cur_ep_font_log.append(line)
                log.write("\n")
        elif font_match_guess:
            with subprocess.Popen(["fontcollector", "-o", attachment_dir, "-mkvpropedit", mkv_propedit_path, "--additional-fonts", temp_dir, "--input"] + fontcollector_args, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True) as p:
                for line in p.stdout:
                    cur_ep_font_log.append(line)

        #detect fonts that weren't found by fontcollector
        if font_match_guess:
            bad_fonts = []
            for i, v in enumerate(cur_ep_font_log):
                if v == "Error: Some fonts were not found. Are they installed? :\n":
                    for x in cur_ep_font_log[i+1:]:
                        if x[:-1] != "":
                            bad_fonts.append(x[:-1])
            if bad_fonts:
                print("\nDetecting fonts that weren't found by fontcollector...")
                if font_collector_log:
                    with open(log_path, "a") as log:
                        log.write("Detecting fonts that weren't found by fontcollector...")

            #copy fonts that are in temp_dir and have similar names to fonts fontcollector couldn't find
            matches = []
            bad_font_num = 0
            fixed_fonts = []
            if font_collector_log:
                search_dir = os.path.dirname(output_file) + "\\Fonts"
            else:
                search_dir = os.path.dirname(output_file) + temp_dir
            for root, dirs, files in os.walk(search_dir):
                for bad_font_o in bad_fonts:
                    matches.append([])
                    for file in files:
                        filename = os.path.splitext(file)[0]
                        bad_font = bad_font_o.replace(" ", "").replace("-", "").replace("_", "").lower()
                        filename = filename.replace(" ", "").replace("-", "").replace("_", "").lower()
                        if difflib.SequenceMatcher(None, filename, bad_font).ratio() > 0.5:
                            matches[bad_font_num].append([difflib.SequenceMatcher(None, filename, bad_font).ratio(), file])
                    if sorted(matches[bad_font_num]):
                        shutil.copy2(os.path.join(root, file), attachment_dir + "\\" + sorted(matches[bad_font_num])[-1][1])
                        print("MATCHED: '" + bad_font_o + "' with '" + sorted(matches[bad_font_num])[-1][1] + "'")
                        if font_collector_log:
                            with open(log_path, "a") as log:
                                log.write("\nMATCHED: '" + bad_font_o + "' with '" + sorted(matches[bad_font_num])[-1][1] + "'")
                        fixed_fonts.append(bad_font_o)
                    bad_font_num += 1

            for bad_font in fixed_fonts:
                bad_fonts.remove(bad_font)
            fixed_fonts = []

            if len(bad_fonts) > 0:
                matches = []
                bad_font_num = 0
                if platform.system() == "Windows":
                    for root, dirs, files in os.walk(os.path.join(os.environ['SystemRoot'], "Fonts")):
                        for bad_font_o in bad_fonts:
                            matches.append([])
                            for file in files:
                                filename = os.path.splitext(file)[0]
                                bad_font = bad_font_o.replace(" ", "").replace("-", "").replace("_", "").lower()
                                filename = filename.replace(" ", "").replace("-", "").replace("_", "").lower()
                                if difflib.SequenceMatcher(None, filename, bad_font).ratio() > 0.5:
                                    matches[bad_font_num].append([difflib.SequenceMatcher(None, filename, bad_font).ratio(), file])
                            if sorted(matches[bad_font_num]):
                                shutil.copy2(os.path.join(root, file), attachment_dir + "\\" + sorted(matches[bad_font_num])[-1][1])
                                print("OS MATCHED: '" + bad_font_o + "' with '" + sorted(matches[bad_font_num])[-1][1] + "'")
                                if font_collector_log:
                                    with open(log_path, "a") as log:
                                        log.write("\nOS MATCHED: '" + bad_font_o + "' with '" + sorted(matches[bad_font_num])[-1][1] + "'")
                                fixed_fonts.append(bad_font_o)
                            bad_font_num += 1
                
            for bad_font in fixed_fonts:
                bad_fonts.remove(bad_font)
            fixed_fonts = []

            if len(bad_fonts) > 0:
                matches = []
                bad_font_num = 0
                if platform.system() == "Windows":
                    for root, dirs, files in os.walk(os.path.join(os.environ['LOCALAPPDATA'], "Microsoft\\Windows\\Fonts")):
                        for bad_font_o in bad_fonts:
                            matches.append([])
                            for file in files:
                                filename = os.path.splitext(file)[0]
                                bad_font = bad_font_o.replace(" ", "").replace("-", "").replace("_", "").lower()
                                filename = filename.replace(" ", "").replace("-", "").replace("_", "").lower()
                                if difflib.SequenceMatcher(None, filename, bad_font).ratio() > 0.5:
                                    matches[bad_font_num].append([difflib.SequenceMatcher(None, filename, bad_font).ratio(), file])
                            if sorted(matches[bad_font_num]):
                                shutil.copy2(os.path.join(root, file), attachment_dir + "\\" + sorted(matches[bad_font_num])[-1][1])
                                print("OS MATCHED: '" + bad_font_o + "' with '" + sorted(matches[bad_font_num])[-1][1] + "'")
                                if font_collector_log:
                                    with open(log_path, "a") as log:
                                        log.write("\nOS MATCHED: '" + bad_font_o + "' with '" + sorted(matches[bad_font_num])[-1][1] + "'")
                                fixed_fonts.append(bad_font_o)
                            bad_font_num += 1

            for bad_font in fixed_fonts:
                bad_fonts.remove(bad_font)

            if len(bad_fonts) == 1:
                print("\n1 font not matched:\n" + bad_fonts[0])
                if font_collector_log:
                    with open(log_path, "a") as log:
                        log.write("\n1 font not matched:\n" + bad_fonts[0])

            elif len(bad_fonts) > 1:
                print("\n" + str(len(bad_fonts)) + " fonts not matched:")
                for bad_font in bad_fonts:
                    print(bad_font)
                if font_collector_log:
                    with open(log_path, "a") as log:
                        log.write("\n" + str(len(bad_fonts)) + " fonts not matched:")
                        for bad_font in bad_fonts:
                            log.write(bad_font)

        #mux needed fonts to ouput mkv
        print("\nMuxing necessary fonts to output file:")
        propedit_args = []
        for root, dirs, files in os.walk(attachment_dir):
            for file in files:
                print(file)
                propedit_args.append("--add-attachment")
                propedit_args.append(os.path.join(root, file))
        subprocess.call([mkv_propedit_path] + [output_file] + propedit_args, stdout=subprocess.DEVNULL)

        #remove temp dir
        shutil.rmtree(temp_dir)

    if CRC_calc:
        print("\n\nCRC is being calculated. This may take a while.")
        with open(output_file, 'rb') as f:
            crc = 0
            while True:
                data = f.read(CRC_buffer)
                if not data:
                    break
                crc = zlib.crc32(data, crc)
        crcstr = ""
        if len(crcstr) != 8:
            zeros = 8 - len(str(hex(crc)[2:]))
            for i in range(0,zeros):
                crcstr = crcstr + "0"
        crcstr = crcstr + str(hex(crc)[2:]).upper()
        print("CRC is [" + crcstr + "]")
        os.rename(output_file, output_file.replace("CRC", crcstr))

    print('\nFinished Processing ----------------')
    ep_num += 1
    first_ep = False

print('\n\nAll files have been processed.')
input('<press any key to exit>')
quit()
