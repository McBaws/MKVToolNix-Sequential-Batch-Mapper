import json
from json import JSONDecoder
import os
from os.path import exists
import subprocess
import zlib
import shutil
import datetime
import re
from colorama import Fore, init
init(convert=True)

#set up config variables
config_filename = 'mkvconfig.json'

#default config
default_config = {
"mkv_toolnix_path":"C:\\Program Files\\MKVToolNix",

"out_folder":"mkvmerge_out",
"ep_var_name":"EPNUM",
"title_var_name":"EPTITLE",
"mkvtitle_var_name":"MKVTITLE",
"crc_var_name":"CRC",

"options_filename":"options.json",
"titles_filename":"titles.txt",
"mkvtitles_filename":"mkvtitles.txt",

"auto_font_mux":"",
"font_collector_log":"no",
"additional_fonts_folder":"",

"titles_in_filename":"",
"titles_in_mkv":"",
"title_separator":" - ",

"skip_mux":"",
"skip_episodes":[],

"CRC_buffer":8192
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

mkv_toolnix_path = config['mkv_toolnix_path']
mkv_merge_path = os.path.join(mkv_toolnix_path, "mkvmerge.exe")
mkv_extract_path = os.path.join(mkv_toolnix_path, "mkvextract.exe")
mkv_propedit_path = os.path.join(mkv_toolnix_path, "mkvpropedit.exe")
mkv_info_path = os.path.join(mkv_toolnix_path, "mkvinfo.exe")

out_folder = config['out_folder']
ep_var_name = config['ep_var_name']
title_var_name = config['title_var_name']
mkvtitle_var_name = config['mkvtitle_var_name']
crc_var_name = config['crc_var_name']

options_filename = config['options_filename']
titles_filename = config['titles_filename']
mkvtitles_filename = config['mkvtitles_filename']

auto_font_q = config['auto_font_mux']
font_collector_log = config['font_collector_log']
additional_fonts_folder = config['additional_fonts_folder']

titles_filename_q = config['titles_in_filename']
titles_mux_q = config['titles_in_mkv']
title_separator = config['title_separator']

skip_mux = config["skip_mux"]
skip_episodes = config["skip_episodes"]

CRC_buffer = config["CRC_buffer"]

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
    titles_filename_q = False
if exists(titles_filename):
    with open(titles_filename) as titles:
        titles_data = [line.strip() for line in titles]
    titles_found = True
if exists(mkvtitles_filename):
    with open(mkvtitles_filename) as mkvtitles:
        mkvtitles_data = [line.strip() for line in mkvtitles]
    mkvtitles_found = True

#asks whether user wants to include titles
if titles_found or mkvtitles_found:
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



#asks for range of episodes to mux
print('\n\nEpisode Ranges:   (eg: 1:2,4,6:24)')

ep_ranges_in = input()
ep_ranges_in = ep_ranges_in.split(",")
ep_ranges = []

for range, i in ep_ranges_in:
    if "-" in range:
        r = range.split("-")
        for n in range(r[0], r[1]+1):
            ep_ranges.append(n)
    else:
        ep_ranges.append(int(range))


#loads options file
with open(options_filename) as json_file:
    options_data = json.load(json_file)

first_ep = True

for ep_num in ep_ranges:
    options_data_temp = []
    options_data_temp += options_data

    if skip_episodes:
        if ep_num in skip_episodes:
            continue

    #reads titles for given episode
    if titles_filename_q == True or titles_mux_q == True:
        if titles_found and mkvtitles_found:
            title = titles_data[ep_num - 1]
            mkvtitle = mkvtitles_data[ep_num - 1]
        elif titles_found:
            title = titles_data[ep_num - 1]
            mkvtitle = titles_data[ep_num - 1]
        elif mkvtitles_found:
            title = mkvtitles_data[ep_num - 1]
            mkvtitle = mkvtitles_data[ep_num - 1]
        title_muxed = False

    #appends a 0 to numbers under 10
    if ep_num < 10:
        ep_string = '0' + str(ep_num)
    else:
        ep_string = str(ep_num)


    #if title variable isn't present, searches for episode variable and places the title after its last occurence
    if titles_filename_q == True:
        for i, v in enumerate(options_data_temp):
            if options_data_temp[i - 1] == '--output' and title_var_name not in v and mkvtitle_var_name not in v:
                full_path = v

                #how a version number (v2, v3) affects title placement
                ver_calc = False
                #regex to find ver num
                for m in re.finditer("v\d{1,}", v):
                    ver_start = m.start()
                    ver_end = m.end()
                    #check if ver num comes after episode number, but not more than 2 indexes after episode number
                    if ver_start > v.rindex(ep_var_name):
                        if ep_var_name + "MOD(" in v:
                            if ver_start - v.find(")", v.rindex(ep_var_name + "MOD(")) < 3:
                                ver_calc = True
                                break
                        elif ver_start - (v.rindex(ep_var_name)+len(ep_var_name)) < 3:
                            ver_calc = True
                            break

                #place title
                if ver_calc:
                    options_data_temp[i] = full_path[:ver_end] + title_separator + title + full_path[ver_end:]
                elif ep_var_name + "MOD(" in v:
                    if v.rindex(ep_var_name + "MOD(") != v.index(ep_var_name + "MOD("):
                        ep_num_pos = v.rindex(ep_var_name + "MOD(")
                        c_brack_pos = v.find(")", ep_num_pos) + 1
                        options_data_temp[i] = full_path[:c_brack_pos] + title_separator + title + full_path[c_brack_pos:]
                    elif v.rindex(ep_var_name) != v.index(ep_var_name + "MOD("):
                        title_pos = v.rindex(ep_var_name) + len(ep_var_name)
                        options_data_temp[i] = full_path[:title_pos] + title_separator + title + full_path[title_pos:]
                    else:
                        ep_num_pos = v.index(ep_var_name + "MOD(")
                        c_brack_pos = v.find(")", ep_num_pos) + 1
                        options_data_temp[i] = full_path[:c_brack_pos] + title_separator + title + full_path[c_brack_pos:]
                elif ep_var_name in v:
                    if v.rindex(ep_var_name) != v.index(ep_var_name):
                        title_pos = v.rindex(ep_var_name) + len(ep_var_name)
                        options_data_temp[i] = full_path[:title_pos] + title_separator + title + full_path[title_pos:]
                    else:
                        title_pos = v.index(ep_var_name) + len(ep_var_name)
                        options_data_temp[i] = full_path[:title_pos] + title_separator + title + full_path[title_pos:]


    for i, v in enumerate(options_data_temp):

        #replaces episode variable with modified episode number
        while ep_var_name + "MOD(" in options_data_temp[i]:
            #finds ep var + mod() in order to get modifier in brackets
            ep_num_pos = options_data_temp[i].index(ep_var_name + "MOD(")
            o_brack_pos = ep_num_pos + len(ep_var_name) + 3
            c_brack_pos = options_data_temp[i].find(")", ep_num_pos)
            entire_ep_var = options_data_temp[i][ep_num_pos:c_brack_pos+1]
            try:
                modder = int(options_data_temp[i][o_brack_pos+1:c_brack_pos])
            except:
                print("make sure episode number modifier is a number")
            new_ep_num = ep_num + modder
            if new_ep_num < 0:
                raise Exception("episode number modifier returns negative number")
            if new_ep_num < 10:
                new_ep_string = "0" + str(new_ep_num)
            else:
                new_ep_string = str(new_ep_num)
            options_data_temp[i] = options_data_temp[i].replace(entire_ep_var, new_ep_string)

        #replaces episode variable with episode number
        if ep_var_name in v:
            options_data_temp[i] = options_data_temp[i].replace(ep_var_name, ep_string)

        #create output folder and redirect output to it
        if v == '--output':
            full_path = options_data_temp[i + 1]
            pos = options_data_temp[i + 1].rindex("\\") + 1
            if out_folder:
                options_data_temp[i + 1] = os.path.join(full_path[:pos], out_folder, full_path[pos:])
            else:
                options_data_temp[i + 1] = full_path
            
        #replaces title variable with title
        if title_var_name in v or mkvtitle_var_name in v:
            if titles_filename_q and not options_data_temp[i - 1] == '--title':
                options_data_temp[i] = options_data_temp[i].replace(title_var_name, title)
                options_data_temp[i] = options_data_temp[i].replace(mkvtitle_var_name, mkvtitle)

        #if --title is in options file, mux mkvtitle. if mkvtitle_name_var is in title, replace it. otherwise the whole title is replaced.
        var_found = False
        if options_data_temp[i - 1] == '--title':
            if titles_mux_q == True:
                if mkvtitle_var_name in v:
                    options_data_temp[i] = options_data_temp[i].replace(mkvtitle_var_name, mkvtitle)
                    var_found = True
                if title_var_name in v:
                    if titles_found:
                        options_data_temp[i] = options_data_temp[i].replace(title_var_name, title)
                    else:
                        options_data_temp[i] = options_data_temp[i].replace(title_var_name, mkvtitle)
                    var_found = True
                if not var_found:
                    options_data_temp[i] = mkvtitle
                title_muxed = True
            else:
                options_data_temp[i] = ""
                title_muxed = True

        if "***" in options_data_temp[i]:
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

        if "**" in options_data_temp[i]:
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

    #check if CRC in output filename, get final output filepath
    for i, v in enumerate(options_data_temp):
        if v == '--output':
            if crc_var_name in options_data_temp[i + 1]:
                CRC_calc = True
            else:
                CRC_calc = False
            output_file = options_data_temp[i + 1]

    #add all attachments in folder
    placeholder_exists = True
    while placeholder_exists:
        for i, v in enumerate(options_data_temp):  
            if v == "batch/attachment":
                attachment_dir = os.path.dirname(options_data_temp[i+2])
                for root, dirs, files in os.walk(attachment_dir):
                    for file in files:
                        options_data_temp.append("--attach-file")
                        options_data_temp.append(os.path.join(root, file))

                #remove placeholder attachment
                del(options_data_temp[i+2])
                del(options_data_temp[i+1])
                del(options_data_temp[i])
                del(options_data_temp[i-1])
                del(options_data_temp[i-2])
                del(options_data_temp[i-3])
                break

        if "batch/attachment" not in options_data_temp:
            placeholder_exists = False


    #muxes mkvtitle if --title is NOT in options file
    if titles_mux_q == True:
        if title_muxed == False:
            options_data_temp.append('--title')
            options_data_temp.append(mkvtitle)
            title_muxed = True

    #call mkvmerge
    print('Starting Episode (' + str(ep_num) + '/' + str(len(ep_ranges)) + ') ---------------')
    if not skip_mux:
        subprocess.call([mkv_merge_path] + options_data_temp)

    if auto_font_q:
        print("\nAutomatically muxing required fonts...")

        print("Extracting subtitle files...")

        #output mkvinfo for output file to a temp directory, then read it
        temp_dir = os.path.join(os.path.dirname(output_file), "mkvtemp")
        x=2
        while exists(temp_dir):
            temp_dir = os.path.join(os.path.dirname(output_file), "mkvtemp" + str(x))
            x+=1

        mkvinfo_output_file = os.path.join(temp_dir, "mkvinfo.txt")
        subprocess.call([mkv_info_path] + [output_file] + ["--redirect-output"] + [mkvinfo_output_file], stdout=subprocess.DEVNULL)
        with open(mkvinfo_output_file, encoding='utf-8', errors='ignore') as mkvinfo:
            mkvinfo_data = [line.strip() for line in mkvinfo]

        #get track ids of all ass files
        trackid = []
        for i, v in enumerate(mkvinfo_data):
            if v == "|  + Codec ID: S_TEXT/ASS":
                for x in range(0,1000):
                    if "Track number" in mkvinfo_data[i-x]:
                        trackid.append(int(re.findall(r'\d+', mkvinfo_data[i-x])[-1]))
                        break

        #extract all subtitle files from output mkv
        extract_args = ["tracks"]
        for i in range(0, len(trackid)):
            extract_args.append(str(trackid[i]) + ":" + os.path.join(temp_dir, "extracted sub " + str(trackid[i]) + ".ass"))
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
            extract_args.append(str(aid[i][0]) + ":" + os.path.join(temp_dir, aid[i][1]))
        subprocess.call([mkv_extract_path] + [output_file] + extract_args, stdout=subprocess.DEVNULL)
        print("   Done.")

        if font_collector_log:
            print("Copying extracted fonts to folder...", end="")
            extract_args = ["attachments"]
            for i in range(0, len(aid)):
                extract_args.append(str(aid[i][0]) + ":" + os.path.join(os.path.dirname(output_file), "Fonts", aid[i][1]))
            subprocess.call([mkv_extract_path] + [output_file] + extract_args, stdout=subprocess.DEVNULL)
            print("   Done.")


        #make log file if log is enabled
        if font_collector_log:
            print("\nLogging...")
            if first_ep:
                log_path = os.path.join(os.path.dirname(output_file), "Fonts", "!fc - " + datetime.datetime.now().strftime("%Y.%m.%d %H-%M-%S") + ".log")
                if not exists(os.path.dirname(log_path)):
                    os.mkdir(os.path.dirname(log_path))
                with open(log_path, "w") as log:
                    log.write("\nEpisode " + ep_string + ":\n")
            else:
                with open(log_path, "a") as log:
                    log.write("\nEpisode " + ep_string + ":\n")

        #detect all ass files in folder
        fontcollector_args = []
        print("\nFinding necessary fonts and muxing...")
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".ass"):
                    fontcollector_args.append(os.path.join(root, file))

        missing_fonts = 0

        #run fontcollector and mux all needed fonts
        if not font_collector_log:
            with subprocess.Popen(["fontcollector", "-mkv", output_file, "-d", "-mkvpropedit", mkv_propedit_path, "--additional-fonts", temp_dir] + additional_fonts_folder + ["--input"] + fontcollector_args, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True) as p:
                for line in p.stderr:
                    if "All fonts found" in line:
                        print(f"{Fore.GREEN}", line, f"{Fore.RESET}", end="")
                    elif "fonts could not be found" in line:
                        missing_fonts += int(re.findall(r'\d+', line)[0])
                        print(f"{Fore.RED}", line, f"{Fore.RESET}", end="")
                    else:
                        print(line, end="")

        #same but with log
        else:
            with open(log_path, "a") as log:
                with subprocess.Popen(["fontcollector", "-mkv", output_file, "-d", "-mkvpropedit", mkv_propedit_path, "--additional-fonts", temp_dir] + additional_fonts_folder + ["--input"] + fontcollector_args, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True) as p:
                    for line in p.stderr:
                        log.write(line)
                        if "All fonts found" in line:
                            print(f"{Fore.GREEN}", line, f"{Fore.RESET}", end="")
                        elif "fonts could not be found" in line:
                            missing_fonts += int(re.findall(r'\d+', line)[0])
                            print(f"{Fore.RED}", line, f"{Fore.RESET}", end="")
                        else:
                            print(line, end="")
                log.write("\n")

        #outputs how many fonts were found missing
        if not font_collector_log:
            if missing_fonts == 0:
                print(f"\n{Fore.GREEN}All fonts were found and muxed! :){Fore.RESET}")
            elif missing_fonts == 1:
                print(f"\n{Fore.RED}1 font was not found! :({Fore.RESET}")
            elif missing_fonts > 1:
                print(f"\n{Fore.RED}At least {missing_fonts} fonts were not found! :({Fore.RESET}")

        #same but with log
        else:
            with open(log_path, "a") as log:
                if missing_fonts == 0:
                    log.write(f"All fonts were found and muxed! :)")
                elif missing_fonts == 1:
                    log.write(f"1 font was not found! :(")
                elif missing_fonts > 1:
                    log.write(f"At least {missing_fonts} fonts were not found! :(")


        #remove temp dir
        shutil.rmtree(temp_dir)

    if CRC_calc and exists(output_file):
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
        os.rename(output_file, output_file.replace(crc_var_name, crcstr))

    print('\nFinished Processing ----------------')
    first_ep = False

print('\n\nAll files have been processed.')
quit()
