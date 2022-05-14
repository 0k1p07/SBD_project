import random
import linecache
from polishidcard import PolishIDCard

liczba_nazwisk=3000
liczba_imion=500


class recordsGenerator:

    def __init__(self,number_of_records,file_name):
        self.liczba_rek=number_of_records
        self.file = open(file_name, 'wb')

    def generate(self):
        cardlist=[];
        for i in range(0,self.liczba_rek):
            imie = linecache.getline("imiona.csv",random.randint(0, liczba_imion))[:-1]
            nazwisko = linecache.getline("nazwiska.csv",random.randint(0, liczba_nazwisk))[:-1]
            card = PolishIDCard().generate()
            while card in cardlist:
                card = PolishIDCard().generate()
            cardlist.append(card)
            record=imie+","+nazwisko+","+card+";"
            self.file.write(record.encode())
            #print(record)

    def __del__(self):
        self.file.close()

    def getFile(self):
        return self.file


