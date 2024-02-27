# Medical Summarization Prototype
# Matthew Williams

# Library imports
import os
import wave
import time
import threading
import tkinter as tk
from tkinter import ttk
import pyaudio
import openai
from openai import OpenAI

client = None
import whisper
import json

# Voice Recorder Class
class VoiceRecorder:
    
    # Init Components Function
    # This function sets the GUI window layout.
    def __init__(self):
        self.root = tk.Tk()
        # Names window "Medical Summarization Prototype"
        self.root.title("Medical Summarization Prototype")
        self.root.resizable(False, False)
        # Checks for user API key
        # self.superclient = OpenAI(api_key=self.read_api_from_file())

        # Creates label for input audio file
        self.label_input = tk.Label(self.root, text="Audio Input File Name (.MP3 file):")
        # Places label in first row and first column
        self.label_input.grid(row=0, column=0, sticky=tk.W)

        # Creates textfield for input audio file
        self.text_input = tk.Entry(self.root)
        # Pre-populates the field with "Audio.mp3"
        self.text_input.insert(tk.END, "audiofiles/.mp3") 
        # Places textfield in first row and second column
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        # Creates label for output audio file
        self.label_output = tk.Label(self.root, text="Text Output File Name (.TXT file):")
        # Places label in second row and first column
        self.label_output.grid(row=1, column=0, sticky=tk.W)

        # Creates textfield for output audio file
        self.text_output = tk.Entry(self.root)
        # Pre-populates the field with "Audio.txt"
        self.text_output.insert(tk.END, "summaries/.txt") 
        # Places textfield in second row and second column
        self.text_output.grid(row=1, column=1, padx=5, pady=5)

        # Creates label
        self.label_modeltitle = tk.Label(self.root, text="Select Whisper Model:")
        # Places label 
        self.label_modeltitle.grid(row=2, column=0, sticky=tk.W)
        ttk.Separator(self.root, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky='ew')

        # Create a BooleanVar to hold the state of the checkbox
        self.tiny_checkbox_var = tk.BooleanVar(value=False) 
        # Create the checkbox widget
        self.tiny_checkbox = tk.Checkbutton(self.root, text="Tiny", variable=self.tiny_checkbox_var)
        # Places the checkbox beneath the message label 
        self.tiny_checkbox.grid(row=4, column=0, sticky=tk.W)

        # Create a BooleanVar to hold the state of the checkbox
        self.base_checkbox_var = tk.BooleanVar(value=False) 
        # Create the checkbox widget
        self.base_checkbox = tk.Checkbutton(self.root, text="Base", variable=self.base_checkbox_var)
        # Places the checkbox beneath the message label 
        self.base_checkbox.grid(row=4, column=1, sticky=tk.W)

        # Create a BooleanVar to hold the state of the checkbox
        self.small_checkbox_var = tk.BooleanVar(value=False) 
        # Create the checkbox widget
        self.small_checkbox = tk.Checkbutton(self.root, text="Small", variable=self.small_checkbox_var)
        # Places the checkbox beneath the message label 
        self.small_checkbox.grid(row=5, column=0, sticky=tk.W)

        # Create a BooleanVar to hold the state of the checkbox
        self.medium_checkbox_var = tk.BooleanVar(value=False) 
        # Create the checkbox widget
        self.medium_checkbox = tk.Checkbutton(self.root, text="Medium", variable=self.medium_checkbox_var)
        # Places the checkbox beneath the message label
        self.medium_checkbox.grid(row=5, column=1, sticky=tk.W)

        # Create a BooleanVar to hold the state of the checkbox
        self.large_checkbox_var = tk.BooleanVar(value=False) 
        # Create the checkbox widget
        self.large_checkbox = tk.Checkbutton(self.root, text="Large", variable=self.large_checkbox_var)
        # Places the checkbox beneath the message label 
        self.large_checkbox.grid(row=6, column=0, sticky=tk.W)

        # Create a BooleanVar to hold the state of the checkbox
        self.largev2_checkbox_var = tk.BooleanVar(value=True) 
        # Create the checkbox widget
        self.largev2_checkbox = tk.Checkbutton(self.root, text="Large-V2", variable=self.largev2_checkbox_var)
        # Places the checkbox beneath the message label 
        self.largev2_checkbox.grid(row=6, column=1, sticky=tk.W)

        # Creates label
        self.label_processtitle = tk.Label(self.root, text="Select Process:")
        # Places label 
        self.label_processtitle.grid(row=7, column=0, sticky=tk.W)
        ttk.Separator(self.root, orient='horizontal').grid(row=8, column=0, columnspan=3, sticky='ew')
        
        # Create a BooleanVar to hold the state of the checkbox
        self.transcript_checkbox_var = tk.BooleanVar(value=True)  # Set to True to select the checkbox at startup
        # Create the checkbox widget
        self.transcript_checkbox = tk.Checkbutton(self.root, text="Transcribe Speech-To-Text", variable=self.transcript_checkbox_var)
        # Places the checkbox beneath the message label 
        self.transcript_checkbox.grid(row=9, column=0, sticky=tk.W)

        # Create a BooleanVar to hold the state of the checkbox
        self.summary_checkbox_var = tk.BooleanVar(value=False)   # Set to False to deselect the checkbox at startup
        # Create the checkbox widget
        self.summary_checkbox = tk.Checkbutton(self.root, text="Generate Summary Report", variable=self.summary_checkbox_var)
        # Places the checkbox beneath the message label 
        self.summary_checkbox.grid(row=9, column=1, sticky=tk.W)

        # Creates button for transcription
        self.whisper_button = tk.Button(text = "             Start Process             ",
                                        command=self.transcribe_click_handler)
        # Places button
        self.whisper_button.grid(row=10, column=1, sticky=tk.W)

        self.blanklabel = tk.Label(text = " ")
        self.blanklabel.grid(row=11, column=0, columnspan=3)
        ttk.Separator(self.root, orient='horizontal').grid(row=12, column=0, columnspan=3, sticky='ew')

        # Creates label for the microphone button
        self.titlelabel = tk.Label(text="Create/Overwrite Input File Using Microphone")
        # Places label
        self.titlelabel.grid(row=13, column=0, sticky=tk.W)

        # Creates button for microphone
        self.button = tk.Button(text="🎤", font=("Arial", 25, "bold"),
                                command=self.click_handler)
        # Places button
        self.button.grid(row=13, column=1, columnspan=3, pady=10)

        # Creates label for the time
        self.label = tk.Label(text="00:00:00")
        # Places label
        self.label.grid(row=14, column=1, columnspan=3)

        ttk.Separator(self.root, orient='horizontal').grid(row=15, column=0, columnspan=3, sticky='ew')
        # Creates a blank message label (This will be used to relay messages to the user)
        self.msglabel = tk.Label(text=" ")
        # Places label
        self.msglabel.grid(row=16, column=0, columnspan=3)
        
        # Sets recording and exists boolean to false. Recording will signify that the user is currently using their microphone
        # and exists will signify that the information in the textfields correlates to an existing file.
        self.recording = False
        self.exists = False

        # Bind functions to checkboxes' state change events
        self.transcript_checkbox_var.trace("w", self.transcript_checkbox_changed)
        self.summary_checkbox_var.trace("w", self.summary_checkbox_changed)
        self.tiny_checkbox_var.trace("w", self.tiny_checkbox_changed)
        self.base_checkbox_var.trace("w", self.base_checkbox_changed)
        self.small_checkbox_var.trace("w", self.small_checkbox_changed)
        self.medium_checkbox_var.trace("w", self.medium_checkbox_changed)
        self.large_checkbox_var.trace("w", self.large_checkbox_changed)
        self.largev2_checkbox_var.trace("w", self.largev2_checkbox_changed)

        self.read_api_from_file()

        # If there is not a valid API key, the Large-V2 Whisper model and summarization options are disabled
        if self.valid_key == False:
            self.msglabel.config(text="An active OpenAI API key must be provided in a text file called 'api_key.txt'")
            self.largev2_checkbox.config(state="disabled")
            self.summary_checkbox.config(state="disabled")
            self.largev2_checkbox_var.set(False)
            self.base_checkbox_var.set(True)

        # Sets main loop
        self.root.mainloop()

    # Function that takes user OpenAI API key
    def read_api_from_file(self):
        # Read API key from the text file
        try:
            with open(r".venv/api_key.txt", "r") as file:
                api_key = file.read().strip()

                try:
                    # Test call to the OpenAI API to check if the API key works
                    global client
                    client = OpenAI(api_key=api_key)
                    client.models.list()
                    self.valid_key = True
                except openai.AuthenticationError:
                    self.valid_key = False
                    print("Could not authenticate.")
                except openai.RateLimitError:
                    self.valid_key = False
                    print("Rate-limited")
        except FileNotFoundError:
            self.valid_key = False
            print("Could not find the key")

    # Record Click handler function
    # This function is called when the user selects the microphone button.
    def click_handler(self):
        # If recording is true, then the user intends to stop recording so the boolean is set to false which interrupts the thread 
        # and the background color is changed to black.
        if self.recording:
            self.recording = False
            self.button.config(fg = "black")
        # Else, the user intends to start recording so the boolean is set to true, the background color is changed to red, and
        # a new recording Thread is started.
        else:
            self.recording = True
            self.button.config(fg="red")
            threading.Thread(target=self.record).start()

    # Record function
    # This function, with code partially taken from (https://www.youtube.com/watch?v=u_xNvC9PpHA&), records audio from the user.
    def record(self):
        # Gets file path from the text field
        file_path = self.text_input.get()
        # If the file path is of '.mp3" format
        if os.path.splitext(file_path)[1].lower() == '.mp3':
            # If the path also exists, exists is set to true
            if os.path.exists(file_path):
                self.exists = True
            # Disables the transcription button
            self.whisper_button.config(state='disabled')
            # Disables the text_input field
            self.text_input.configure(state='disabled')
            # Disables the text_output field
            self.text_output.configure(state='disabled')
            # Displays a message in the label field telling the user that recording is in progress
            self.msglabel.config(text="Recording in progress...")
            self.transcript_checkbox.config(state="disabled")
            self.summary_checkbox.config(state="disabled")
            self.tiny_checkbox.config(state="disabled")
            self.base_checkbox.config(state="disabled")
            self.small_checkbox.config(state="disabled")
            self.medium_checkbox.config(state="disabled")
            self.large_checkbox.config(state="disabled")
            self.largev2_checkbox.config(state="disabled")

            # Takes audio while the thread is running
            audio = pyaudio.PyAudio()
            # Try block catches errors, such as a lack of a microphone connected or an unexpected issue while recording
            try:
                stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                    input=True, frames_per_buffer=1024)
            except OSError as e:
                if str(e) == "[Errno -9996] Invalid input device (no default output device)":
                    self.msglabel.config(text="Invalid input device. Make sure a microphone is connected.")
                else:
                    self.msglabel.config(text="An error occurred while accessing the audio input.")
                # Stops recording if there is an error
                self.recording = False
                self.button.config(fg = "black")
                audio.terminate()
                # Enable transcription button
                self.whisper_button.config(state='normal')
                # Enable the text_input field
                self.text_input.configure(state='normal')
                # Enable the text_output field
                self.text_output.configure(state='normal')
                self.transcript_checkbox.config(state="normal")
                self.tiny_checkbox.config(state="normal")
                self.base_checkbox.config(state="normal")
                self.small_checkbox.config(state="normal")
                self.medium_checkbox.config(state="normal")
                self.large_checkbox.config(state="normal")
                
                # If there is a valid API key, the large-v2 and summarization buttons are also enabled
                if self.valid_key == True:
                    self.largev2_checkbox.config(state="normal")
                    self.summary_checkbox.config(state="normal")

                self.exists = False
                return

            # For tracking the time of recording
            frames = []
            start = time.time()
            
            # While recording (the thread is running)
            while self.recording:
                data = stream.read(1024)
                frames.append(data)
                passed = time.time() - start
                secs = passed % 60
                mins = passed // 60
                hours = mins // 60
                self.label.config(text=f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")

            # Arrives here when the thread is interrupted (the user selects the record button to stop)
            # Stops audio stream and terminates
            stream.stop_stream()
            stream.close()
            audio.terminate()
            # Enable transcription button
            self.whisper_button.config(state='normal')
            # Enable the text_input field
            self.text_input.configure(state='normal')
            # Enable the text_output field
            self.text_output.configure(state='normal')
            self.transcript_checkbox.config(state="normal")
            self.tiny_checkbox.config(state="normal")
            self.base_checkbox.config(state="normal")
            self.small_checkbox.config(state="normal")
            self.medium_checkbox.config(state="normal")
            self.large_checkbox.config(state="normal")
            # If there is a valid API key, the large-v2 and summarization buttons are also enabled
            if self.valid_key == True:
                self.largev2_checkbox.config(state="normal")
                self.summary_checkbox.config(state="normal")

            # Creates audio file
            input_text = self.text_input.get()
            sound_file = wave.open(input_text, "wb")
            sound_file.setnchannels(1)
            sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            sound_file.setframerate(44100)
            sound_file.writeframes(b"".join(frames))
            sound_file.close()
            # If the audio file already exists
            if self.exists:
                # Tell user that the file was overwritten
                self.msglabel.config(text="'"+ input_text + "' successfully overwritten.")
            # Else
            else:
                # Tell user that the file was created
                self.msglabel.config(text="'"+ input_text + "' successfully created.")
        # Else
        else:
            # Tells the user that the input file is not a .mp3 file
            self.msglabel.config(text="The input file is not a .mp3 file.")
            # Sets recording to false
            self.recording = False
            # Changes record button color back to black
            self.button.config(fg = "black")
        # Reverts exists to False for future record threads
        self.exists = False
    
    # Transcribe Click Handler Function
    def transcribe_click_handler(self):
        # Specify the path to the audio file
        file_path = self.text_input.get()

        # Check if the file exists using os.path.isfile()
        if os.path.exists(file_path):
            # Check if the file extension is '.mp3'
            if os.path.splitext(file_path)[1].lower() == '.mp3':
                # Specify the path to the text file
                text_path = self.text_output.get()
                # Check if the text file ends with '.txt'
                if os.path.splitext(text_path)[1].lower() == '.txt':
                        # If so, start transcription thread
                        threading.Thread(target=self.transcribe_process).start()
                else:
                    # Tell user that the output file must be a .txt file
                    self.msglabel.config(text="The output file must be a .txt file!")
            else:
                # Tell user that the input file is not a .mp3 file
                self.msglabel.config(text="The input file is not a .mp3 file.")
        else:
            # Tell user that the input file does not exist
            self.msglabel.config(text="The input file does not exist!")

    # Transcribe Process Function
    # This function is called when the transcription thread is started
    def transcribe_process(self):
        # Specify the path to the audio file
        file_path = self.text_input.get()
        print(file_path)
        # Tell user that the transcription is starting and that they should not exit the application
        self.msglabel.config(text="Transcribing '"+file_path+"'. Do not exit the application.")
        # Disable the text_input field
        self.text_input.configure(state='disabled')
        # Disable the text_output field
        self.text_output.configure(state='disabled')
        # Disable transcription button
        self.whisper_button.config(state='disabled')
        self.transcript_checkbox.config(state="disabled")
        self.summary_checkbox.config(state="disabled")
        self.tiny_checkbox.config(state="disabled")
        self.base_checkbox.config(state="disabled")
        self.small_checkbox.config(state="disabled")
        self.medium_checkbox.config(state="disabled")
        self.large_checkbox.config(state="disabled")
        self.largev2_checkbox.config(state="disabled")
        # Disable record button
        self.button.config(state='disabled')
        audio_file= open(file_path, "rb")
        transcribe_start = time.time()

        if self.tiny_checkbox_var.get():
            # Sets the Whisper model. The model is set to tiny.
            model = whisper.load_model("tiny")
            # Transcribe the text from the audio (specified by the file_path) and place the string into result
            result = model.transcribe(file_path)
        elif self.base_checkbox_var.get():
            # Sets the Whisper model. The model is set to base.
            model = whisper.load_model("base")
            # Transcribe the text from the audio (specified by the file_path) and place the string into result
            result = model.transcribe(file_path)
        elif self.small_checkbox_var.get():
            # Sets the Whisper model. The model is set to small.
            model = whisper.load_model("small")
            # Transcribe the text from the audio (specified by the file_path) and place the string into result
            result = model.transcribe(file_path)
        elif self.medium_checkbox_var.get():
            # Sets the Whisper model. The model is set to medium.
            model = whisper.load_model("medium")
            # Transcribe the text from the audio (specified by the file_path) and place the string into result
            result = model.transcribe(file_path)
        elif self.large_checkbox_var.get():
            # Sets the Whisper model. The model is set to large.
            model = whisper.load_model("large")
            # Transcribe the text from the audio (specified by the file_path) and place the string into result
            result = model.transcribe(file_path)
        elif self.largev2_checkbox_var.get():
            model = whisper.load_model("large-v2")

            result = model.transcribe(file_path)
        else:
            self.msglabel.config(text="A Whisper model must be selected!")
            self.button.config(state='normal')
            # Enable transcription button
            self.whisper_button.config(state='normal')
            # Enable the text_input field
            self.text_input.configure(state='normal')
            # Enable the text_output field
            self.text_output.configure(state='normal')
            self.transcript_checkbox.config(state="normal")
            self.tiny_checkbox.config(state="normal")
            self.base_checkbox.config(state="normal")
            self.small_checkbox.config(state="normal")
            self.medium_checkbox.config(state="normal")
            self.large_checkbox.config(state="normal")
            # If there is a valid API key, the large-v2 and summarization buttons are also enabled
            if self.valid_key == True:
                self.largev2_checkbox.config(state="normal")
                self.summary_checkbox.config(state="normal")
            return
        transcribe_end = time.time()
        print("Transcription time:", transcribe_end - transcribe_start)
        if self.transcript_checkbox_var.get():
            # Create output file
            output_file = self.text_output.get()
            with open(output_file, 'w') as file:
                # Write the transcribed text to the output file
                file.write(result["text"])
            self.msglabel.config(text="Transcribed text saved to '"+ output_file + "'")
        elif self.summary_checkbox_var.get():
            self.msglabel.config(text="Summarizing '"+file_path+"'. Do not exit the application.")
            self.summarize_transcription(result["text"])
        else:
            self.msglabel.config(text="A task must be selected!")
        # Enable transcription button
        self.whisper_button.config(state='normal')
        # Enable microphone button
        self.button.config(state='normal')
        # Enable the text_input field
        self.text_input.configure(state='normal')
        # Enable the text_output field
        self.text_output.configure(state='normal')
        self.transcript_checkbox.config(state="normal")
        self.tiny_checkbox.config(state="normal")
        self.base_checkbox.config(state="normal")
        self.small_checkbox.config(state="normal")
        self.medium_checkbox.config(state="normal")
        self.large_checkbox.config(state="normal")
        # If there is a valid API key, the large-v2 and summarization buttons are also enabled
        if self.valid_key == True:
            self.largev2_checkbox.config(state="normal")
            self.summary_checkbox.config(state="normal")

    # The following functions handle the checkbox radio buttons
    def transcript_checkbox_changed(self, *args):
        if self.transcript_checkbox_var.get():
            # Deselect the summary checkbox
            self.summary_checkbox_var.set(False)
        
    def summary_checkbox_changed(self, *args):
        if self.summary_checkbox_var.get():
            # Deselect the transcript checkbox
            self.transcript_checkbox_var.set(False)
    
    def tiny_checkbox_changed(self, *args):
        if self.tiny_checkbox_var.get():
            # Deselect the other checkboxs
            self.base_checkbox_var.set(False)
            self.small_checkbox_var.set(False)
            self.medium_checkbox_var.set(False)
            self.large_checkbox_var.set(False)
            self.largev2_checkbox_var.set(False)
    
    def base_checkbox_changed(self, *args):
        if self.base_checkbox_var.get():
            # Deselect the other checkboxs
            self.tiny_checkbox_var.set(False)
            self.small_checkbox_var.set(False)
            self.medium_checkbox_var.set(False)
            self.large_checkbox_var.set(False)
            self.largev2_checkbox_var.set(False)

    def small_checkbox_changed(self, *args):
        if self.small_checkbox_var.get():
            # Deselect the other checkboxs
            self.base_checkbox_var.set(False)
            self.tiny_checkbox_var.set(False)
            self.medium_checkbox_var.set(False)
            self.large_checkbox_var.set(False)
            self.largev2_checkbox_var.set(False)

    def medium_checkbox_changed(self, *args):
        if self.medium_checkbox_var.get():
            # Deselect the other checkboxs
            self.base_checkbox_var.set(False)
            self.small_checkbox_var.set(False)
            self.tiny_checkbox_var.set(False)
            self.large_checkbox_var.set(False)
            self.largev2_checkbox_var.set(False)

    def large_checkbox_changed(self, *args):
        if self.large_checkbox_var.get():
            # Deselect the other checkboxs
            self.base_checkbox_var.set(False)
            self.small_checkbox_var.set(False)
            self.medium_checkbox_var.set(False)
            self.tiny_checkbox_var.set(False)
            self.largev2_checkbox_var.set(False)
    
    def largev2_checkbox_changed(self, *args):
        if self.largev2_checkbox_var.get():
            # Deselect the other checkboxs
            self.base_checkbox_var.set(False)
            self.small_checkbox_var.set(False)
            self.medium_checkbox_var.set(False)
            self.large_checkbox_var.set(False)
            self.tiny_checkbox_var.set(False)

    # Summarize Transcription Function
    # The following function makes a call to the GPT-3.5-Turbo API with a summarization prompt. Takes audio transcript in as parameter.
    def summarize_transcription(self, transcript):
        # Completes a chat simulation, utilizes the audio transcript
        summarize_start = time.time()
        completion = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an attentive note-keeper."},
            {"role": "user", "content": "Pretend that you are an insurance provider and you need to summarize an interview between patient and provider. Please create the summary using the format “SUBJECTIVE, MEDICATIONS, ALLERGIES, FAMILY HISTORY, LIFESTYLE HISTORY, OBJECTIVE, HEENT, ASSESSMENT,  PLAN.” Each category gets its own new line. After you read the interview that I will provide you with, you will write a paragraph for subjective, and a few sentences each for medications (anything that the patient currently takes that is over-the-counter or prescribed), allergies, family history, lifestyle history (alcohol/tobacco/other drug use), objective (The patient’s physical characteristics, this field is not to be left blank and you must say that there is no information if there truly is none), heent, assessment, and a numbered list for plan. (HEENT stands for HEAD, EYES, EARS, NOSE, and THROAT but present it as HEENT in the response. This category pertains to abnormal symptoms pertaining to these body parts, such as sore throat, headache, runny nose, earache, pink eye, etc.) Please provide a summary based solely on the information given in the interview. Do not include any additional tests or procedures that were not mentioned by the doctor."},
            {"role": "assistant", "content": "Understood. Please provide the transcript of the fake interview, and I will proceed to generate the summary as per the specified format."},
            {"role": "user", "content": transcript},
        ])
        # Recieves the summarizaed text from the chat simulation
        summarized_text = completion.choices[0].message.content
        summarize_end = time.time() - summarize_start
        print(summarize_end)
        # Create output file
        output_file = self.text_output.get()
        with open(output_file, 'w') as file:
            # Write the transcribed text to the output file
            file.write(summarized_text)
        # Tell user that summarized text has been saved to the output file.
        self.msglabel.config(text="Summarized text saved to '"+ output_file + "'")

# Start Voice Recorder Class
VoiceRecorder()