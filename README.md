# Music File Validator

A Python tool designed to validate and analyze MP3 files in bulk. This tool helps identify potential issues in audio files by checking playability, detecting audio quality problems, and generating comprehensive reports.

## 🌟 Features

- **File Validation**
  - Checks if MP3 files are playable
  - Validates file format and structure
  - Examines audio metadata

- **Audio Analysis**
  - Detects audio clipping issues
  - Identifies silent segments
  - Analyzes audio quality metrics

- **Reporting**
  - Generates detailed Excel reports
  - Includes file-by-file analysis
  - Provides summary statistics

- **User Experience**
  - Progress bar for processing status
  - Colorized console output
  - Detailed error messages
  - Supports batch processing

## 📋 Requirements

- Python 3.7 or higher
- FFmpeg (included in executable version)
- Required Python packages:
  ```
  mutagen
  pydub
  pandas
  numpy
  openpyxl
  tqdm
  ```

## 🚀 Installation

### Using Released Executable

1. Download `check_music_validity.exe` from the [latest release](https://github.com/Astraaaaaaa/test-music-validity/releases)
2. Run directly - no installation needed!

### Building from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/Astraaaaaaa/test-music-validity.git
   cd test-music-validity
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Build executable:
   ```bash
   pyinstaller test-music-validity.py --onefile --icon=icon.ico --name=check_music_validity
   ```

## 💻 Usage

### Command Line Interface

Basic usage:
```bash
python test-music-validity.py --input "path/to/music/folder" --output "report.xlsx"
```

Or with executable:
```bash
check_music_validity.exe --input "path/to/music/folder" --output "report.xlsx"
```

### Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `--input` | Input folder path | Yes | - |
| `--output` | Output Excel file | No | report.xlsx |

## 📊 Output Report

The Excel report includes:

| Column | Description |
|--------|-------------|
| File Name | Name of the MP3 file |
| File Path | Full path to the file |
| Playable | Whether the file can be played |
| Duration (s) | Length of the audio in seconds |
| Clipping Count | Number of detected clipping instances |
| Silent Segments | Number of silent segments detected |
| Bitrate | Audio bitrate in kbps |
| Sample Rate | Sample rate in Hz |
| Error Message | Any errors encountered during analysis |

## 🔍 Example Output

```
Processing files: 100%|██████████| 50/50 [00:30<00:00, 1.67file/s]
Summary Report:
Total files processed: 50
Playable files: 48
Files with clipping: 3
Unplayable files: 2

Report saved to: report.xlsx
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [pydub](https://github.com/jiaaro/pydub) for audio processing
- [mutagen](https://github.com/quodlibet/mutagen) for MP3 metadata handling
- [pandas](https://pandas.pydata.org/) for data processing
- [FFmpeg](https://ffmpeg.org/) for audio file handling

## 📧 Contact

Astra - astralee95@gmail.com

Project Link: [https://github.com/Astraaaaaaa/test-music-validity](https://github.com/Astraaaaaaa/test-music-validity)

## 🔄 Version History

- v1.0.0
  - Initial release
  - Basic MP3 validation features
  - Excel report generation