## Usage

```
usage: Batch convert [-h] [-r] [--format {jpg,jpeg,png,avi,mp4,wmv,mov}]
                     [--resize LENGTH WIDTH] [--input [FOLDER] | --file
                     [FILE [FILE ...]]]
                     FOLDER

Convert and resize images and video's.

positional arguments:
  FOLDER                                   Output folder

optional arguments:
  -h, --help                               show this help message and exit
  -r                                       Include subfolders
  --format {jpg,jpeg,png,avi,mp4,wmv,mov}  Output format after conversion
  --resize LENGTH WIDTH                    Output image size
  --input [FOLDER]                         Input folder
  --file [FILE [FILE ...]]                 One or more input files
```

## Example usages

#### Show help
`batchconvert -h`

#### Resize images in folder and output destination files to a different directory
`batchconvert --input /home/Pictures --resize 3000 2000 /home/Pictures/new`

#### Resize specific images and output destination files to a different directory
`batchconvert --file /home/Pictures/sun.jpg /home/Pictures/tree.jpg --resize 3000 2000 /home/Pictures/new`

#### Convert images in folder to JPEG and output destination files to a different directory
`batchconvert --input /home/Pictures --format jpg /home/Pictures/new`

#### Convert specific images to JPEG and output destination files to a different directory
`batchconvert --file /home/Pictures/sun.jpg /home/Pictures/tree.jpg --format jpg /home/Pictures/new`

#### Convert *and* resize images in folder to PNG and output destination files to a different directory
`batchconvert --input /home/Pictures --format jpg --resize 4000 3000 /home/Pictures/new`

#### Convert *and* resize videos in folder to MP4 and output destination files to a different directory
`batchconvert --input /home/Videos --format mp4 --resize 400 300 /home/Videos/new`