import sys
import os 
if os.name == 'posix':
    import resource # pylint: disable=import-error
import time
import psutil

# Penalty constant
MISMATCH_PENALTY = [
    [0,110,48,94],
    [110,0,118,48],
    [48,118,0,110],
    [94,48,110,0],
]

INDEX_OF_CHAR = {
    "A": 0,
    "C": 1,
    "G": 2,
    "T": 3,
}

GAP_PENALTY = 30

# Preprocess input data
def get_input_data(filepath):
    current_string_index = 0
    base_string1 = ""
    indices1 = []
    base_string2 = ""
    indices2 = []
    file = open(filepath,"r")
    for x in file:
        if x[0] == "A" or x[0] == "T" or x[0] == "C" or x[0] == "G":# x is base string
            if current_string_index == 0:
                current_string_index = 1
                base_string1 = x.replace("\n","").replace("\r","")
            else:
                current_string_index = 2
                base_string2 = x.replace("\n","").replace("\r","")
        else: # x is indice
            if current_string_index == 1:
                indices1.append(int(x.replace("\n","").replace("\r","")))
            else:
                indices2.append(int(x.replace("\n","").replace("\r","")))
    file.close()
    return base_string1, indices1, base_string2, indices2

def generate_string(base_string, indices):
    current_string = base_string
    for i in indices:
        current_string = "".join([current_string[:i+1],current_string,current_string[i+1:]])
    return current_string

# Basic solution to Sequence Alignment (DP)
def align_sequence_basic(string1,string2):
    # Initialize OPT matrix
    OPT = [ [0] * (len(string2)+1) for _ in range(len(string1)+1)]
    for i in range(len(string1)+1):
        OPT[i][0] = GAP_PENALTY * i
    for j in range(len(string2)+1):
        OPT[0][j] = GAP_PENALTY * j
    # Fill OPT matrix using recurrence formula
    for i in range(1,len(string1)+1):
        for j in range(1,len(string2)+1):
            OPT[i][j] = min(
                OPT[i-1][j-1] + MISMATCH_PENALTY[INDEX_OF_CHAR[string1[i-1]]][INDEX_OF_CHAR[string2[j-1]]],
                OPT[i][j-1] + GAP_PENALTY,
                OPT[i-1][j] + GAP_PENALTY
            )
    # Get similarity from OPT matrix
    similarity = OPT[len(string1)][len(string2)]
    # Get alignment from OPT matrix
    string1_alignment = ""
    string2_alignment =""
    i = len(string1)
    j = len(string2)
    while i>0 and j>0:
        if OPT[i][j] == OPT[i-1][j-1] + MISMATCH_PENALTY[INDEX_OF_CHAR[string1[i-1]]][INDEX_OF_CHAR[string2[j-1]]]:
            string1_alignment = "".join([string1[i-1],string1_alignment])
            string2_alignment = "".join([string2[j-1],string2_alignment])
            i = i-1
            j = j-1
        elif OPT[i][j] == OPT[i][j-1] + GAP_PENALTY:
            string1_alignment = "".join(["_",string1_alignment])
            string2_alignment = "".join([string2[j-1],string2_alignment])
            j = j-1
        else: # OPT[i][j] == OPT[i-1][j] + GAP_PENALTY
            string1_alignment = "".join([string1[i-1],string1_alignment])
            string2_alignment = "".join(["_",string2_alignment])
            i = i-1
    if i == 0:
        for k in reversed(range(j)):
            string1_alignment = "".join(["_",string1_alignment])
            string2_alignment = "".join([string2[k],string2_alignment])
    else: # j == 0
        for k in reversed(range(i)):
            string1_alignment = "".join([string1[k],string1_alignment])
            string2_alignment = "".join(["_",string2_alignment])
    return similarity, string1_alignment, string2_alignment

