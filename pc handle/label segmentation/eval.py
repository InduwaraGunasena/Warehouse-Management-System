import os, glob
import cv2
import torch
import numpy as np
from unet import UNet
from tqdm import tqdm
from pathlib import Path
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, jaccard_score
import torchvision.transforms.functional as TF

# Use GPU if available
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

# Paths for test dataset and predicted mask output
test_dataset_image_path = "dataset/test/images"
test_dataset_mask_path = "dataset/test/masks/original"  # Ground truth masks
predicted_mask_path = "dataset/test/masks/predicted"

# Load the trained UNet model
model = UNet().to(device).eval()
model.load_state_dict(torch.load("models/99.pt", map_location=device)['model'])

# Normalize function
def normalize(img):
    return (img - 0.5) / 0.5

# Denormalize function
def denormalize(img):
    return (img * 0.5) + 0.5

# Function to calculate metrics
def calculate_metrics(pred, target):
    pred_flat = pred.flatten()
    target_flat = target.flatten()

    precision = precision_score(target_flat, pred_flat)
    recall = recall_score(target_flat, pred_flat)
    f1 = f1_score(target_flat, pred_flat)
    accuracy = accuracy_score(target_flat, pred_flat)
    mean_iou = jaccard_score(target_flat, pred_flat)

    return precision, recall, f1, accuracy, mean_iou

# Process each image and compute metrics
def process(file, mask_file):
    img = cv2.imread(file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Preprocess the image and run it through the model
    x = normalize(TF.to_tensor(img))
    x = x.to(device).unsqueeze(0)

    # Inference
    with torch.inference_mode():
        y = model(x)

    # Post-process the output and generate a mask
    y = denormalize(y[0].cpu())
    y = np.array(TF.to_pil_image(y))

    # Optional mask enhancement
    y = cv2.blur(y, (5, 5))
    _, y = cv2.threshold(y, 127, 255, cv2.THRESH_BINARY)
    pred_mask = np.zeros_like(y)
    cont, _ = cv2.findContours(y, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cont) > 0:  # Ensure contours are found
        largest_contour = max(cont, key=cv2.contourArea)
        cv2.fillPoly(pred_mask, pts=[largest_contour], color=255)

    # Load ground truth mask
    target_mask = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)

    # Ensure both masks have the same shape
    pred_mask_resized = cv2.resize(pred_mask, (target_mask.shape[1], target_mask.shape[0]))

    # Calculate metrics
    precision, recall, f1, accuracy, mean_iou = calculate_metrics(pred_mask_resized // 255, target_mask // 255)

    # Save the predicted mask in the predicted_mask_path with the same name as the original image
    save_path = os.path.join(predicted_mask_path, f'{Path(file).stem}_mask.png')
    cv2.imwrite(save_path, pred_mask)

    return precision, recall, f1, accuracy, mean_iou

# Main function
def main():
    # Ensure the predicted output directory exists
    if not os.path.exists(predicted_mask_path):
        os.makedirs(predicted_mask_path)

    # Get the list of test images and masks
    test_images = sorted(glob.glob(os.path.join(test_dataset_image_path, '*')))
    test_masks = sorted(glob.glob(os.path.join(test_dataset_mask_path, '*')))

    # Ensure the number of images and masks are the same
    assert len(test_images) == len(test_masks), "Mismatch in the number of test images and masks."

    # Initialize metric accumulators
    precision_sum, recall_sum, f1_sum, accuracy_sum, mean_iou_sum = 0, 0, 0, 0, 0
    total = len(test_images)

    # Process each image and accumulate metrics
    for img_file, mask_file in tqdm(zip(test_images, test_masks), total=total):
        precision, recall, f1, accuracy, mean_iou = process(img_file, mask_file)
        precision_sum += precision
        recall_sum += recall
        f1_sum += f1
        accuracy_sum += accuracy
        mean_iou_sum += mean_iou

    # Calculate average metrics
    avg_precision = precision_sum / total
    avg_recall = recall_sum / total
    avg_f1 = f1_sum / total
    avg_accuracy = accuracy_sum / total
    avg_mean_iou = mean_iou_sum / total

    # Print the evaluation results
    print(f"Average Precision: {avg_precision:.4f}")
    print(f"Average Recall: {avg_recall:.4f}")
    print(f"Average F1 Score: {avg_f1:.4f}")
    print(f"Average Accuracy: {avg_accuracy:.4f}")
    print(f"Average Mean IoU: {avg_mean_iou:.4f}")


if __name__ == "__main__":
    main()

