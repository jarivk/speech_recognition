#!/usr/bin/env python3

import os.path
import glob
import argparse
import signal
import sys
import string
import speech_recognition as sr

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

def recognize(speech_file, api='GOOGLE', save_output=False, suffix='', ref='', verbose=False):

    print_error = True
    transcript = ''
    confidence = '0.0'
    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(speech_file) as source:
        audio = r.record(source) # read the entire audio file

    if api == 'SPHINX':
        # recognize speech using Sphinx
        try:
            h = r.recognize_sphinx(audio)
        except sr.UnknownValueError:
            if print_error:
                print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

    elif api == 'GOOGLE':
        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            h = r.recognize_google_cloud(audio, language = "en-US", show_all=True)
            if "results" in h and len(h["results"]) > 0:
                transcript = str(h["results"][0]["alternatives"][0]["transcript"])
                confidence = str(h["results"][0]["alternatives"][0]["confidence"])
        except sr.UnknownValueError:
            if print_error:
                print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    elif api == 'WIT':
        # recognize speech using Wit.ai
        WIT_AI_KEY = "SQRHFJDMWBZNKAKEREESZFYQFUREMBVZ" # Wit.ai keys are 32-character uppercase alphanumeric strings
        try:
            h = r.recognize_wit(audio, key=WIT_AI_KEY, show_all=True)
            if "_text" in h and h["_text"] is not None:
                transcript = str(h["_text"])
        except sr.UnknownValueError:
            if print_error:
                print("Wit.ai could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Wit.ai service; {0}".format(e))

    elif api == 'MICROSOFT':
        # recognize speech using Microsoft Bing Voice Recognition
        BING_KEY = "36305eaa34ea4c6a9584404599c72ef9" # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
        try:
            h = r.recognize_bing(audio, key=BING_KEY, show_all=True)
            if "results" in h and len(h["results"]) > 0:
                transcript = str(h['results'][0]['lexical'])
                confidence = str(h['results'][0]['confidence'])
        except sr.UnknownValueError:
            if print_error:
                print("Microsoft Bing Voice Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))

    elif api == 'HOUNDIFY':
        # recognize speech using Houndify
        HOUNDIFY_CLIENT_ID = "jB6hEAMViS94KjGrrK2MPA==" # Houndify client IDs are Base64-encoded strings
        HOUNDIFY_CLIENT_KEY = "FuuByAvmq4K5GBZk84Mj0VqwxtW5PyGFm3Fq_HacYKt4y69orKyKf3Fcz_Ju4upJpJ0JPhPL1Q9coEeUMvyC-w==" # Houndify client keys are Base64-encoded strings
        try:
            h = r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY, show_all=True)
            if "Disambiguation" in h and h["Disambiguation"] is not None:
                transcript = str(h['Disambiguation']['ChoiceData'][0]['Transcription'])
                confidence = str(h['Disambiguation']['ChoiceData'][0]['ConfidenceScore'])
        except sr.UnknownValueError:
            if print_error:
                print("Houndify could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Houndify service; {0}".format(e))

    elif api == 'IBM':
        # recognize speech using IBM Speech to Text
        IBM_USERNAME = "8fcded2a-0229-4d88-8778-48ce588c5b2e" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
        IBM_PASSWORD = "DYHbw4uzGNmd" # IBM Speech to Text passwords are mixed-case alphanumeric strings
        try:
            h = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD, show_all=True)
            if "results" in h and len(h["results"]) > 0 and "alternatives" in h["results"][0]:
                transcript = str(h['results'][0]['alternatives'][0]['transcript'])
                confidence = str(h['results'][0]['alternatives'][0]['confidence'])
        except sr.UnknownValueError:
            if print_error:
                print("IBM Speech to Text could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from IBM Speech to Text service; {0}".format(e))

    else:
        print("Invalid API specified")

    if save_output:
        trn_fname = os.path.splitext(speech_file)[0] + suffix + '.trn'
        print "Saving transcription to " + trn_fname
        with open(trn_fname, 'w') as f:
            for s in h:
                f.write(s + '\n')
            f.close()

    h = transcript.translate(None, string.punctuation)
    if verbose:
        print('\n' + api + '(h) : ' + str(h.split()))
    if len(ref) > 0:
        if os.path.isfile(ref):
            with open(ref, 'r') as f:
                r = f.readline().rstrip('\n')
                r = r.translate(None, string.punctuation)
                c = wer(r.split(), h.split())
                if verbose:
                    print 'Reference(r) : ' + str(r.split())
                    print "len(h): ", len(h), " ", "len(r): ", len(r), " ", "Missed/Incorrect words: ", c, " ", "Total words: ", len(r.split())
                    print "RESULT: ", speech_file, ', ', '{0:.2f}'.format(float(c)/len(r.split())), ', ' + confidence
    else:
        print(args.input + " : " + h + " : " + confidence)

    return transcript, '{0:.2f}'.format(float(c)/len(r.split())), confidence,


