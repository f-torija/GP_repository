def fitness_case_gen(fxn, range_limits=10, neg_range=True):
    """Takes a function as a string and creates a number list for the GPsearch"""
    fitness_list = []
    target_list = []
    range_lim_c = range_limits*100
    if not neg_range:
        negs = 0
    else:
        negs = range_lim_c*-1
  
    if 'x0' in fxn:
        for x0 in range(negs, range_lim_c, 50):
            x0 = float(x0)/100
            if 'x1' in fxn:
                for x1 in range(negs, range_lim_c, 50):
                    x1 = x1/100
                    list_1 = [x0,x1]
                    solution = eval(fxn)
                    fitness_list.append(list_1)
                    target_list.append(solution)
                
            else:
                solution = eval(fxn)
                list_1 = [x0]
                fitness_list.append(list_1)
                target_list.append(solution)
        print target_list, fitness_list    
        
    elif 'x1' in fxn and not 'x0' in fxn:
        for x1 in range (negs, range_lim_c, 50):
            x1 = float(x1)/100
            list_1 = [x0,x1]
            solution = eval(fxn)
            fitness_list.append(list_1)
            target_list.append(solution)
            return target_list, fitness_list
##For numerical only cases
##    else:
##        for _ in range(negs, range_lim_c, 50):
##            try:
##                solution = eval(fxn)
##                fitness_list.append(
##            except:
##                pass
            
if __name__ == '__main__':
    fitness_case_gen('x0**2+2*x1', 5, False)

