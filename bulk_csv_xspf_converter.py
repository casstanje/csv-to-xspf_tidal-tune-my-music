import os                       # Command line utilities
import csv                      # CSV utilties
from tkinter import filedialog  # Graphical interface
import re                       # Regular expressions
import logging                  # Log file utilities

# TODO: Store track titles and album names as literal strings?
# TODO: Fix duplicates by creating a list of track title + artist + album and searching each new entry in the list to see if it's already represented. If so, skip the entry instead of making a duplicate.

# THIS PROGRAM IS IDEALLY USED WITH A DIRECTORY OF UNMODIFIED EXPORTIFY CSVs COMBINED WITH DEFAULT SpotDL DOWNLOADED FILES.
# MIXTURES OF FILE FORMATS ARE NOT COMPATIBLE WITH THIS PROGRAM.
# EVERY PLAYLIST CREATED WITH THIS TOOL MAY ONLY USE ONE AUDIO FILETYPE.

# AUDIO FILETYPE (MODIFY STRING IF YOUR FILES ARE ANY OTHER FORMAT.)
audio_filetype = ".mp3"

# SOLO ARTIST WITH SPECIAL CHARACTERS IN THEIR NAMES SHOULD BE ENTERED INTO THIS LIST:
special_char_artists = ["""Emerson\, Lake & Palmer""", """The Good\, the Bad & the Queen"""]

# Remember that computers count from zero...
# Standard exportify CSV layout is "Track URI","Track Name","Artist URI(s)","Artist Name(s)","Album URI","Album Name","Album Artist URI(s)","Album Artist Name(s)","Album Release Date","Album Image URL","Disc Number","Track Number","Track Duration (ms)","Track Preview URL","Explicit","Popularity","ISRC","Added By","Added At"
track_column = 1
artist_column = 3
album_column = 5


