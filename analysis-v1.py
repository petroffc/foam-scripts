# Christopher Petroff
# Hutchison Group
# University of Pittsburgh
# September 2017

import numpy as np
import math
import statsmodels.api as sm
import os, glob

################################################################################
# Help format displayed stats.                                                 #
# Source: http://randlet.com/blog/python-significant-figures-format/           #
################################################################################
def to_precision(x,p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/num
    ber_object.cpp
    """

    x = float(x)

    if x == 0.:
        return "0." + "0"*(p-1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)

    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1

    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return "".join(out)
################################################################################

# Process files.
def main(path):
    with open(os.path.abspath(path), 'r') as fl:
        title = path[:-13]
        # Load data & remove force values over 10N (outside sensor calibration).
        a = np.loadtxt(path, skiprows=1, usecols=(1,2), unpack=True)
        x, y = a[:, a[0]<=10]

        # Calculate linear regression through origin.
        model = sm.OLS(y, x)
        results = model.fit()
        slope = results.params
        #print "Slope", results.params
        r_value = results.rsquared
        #print "R-Squared", results.rsquared
        std_err = results.bse
        #print "Standard Error", results.bse
        #print results.summary()

        # Round stats for display.
        slope_r = to_precision(slope, 3)
        r_value_r = to_precision(r_value, 2)
        std_err_r = to_precision(std_err, 2)
        #print "Rounded Slope", slope_r
        #print "Rounded R-Squared", r_value_r
        #print "Rounded Standard Error", std_err_r

        # Print data for easy copy and paste to excel.
        print(str(title) + ' ' + str(slope_r) + ' ' + str(std_err_r) + ' ' +
              str(r_value_r))

################################################################################
# Iterate through all files in directory.                                      #
# Adapted from Tom's peak finding script.                                      #
################################################################################
rootdir = os.path.abspath(raw_input('Enter starting directory: '))

# Print header row for data output [here to avoid repetition for each file].
print('Sample Slope Std_Err R-Squared')

#case if data text file path is entered directly
if rootdir.endswith('analysis.txt'):
    main(rootdir)

#case if folder containing data files is entered
else:
    os.chdir(os.path.abspath(rootdir))

    #used to break out of excess loops if 'rootdir' contains data text files
    end_break = False

    #go through each day's folder within the overall data folder
    for f in glob.iglob('*'):
        #error catch if individual data folders are selected
        if('.' not in f):
            os.chdir(os.path.abspath(f))
        else:
            end_break = True
        #go through each data text file and perform calculations
        for t in glob.iglob('*analysis.txt'):
            main(t)

        #reset current working directory to the root directory in order to
        #move onto the next file
        os.chdir(rootdir)
        #break out of excess loops
        if end_break:
            break
################################################################################
