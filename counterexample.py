# coding=utf-8
from collections import defaultdict

def count_beginning_of_cycle(string):
    return string.count("Beginning of Cycle")

def get_words_after_second_space(string_array):
    if len(string_array) < 2:
        return "输入的字符串数组至少应包含两个字符串"

    result = []
    for string in string_array[1:]:
        words = string.split()
        if len(words) >= 3:
            result.append(words[2])
        else:
            result.append("第二个后的单词不存在")
    return result

def get_arr_value(string_array,kong_int):
    if len(string_array) < 2:
        return "输入的字符串数组至少应包含两个字符串"
    result = []
    for string in string_array[1:]:
        words = string.split()
        if len(words) >= 3:
            result.append(words[kong_int])
        else:
            result.append("第"+kong_int+"个后的单词不存在")
    return result
def print_string_pairs(array1, array2):
    if len(array1) != len(array2):
        return "两个数组长度不相等，无法按序列成对输出"

    for i in range(len(array1)):
        print(f"{array1[i]}={array2[i]}",end=' ')

print('input Counterexample:')
arr = []
while True:
    s = input()
    if s == '':
        break
    arr.append(s)

cyclenum = count_beginning_of_cycle(arr[0])
arrname = get_words_after_second_space(arr)

count=3
while(count<=(2*(cyclenum+1))):
    arr_value = get_arr_value(arr,count)
    if count%2 == 0:
        print('cycle'+str(int(count/2-1))+'end',end=' ')
    else:
        print('cycle' + str(int((count+1)/2-1))+'start', end=' ')
    print_string_pairs(arrname,arr_value)
    print()
    count = count+1