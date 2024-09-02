# MRA MIP

## Introduction
This project downloads a chest MRA DICOM, separate vasculature through thresholding, and generates a rotating maximum intensity projection (MIP).

## Setup

### Option 1: Using pip

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mra-mip.git
   cd mra-mip
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Option 2: Using Docker

1. Build the Docker image:
   ```
   docker build -t mra-mip .
   ```

2. Run the Docker container:
   ```
   docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output mra-mip
   ```

### Command Line Interface

Execute the Python script to perform the MRA MIP generation task:

```bash
python src/mra_mip.py --input-file "/path/to/dicom/file" --output-dir "/path/to/output"
```

or

```bash
python src/mra_mip.py --input-dir "/path/to/dicom/directory" --output-dir "/path/to/output"
```


## Files Generated

The script generates three files:

1. `example.nii.gz` - The original DICOM images converted to nifti format.
2. `masked_image.nii.gz` - The nifti images after applying the thresholding to remove the background.
3. `rotational_mip.nii.gz` - The nifti file containing the rotating MIP.
4. `rotating_mip.gif` - A GIF animation of the rotating MIP.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.