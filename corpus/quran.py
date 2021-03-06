from tqdm import tqdm
from pathlib import Path
from os.path import join, getsize
from joblib import Parallel, delayed
from torch.utils.data import Dataset
from os import getcwd

# Additional (official) text src provided
#OFFICIAL_TXT_SRC = ['librispeech-lm-norm.txt']
# Remove longest N sentence in librispeech-lm-norm.txt
#REMOVE_TOP_N_TXT = 5000000
# Default num. of threads used for loading LibriSpeech
#READ_FILE_THREADS = 4


class QuranDataset(Dataset):
    def __init__(self, path, split, tokenizer, bucket_size, ascending=False):
        # Setup
        self.path = path
        self.bucket_size = bucket_size

        # List all wave files
        file_list = []
        for s in split:
            with open(getcwd()+ '/data/'+s+'/src.txt') as f:
                split_list = f.readlines()
                split_list = [x.replace('\n', '') for x in split_list]
            file_list += split_list

        # Read text
        text = []
        for s in split:
            with open(getcwd()+ '/data/'+s+'/tgt.txt') as f:
                split_text = f.readlines()
                split_text = [x.replace('\n', '') for x in split_text]
            text += split_text
        #text = Parallel(n_jobs=-1)(delayed(tokenizer.encode)(txt) for txt in text)
        text = [tokenizer.encode(txt) for txt in text]

        # Sort dataset by text length
        #file_len = Parallel(n_jobs=READ_FILE_THREADS)(delayed(getsize)(f) for f in file_list)
        self.file_list, self.text = zip(*[(f_name, txt)
                                          for f_name, txt in sorted(zip(file_list, text), reverse=not ascending, key=lambda x:len(x[1]))])

    def __getitem__(self, index):
        if self.bucket_size > 1:
            # Return a bucket
            index = min(len(self.file_list)-self.bucket_size, index)
            return [(f_path, txt) for f_path, txt in
                    zip(self.file_list[index:index+self.bucket_size], self.text[index:index+self.bucket_size])]
        else:
            return self.file_list[index], self.text[index]

    def __len__(self):
        return len(self.file_list)


class QuranTextDataset(Dataset):
    def __init__(self, path, split, tokenizer, bucket_size):
        # Setup
        self.path = path
        self.bucket_size = bucket_size
        self.encode_on_fly = False
        read_txt_src = []

        # List all wave files
        file_list, all_sent = [], []

        file_list = []
        for s in split:
            with open(getcwd()+'/data/'+s+'/src.txt') as f:
                split_list = f.readlines()
                split_list = [x.replace('\n', '') for x in split_list]
            file_list += split_list

        # Read text

        text = []
        for s in split:
            with open(getcwd()+'/data/'+s+'/tgt.txt') as f:
                split_text = f.readlines()
                split_text = [x.replace('\n', '') for x in split_text]
            text += split_text
        all_sent.extend(text)
        del text

        # Encode text
        if self.encode_on_fly:
            self.tokenizer = tokenizer
            self.text = all_sent
        else:
            self.text = [tokenizer.encode(txt) for txt in tqdm(all_sent)]
        del all_sent

        # Read file size and sort dataset by file size (Note: feature len. may be different)
        self.text = sorted(self.text, reverse=True, key=lambda x: len(x))
        #if self.encode_on_fly:
        #    del self.text[:REMOVE_TOP_N_TXT]

    def __getitem__(self, index):
        if self.bucket_size > 1:
            index = min(len(self.text)-self.bucket_size, index)
            if self.encode_on_fly:
                for i in range(index, index+self.bucket_size):
                    if type(self.text[i]) is str:
                        self.text[i] = self.tokenizer.encode(self.text[i])
            # Return a bucket
            return self.text[index:index+self.bucket_size]
        else:
            if self.encode_on_fly and type(self.text[index]) is str:
                self.text[index] = self.tokenizer.encode(self.text[index])
            return self.text[index]

    def __len__(self):
        return len(self.text)
