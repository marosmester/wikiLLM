import re

text = "Elizabeth (far left) on the balcony of Buckingham Palace with her family and Winston Churchill, 8 May 1945"
text += " and her 3046 soldiers born in 982"

# patterns
p1 = r"\d{4}"                       # 4 digit number
p2 = r"\b[12]\d{3}\b"               # 4 digit number beginning with a 1 or a 2
p3 = r"\b([12]\d{3}|\d{3})\b"       # 4 digit number beginning with a 1 or a 2, or, any 3 digit number

x1 = re.search(p3, text)
x2 = re.findall(p3, text)
print(x1)
print(x2)