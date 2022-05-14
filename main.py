import file_generator as fg

BYTES_TO_TAKE = 100  #Number of bytes for block operation simulation
RECORDS_FILE_NAME="records2"
GENERATE_NEW_FILE=True #change to True to generate new bin file. New File name is RECORDS_FILE_NAME
NUMBER_OF_RECORDS=5 #number of records to generate, if GENERATE_NEW_FILE=True
PRINT_RECORDS_DEBUG = True
RECORDS_FROM_KEYBOARD=False

writes=0
reades=0

class blockBinReader:

    ending_rec = b''
    records_list=[]

    def __init__(self,file):
        self.f = file

    def get_next_records(self):
        global reades;
        reades+=1
        records = self.f.read(BYTES_TO_TAKE)
        if self.ending_rec!='b':
            records = self.ending_rec+records
        #print(records);
        self.records_list = records.split(b';')
        #print(records)
        self.ending_rec = self.records_list.pop()
        if len(self.records_list)==0:
            self.records_list.append(b'endoffile')

    def get_record(self):
        if len(self.records_list)==0:
            self.get_next_records()
        #print("get ",self.records_list[0])
        if self.records_list[0]==b'endoffile':
            return self.records_list[0]
        else:
            return self.records_list.pop(0)

    def returnRecord(self, recordToReturn):
        self.records_list.insert(0,recordToReturn)

    def __del__(self):
        self.f.close()

class blockBinWriter:

    def __init__(self,file):
        self.f = file
        self.buffer=b''

    def append_next_records(self,list_of_records):
        self.f.write(b''.join(list_of_records))

    def writeRecords(self):
        global writes
        writes+=1
        end_of_buffer = self.buffer[BYTES_TO_TAKE:len(self.buffer)]
        bytestowrite = self.buffer[:BYTES_TO_TAKE]
        self.f.write(bytestowrite)
        self.buffer = end_of_buffer

    def putRecord(self,record):
        #print("put ",record)
        self.buffer+=record
        self.buffer+=b';'
        if len(self.buffer)>BYTES_TO_TAKE:
            self.writeRecords()


    def __del__(self):
        self.writeRecords()
        global writes
        if len(self.buffer)>0:
            writes += 1
            self.f.write(self.buffer)
        self.f.close()

def printAllRecords(filename):
    global writes
    global reades
    tmp_writes=writes
    tmp_reades=reades
    print(filename,":")
    bbr = blockBinReader(open(filename, "rb"))
    record=bbr.get_record()
    i =0
    while(record!=b'endoffile'):
        i+=1
        print(i,": ",record.decode())
        record = bbr.get_record()
    del bbr
    print(i,"records")
    writes=tmp_writes
    reades=tmp_reades

def get_id_number(record):
    return  record.split(b',')[-1]

def compare_records(record1,record2):
    #print(get_id_number(record1),get_id_number(record2),'\n',list(get_id_number(record1)),list(get_id_number(record2)),'\n',get_id_number(record1)<get_id_number(record2))
    return get_id_number(record1)<get_id_number(record2)

def compare_and_append(lastActualTape,lastSecTape,actual1,bw_ActTape:blockBinWriter,bw_SecTape:blockBinWriter,lastRecord):
    #print(lastActualTape,lastRecord)
    if compare_records(lastActualTape,lastRecord):
        bw_ActTape.putRecord(lastRecord)
        #print('act')
        lastActualTape=lastRecord
    else:
        bw_SecTape.putRecord(lastRecord)
        #print('sec')
        lastSecTape=lastRecord
        actual1=xor(actual1,True)
    return lastActualTape,lastSecTape,actual1

def xor(x, y):
    return bool((x and not y) or (not x and y))

def distribute_on_tapes(bw_tape1:blockBinWriter,bw_tape2:blockBinWriter,br_records:blockBinReader):
    actual1 = True #is tape1 actual tape
    last_record=br_records.get_record()
    last_tape1=last_record
    last_tape2=b''
    bw_tape1.putRecord(last_tape1)
    last_record = br_records.get_record()
    while(last_record!=b'endoffile'):
        if actual1:
            last_tape1,last_tape2,actual1 = compare_and_append(last_tape1,last_tape2,actual1, bw_tape1,bw_tape2,last_record)
        else:
            last_tape2,last_tape1,actual1 = compare_and_append(last_tape2, last_tape1, actual1, bw_tape2, bw_tape1, last_record)
        last_record = br_records.get_record()

def putRun(FirstRec,br_tape:blockBinReader,bw_records:blockBinWriter):
    lastWrite=FirstRec
    bw_records.putRecord(lastWrite)
    FirstRec=br_tape.get_record()
    while FirstRec!=b'endoffile':
        if compare_records(lastWrite,FirstRec):
            lastWrite = FirstRec
            bw_records.putRecord(lastWrite)
            FirstRec = br_tape.get_record()
        else:
            br_tape.returnRecord(FirstRec)
            return False
    return True

