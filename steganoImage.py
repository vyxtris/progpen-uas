# Reference:https://medium.com/@stephanie.werli/image-steganography-with-python-83381475da57
# 2301894155 - Valentino Nooril

from PIL import Image
import base64

# Mengubah encoding data menjadi 8-bit binary menggunakan nilai dari karakter ASCII
def genData(data):

	# membuat variabel list untuk menyimpan nilai binary
	newd = []

	for i in data:
		newd.append(format(i, '08b'))
	return newd


# Pixel diubah sesuai dengan 8-bit binary 
def modPix(pix, data):

	# memanggil fungsi genData untuk mengubah encoding menjadi 8-bit binary
	datalist = genData(data)
	# menghitung banyaknya data
	lendata = len(datalist)
	# iterator value pix
	imdata = iter(pix)

	for i in range(lendata):

		# Mengambil 3 pixel 
		pix = [value for value in imdata.__next__()[:3] +
								imdata.__next__()[:3] +
								imdata.__next__()[:3]]

		# Nilai pixel harus diubah menjadi 0 untuk genap dan 1 untuk ganjil
		for j in range(0, 8):
			if (datalist[i][j] == '0' and pix[j]% 2 != 0):
				pix[j] -= 1

			elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
				if(pix[j] != 0):
					pix[j] -= 1
				else:
					pix[j] += 1

		# Pixel ke-8 dari setiap baris menunjukkan untuk berhenti atau lanjut membaca
		# 0 berarti lanjut dan 1 berarti pesan berhenti
		if (i == lendata - 1):
			if (pix[-1] % 2 == 0):
				if(pix[-1] != 0):
					pix[-1] -= 1
				else:
					pix[-1] += 1

		else:
			if (pix[-1] % 2 != 0):
				pix[-1] -= 1

		# return value sebagai generator
		pix = tuple(pix)
		yield pix[0:3]
		yield pix[3:6]
		yield pix[6:9]

# fungsi encoding data ke dalam newimg dengan mengubah Least Significant Bytes 
def encode_enc(newimg, data):
	w = newimg.size[0]
	(x, y) = (0, 0)

	for pixel in modPix(newimg.getdata(), data):

		# memasukkan pixel yang diubah ke dalam image baru
		newimg.putpixel((x, y), pixel)
		if (x == w - 1):
			x = 0
			y += 1
		else:
			x += 1

# Encode user_input ke dalam image
def encode(img, new_img_name, data):

	image = Image.open(img, 'r')

	# encode data dengan base64
	data = data.encode()
	data = base64.b64encode(data)

	# membuat image baru lalu menggunakan teknik LSB untuk memasukkan pesan ke dalam image
	newimg = image.copy()
	encode_enc(newimg, data)

	# meminta nama image baru lalu save image tersebut
	newimg.save(new_img_name, str(new_img_name.split(".")[1].upper()))

	image.close()
	return new_img_name

# Decode pesan yang tersimpan dari image
def decode(img):
	# meminta nama image yang ingin diambil pesannya
	image = Image.open(img, 'r')

	# inisiasi variabel untuk menyimpan pixel
	data = ''
	imgdata = iter(image.getdata())
	
	while (True):
		# mengambil 3 pixel
		pixels = [value for value in imgdata.__next__()[:3] +
								imgdata.__next__()[:3] +
								imgdata.__next__()[:3]]

		# inisiasi variabel untuk menyimpan binary
		binstr = ''

		for i in pixels[:8]:
			if (i % 2 == 0):
				binstr += '0'
			else:
				binstr += '1'

		data += chr(int(binstr, 2))
		if (pixels[-1] % 2 != 0):
			break
	
	image.close()

	data = base64.b64decode(data)
	data = data.decode()
	return data


# Main Function
def main():
	a = int(input("Steganography C&C\n1.Create new C&C\n2.Get C&C command\n>> "))

	if (a == 1):
		filename = encode()

	elif (a == 2):
		print("Decoded Word : " + decode())
	else:
		raise Exception("Enter correct input")


if __name__ == '__main__' :
	main()
