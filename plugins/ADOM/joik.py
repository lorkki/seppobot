import random

def joik(minlength=60, maxlength=80, charset="aeiouy"):
	out = ""
	while len(out) < minlength:
		out += random.choice(charset) * random.randint(1, min(10, maxlength-len(out)))
	return out

if __name__ == "__main__":
	print(joik())
