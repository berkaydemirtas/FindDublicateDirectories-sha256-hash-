import hashlib
import os
import argparse


#necessary calls are done at the end of the code

#here I create a argument parser ( identic [-f | -d] [-n | -c | -cn] [-s] and there may be some paths)
my_parser = argparse.ArgumentParser()
group = my_parser.add_mutually_exclusive_group()
group2=my_parser.add_mutually_exclusive_group()

group.add_argument('-d',
                       action='store_true',
                       )
group.add_argument('-f',
                       action='store_true',
                       )
group2.add_argument('-c',
                       action='store_true',
                       )
group2.add_argument('-n',
                       action='store_true',
                       )
group2.add_argument('-cn',
                       action='store_true',
                       )
my_parser.add_argument('-s',
                       action='store_true',
                       )
my_parser.add_argument('directories',
                       action='store',
                       nargs='*',
                       default=[])

args = my_parser.parse_args()


#these are default values of flags
flag1="f"
flag2="c"
flag3="none"

#here value of flag1, flag2, flag3 are changing according to the argument flags
if args.d:
    flag1="d"
if args.c:
    flag2="c"
if args.n:
    flag2="n"
if args.cn:
    flag2="cn"
if args.s:
    flag3="s"

# if there are "n" flag then ignore "s" flag
if flag2 is "n":
    if flag3 is "s":
        flag3 ="none"

# this list hold the full path version of given argument paths. If there is no argument path, it holds cwd
directoryFullPath=[]

#fills directoryFullPath
if len(args.directories)!=0:
    for i in args.directories:
        if os.path.isdir(os.path.abspath(i)):
            directoryFullPath.append(os.path.abspath(i))
        else:
            print("error")
            quit()

else:
    directoryFullPath.append(os.path.abspath(os.getcwd()))


dict={}  #holds path-hash pair for "c" option (it is filled in traverseDir3)
dict2={} #holds hash-list of directories(directories with same hash) for "c" option (it is filled in traverseDir3)
dict3={} #holds hash-list of files(files with same hash) for "c" option (it is filled in traverseDir3)
dict4={} #holds path-size pair (it is filled in calculateSize)
dict5={} #it is used in printing process to sort dublicates according to their size.
dict7={} # same with dict2 but for "n" flag
dict8={} # same with dict3 but for "n" flag
dict9={} #it is used in intersection to store elements with same "n" and "c"
dict10={} #same with dict but for "n" flag
List1=[] #these list are used to store root, subdirectories, and subfiles.They will be explained clearly at the end of the code
List2=[]
List3=[]


#it takes path of file that will be hashed, name of file and "n" or "c" as flag.
#according to flag, it hashes name or content of the file
def filehash2(filepath,name,flag):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as fp:
        while True:
            if flag is "n":
                return encrypt_string(name)
            if flag is "c":
                data = fp.read()
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()


def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


#traverses given path(directory) recursively and fills the dictionaries with hash-dir or file pairs.
#inside of this, there are 2 big for. One of them iterates over subfiles of given directory, takes their
#hashes according the flag("c" or "n"). Other "for" iterates over subdirectories, calls this function recursively
#and fills the correct dictionaries.
#list4 holds hash value of all entries for given directory and at the end of this function, it is sorted and all elements
#are concataneted (dict , dict2 ,dict3 is filled for "c" flag , dict7 ,dict8, dict10 is filled for "n" flag)
def traverseDir3(path1,flag):
    index= List1.index(path1)
    dirs=List2[index]
    files=List3[index]
    list4=[]
    ind=path1.rfind('/')
    path2=path1[ind+1:]
    for i in files:
        str6=filehash2(path1+'/'+i,i,flag)
        list4.append(str6)
        if flag is "c":
            if str6 in dict3:
                dict3[str6].append(path1+'/'+i)
            else:
                dict3[str6]=[path1+'/'+i]
            dict[path1+'/'+i]=str6
        else:
            if str6 in dict8:
                dict8[str6].append(path1+'/'+i)
            else:
                dict8[str6]=[path1+'/'+i]
            dict10[path1+'/'+i]=str6
    for i in dirs:
        if flag is "c":
            if path1+'/'+i in dict:
                list4.append(dict[path1+'/'+i])
            else:
                list4.append(traverseDir3(path1+'/'+i,flag))
        else:
            if path1+'/'+i in dict10:
                list4.append(dict10[path1+'/'+i])
            else:
                list4.append(traverseDir3(path1+'/'+i,flag))
    list5=[str(i) for i in list4]
    list5.sort()
    str2=""
    for i in list5:
        str2 = str2+ i
    if flag is "n":
        str2=encrypt_string(path2)+str2
    str3=encrypt_string(str2)
    if flag is "c":
        if str3 in dict2:
            dict2[str3].append(path1)
        else:
            dict2[str3]=[path1]
    else:
        if str3 in dict7:
            dict7[str3].append(path1)
        else:
            dict7[str3]=[path1]
    if flag is "c":
        dict[path1]=str3
    else:
        dict10[path1]=str3
    return str3

