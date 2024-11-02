import os, sys, glob, time
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision.utils import make_grid
import torchvision.transforms.functional as TF
#from torch.cuda.amp import autocast, GradScaler
from torch.amp import autocast, GradScaler
from unet import UNet


device = 'cuda:0'
image = None

amp = True

scaler = torch.amp.GradScaler(enabled=amp)
criterion = F.l1_loss


dataset_path = "dataset"                  # Change this to your dataset path
checkpoint_path = "models/YOUR_MODEL.pt"  # Change this to your checkpoint path or leave as None


def train(model, optimizer, loader, epoch):
	model.train()

	train_loss = []

	for i, (x, y) in enumerate(loader):

		x = x.to(device)
		y = y.to(device)

		optimizer.zero_grad()

		with autocast(device, enabled=amp):
			out = model(x)
			loss = criterion(out, y)

		scaler.scale(loss).backward()
		scaler.step(optimizer)
		scaler.update()

		train_loss.append(loss.item())

		if (i+1) % 4 == 0:
			loss = np.mean(train_loss[-4:])
			print("\rEpoch %d [%d/%d] [loss: %f]" %
					(epoch, i, len(loader), loss))

		#if i % 32 == 0:
			global image
			imgs = [x[0], y[0].repeat(3,1,1), out[0].repeat(3,1,1)]
			imgs = torch.stack(imgs).detach().cpu()
			imgs = denormalize(imgs)
			image = TF.to_pil_image(make_grid(imgs, len(imgs)))
			w, h = image.size
			image = image.resize((w*2, h*2), 1)
			image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

		if i == 0:
			flags = cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE
			cv2.namedWindow(sys.argv[0], flags)

		if image is not None:
			resized_image = cv2.resize(image, (758, 248))  # Resize the image to 640x480 or any size you prefer
			cv2.imshow(sys.argv[0], resized_image)
			cv2.waitKey(1)

	return np.mean(train_loss)


def random_transform(img, mask, hflip=True, vflip=False):
	rotate, zoom, shift = 10, 0.05, 0.05
	rotation = np.random.uniform(-rotate, rotate)
	scale = np.random.uniform(1 - zoom, 1 + zoom)
	h, w = img.shape[:2]
	tx = np.random.uniform(-shift, shift) * w
	ty = np.random.uniform(-shift, shift) * h
	mat = cv2.getRotationMatrix2D((w // 2, h // 2), rotation, scale)
	mat[:, 2] += (tx, ty)
	img = cv2.warpAffine(img, mat, (w, h), flags=cv2.INTER_CUBIC)
	mask = cv2.warpAffine(mask, mat, (w, h), flags=cv2.INTER_CUBIC)
	if hflip and np.random.random() < 0.5:
		img = cv2.flip(img, 1)
		mask = cv2.flip(mask, 1)
	if vflip and np.random.random() < 0.5:
		img = cv2.flip(img, 0)
		mask = cv2.flip(mask, 0)
	return img, mask


def random_warp(img, mask):
	w = img.shape[1]
	cell = [w // (2**i) for i in range(1, 4)][np.random.randint(3)]
	ncell = w // cell + 1
	grid = np.linspace(0, w, ncell)
	mapx = np.broadcast_to(grid, (ncell, ncell)).copy()
	mapy = mapx.T
	rx = np.random.normal(0, 0.9, (ncell-2, ncell-2)) / 2.5 * (cell*0.24)
	ry = np.random.normal(0, 0.9, (ncell-2, ncell-2)) / 2.5 * (cell*0.24)
	mapx[1:-1, 1:-1] = mapx[1:-1, 1:-1] + rx
	mapy[1:-1, 1:-1] = mapy[1:-1, 1:-1] + ry
	half = cell//2
	size = (w+cell, w+cell)
	mapx = cv2.resize(mapx, size)[half:-half, half:-half].astype("float32")
	mapy = cv2.resize(mapy, size)[half:-half, half:-half].astype("float32")
	img = cv2.remap(img, mapx, mapy, cv2.INTER_CUBIC)
	mask = cv2.remap(mask, mapx, mapy, cv2.INTER_CUBIC)
	return img, mask


def normalize(img):
	return (img - 0.5) / 0.5


def denormalize(img):
	return (img * 0.5) + 0.5


def load_images(files):
	img = cv2.imread(files[0])
	mask = cv2.imread(files[1], 0)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

	print(f"Loading image: {files[0]}, mask: {files[1]}")

	# Check if images are loaded correctly
	if img is None or mask is None:
		raise ValueError(f"Error loading image or mask: {files}")

	img, mask = random_transform(img, mask, vflip=False)
	img, mask = random_warp(img, mask)

	img = normalize(TF.to_tensor(img))
	mask = normalize(TF.to_tensor(mask))
	return img, mask


class dataset(Dataset):
	def __init__(self, root):
		img_files = sorted(glob.glob(root+'/images/*'))
		mask_files = sorted(glob.glob(root+'/masks/*'))
		self.files = list(zip(img_files, mask_files))

	def __len__(self):
		return len(self.files)

	def __getitem__(self, idx):
		image, mask = load_images(self.files[idx])
		return image, mask


def main():
	if os.path.exists('log.txt'):
		os.remove('log.txt')

	if not os.path.exists('models'):
		os.mkdir('models')

	train_loader = DataLoader(dataset(dataset_path), batch_size=1,
						num_workers=1, pin_memory=True, shuffle=True)

	model = UNet().to(device)

	epoch0 = -1
	if checkpoint_path:
		state = torch.load(checkpoint_path, map_location='cpu')
		model.load_state_dict(state['model'])
		epoch0 = state['epoch']

	optimizer = optim.Adam(model.parameters(), lr=0.0002, betas=(0.5, 0.999))

	for epoch in range(epoch0+1, 200):
		t = time.perf_counter()

		loss = train(model, optimizer, train_loader, epoch)

		print('\nloss: %.6f [%.2f s]\n'%(loss, time.perf_counter()-t))

		with open('log.txt', 'a') as f:
			print('%d\t%f'%(epoch, loss), file=f)

		if (epoch+1)%5 == 0:
			torch.save({
				'epoch': epoch,
				'loss': loss,
				'model': model.state_dict(),
				}, "models/%d.pt"%epoch)
			print('model saved')


if __name__ == "__main__":
	torch.backends.cudnn.benchmark = True
	main()