def bulk_convert():

    logging.basicConfig(filename="bulk_log.txt", encoding="utf-8", level=logging.DEBUG)

    # Prompts the user to select the directory of CSV files
    bulk_origin_folder = filedialog.askdirectory(title = "Select the location of your CSV files to bulk convert.")
    bulk_origin_folder = bulk_origin_folder + "/"
    logging.debug("Starting bulk convert of " + bulk_origin_folder + "\n")

    # Prompts the user to select the directory of XSPF files
    bulk_destination_folder = filedialog.askdirectory(title = "Select the location to save your XSPF playlists to.")
    bulk_destination_folder = bulk_destination_folder + "/"
    logging.debug("XSPFs will be saved to " + bulk_destination_folder + "\n")

    # Prompts the user to select the directory of music files
    music_folder = filedialog.askdirectory(title = "Select the location of your music files")
    logging.info("Selected music directory: " + music_folder + "\n")
    logging.debug("Selected audio filetype: " + audio_filetype + "\n")


    for filename in os.listdir(bulk_origin_folder):
        if filename.endswith(".csv"):

            csv_entry = filename
            xspf_definition = csv_entry.removesuffix(".csv")
            xspf_definition = re.sub("_", " ", xspf_definition)

            # Sets the playlist name to that of the xspf BEFORE all the directory stuff gets added.
            playlist_name = xspf_definition

            xspf_definition = xspf_definition + ".xspf"
            print("PROCESSING PLAYLIST: " + csv_entry + " INTO " + xspf_definition)
            logging.debug("PROCESSING PLAYLIST: " + csv_entry + " INTO " + xspf_definition)
            xspf_definition = bulk_destination_folder + xspf_definition

            # Before processing the CSV, prepend:
            file_dict = {'insert_playlist_name' : playlist_name, 'insert_xspf_title' : xspf_definition}
            playlist_prepend = """<?xml version="1.0" encoding="utf-8"?>
            <playlist xmlns="http://xspf.org/ns/0/" xmlns:aimp="http://www.aimp.ru/playlist/ns/0/" version="1">
                <title>{insert_playlist_name}</title>
                <location>"file:///{insert_xspf_title}"</location>
                <trackList>"""
            # Formats the prepend string properly
            playlist_prepend = playlist_prepend.format(**file_dict)

            # after the last line of the CSV has been processed, append:
            playlist_endstop = "\n    </trackList>\n</playlist>"

            with open(bulk_origin_folder + csv_entry, 'r', encoding='utf-8') as file:
                    csv_data = csv.reader(file, delimiter=',')

                    with open(xspf_definition, 'w', encoding='utf-8') as file:
                        header = next(csv_data)

                        file.write(playlist_prepend) # Adds the line to the file

                        for row in csv_data:
                            track_name = row[track_column]
                            artist_name = row[artist_column]

                            processed_track_name = track_name
                            processed_track_name = re.sub(" " , "%20", processed_track_name)  # Replace spaces with "%20"
                            processed_track_name = re.sub(":" , '-', processed_track_name)   # Replace colons with hyphens
                            processed_track_name = re.sub(r'""' , "'", processed_track_name)   # Replace "" with '
                            processed_track_name = re.sub(r'"' , "'", processed_track_name)   # Replace " with '
                            processed_track_name = re.sub("""[\\\/*?]""" , '', processed_track_name)   # Remove asterisks, forward slashes, backslashes, question marks
                            # print(track_name + " processed to " + processed_track_name)

                            artist_comma_location = artist_name.find(",")
                            artist_name_length = len(artist_name)

                            if artist_comma_location >= 1:
                                if artist_name in special_char_artists:
                                    processed_artist_name = artist_name
                                    # logging.info("The name " + artist_name + " IS in the list of formatting exceptions and will be preserved.")
                                else:
                                    processed_artist_name = artist_name[:(artist_comma_location):] # Removes the comma and all characters after it.
                                    # logging.warning("The name " + artist_name + " is NOT in the list of formatting exceptions. It will be formatted to " + processed_artist_name)

                            elif artist_comma_location == 0:
                                logging.warning("The program thinks this artist's name begins with a comma. Check CSV formatting.")
                                processed_artist_name = artist_name
                            
                            else:
                                processed_artist_name = artist_name
                            
                            processed_artist_name = re.sub(" " , "%20", processed_artist_name)    # Replace spaces with "%20"
                            processed_artist_name = re.sub(":" , '-', processed_artist_name)   # Replace colons with hyphens
                            processed_artist_name = re.sub(r'""' , "'", processed_artist_name)   # Replace "" with '
                            processed_artist_name = re.sub(r'"' , "'", processed_artist_name)   # Replace " with '
                            processed_artist_name = re.sub("""[\\\/*?]""" , '', processed_artist_name)   # Remove asterisks, forward slashes, backslashes, question marks
                            

                            track_dict = {'insert_track_name' : track_name, 'insert_artist_name' : artist_name, 'insert_music_folder' : music_folder, 'insert_processed_track_name' : processed_track_name, 'insert_processed_artist_name' : processed_artist_name, 'insert_filetype' : audio_filetype }

                            # Write the following to a new line
                            track_info = """
                    <track>
                        <location>file:///{insert_music_folder}/{insert_processed_artist_name}%20-%20{insert_processed_track_name}{insert_filetype}</location>
                        <title>{insert_track_name}</title>
                    </track>"""

                            track_info = track_info.format(**track_dict)
                            file.write(track_info) # Adds the line to the file
                            log_message_added_track = str("Added track: {insert_track_name} by artist: {insert_artist_name}").format(**track_dict)
                            # logging.info(log_message_added_track)
                        
                        # Ends the playlist properly.
                        logging.info("COMPLETING PLAYLIST: " + playlist_name)
                        print("COMPLETING PLAYLIST: " + playlist_name)
                        file.write(playlist_endstop)

        else:
            continue


bulk_convert()