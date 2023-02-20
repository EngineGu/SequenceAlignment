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

def write_result_to_file(filepath,string1_count,string2_count,similarity,string1_alignment,string2_alignment, time, memory):
    file = open(filepath,"w")
    file.write(str(string1_count + string2_count)+"\n")
    file.write(str(similarity)+"\n")
    actual_similarity = get_similarity_of_alignment(string1_alignment,string2_alignment)
    file.write(str(actual_similarity)+"\n")
    file.write(str(similarity == actual_similarity)+"\n")
    file.write(string1_alignment+"\n")
    file.write(string2_alignment+"\n")
    file.write(str(time)+"\n")
    file.write(str(memory)+"\n")
    file.close()

# main function
def main():
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]
    base_string1, indices1, base_string2, indices2 = get_input_data(input_filepath)
    string1 = generate_string(base_string1,indices1)
    string2 = generate_string(base_string2,indices2)
    start_time = time.time()
    similarity, string1_alignment,string2_alignment = align_sequence_basic(string1,string2)
    end_time = time.time()
    time_taken = (end_time - start_time)*1000
    memory_consumed =  process_memory()
    write_result_to_file(output_filepath,len(string1),len(string2),similarity,string1_alignment,string2_alignment,time_taken,memory_consumed)

if __name__=="__main__":
    main()
