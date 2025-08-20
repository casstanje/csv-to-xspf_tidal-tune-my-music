import os                       # Command line utilities
import csv                      # CSV utilties
from tkinter import filedialog  # Graphical interface
import re                       # Regular expressions
import logging                  # Log file utilities

# WORKS WITH TIDAL LIBRARY EXPORTED FROM TUNEMYMUSIC


audio_filetype = ".mp3"

# SOLO ARTIST WITH SPECIAL CHARACTERS IN THEIR NAMES SHOULD BE ENTERED INTO THIS LIST:
special_char_artists = ["""Emerson\, Lake & Palmer""", """The Good\, the Bad & the Queen"""]

def convert_to_xspf():
    
    

    # Remember that computers count from zero...
    # Standard exportify CSV layout is "Track URI","Track Name","Artist URI(s)","Artist Name(s)","Album URI","Album Name","Album Artist URI(s)","Album Artist Name(s)","Album Release Date","Album Image URL","Disc Number","Track Number","Track Duration (ms)","Track Preview URL","Explicit","Popularity","ISRC","Added By","Added At"
    track_column = 0
    artist_column = 1
    album_column = 2
    tidal_id_column = 6
    playlist_name_column = 3

    # Prompts the user to select a CSV file
    csv_file = filedialog.askopenfilename(filetypes=[("Comma Separated Values Source File", "*.csv")], title = "Open your playlist CSV file")

    # Prompts the user to name the playlist and XSPF file and choose the directory
    folder = filedialog.askdirectory(title = "Select the location of your music files")

    logging.basicConfig(filename="log_" + "wow" + ".txt", encoding="utf-8", level=logging.DEBUG)
    logging.debug("wow" + " creation log:")
    logging.debug("Selected audio filetype: " + audio_filetype)
    logging.info("Selected CSV file: " + csv_file + "\n")
    logging.info("Playlist name: " + "wow" + "\n")


    # Substitutions to be made in prepend output
    file_dict = {'insert_folder' : folder, 'insert_playlist_name' : "wow", 'insert_xspf_title' : "wow2"}





    # after the last line of the CSV has been processed, append:
    playlist_endstop = "\n    </trackList>\n</playlist>"

    track_name = "Example (--Track with /Special/\ Ch*racters...)"
    artist_name = "Example Artist With Spaces In Their Name"
    album_name = "Album Name...With Spaces and Ellipses!"

    prev_playlist = "wow, haha"
    playlist_count = 0
    playlist_prepend = ""
    file_name = ""

    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_data = csv.reader(file, delimiter=',')
        header = next(csv_data)
        for row in csv_data:
            track_name = row[track_column]
            artist_name = row[artist_column]
            album_name = row[album_column]
            playlist_name = row[playlist_name_column]
            new_playlist = playlist_name != prev_playlist
            if new_playlist:
                if file_name != "":
                    with open(file_name, 'a', encoding='utf-8') as file:
                        # Ends the playlist properly.
                        logging.info("Completing playlist...")
                        file.write(playlist_endstop)    
                playlist_count += 1
                file_name = "playlist_" + str(playlist_count) + ".xspf"
                prev_playlist = playlist_name
                # Before processing the CSV, prepend:
                playlist_prepend = """<?xml version="1.0" encoding="utf-8"?>
                <playlist xmlns="http://xspf.org/ns/0/" xmlns:aimp="http://www.aimp.ru/playlist/ns/0/" version="1">
                <title>""" + playlist_name +  """</title>
                <location>""" + "\"" + folder + "/" + file_name +  "\"" + """</location>
                <trackList>"""

                # Formats the prepend string properly
                playlist_prepend = playlist_prepend.format(**file_dict)
            with open(file_name, 'a', encoding='utf-8') as file:

                if new_playlist:
                    file.write(playlist_prepend) # Adds the line to the file

                processed_track_name = track_name
                processed_track_name = re.sub(" " , "%20", processed_track_name)  # Replace spaces with "%20"
                processed_track_name = re.sub(""":""" , '-', processed_track_name)   # Replace colons with hyphens
                processed_track_name = re.sub("""[\\\/*?]""" , '', processed_track_name)   # Remove asterisks, forward slashes, backslashes, question marks
                print(track_name + " processed to " + processed_track_name)

                track_name = re.sub("&" , "And", track_name)
                artist_name = re.sub("&" , "And", artist_name)
                album_name = re.sub("&" , "And", album_name)

                artist_comma_location = artist_name.find(",")
                artist_name_length = len(artist_name)

                if artist_comma_location >= 1:
                    if artist_name in special_char_artists:
                        processed_artist_name = artist_name
                        logging.info("The name " + artist_name + " IS in the list of formatting exceptions and will be preserved.")
                    else:
                        processed_artist_name = artist_name[:(artist_comma_location):] # Removes the comma and all characters after it.
                        logging.warning("The name " + artist_name + " is NOT in the list of formatting exceptions. It will be formatted to " + processed_artist_name)

                elif artist_comma_location == 0:
                    logging.warning("The program thinks this artist's name begins with a comma. Check CSV formatting.")
                    processed_artist_name = artist_name
                
                else:
                    processed_artist_name = artist_name
                
                processed_artist_name = re.sub(" " , "%20", processed_artist_name)    # Replace spaces with "%20"
                processed_artist_name = re.sub(""":""" , '-', processed_artist_name)   # Replace colons with hyphens
                processed_artist_name = re.sub("""[\\\/*?]""" , '', processed_artist_name)   # Remove asterisks, forward slashes, backslashes, question marks
                
                tidal_url = "tidal:" + str(row[tidal_id_column])
                track_dict = {'insert_track_name' : track_name, 'insert_artist_name' : artist_name, 'insert_album_name' : album_name, 'insert_folder' : folder, 'insert_processed_track_name' : processed_track_name, 'insert_processed_artist_name' : processed_artist_name, 'insert_filetype' : audio_filetype, 'insert_tidal_url' : tidal_url }

                # Write the following to a new line
                # REMOVED <creator>{insert_artist_name}</creator> due to conflicts between AIMP and Exportify's methods of labeling multiple artists.

                track_info = """
                <track>
                    <location>{insert_tidal_url}</location>
                    <title>{insert_track_name}</title>
                    <creator>{insert_artist_name}</creator>
                    <album>{insert_album_name}</album>
                </track>"""

                track_info = track_info.format(**track_dict)

                file.write(track_info) # Adds the line to the file
                log_message_added_track = str("Added track: {insert_track_name} by artist: {insert_artist_name}").format(**track_dict)
                logging.info(log_message_added_track)   
        with open(file_name, 'a', encoding='utf-8') as file:
            # Ends the playlist properly.
            logging.info("Completing playlist...")
            file.write(playlist_endstop)    

convert_to_xspf()