# Memory efficient solution to Sequence Alignment (Divide&Conquer + DP)
def align_sequence_memory_efficient(string1,string2):
    if string1 == string2:
        similarity = 0
        string1_alignment = string1
        string2_alignment = string2
    if len(string1)>1 and len(string2)>1:
        # prepare the strings
        string1_L = string1[:int(len(string1)/2)]
        string1_R = string1[int(len(string1)/2):]
        string1_R_reversed = string1_R[::-1]
        string2_reversed = string2[::-1]
        # Initialize OPT matrix
        OPT_XL = [ [0] * (len(string2)+1) for _ in range(2)]
        for i in range(2):
            OPT_XL[i][0] = GAP_PENALTY * i
        for j in range(len(string2)+1):
            OPT_XL[0][j] = GAP_PENALTY * j
        OPT_XR = [ [0] * (len(string2)+1) for _ in range(2)]
        for i in range(2):
            OPT_XR[i][0] = GAP_PENALTY * i
        for j in range(len(string2)+1):
            OPT_XR[0][j] = GAP_PENALTY * j
        # Fill OPT matrix using recurrence formula
        for i in range(1,len(string1_L)+1):
            OPT_XL[1][0] = GAP_PENALTY * i
            for j in range(1,len(string2)+1):
                OPT_XL[1][j] = min(
                    OPT_XL[0][j-1] + MISMATCH_PENALTY[INDEX_OF_CHAR[string1_L[i-1]]][INDEX_OF_CHAR[string2[j-1]]],
                    OPT_XL[1][j-1] + GAP_PENALTY,
                    OPT_XL[0][j] + GAP_PENALTY
                )
            for j in range(len(string2)+1):
                OPT_XL[0][j] = OPT_XL[1][j]
        for i in range(1,len(string1_R_reversed)+1):
            OPT_XR[1][0] = GAP_PENALTY * i
            for j in range(1,len(string2_reversed)+1):
                OPT_XR[1][j] = min(
                    OPT_XR[0][j-1] + MISMATCH_PENALTY[INDEX_OF_CHAR[string1_R_reversed[i-1]]][INDEX_OF_CHAR[string2_reversed[j-1]]],
                    OPT_XR[1][j-1] + GAP_PENALTY,
                    OPT_XR[0][j] + GAP_PENALTY
                )
            for j in range(len(string2_reversed)+1):
                OPT_XR[0][j] = OPT_XR[1][j]
        OPT_final = [0] * (len(string2)+1)
        for j in range(len(string2)+1):
            OPT_final[j] = OPT_XL[1][j] + OPT_XR[1][-(j+1)]
        # get similarity from OPT array
        similarity = min(OPT_final)
        spilt_index = OPT_final.index(similarity)-1
        string2_L = string2[:spilt_index+1]
        string2_R = string2[spilt_index+1:]
        _,string1_L_alignment,string2_L_alignment = align_sequence_memory_efficient(string1_L,string2_L)
        _,string1_R_alignment,string2_R_alignment = align_sequence_memory_efficient(string1_R,string2_R)
        string1_alignment = "".join([string1_L_alignment,string1_R_alignment])
        string2_alignment = "".join([string2_L_alignment,string2_R_alignment])
    elif len(string1) == 0 or len(string2) == 0:
        if len(string1) == 0:
            similarity = len(string2) * GAP_PENALTY
            string1_alignment = "".join(["_"] * (len(string2)))
            string2_alignment = string2
        else:# len(string2) == 0
            similarity = len(string1) * GAP_PENALTY
            string1_alignment = string1
            string2_alignment =  "".join(["_"] * (len(string1)))
    else: # len(string1) == 1 or len(string2) == 1
        #similarity, string1_alignment, string2_alignment = align_sequence_basic(string1,string2)
        if len(string1) == 1:
            if string1 == "A":
                if "A" in string2:
                    i = string2.index("A")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                elif "G" in string2:
                    i = string2.index("G")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                else:
                    similarity = (len(string2) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string2))
                    string1_alignment = "".join([string1,back])
                    string2_alignment = "".join("_"    ,string2)
            elif string1 == "G":
                if "G" in string2:
                    i = string2.index("G")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                elif "A" in string2:
                    i = string2.index("A")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                else:
                    similarity = (len(string2) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string2))
                    string1_alignment = "".join([string1,back])
                    string2_alignment = "".join("_"    ,string2)
            elif string1 == "C":
                if "C" in string2:
                    i = string2.index("C")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                elif "T" in string2:
                    i = string2.index("T")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                else:
                    similarity = (len(string2) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string2))
                    string1_alignment = "".join([string1,back])
                    string2_alignment = "".join("_"    ,string2)
            else: # string1 == "T"
                if "T" in string2:
                    i = string2.index("T")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                elif "C" in string2:
                    i = string2.index("C")
                    similarity = (len(string2)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string1]][INDEX_OF_CHAR[string2[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string2)-1-i))
                    string1_alignment = "".join([front,string1,back])
                    string2_alignment = string2
                else:
                    similarity = (len(string2) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string2))
                    string1_alignment = "".join([string1,back])
                    string2_alignment = "".join("_"    ,string2)
        else:# len(string2) == 1
            if string2 == "A":
                if "A" in string1:
                    i = string1.index("A")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                elif "G" in string1:
                    i = string1.index("G")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                else:
                    similarity = (len(string1) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string1))
                    string2_alignment = "".join([string2,back])
                    string1_alignment = "".join("_"    ,string1)
            elif string2 == "G":
                if "G" in string1:
                    i = string1.index("G")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                elif "A" in string1:
                    i = string1.index("A")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                else:
                    similarity = (len(string1) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string1))
                    string2_alignment = "".join([string2,back])
                    string1_alignment = "".join("_"    ,string1)
            elif string2 == "C":
                if "C" in string1:
                    i = string1.index("C")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                elif "T" in string1:
                    i = string1.index("T")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                else:
                    similarity = (len(string1) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string1))
                    string2_alignment = "".join([string2,back])
                    string1_alignment = "".join("_"    ,string1)
            else: # string2 == "T"
                if "T" in string1:
                    i = string1.index("T")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                elif "C" in string1:
                    i = string1.index("C")
                    similarity = (len(string1)-1) * GAP_PENALTY + MISMATCH_PENALTY[INDEX_OF_CHAR[string2]][INDEX_OF_CHAR[string1[i]]]
                    front = "".join(["_"] * (i))
                    back = "".join(["_"] * (len(string1)-1-i))
                    string2_alignment = "".join([front,string2,back])
                    string1_alignment = string1
                else:
                    similarity = (len(string1) + 1) * GAP_PENALTY
                    back = "".join(["_"] * len(string1))
                    string2_alignment = "".join([string2,back])
                    string1_alignment = "".join("_"    ,string1)
    return similarity,string1_alignment,string2_alignment



