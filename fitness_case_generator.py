import csv
def fitness_case_gen(fxn, range_limits=10, neg_range=True):
    """Takes a function as a string and creates a number list for the GPsearch"""
    fitness_list = []
    target_list = []
    var_list = []
    var_list.insert(0, 'y')
    range_lim_c = int((range_limits+.5)*100)
    if not neg_range:
        negs = 0
    else:
        negs = range_lim_c*-1
    var_list.insert(0,'x0')
    for x0 in range(negs, range_lim_c, 50):
        x0 = float(x0)/100
        if 'x1' in fxn:
            
            for x1 in range(negs, range_lim_c, 50):
                x1 = float(x1)/100
                list_1 = [x0,x1]
                solution = eval(fxn)
                fitness_list.append(list_1)
                target_list.append(solution)
            
        else:
            solution = eval(fxn)
            list_1 = [x0]
            fitness_list.append(list_1)
            target_list.append(solution)
    if 'x1' in fxn:
        var_list.insert(1,'x1')
    list_file = open('list_file.csv', 'w+b')
    writer = csv.writer(list_file)
    writer.writerow(var_list)
    range_of_val = ((range_lim_c-negs)/50)**2
    
    for i in range(range_of_val):
        writer.writerow((fitness_list[i][0], fitness_list[i][1] , target_list[i]))
    
    
            
if __name__ == '__main__':
    fitness_case_gen('x0**2', 5, False)

