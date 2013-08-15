import re
import itertools
import csv


def get_range(train_range, test_range):
    """Creates lower and upper range for test and train data"""
    tests = []
    trains = []
            
    if len(test_range) == 3:
        test_increment  = test_range[2]
    else:
        test_increment = .5
        
    if len(train_range) == 3:
        train_increment = train_range[2]
    else:
        train_increment = .5
   
    test_scale = 1/test_increment                   
    upper_lim_ts = int((test_range[1]+test_increment)*test_scale)
    lower_lim_ts = int(test_range[0]*test_scale)

    train_scale = 1/train_increment
    upper_lim_tr = int((train_range[1]+train_increment)*train_scale)
    lower_lim_tr = int(train_range[0]*train_scale)
    
    
    #Creates range of numbers
    for y in range(lower_lim_ts, upper_lim_ts):
        y = float(y)/test_scale
        tests.append(y)

    for x in range(lower_lim_tr, upper_lim_tr):
        x = float(x)/train_scale
        trains.append(x)
        
    return trains,tests
        
def split_function(fxn):
    split_list = []
    char_list = []
    operators = ['+', '-', '/', '*', '**']
    
    #Function string split into list elements
    split_list = list(fxn)

    #Replace all operators with '!' in new list
    for char in split_list:
        if  char in operators :
            char_list.append('!')
            
        else:
            char_list.append(char)

    char_str = ''.join(char_list)
    split_chars = char_str.split('!')
    var_list = []
    #Split fxn into 'x's and numbers
    for elem in split_chars:
        if 'x' in elem:
            var_list.append(str(elem))
        else:
            pass
              
    #Removes any repeats in the var_list
    var_set = set(var_list)
    var_list= list(var_set)
    return var_list

def fitness_targets_gen(var_set, ranges):
    """Creates one tuple for each individual comibination of variables in the
    range all in one list called 'iters' and generates the targets based on the
    function and each fitness case."""
    var_set = list(var_set)
    big_dict = {}
    
    iters = list(itertools.product(ranges,repeat=len(var_set)))
    
    #Make all elements lists instead of tuples to allow appending
    iters = map(list,iters)
    iters.sort()
    var_set.sort()
    
    for fit_case in iters:
        count = 0
        fxn_edt = fxn
        for var in var_set:
            big_dict[var]= fit_case[count]
            count+=1
            fxn_edt = fxn_edt.replace(var, str(big_dict[var]))
        fit_case.append(eval(fxn_edt))
          
    return iters

def write_to_file (fitness_case, var_set, path):
    """Preparaion and writing to csv file, creation of writer object and write
    to file"""
    header = var_set
    header.append('y')
    list_file = open(path, 'w+b')
    writer = csv.writer(list_file)
    writer.writerow(header)
    for fit in fitness_case:
        writer.writerow(fit)
    
def stripper_gen_writer(fxn, train_range, test_range):
    """Generates and writes fitness cases and targets to a csv file to be read
    by the ponyGP.py"""
    
    trains, tests = get_range(train_range, test_range)
    
    var_list = split_function(fxn)
    
    fitness_train = fitness_targets_gen(var_list, trains)
    fitness_test = fitness_targets_gen(var_list,tests)
    
    fitness_cases = fitness_train, fitness_test
    
    files = file_name_train, file_name_test    
    for fit,path in zip(fitness_cases,files):
        write_to_file(fit, var_list, path)

if __name__ == '__main__':
    fxn = "12*x0-3*x1"
    file_name_train = 'list_file_train.csv'
    file_name_test = 'list_file_test.csv'
    files = file_name_train,file_name_test 
    stripper_gen_writer(fxn, [-2,2,.5], [3,5,.5])
