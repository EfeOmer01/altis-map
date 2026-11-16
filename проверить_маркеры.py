with open(r"C:\Users\efeom\OneDrive\Рабочий стол\1\newAmazingLife.AmazingMap\mission.cpp", "r", encoding="latin1") as f:
    text = f.read()

pos = text.find('dataType="Object";')
if pos != -1:
    print(text[pos-50:pos+600])
