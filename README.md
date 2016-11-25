## Usage

```
Starting execution.
usage: Batch convert [-h] [-r]
                     [--format {jpg,jpeg,png} | --resize LENGTH WIDTH]
                     [--input [FOLDER] | --file [FILE [FILE ...]]]
                     FOLDER

Convert and resize images and video's.

positional arguments:
  FOLDER                    Output folder

optional arguments:
  -h, --help                show this help message and exit
  -r                        Include subfolders
  --format {jpg,jpeg,png}   Output format after conversion
  --resize LENGTH WIDTH     Output image size
  --input [FOLDER]          Input folder
  --file [FILE [FILE ...]]  One or more input files
```

## Example usages

#### Show help
`batchconvert -h`

#### Resize images in folder and output destination files to a different directory
`batchconvert --input /home/pc/Pictures --resize 3000 2000 /home/pc/Pictures/converted`

#### Resize specific images and output destination files to a different directory
`batchconvert --file /home/pc/Pictures/sun.jpg /home/pc/Pictures/tree.jpg --resize 3000 2000 /home/pc/Pictures/converted`

#### Convert images in folder to JPEG and output destination files to a different directory
`batchconvert --input /home/pc/Pictures --format jpg /home/pc/Pictures/converted`

#### Convert specific images to JPEG and output destination files to a different directory
`batchconvert --file /home/pc/Pictures/sun.jpg /home/pc/Pictures/tree.jpg --format jpg /home/pc/Pictures/converted`