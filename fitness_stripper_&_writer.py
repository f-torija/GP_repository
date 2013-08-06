import re
import itertools
import csv

def num_stripper(fxn, lower_range, upper_range):
    
    #List initializing all lists
    var_list = []
    var_list_s = []
    char_list = []
    var_dict = {}
    num_list = []
    num_list_t = []
    big_dict = {}
    y_list = []
    iter_list = []

    #Scaled range for .5 incements and create negative range
    upper_lim_sc = int((upper_range+.5)*100)
    lower_lim_sc = int((lower_range)*100)

    #Creates range of numbers
    for x in range(lower_lim_sc, upper_lim_sc, 50):
        x = float(x)/100
        num_list.append(x)
        

    #Function string split into list elements
    split_list = list(fxn)

    #Replace all operators with '!' in new list
    for num in range(len(split_list)):
        if '+' not in split_list[num] and '-' not in split_list[num] and '*' not in split_list[num] and '/' not in split_list[num]:
            char_list.append(split_list[num])
        else:
            char_list.append('!')
            
    #Join all variables and remove all '!' from lists      
    almost_str = ''.join(char_list)
    vars_sub = almost_str.split('!')
    
    #Split fxn into 'x's and numbers
    for elem in vars_sub:
        if 'x' in elem:
            var_list.append(elem)
        else:
            pass
            
##    print "Var_list:", var_list, "Else_list:", else_list   #Debug print
    
    #Removes any repeats in the var_list
    for elem in var_list:
        if elem not in var_list_s:
            var_list_s.append(elem)

    #Creates one tuple for each individual comibination of variables in the
    #range all in one list called 'iters'
    iters = list(itertools.product(num_list,repeat=len(var_list_s)))
    for i in iters:
        iter_list.append(list(i))
    iters.sort()

##    print "Var_list_s:", var_list_s, #Debug print
       
    #Evaluates all of the cases for the given function
    for tup in iters:
        count = 0
        fxn_edt = fxn
        var_list_s.sort()
        for var in var_list_s:
            big_dict[var]= tup[count]
            count+=1
            fxn_edt = fxn_edt.replace(var, str(big_dict[var]))
        y_list.append(eval(fxn_edt))
    
##    print y_list, iter_list   #Debug print

##Preparaion and writing to csv file
    count = 0
    for n in iter_list:
        n.append(y_list[count])
        count+=1

##    print iter_list ##Debug print; make sure y_value is added to iter_list

    var_list_s.append('y')
    
    #Creates writer object
    list_file = open(file_name, 'w+b')
    writer = csv.writer(list_file)
    writer.writerow(var_list_s)
    for elem in iter_list:
        writer.writerow(elem)

if __name__ == '__main__':
    fxn = "3*x0"
    file_name = 'list_file.csv'
    num_stripper(fxn, 1, 10)
