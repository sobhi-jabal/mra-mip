import unittest
import SimpleITK as sitk
import numpy as np
from src.image_processing import remove_background_using_thresholding, process_connected_components

class TestMRAProcessing(unittest.TestCase):
    def setUp(self):
        # Create a simple test image
        self.test_image = sitk.GetImageFromArray(np.random.rand(100, 100))

    def test_remove_background_using_thresholding(self):
        result = remove_background_using_thresholding(sitk.GetArrayFromImage(self.test_image))
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (100, 100))

    def test_process_connected_components(self):
        binary_image = np.random.choice([0, 1], size=(100, 100))
        result = process_connected_components(binary_image)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (100, 100))

if __name__ == '__main__':
    unittest.main()