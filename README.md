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

### Convert multiple images to a new image format and output destination files in the same directory.
`batchconvert --file [FILE [FILE ...]]] --format 'jpg' .`

### Convert multiple images to a new image format and output destination files in a different directory.
`batchconvert --file [FILE [FILE ...]]] --format 'jpg' FOLDER`

### Convert all images in a folder to a new image format and output the destination files in a different directory
`batchconvert --input [FOLDER] --format 'jpg' FOLDER`

### Resize multiple images to a new image size and output destination files in the same directory.
`batchconvert --file [FILE [FILE ...]]] --resize 3000 2000 .`

### Resize multiple images to a new image size and output destination files in a different directory.
`batchconvert --file [FILE [FILE ...]]] --resize 3000 2000 FOLDER`

### Resize multiple images in a folder to a new image size and output destination files in a different directory.
`batchconvert --input [FOLDER] FOLDER --resize 3000 2000 FOLDER`
