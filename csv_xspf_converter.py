import os                       # Command line utilities
import csv                      # CSV utilties
from tkinter import filedialog  # Graphical interface
import re                       # Regular expressions
import logging                  # Log file utilities

# TODO: Select multiple CSV files sequentially without having to restart the program (probably needs GUI...)
# TODO: Make export file match export directory chosen by user
# TODO: If there are two artists in the CSV file, only use the first one. Strip characters after comma, UNLESS the single artist has commas in their name...looking at you, Emerson, Lake & Palmer
# TODO: Make whitelist for single artists with commas...
# TODO: Store track titles and album names as literal strings?

# THIS PROGRAM IS IDEALLY USED WITH UNMODIFIED EXPORTIFY CSVs COMBINED WITH DEFAULT SpotDL DOWNLOADED FILES.
# MIXTURES OF FILE FORMATS ARE NOT COMPATIBLE WITH THIS PROGRAM. EVERY PLAYLIST CREATED WITH THIS TOOL MAY ONLY USE ONE FILETYPE.

audio_filetype = ".mp3"

# SOLO ARTIST WITH SPECIAL CHARACTERS IN THEIR NAMES SHOULD BE ENTERED INTO THIS LIST:
special_char_artists = ["""Emerson\, Lake & Palmer""", """The Good\, the Bad & the Queen"""]

def convert_to_xspf():
    
    

    # Remember that computers count from zero...
    # Standard exportify CSV layout is "Track URI","Track Name","Artist URI(s)","Artist Name(s)","Album URI","Album Name","Album Artist URI(s)","Album Artist Name(s)","Album Release Date","Album Image URL","Disc Number","Track Number","Track Duration (ms)","Track Preview URL","Explicit","Popularity","ISRC","Added By","Added At"
    track_column = 1
    artist_column = 3
    album_column = 5

    # Prompts the user to select a CSV file
    csv_file = filedialog.askopenfilename(filetypes=[("Comma Separated Values Source File", "*.csv")], title = "Open your playlist CSV file")

    # Prompts the user to select the directory of music files
    folder = filedialog.askdirectory(title = "Select the location of your music files")

    # Prompts the user to name the playlist and XSPF file and choose the directory
    xspf_file = filedialog.asksaveasfilename(defaultextension=[("XML Shareable Playlist Format", "*.xspf")], filetypes=[("XML Shareable Playlist Format", "*.xspf")], title = "Title your playlist and save your XSPF file")

    # Sets the playlist name to the title of the xspf file
    playlist_name = str(xspf_file).removeprefix(str(folder) + "/")
    playlist_name = playlist_name.removesuffix('.xspf')

    logging.basicConfig(filename="log_" + playlist_name + ".txt", encoding="utf-8", level=logging.DEBUG)
    logging.debug(playlist_name + " creation log:")
    logging.debug("Selected audio filetype: " + audio_filetype)
    logging.info("Selected CSV file: " + csv_file + "\n")
    logging.info("Selected music directory: " + folder + "\n")
    logging.info("Playlist name: " + playlist_name + "\n")
    logging.info("Your XSPF file will be saved as " + xspf_file.removeprefix(str(folder) + "/") + " in " + folder.removesuffix('/') + "\n")


    # Substitutions to be made in prepend output
    file_dict = {'insert_folder' : folder, 'insert_playlist_name' : playlist_name, 'insert_xspf_title' : xspf_file}

    # Before processing the CSV, prepend:
    playlist_prepend = """<?xml version="1.0" encoding="utf-8"?>
    <playlist xmlns="http://xspf.org/ns/0/" xmlns:aimp="http://www.aimp.ru/playlist/ns/0/" version="1">
        <title>{insert_playlist_name}</title>
        <location>"file:///{insert_xspf_title}"</location>
        <trackList>"""

    # Formats the prepend string properly
    playlist_prepend = playlist_prepend.format(**file_dict)

    # after the last line of the CSV has been processed, append:
    playlist_endstop = "\n    </trackList>\n</playlist>"

    track_name = "Example (--Track with /Special/\ Ch*racters...)"
    artist_name = "Example Artist With Spaces In Their Name"
    # album_name = "Album Name...With Spaces and Ellipses!"

    with open(csv_file, 'r', encoding='utf-8') as file:
            csv_data = csv.reader(file, delimiter=',')

            with open(xspf_file, 'w', encoding='utf-8') as file:
                header = next(csv_data)

                file.write(playlist_prepend) # Adds the line to the file

                for row in csv_data:
                    track_name = row[track_column]
                    artist_name = row[artist_column]

                    processed_track_name = track_name
                    processed_track_name = re.sub(" " , "%20", processed_track_name)  # Replace spaces with "%20"
                    processed_track_name = re.sub(""":""" , '-', processed_track_name)   # Replace colons with hyphens
                    processed_track_name = re.sub("""[\\\/*?]""" , '', processed_track_name)   # Remove asterisks, forward slashes, backslashes, question marks
                    print(track_name + " processed to " + processed_track_name)

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
                    

                    track_dict = {'insert_track_name' : track_name, 'insert_artist_name' : artist_name, 'insert_folder' : folder, 'insert_processed_track_name' : processed_track_name, 'insert_processed_artist_name' : processed_artist_name, 'insert_filetype' : audio_filetype }

                    # Write the following to a new line
                    # REMOVED <creator>{insert_artist_name}</creator> due to conflicts between AIMP and Exportify's methods of labeling multiple artists.

                    track_info = """
            <track>
                <location>file:///{insert_folder}/{insert_processed_artist_name}%20-%20{insert_processed_track_name}{insert_filetype}</location>
                <title>{insert_track_name}</title>
            </track>"""

                    track_info = track_info.format(**track_dict)

                    file.write(track_info) # Adds the line to the file
                    log_message_added_track = str("Added track: {insert_track_name} by artist: {insert_artist_name}").format(**track_dict)
                    logging.info(log_message_added_track)
                
                # Ends the playlist properly.
                logging.info("Completing playlist...")
                file.write(playlist_endstop)

convert_to_xspf()