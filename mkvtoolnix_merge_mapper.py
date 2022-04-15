import json
from json import JSONDecoder
import os
from os.path import exists
import subprocess

#set up config variables
mkv_merge_path = ''
options_filename = ''
config_filename = 'mkvconfig.json'
titles_filename = ''
mkvtitles_filename = ''
ep_var_name = ''
out_folder = ''

#default config
default_config = {
"options_filename":"options.json",
"titles_filename":"titles.txt",
"mkvtitles_filename":"mkvtitles.txt",
"ep_var_name":"EPNUM",
"out_folder":"mkvmerge_out",
"mkv_merge_path":"C:\\Program Files\\MKVToolNix\\mkvmerge.exe"
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
    #looks up and assigns config values
    options_filename = config['options_filename']
    titles_filename = config['titles_filename']
    mkvtitles_filename = config['mkvtitles_filename']
    ep_var_name = config['ep_var_name']
    out_folder = config['out_folder']
    mkv_merge_path = config['mkv_merge_path']
else:
    print('Config file was not found. Using defaults.')
    config = dict(default_config)
    options_filename = config['options_filename']
    titles_filename = config['titles_filename']
    mkvtitles_filename = config['mkvtitles_filename']
    ep_var_name = config['ep_var_name']
    out_folder = config['out_folder']
    mkv_merge_path = config['mkv_merge_path']

#checks if crucial files exist
if not exists(mkv_merge_path):
    print('mkvmerge was not found at given path')
    input('<press enter>')
    quit()

if not exists(options_filename):
    print('options file was not found')
    input('<press enter>')
    quit()

print('Would you like to mux titles to mkv?')
titles_mux_q = input()
if titles_mux_q.lower() == "yes" or titles_mux_q.lower() == "y":
    print("I'll take that as a yes.")
    titles_mux_q = True
else:
    print("I'll take that as a no.")
    titles_mux_q = False

if titles_mux_q == True:
    print('\nWould you like to add episode number to mkv title?')
    titles_mux_ep_q = input()
    if titles_mux_ep_q.lower() == "yes" or titles_mux_ep_q.lower() == "y":
        print("I'll take that as a yes.")
        titles_mux_ep_q = True
    else:
        print("I'll take that as a no.")
        titles_mux_ep_q = False
    
print('\nWould you like to add titles to filename?')
titles_filename_q = input()
if titles_filename_q.lower() == "yes" or titles_filename_q.lower() == "y":
    print("I'll take that as a yes.")
    titles_filename_q = True
else:
    print("I'll take that as a no.")
    titles_filename_q = False

#checks if a text file containing titles exists
if titles_mux_q == True or titles_filename_q == True:
    if not exists(mkvtitles_filename) and not exists(titles_filename):
        print('\nCould not find titles.json or titles.txt')
        print("Will continue without including titles.")
        titles_mux_q = False
        titles_mux_ep_q = False
        titles_filename_q = False
    if exists(titles_filename):
        titles = open(titles_filename, 'r')
        titles_data = [line.strip() for line in titles]
    if exists(mkvtitles_filename):
        mkvtitles = open(mkvtitles_filename, 'r')
        mkvtitles_data = [line.strip() for line in mkvtitles]

#asks for range of episodes to mux
print('\nStart Episode:')
start_episode = input()

print('\nEnd Episode:')
end_episode = input()

#loads options file
with open(options_filename) as json_file:
    options_data = json.load(json_file)

ep_num = int(start_episode)

while ep_num < int(end_episode)+1:
    options_data_temp = []
    options_data_temp += options_data

    #reads titles for given episode
    if titles_filename_q == True or titles_mux_q == True:
        title = titles_data[ep_num - 1]
        if exists(mkvtitles_filename):
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
            options_data_temp[i + 1] = full_path[:pos] + out_folder + "\\" + full_path[pos:]
            
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
            else:
                options_data_temp[i + 1] = ""


    #add all attachments in folder 
    for i, v in enumerate(options_data_temp):  
        if v == "inode/directory":
            attachment_dir = options_data_temp[i+2]
            for root, dirs, files in os.walk(attachment_dir):
                for file in files:
                    if file.endswith('.otf'):
                        #print(os.path.join(root, file))
                        options_data_temp.append("--attachment-name")
                        options_data_temp.append(file[:-4])
                        options_data_temp.append("--attachment-mime-type")
                        options_data_temp.append("font/otf")
                        options_data_temp.append("--attach-file")
                        options_data_temp.append(os.path.join(root, file))
                    if file.endswith('.ttf'):
                        #print(os.path.join(root, file))
                        options_data_temp.append("--attachment-name")
                        options_data_temp.append(file[:-4])
                        options_data_temp.append("--attachment-mime-type")
                        options_data_temp.append("font/ttf")
                        options_data_temp.append("--attach-file")
                        options_data_temp.append(os.path.join(root, file))
                    if file.endswith('.jpg'):
                        #print(os.path.join(root, file))
                        options_data_temp.append("--attachment-name")
                        options_data_temp.append(file[:-4])
                        options_data_temp.append("--attachment-mime-type")
                        options_data_temp.append("image/jpeg")
                        options_data_temp.append("--attach-file")
                        options_data_temp.append(os.path.join(root, file))
                    if file.endswith('.jpeg'):
                        #print(os.path.join(root, file))
                        options_data_temp.append("--attachment-name")
                        options_data_temp.append(file[:-5])
                        options_data_temp.append("--attachment-mime-type")
                        options_data_temp.append("image/jpeg")
                        options_data_temp.append("--attach-file")
                        options_data_temp.append(os.path.join(root, file))
                    if file.endswith('.png'):
                        #print(os.path.join(root, file))
                        options_data_temp.append("--attachment-name")
                        options_data_temp.append(file[:-4])
                        options_data_temp.append("--attachment-mime-type")
                        options_data_temp.append("image/png")
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
        if title_muxed == True:
            print("\nMKV title was muxed successfully!")
        else:
            print("\nFailed to mux MKV title.")

    call_arguments = [mkv_merge_path] + options_data_temp
    
    print('Starting Episode (' + str(ep_num) + '/' + str(int(end_episode)) + ') ---------------')
    subprocess.call(call_arguments)
    print('Finished Processing ----------------')
    ep_num += 1

print('\n\nAll files have been processed.')
input('<press any key to exit>')
quit()
