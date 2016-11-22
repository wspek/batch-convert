## Usage

```
batchconvert [-h] [-r]
             [--format {jpg,jpeg,nef,mp4} | --resize LENGTH WIDTH]
             [--input [FOLDER] | --file [FILE [FILE ...]]]
             FOLDER

Convert and resize images and video's.

positional arguments:
  FOLDER                       Output folder

optional arguments:
  -h, --help                   show this help message and exit
  -r                           Include subfolders
  --format {jpg,jpeg,nef,mp4}  Output format after conversion
  --resize LENGTH WIDTH        Output image size
  --input [FOLDER]             Input folder
  --file [FILE [FILE ...]]     One or more input files`
```

### Show help
`batchconvert -h`

### Resize images in folder to new image size and output destination files in a different directory.
`batchconvert --input [FOLDER] --resize 3000 2000 FOLDER`