def wer(r, h):
    """
    Calculation of WER with Levenshtein distance.

    Works only for iterables up to 254 elements (uint8).
    O(nm) time ans space complexity.

    Parameters
    ----------
    r : list
    h : list

    Returns
    -------
    int

    Examples
    --------
    >>> wer("who is there".split(), "is there".split())
    1
    >>> wer("who is there".split(), "".split())
    3
    >>> wer("".split(), "who is there".split())
    3
    """
    # initialisation
    import numpy
    d = numpy.zeros((len(r)+1)*(len(h)+1), dtype=numpy.uint8)
    d = d.reshape((len(r)+1, len(h)+1))
    for i in range(len(r)+1):
        for j in range(len(h)+1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            if r[i-1].lower() == h[j-1].lower():
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion    = d[i][j-1] + 1
                deletion     = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    return d[len(r)][len(h)]


# [START run_application]
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input', help='Full path of WAV file to be recognized OR directory containing wav files OR text file containing absolute paths of audio files to be recognized')
    parser.add_argument(
        '-api', help='API used for recognition', choices=['SPHINX', 'GOOGLE', 'WIT', 'MICROSOFT', 'HOUNDIFY', 'IBM', 'ALL'])
    parser.add_argument(
        '-s', '--save', help='Save transcribed text to file. Text file is saved at source location with .trn extension', action="store_true")
    parser.add_argument(
        '-ref', help='Full path of reference transcript text file to compare with OR text file containing absolute paths of referece transcript files')
    parser.add_argument(
        '-suffix', help='Suffix to add to name of transcribed text file (e.g. _google). Applicable only when saving trasnscription to file')
    parser.add_argument(
        '-v', '--verbose', help='Enable verbose logging', action="store_true")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    args = parser.parse_args()

    if args.input == None:
        print

    if args.suffix == None:
        args.suffix = ''

    if args.api == None:
        args.api = ['GOOGLE']
    elif args.api == 'ALL':
        #args.api = ['SPHINX', 'GOOGLE', 'WIT', 'MICROSOFT', 'HOUNDIFY']# 'IBM']
        args.api = ['GOOGLE', 'WIT', 'MICROSOFT']
    else:
        args.api = [args.api]

    if args.suffix == None:
        args.suffix = args.api.tolower()

    if os.path.isfile(args.input):
        if args.input.lower().endswith('.wav'):
            print 'File,', ','.join(map(str, args.api))
            sys.stdout.write(args.input)
            sys.stdout.flush()
            for api in args.api:
                h, wer_result, confidence = recognize(args.input, api, save_output=args.save, suffix=args.suffix, ref=args.ref, verbose=args.verbose)
                if args.verbose == False:
                    sys.stdout.write(', ' + wer_result + ', ' + confidence + '\n')

        elif args.input.lower().endswith('.txt'):
            if args.ref != None:
                try:
                    reflist = open(args.ref, 'r')
                except IOError, e:
                    print sys.stderr, "Failed to open : %s" % e
                    sys.exit(1)

            print 'File,', ','.join(map(str, args.api))
            with open(args.input, 'r') as flist:
                for fname in flist:
                    fname = os.path.expanduser(fname.rstrip())
                    ref_file = ''
                    if args.ref != None:
                        ref_file = os.path.expanduser(reflist.readline().rstrip())
                    sys.stdout.write("File: " + fname)
                    sys.stdout.flush()
                    for api in args.api:
                        h, wer_result, confidence = recognize(fname, api, save_output=args.save, suffix=args.suffix, ref=ref_file, verbose=args.verbose)
                        if args.verbose == False:
                            sys.stdout.write(', ' + wer_result + ', ' + confidence)
                            sys.stdout.flush()
                    sys.stdout.write('\n')
                    sys.stdout.flush()

    elif os.path.isdir(args.input):
        for f in sorted(glob.glob(args.input + '*.wav')):
            print(f)
            for api in args.api:
                h = recognize(f, api, save_output=args.save, suffix=args.suffix)

    # [END run_application]
