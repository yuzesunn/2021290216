# Code for implementing the methods of the paper: “Low-Resource” Text Classification... on other datasets.

The full title of the paper is “Low-Resource” Text Classification: A Parameter-Free Classification Method with Compressors.

You can check out the paper at Findings of [ACL2023](https://aclanthology.org/2023.findings-acl.426/).

We use the Content-based Fake dataset from this link: [Google Drive](https://drive.google.com/drive/folders/1rLrh5x5UlYskfbhhVyz523MKgmCDyuX2?usp=sharing)

Content-based Fake dataset filename: gossipcop_v3-2_content_based_fake.json

## Getting Started
According to the paper, the codebase is [available on pypi.org via](https://pypi.org/project/npc-gzip):

```sh
pip install npc-gzip
```

## Original Codebase

### Require

See `requirements.txt`.

Install requirements in a clean environment:

```sh
conda create -n npc python=3.7
conda activate npc
pip install -r requirements.txt
```

### Data preprocessing

See `preprocessing.py`.

This will give the results of the two files: `train.txt` and `test.txt`.

Since the `train.txt` was so large that it could not be uploaded here, only `test.txt` was uploaded.

It is important to note that the format of the test file and the train file are the same, an example of which is given below:

```text
real	Teddy apparently has some unfinished Season 14 business at Grey Sloan Memorial...
fake	[On Monday, the day news of pop sensation Justin Bieber's impending marriage to model Hailey Baldwin emerged,...
```

### Run

```sh
python main_text.py --dataset custom --data_dir /path/to/your/data
```

`/path/to/your/data`: You need to provide a directory path that should contain the files `train.txt` and `test.txt`.

The command utilized in this project is:

```sh
python main_text.py --dataset custom --data_dir /my/path/ --class_num 2 --compressor gzip --num_train 500 --num_test 100
```