def merge2runs(br_tape1:blockBinReader,br_tape2:blockBinReader,bw_records:blockBinWriter):
    lw_from_tape1=True
    first_tape1=br_tape1.get_record()
    first_tape2=br_tape2.get_record()
    last_write_t1=None
    last_write_t2=None
    if compare_records(first_tape1,first_tape2):
        last_write_t1=first_tape1
        bw_records.putRecord(last_write_t1)
        first_tape1=br_tape1.get_record()
        lw_from_tape1 = True
    else:
        last_write_t2 = first_tape2
        bw_records.putRecord(last_write_t2)
        first_tape2 = br_tape2.get_record()
        lw_from_tape1=False
    while (first_tape1!=b'endoffile') & (first_tape2!=b'endoffile'):
        if lw_from_tape1:
            if compare_records(last_write_t1,first_tape1):
                if compare_records(first_tape1, first_tape2):
                    last_write_t1 = first_tape1
                    bw_records.putRecord(last_write_t1)
                    first_tape1 = br_tape1.get_record()
                    lw_from_tape1 = True
                else:
                    last_write_t2 = first_tape2
                    bw_records.putRecord(last_write_t2)
                    first_tape2 = br_tape2.get_record()
                    lw_from_tape1 = False
            else:
                br_tape1.returnRecord(first_tape1)
                return putRun(first_tape2,br_tape2,bw_records)
        else:
            if compare_records(last_write_t2,first_tape2):
                if compare_records(first_tape1, first_tape2):
                    last_write_t1 = first_tape1
                    bw_records.putRecord(last_write_t1)
                    first_tape1 = br_tape1.get_record()
                    lw_from_tape1 = True
                else:
                    last_write_t2 = first_tape2
                    bw_records.putRecord(last_write_t2)
                    first_tape2 = br_tape2.get_record()
                    lw_from_tape1 = False
            else:
                br_tape2.returnRecord(first_tape2)
                return putRun(first_tape1,br_tape1,bw_records)
    br_tape1.returnRecord(first_tape1)
    br_tape2.returnRecord(first_tape2)
    return True

def putRestOfTape(br_tape:blockBinReader,bw_records:blockBinWriter):
    rec = br_tape.get_record()
    i=0
    while rec!=b'endoffile':
        i+=1
        putRun(rec,br_tape,bw_records)
        rec = br_tape.get_record()
    return i


def merge(br_tape1:blockBinReader,br_tape2:blockBinReader,bw_records:blockBinWriter):
    b=0
    while merge2runs(br_tape1,br_tape2,bw_records)!=True:
        b+=1
    check = br_tape1.get_record()
    restofruns=0
    if check==b'endoffile':
        restofruns = putRestOfTape(br_tape2,bw_records)
    else:
        br_tape1.returnRecord(check)
        restofruns = putRestOfTape(br_tape1, bw_records)
    if (b+restofruns)==1:
        return False
    else:
        return True

def sort():
    i=0
    notEnd = True
    while notEnd:
        i+=1
        br_records = blockBinReader(open(RECORDS_FILE_NAME, "rb"))
        bw_tape1=blockBinWriter(open("tasma1", "wb"))
        bw_tape2=blockBinWriter(open("tasma2", "wb"))

        distribute_on_tapes(bw_tape1,bw_tape2,br_records)

        del br_records
        del bw_tape1
        del bw_tape2

        if PRINT_RECORDS_DEBUG==True:
            print("AFTER distribution")
            printAllRecords(RECORDS_FILE_NAME)
            printAllRecords("tasma1")
            printAllRecords("tasma2")

        bw_records = blockBinWriter(open(RECORDS_FILE_NAME, "wb"))
        br_tape1= blockBinReader(open("tasma1", "rb"))
        br_tape2= blockBinReader(open("tasma2", "rb"))

        notEnd = merge(br_tape1,br_tape2,bw_records)

        del bw_records
        del br_tape1
        del br_tape2


        if PRINT_RECORDS_DEBUG==True:
            print("AFTER merge")
            printAllRecords(RECORDS_FILE_NAME)
            printAllRecords("tasma1")
            printAllRecords("tasma2")
    return i




if GENERATE_NEW_FILE==True:
    gen=fg.recordsGenerator(NUMBER_OF_RECORDS,RECORDS_FILE_NAME)
    gen.generate()
    del gen
if RECORDS_FROM_KEYBOARD==True:
    bw = blockBinWriter(open(RECORDS_FILE_NAME, "ab"))
    number_of_rec=input("How many records?")
    number_of_rec=int(number_of_rec)
    for i in range(number_of_rec):
        name=input("Enter name:")
        surname=input("Enter surname:")
        idnum=input("enter id number:")
        rec=name+","+surname+","+idnum
        print("You entered record:",rec)
        rec=rec.encode()
        bw.putRecord(rec)
    del bw

printAllRecords(RECORDS_FILE_NAME)
writes=0
reades=0
phases=sort()
print("Number of paheses: ", phases,'\nreades: ', reades,"\nwrites: ", writes)
printAllRecords(RECORDS_FILE_NAME)


