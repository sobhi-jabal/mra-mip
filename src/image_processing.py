import numpy as np
from scipy import ndimage as ndi
import SimpleITK as sitk
from skimage import filters, feature, segmentation
from tqdm import tqdm
import imageio
import itertools

def remove_background_using_thresholding(img):
    center_coords1 = np.array([img.shape[0] // 2, img.shape[1] // 3])
    center_coords2 = np.array([img.shape[0] - 1, img.shape[1] // 2])
    center_mask = np.zeros_like(img, dtype=bool)
    center_radius = 200
    y_indices, x_indices = np.indices(img.shape)
    center_mask1 = ((y_indices - center_coords1[0])**2 + (x_indices - center_coords1[1])**2) <= center_radius**2
    center_mask2 = ((y_indices - center_coords2[0])**2 + (x_indices - center_coords2[1])**2) <= center_radius**2
    center_mask = np.logical_or(center_mask1, center_mask2)
    distance_map = ndi.distance_transform_edt(~center_mask)
    scaled_distance_map = (distance_map / distance_map.max()) ** 2 * img.max()
    img_adjusted = np.clip(img - scaled_distance_map, 0, None)
    thresh = filters.threshold_otsu(img_adjusted)
    binary = img_adjusted > thresh
    return binary

def process_connected_components(binary):
    labeled_img, num_features = ndi.label(binary)
    center_coords = np.array(binary.shape) / 2
    for i in range(1, num_features + 1):
        component_mask = (labeled_img == i)
        centroid = np.array(ndi.center_of_mass(component_mask))
        distance = np.linalg.norm(center_coords - centroid)
        if distance > 350:
            binary[component_mask] = 0
    return binary

def process_distance_transform(binary):
    distance = ndi.distance_transform_edt(binary)
    coords = feature.peak_local_max(distance, min_distance=1, labels=binary)
    mask = np.zeros_like(binary)
    mask[tuple(coords.T)] = True
    markers, _ = ndi.label(mask)
    labels = segmentation.watershed(-distance, markers, mask=binary)
    return labels, binary

def mask_image(image):
    masked_array = []
    for slice in sitk.GetArrayFromImage(image):
        binary = remove_background_using_thresholding(slice)
        binary = process_connected_components(binary)
        _, binary = process_distance_transform(binary)
        masked_slice = slice * binary
        masked_array.append(masked_slice)
    masked_array = np.stack(masked_array)
    return sitk.GetImageFromArray(masked_array)

def rotation3d(image, theta_x, theta_y, theta_z, output_spacing=None, background_value=0.0):
    euler_transform = sitk.Euler3DTransform(image.TransformContinuousIndexToPhysicalPoint([(sz-1)/2.0 for sz in image.GetSize()]), 
                                            np.deg2rad(theta_x), 
                                            np.deg2rad(theta_y), 
                                            np.deg2rad(theta_z))
    max_indexes = [sz-1 for sz in image.GetSize()]
    extreme_indexes = list(itertools.product(*(list(zip([0]*image.GetDimension(),max_indexes)))))
    extreme_points_transformed = [euler_transform.TransformPoint(image.TransformContinuousIndexToPhysicalPoint(p)) for p in extreme_indexes]
    output_min_coordinates = np.min(extreme_points_transformed, axis=0)
    output_max_coordinates = np.max(extreme_points_transformed, axis=0)
    if output_spacing is None:
        output_spacing = min(image.GetSpacing())
    output_spacing = [output_spacing]*image.GetDimension()  
    output_origin = output_min_coordinates
    output_size = [int(((omx-omn)/ospc)+0.5) for ospc, omn, omx in zip(output_spacing, output_min_coordinates, output_max_coordinates)]
    output_direction = [1,0,0,0,1,0,0,0,1]
    output_pixeltype = image.GetPixelIDValue()
    resampled_image = sitk.Resample(image, 
                        output_size, 
                        euler_transform.GetInverse(), 
                        sitk.sitkLinear, 
                        output_origin,
                        output_spacing,
                        output_direction,
                        background_value,
                        output_pixeltype)
    return resampled_image

def createMIP(image, slices_num):
    np_img = sitk.GetArrayFromImage(image)
    img_shape = np_img.shape
    np_mip = np.zeros(img_shape)
    for i in range(img_shape[0]):
        start = max(0, i-slices_num)
        np_mip[i,:,:] = np.amax(np_img[start:i+1],0)
    sitk_mip = sitk.GetImageFromArray(np_mip[-1])
    sitk_mip.SetOrigin(image.GetOrigin())
    sitk_mip.SetSpacing(image.GetSpacing())
    sitk_mip.SetDirection([image.GetDirection()[0],image.GetDirection()[1], image.GetDirection()[3], image.GetDirection()[4]])
    return sitk_mip

def pad_and_center(im_array, target_size):
    height_difference, width_difference = [j - i for i, j in zip(im_array.shape, target_size)]
    if width_difference >= 0:
        surplus = width_difference % 2
        extra_left, extra_right = width_difference // 2 + surplus, width_difference // 2
        extra_top, extra_bottom = height_difference, 0
        mip_ar_reshaped = np.pad(im_array, ((extra_top, extra_bottom), (extra_left, extra_right)),
                                 constant_values=0)
    else:
        extra_top, extra_bottom = height_difference, 0
        mip_ar_reshaped = im_array[:, :width_difference]
        mip_ar_reshaped = np.pad(mip_ar_reshaped, ((extra_top, extra_bottom), (0, 0)),
                                 constant_values=0)
    return mip_ar_reshaped

def get_rotational_MIP(image):
    single_angle_MIP = []
    for i in tqdm(range(360)):
        rotated_image = rotation3d(image, 0, i, 0)
        sitk_mip = createMIP(rotated_image, image.GetSize()[0])
        reshaped_mip = pad_and_center(sitk.GetArrayFromImage(sitk_mip), image.GetSize()[:2])
        single_angle_MIP.append(reshaped_mip)
    single_angle_MIP = np.stack(single_angle_MIP)
    rotational_mip = sitk.GetImageFromArray(np.stack(single_angle_MIP))
    return rotational_mip, single_angle_MIP

def create_rotating_gif(mip_images, output_path, duration=0.1):
    mip_images = [(img - img.min()) / (img.max() - img.min()) * 255 for img in mip_images]
    mip_images = [img.astype(np.uint8) for img in mip_images]
    imageio.mimsave(output_path, mip_images, duration=duration, loop=0)