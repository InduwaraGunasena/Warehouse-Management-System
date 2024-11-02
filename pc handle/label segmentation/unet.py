import torch
import torch.nn as nn


class ConvEnc(nn.Module):
	def __init__(self, in_chan, out_chan, normalize=True):
		super(ConvEnc, self).__init__()

		conv = nn.Conv2d(in_chan, out_chan, 4, stride=2, padding=1)
		nn.init.normal_(conv.weight, 0, 0.02)
		model = [conv]

		if normalize:
			norm = nn.InstanceNorm2d(out_chan)
			model += [norm]

		model += [nn.LeakyReLU(0.2)]
		self.model = nn.Sequential(*model)

	def forward(self, x):
		return self.model(x)


class ConvDec(nn.Module):
	def __init__(self, in_chan, out_chan, dropout=False):
		super(ConvDec, self).__init__()

		conv = nn.ConvTranspose2d(in_chan, out_chan, 4, stride=2, padding=1)
		nn.init.normal_(conv.weight, 0, 0.02)
		model = [conv]

		norm = nn.InstanceNorm2d(out_chan)
		model += [norm]

		if dropout:
			model += [nn.Dropout(0.5)]

		model += [nn.ReLU()]
		self.model = nn.Sequential(*model)

	def forward(self, x):
		return self.model(x)


class UNet(nn.Module):
	def __init__(self, in_chan=3, out_chan=1, logits=False):
		super(UNet, self).__init__()
		self.logits = logits
		self.enc1 = ConvEnc(in_chan, 64, normalize=False)
		self.enc2 = ConvEnc(64, 128)
		self.enc3 = ConvEnc(128, 256)
		self.enc4 = ConvEnc(256, 512)
		self.enc5 = ConvEnc(512, 512)
		self.enc6 = ConvEnc(512, 512)
		self.enc7 = ConvEnc(512, 512)
		self.bott = ConvEnc(512, 512, normalize=False)

		self.dec7 = ConvDec(512, 512, dropout=True)
		self.dec6 = ConvDec(1024, 512, dropout=True)
		self.dec5 = ConvDec(1024, 512, dropout=True)
		self.dec4 = ConvDec(1024, 512)
		self.dec3 = ConvDec(1024, 256)
		self.dec2 = ConvDec(512, 128)
		self.dec1 = ConvDec(256, 64)

		self.conv = nn.ConvTranspose2d(128, out_chan, 4, stride=2, padding=1)

	def forward(self, x):
		enc1 = self.enc1(x)
		enc2 = self.enc2(enc1)
		enc3 = self.enc3(enc2)
		enc4 = self.enc4(enc3)
		enc5 = self.enc5(enc4)
		enc6 = self.enc6(enc5)
		enc7 = self.enc7(enc6)

		bott = self.bott(enc7)

		dec7 = self.dec7(bott)
		dec6 = self.dec6(torch.cat((dec7, enc7), 1))
		dec5 = self.dec5(torch.cat((dec6, enc6), 1))
		dec4 = self.dec4(torch.cat((dec5, enc5), 1))
		dec3 = self.dec3(torch.cat((dec4, enc4), 1))
		dec2 = self.dec2(torch.cat((dec3, enc3), 1))
		dec1 = self.dec1(torch.cat((dec2, enc2), 1))
		conv = self.conv(torch.cat((dec1, enc1), 1))

		if self.logits:
			return conv
		return torch.tanh(conv)