import os
from pathlib import Path
import SimpleITK as sitk
from src.image_processing import mask_image, get_rotational_MIP, create_rotating_gif
from src.download_utils import download_from_url

def main(input_file=None, input_dir=None, output_dir='output'):
    if input_dir:
        input_dir = Path(input_dir)
        dicom_files = list(input_dir.glob('*.dcm'))
        if not dicom_files:
            print(f"No DICOM files found in {input_dir}. Attempting to download...")
            download_from_url("https://physionet.org/files/images/1.0.0/", str(input_dir))
            dicom_files = list(input_dir.glob('*.dcm'))
            if not dicom_files:
                raise ValueError(f"No DICOM files found in {input_dir} after download attempt.")
        image = sitk.ReadImage(str(dicom_files[0]))
    elif input_file:
        image = sitk.ReadImage(input_file)
    else:
        raise ValueError("Either input_file or input_dir must be provided.")

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    sitk.WriteImage(image, str(output_dir / "example.nii.gz"))
    print(f"Nifti image saved to {str(output_dir / 'example.nii.gz')}")

    print("Thresholding and masking image")
    masked_image = mask_image(image)
    sitk.WriteImage(masked_image, str(output_dir / "masked_image.nii.gz"))
    print(f"Masked image saved to {str(output_dir / 'masked_image.nii.gz')}")

    print("Computing rotational MIP")
    rotational_mip, mip_images = get_rotational_MIP(masked_image)
    nifti_path = str(output_dir / 'rotational_mip.nii.gz')
    sitk.WriteImage(rotational_mip, nifti_path)
    print(f"Rotational MIP saved to {nifti_path}")

    print("Creating rotating GIF")
    gif_path = str(output_dir / 'rotating_mip.gif')
    create_rotating_gif(mip_images, gif_path)
    print(f"Rotating GIF saved to {gif_path}")

    return nifti_path, gif_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str, help="Path to input DICOM file")
    parser.add_argument("--input-dir", type=str, help="Path to directory containing DICOM files")
    parser.add_argument("--output-dir", type=str, default="output", help="Path to output directory")
    args = parser.parse_args()
    
    main(input_file=args.input_file, input_dir=args.input_dir, output_dir=args.output_dir)