# Measure time and memory
def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss/1024)
    return memory_consumed

def time_wrapper():
    start_time = time.time()
    # call alg
    end_time = time.time()
    time_taken = (end_time - start_time)*1000
    return time_taken

def record_resource(func):
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        time_taken = (end_time - start_time)*1000
        memory_taken = process_memory()
        return 0
    return wrapper

# Validate the result
def get_output_result(filepath):
    file = open(filepath,"r")
    lines = file.readlines()
    similarity = int(lines[0].replace("\n","").replace("\r",""))
    string1_alignment=lines[1].replace("\n","").replace("\r","")
    string2_alignment=lines[2].replace("\n","").replace("\r","")
    file.close()
    return similarity, string1_alignment, string2_alignment

def get_similarity_of_alignment(string1_alignment,string2_alignment):
    similarity = 0
    for i in range(len(string1_alignment)):
        if string1_alignment[i] == "_" or string2_alignment[i] == "_":
            similarity = similarity + GAP_PENALTY
        else:
            similarity = similarity + MISMATCH_PENALTY[INDEX_OF_CHAR[string1_alignment[i]]][INDEX_OF_CHAR[string2_alignment[i]]]
    return similarity


if __name__=="__main__":
    i = 5
    input_filepath = "./SampleTestCases/input"+ str(i) +".txt"
    output_filepath = "./SampleTestCases/output"+ str(i) +".txt"
    base_string1, indices1, base_string2, indices2 = get_input_data(input_filepath)
    string1 = generate_string(base_string1,indices1)
    string2 = generate_string(base_string2,indices2)
    # similarity_i, string1_alignment_i,string2_alignment_i = align_sequence_basic(string1,string2)
    similarity_i, string1_alignment_i,string2_alignment_i = align_sequence_memory_efficient(string1,string2)
    similarity_o, string1_alignment_o, string2_alignment_o = get_output_result(output_filepath)
    print(similarity_i == similarity_o)
    actual_similarity = get_similarity_of_alignment(string1_alignment_i,string2_alignment_i)
    print(actual_similarity == similarity_o)
    print(string1_alignment_i == string1_alignment_o)
    print(string2_alignment_i == string2_alignment_o)
