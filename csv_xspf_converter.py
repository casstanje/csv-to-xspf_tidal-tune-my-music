import os                       # Command line utilities
import csv                      # CSV utilties
from tkinter import filedialog  # Graphical interface
import re                       # Regular expressions
import logging                  # Log file utilities

# WORKS WITH TIDAL LIBRARY EXPORTED FROM TUNEMYMUSIC

def convert_to_xspf():
    # Remember that computers count from zero...
    track_column = 0
    artist_column = 1
    album_column = 2
    tidal_id_column = 6
    playlist_name_column = 3

    # Prompts the user to select a CSV file
    csv_file = filedialog.askopenfilename(filetypes=[("Comma Separated Values Source File", "*.csv")], title = "Open your playlist CSV file")

    # Prompts the user to choose the folder to place the playlist
    folder = filedialog.askdirectory(title = "Select where you would like to place your playlists")

    logging.basicConfig(filename=folder+"/log_" + "csv_to_xspf" + ".txt", encoding="utf-8", level=logging.DEBUG)
    logging.debug("creation log:")

    # after the last line of the CSV has been processed, append:
    playlist_endstop = "\n    </trackList>\n</playlist>"

    track_name = "Example (--Track with /Special/ Ch*racters...)"
    artist_name = "Example Artist With Spaces In Their Name"
    album_name = "Album Name...With Spaces and Ellipses!"

    prev_playlist = "wow, haha (just a value that no album is probably named... i hope)"
    playlist_count = 0
    playlist_prepend = ""
    file_name = ""

    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_data = csv.reader(file, delimiter=',')
        header = next(csv_data)
        for row in csv_data:
            # Set metadata values
            track_name = row[track_column]
            artist_name = row[artist_column]
            album_name = row[album_column]
            playlist_name = row[playlist_name_column]

            # Start creation of new playlist if playlist name of current song is different from previous playlist
            new_playlist = playlist_name != prev_playlist
            if new_playlist:
                if file_name != "":
                    # End the previous playlist before starting the new one
                    with open(file_name, 'a', encoding='utf-8') as file:
                        # Ends the playlist properly.
                        logging.info("Completing playlist...")
                        file.write(playlist_endstop)    
                logging.info("Selected CSV file: " + csv_file + "\n")
                logging.info("Playlist name: " + playlist_name + "\n")
                playlist_count += 1
                file_name = folder + "/playlist_" + str(playlist_count) + ".xspf"
                prev_playlist = playlist_name

                # Before processing the CSV, prepend:
                playlist_prepend = """<?xml version="1.0" encoding="utf-8"?>
                <playlist xmlns="http://xspf.org/ns/0/" xmlns:aimp="http://www.aimp.ru/playlist/ns/0/" version="1">
                <title>""" + playlist_name +  """</title>
                <location>""" + "\"" + folder + "/" + file_name +  "\"" + """</location>
                <trackList>"""
            with open(file_name, 'a', encoding='utf-8') as file:

                # Prepend the text from earlier if new playlist
                if new_playlist:
                    file.write(playlist_prepend) # Adds the line to the file

                # Replace all & (ampersands) with 'And'
                track_name = re.sub("&" , "And", track_name)
                artist_name = re.sub("&" , "And", artist_name)
                album_name = re.sub("&" , "And", album_name)

                tidal_url = "tidal:" + str(row[tidal_id_column])
                track_dict = {'insert_track_name' : track_name, 'insert_artist_name' : artist_name, 'insert_album_name' : album_name, 'insert_tidal_url' : tidal_url }

                # Write the following to a new line

                track_info = """
                <track>
                    <location>{insert_tidal_url}</location>
                    <title>{insert_track_name}</title>
                    <creator>{insert_artist_name}</creator>
                    <album>{insert_album_name}</album>
                </track>"""

                track_info = track_info.format(**track_dict)

                file.write(track_info) # Adds the line to the file
                print("Added track: " + track_name + " to " + playlist_name)
                log_message_added_track = str("Added track: {insert_track_name} by artist: {insert_artist_name}").format(**track_dict)
                logging.info(log_message_added_track)   
        #End the last playlist when all songs have been processed
        with open(file_name, 'a', encoding='utf-8') as file:
            # Ends the playlist properly.
            logging.info("Completing playlist...")
            file.write(playlist_endstop)    

convert_to_xspf()