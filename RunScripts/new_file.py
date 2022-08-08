import re


mystring="Exit Location: (28.5367,31.7143,8.79)"
mystring = mystring[::-1]
result = re.search('\)(.*?)\,', mystring).group(1)[::-1]
#print(result.group(1)[::-1])
print (result)


def get_locations(content, i, res, detector_size, scintilator_size , scint_1_center):
    global NUMBER_OF_SLABS
    const_slabs = NUMBER_OF_SLABS
    scint_zdim = [[]]
    enter_ordered = []
    #start = ','
    for j in range(const_slabs):
        scint_zdim[j]= [scint_1_center-scintilator_size/2 + detector_size*j, scint_1_center+scintilator_size/2 + detector_size*j]
    #old_len = len(res)
    while i < len(content):
        i += 1
        if "Enter Location" in content[i]: # or "Exit Location" in content[i]:
            if NUMBER_OF_SLABS == 0:
                continue
            string = content[i][16:][::-1]
            zdim_enter = re.search('\)(.*?)\,', string).group(1)[::-1]
            for j in range(const_slabs):
                if zdim_enter.float < scint_zdim[j][1].float and zdim_enter.float > scint_zdim[j][0].float:
                    enter_ordered[j] = content[i][16:]
            #res.append(content[i][16:])
            NUMBER_OF_SLABS -= 1
        elif "Number of" in content[i]:
            for j in range(const_slabs):
                if  not enter_ordered[j]:
                    enter_ordered[j] = 'None'
            break
    
    res.append(enter_ordered) # MAYBE I need to loop on all the 5 options in enter_ordered
    # if len(res) < old_len + 2:  # in case the particle stopped in this slab
    #     res.append('None')
    return i


def add_missing_slabs(res):
    global NUMBER_OF_SLABS
    while NUMBER_OF_SLABS > 0:
        res.append('None') # enter
        # res.append('None') # exit
        NUMBER_OF_SLABS -= 1