#calculates size for given directory and all subdirectory and subfiles.
#fills dict4 with fullPath-size
#size of empty file is zero
def calculateSize(path1):
    index= List1.index(path1)
    dirs=List2[index]
    files=List3[index]
    sum=0
    size=0
    for i in files:
        size = os.path.getsize(path1+'/'+i)
        dict4[path1+'/'+i]=size
        sum+=size
    for i in dirs:
        size=calculateSize(path1+'/'+i)
        sum+=size
    dict4[path1]=sum
    return sum


#find all lists(hashes contains lists as value) that have at least 2 distinct element
def findDublicates(hashes):
    dublicates=[]
    for i in hashes.values():
        if len(set(i)) > 1 :
            dublicates.insert(0,i)
    return dublicates


#hashesByName contains lists which are consists of files or directories which have same name  (hashByName is a list that
# produced by findDublicates)
#this function takes directories or files with same name and if they also have same content put them in a list and add
#this list to list3 which is list of lists
def intersection(hashesByName):
    list3=[]
    for i in hashesByName:
        for j in i:
            if dict[j] in dict9:
                dict9[dict[j]].append(j)
            else:
                dict9[dict[j]]=[j]
        for j in findDublicates(dict9):
            list3.append(j)
        dict9.clear()
    return list3

#(flag1 is "f" or "d" , flag2 is "c" or "cn" or "n", flag3 is "s" or "none")
#this funtion calls findDublicates with correct dictionary and gets list of lists that contains dublicates.
#if flag2 is "cn" , this function calls intersection function and gets a list of list that contains dublicates
#for "cn" option
#if flag3 is "s" , then dublicates sorted according to their sizes and each dublicate group is sorted according to alpha-
#betical order.(then dublicates are printed with their sizes)(1. for)
#if flag3!="s", dublicates sorted according to their smallest element and printed in this order
def printResult(flag1,flag2,flag3):
    if flag1 is "d":
        dublicates=findDublicates(dict2)
        dublicates2=findDublicates(dict7)
    if flag1 is "f":
        dublicates=findDublicates(dict3)
        dublicates2=findDublicates(dict8)
    if flag2 is "n":
        dublicates=dublicates2
    if flag2 is "cn":
        dublicates=intersection(dublicates2)
    if flag3 is "s":
        for i in dublicates:
            i=set(i)                #there are some set() operations to prevent repetion
            i=list(i)
            if dict4[i[0]] in dict5:
                dict5[dict4[i[0]]].append(i)
            else:
                dict5[dict4[i[0]]]=[i]
        for i in sorted(dict5.keys(),reverse=True):
            withSameSize=sorted(dict5[i], key=min)
            for k in withSameSize:
                k.sort()
                for j in k:
                    print(j+"\t"+str(dict4[j]))
                print()
    else:
        concatanetedPaths=[]
        for i in dublicates:
            paths=""
            i=set(i)
            i=list(i)
            i.sort()
            for j in i:
                paths+=j+"\n"
            concatanetedPaths.append(paths)
        concatanetedPaths.sort()
        for i in concatanetedPaths:
            print(i)

#for each given path find root ,dirs and fill dictionaries for "n" and "c"
#calculate size of each directory
for i in directoryFullPath:
    for root, dirs, files in os.walk(i):
        if os.path.isdir(root):
            List1.append(root)
            List2.append(dirs)
            List3.append(files)
    traverseDir3(i,"n")
    traverseDir3(i,"c")
    calculateSize(i)

printResult(flag1,flag2,flag3)




