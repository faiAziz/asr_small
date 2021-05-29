import os
import shutil
import json
from sklearn.model_selection import train_test_split as split
import copy
import re

# traininng Data

path = os.getcwd()

audio_path = path+'/audio/'
json_path = path+'/surah/'
text_path = path

json_files = [x for x in os.listdir(json_path) if x.endswith('.json')]

mapping = {
    '\u0621' : 'A',   ## HAMZA
    '\u0622' : 'A' ,  ## ALEF WITH MADDA ABOVE
    '\u0623' : 'A',   ## ALEF WITH HAMZA ABOVE
    '\u0624' : 'A',   ## WAW WITH HAMZA ABOVE
    '\u0625' : 'A',   ## ALEF WITH HAMZA BELOW
    '\u0626' : 'A',   ## YEH WITH HAMZA ABOVE
    '\u0627' : 'A',    ## ALEF
    '\u0628' : 'b',    ## BEH
    '\u0629' : 'p',    ## TEH MARBUTA
    '\u062A' : 't',     ## TEH
    '\u062B' : 'v',     ## THEH
    '\u062C' : 'j',     ## JEEM
    '\u062D' : 'H',     ## HAH
    '\u062E' : 'x',     ## KHAH
    '\u062F' : 'd',     ## DAL
    '\u0630' : 'TH',    ## THAL
    '\u0631' : 'r',     ## REH
    '\u0632' : 'z',     ## ZAIN
    '\u0633' : 's',     ## SEEN
    '\u0634' : 'SH',    ## SHEEN
    '\u0635' : 'S',     ## SAD
    '\u0636' : 'D',     ## DAD
    '\u0637' : 'T',     ## TAH
    '\u0638' : 'Z',     ## ZAH
    '\u0639' : 'E',     ## AIN
    '\u063A' : 'g',     ## GHAIN
    #'\u0640' : '_',     ## TATWEEL
    '\u0641' : 'f',     ## FEH
    '\u0642' : 'q',     ## QAF
    '\u0643' : 'k',     ## KAF
    '\u0644' : 'l',     ## LAM
    '\u0645' : 'm',     ## MEEM
    '\u0646' : 'n',     ## NOON
    '\u0647' : 'h',     ## HEH
    '\u0648' : 'w',     ## WAW
    '\u0649' : 'Y',     ## ALEF MAKSURA
    '\u064A' : 'y',     ## YEH

    ## Diacritics
    #'\u064B' : 'F',     ## FATHATAN
    #'\u064C' : 'N',     ## DAMMATAN
    #'\u064D' : 'K',     ## KASRATAN
    #'\u064E' : 'a',     ## FATHA
    #'\u064F' : 'u',     ## DAMMA
    #'\u0650' : 'i',     ## KASRA
    #'\u0651' : '\~',    ## SHADDA
    #'\u0652' : 'o',     ## SUKUN
    #'\u0670' : 'A',    ## SUPERSCRIPT ALEF

    '\u0671' : 'A',    ## ALEF WASLA
    '\u067E' : 'P',     ## PEH
    '\u0686' : 'J',     ## TCHEH
    '\u06A4' : 'V',     ## VEH
    '\u06AF' : 'G',     ## GAF
}


alef = [
    '\u0656', #subscript alef
    '\u0670', #superscript alef
    '\uFB50', #alef wasla isolated form
    '\u0671', #alef wasla
    '\u0622', #alef with madda above
    '\u0623' #alef with hamza above
    #'\u0649' #alef maksura
]

def pad (x):
    x = str(x)
    if len(x) == 1 :
        return '00'+x
    elif len(x) == 2 :
        return '0'+x
    else:
        return x

def replace_alef (x):
    for a in alef:
        x = x.replace(a, '\u0627')
    return x

patt = '[\u0621-\u064A ]+'

def clean_text (x):
    return "".join(re.findall(patt, x))

def to_eng (x):
    for key, val in mapping.items():
        x = x.replace(key, val)
    return x

tgt = []
src = []

for json_file in json_files:
    with open(json_path + json_file) as surah:
        surah_num = str(json_file).split('.')[0]
        x = json.load(surah)
        num_ayah = x['count']
        ayahs = [x['verse']['verse_'+str(k)] for k in range(1, num_ayah+1)] #ignore bismillah
        ayahs = [to_eng(clean_text(replace_alef(x))) for x in ayahs]
        tgt.extend(ayahs)

        ayah_paths = [audio_path+ surah_num+'/'+pad(x)+'.mp3' for x in range(1, num_ayah+1)]
        src.extend(ayah_paths)

audio_train, audio_dev, text_train, text_dev = split(src, tgt, random_state=42, shuffle=True, test_size=0.2)

with open(text_path + '/tgt.txt', 'w') as tgt_file:
    for row in tgt:
        tgt_file.write("%s\n" % row)

with open(text_path + '/src.txt', 'w') as tgt_file:
    for row in src:
        tgt_file.write("%s\n" % row)


with open (path+'/train1/src.txt', 'w') as f:
    for l in audio_train:
        f.write(l+'\n')

with open (path+'/train1/tgt.txt', 'w') as f:
    for l in text_train:
        f.write(l+'\n')

with open (path+'/dev/src.txt', 'w') as f:
    for l in audio_dev:
        f.write(l+'\n')

with open (path+'/dev/tgt.txt', 'w') as f:
    for l in text_dev:
        f.write(l+'\n')
