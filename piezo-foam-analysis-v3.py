#Python 2.7
import os, math, glob

#integrate area using a combination of triangles and trapezoids
#returns sum of all positive areas within given range
    #'initial' -> initial index, 'final' -> final index
def exactPosArea(initial, final, time, data):
    area = 0.0
    for i in range(initial, final):
        if ( i + 1 ) >= len(data):
            break
        data_init = float(data[i])
        data_fin = float(data[i + 1])
        dt = float(time[i + 1]) - float(time[i])
        #if two consecutive points have opposite signs (from - to + OR + to -)
        if (data_init > 0) ^ (data_fin > 0):
            #'zero_inter' -> point where line between data points of opposite signs
            #crosses zero
            zero_inter = abs(dt * (max(data_init,data_fin) / (abs(data_fin) + abs(data_init))))
            if 0.5 * zero_inter * (data_init) > 0:
                area += 0.5 * zero_inter * (data_init)
            if 0.5 * zero_inter * (data_fin) > 0:
                area += 0.5 * zero_inter * (data_fin)
        else:   #trapezoidal method
            if 0.5 * (data_init + data_fin) * (dt) > 0:
                area += 0.5 * (data_init + data_fin) * (dt)
    return area

#calculate standard deviation of dataset 'data'
def standardDev(data, data_avg):
    std_tmp = 0.0
    for i in range(len(data)):
         std_tmp += pow((data[i] - data_avg),2)
    return math.sqrt(std_tmp / len(data))

#calculate the average of dataset 'data'
def avg(data):
    return sum([float(i) for i in data]) / len(data)

#open data file, calculate / analyze data, write to analysis file
def main(path):
   with open(os.path.abspath(path), 'r') as fl:
       time = []
       force = []
       current = []

       for lines in fl:
           entries = lines.split()
           if len(entries) > 5:
               continue
           #take time, current, and force values from text data
           time.append(float(entries[0]))
           current.append(float(entries[2]))
           force.append(float(entries[3]))

       #average force and current for first 25 data points
       force_avg25 = avg(force[:25])
       current_avg25 = avg(current[:25])

       #calculate standard deviation of force and current for first 25 data points
       force_std = standardDev(force[:25], force_avg25)
       current_std = standardDev(current[:25], current_avg25)

       #calculate threshold value for force and current using first 25 data points
       force_baseline = force_avg25 + 3*force_std
       current_baseline = current_avg25 + 3*current_std

       #creates list of lists holding all time values for which force
       #is above baseline
       force_times = []
       active_force = []
       i = 0
       while i < len(force):
           while force[i] > force_baseline:
               active_force.append(time[i])
               i += 1
           if active_force != []:
               force_times.append(active_force)
               active_force = []
           i += 1

       #remove all forces with length one(1) or less
       for i in force_times:
           if len(i) <= 1:
               force_times.remove(i)

       #remove final data point to avoid errors with force applied during final time area
       del force_times[len(force_times) - 1]

       #finds the max force applied for each interval of active force
       max_forces = []
       for intervals in force_times:
           tmp_max = 0
           for times in intervals:
               if force[time.index(times)] > tmp_max:
                   tmp_max = force[time.index(times)]
           max_forces.append(tmp_max)

       #calculate each delay between end of force and current going above baseline
       delay_from_end = []
       for i in force_times:
           force_end_time = i[-1]
           end_time_index = time.index(force_end_time)
           while ( current[end_time_index] < current_baseline ):
               end_time_index += 1
               if end_time_index >= len(current):
                   break
           if not end_time_index >= len(current):
               delay_from_end.append(time[end_time_index] - force_end_time)

       avg_delay_from_end = avg(delay_from_end)
       std_delay_from_end = standardDev(delay_from_end, avg_delay_from_end)

       #calculate delay between start of force and current going over baseline
       delay_from_start = []
       for i in force_times:
           end_time_index = time.index(i[0])
           while ( current[end_time_index] < current_baseline ):
               end_time_index += 1
               if end_time_index >= len(current):
                   break
           if not end_time_index >= len(current):
               delay_from_start.append(time[end_time_index] - i[0])

       avg_delay_from_start = avg(delay_from_start)
       std_delay_from_start = standardDev(delay_from_start, avg_delay_from_start)


       #CALCULATE AREA UNDER CURRENT V. TIME CURVES

       #area from start of force using only positive current values
       posArea = []
       max_currents = []
       for i in force_times:
           #calculate area beyond force curve until the mean of 3 consecutive
           #currents is greater than the baseline
           final_index = time.index(i[-1]) + 3
           avg3 = float('inf')
           iteration = 0
           #'avg3' -> most recent three current values, beginning after end of force
           while ( avg3 > 0 ):
               avg3 = avg(current[time.index(i[-1]) + iteration : final_index])
               final_index += 1
               iteration += 1
           posArea.append(exactPosArea(time.index(i[0]), final_index, time, current))

       #calculate peak current values in time period after applied force
       tmp_max = 0
       for i in range(time.index(i[0]), final_index):
           if ( i + 1 ) >= len(current):
               break
           if current[i] > tmp_max:
               tmp_max = current[i]
       max_currents.append(tmp_max)

       #remove all area and force values corresponding to where the area equals zero
       #(zero area corresponds to a non-significant force, only slightly above baseline)
       tmp = 0
       while tmp < len(posArea):
           if posArea[tmp] == 0.0:
               del posArea[tmp]
               del max_forces[tmp]
               tmp -= 1
           tmp += 1

       #remove forces and currents such that all corrected forces are relevant (remove any forces < 0.5 N)
       tmp = 0
       while tmp < len(max_forces):
           if (max_forces[tmp] - force_avg25) < 0.5:
               del max_forces[tmp]
               del posArea[tmp]
               tmp -= 1
           tmp += 1

       #write results of analysis to a new file in the same location with
       #the same name, appended by '_analysis.txt'
       write_target_dir = os.path.abspath(path)[:-4] + '_analysis.txt'
       with open(write_target_dir, 'w') as newFile:
           #column headers
           newFile.write('Applied Force\t')
           newFile.write('Corrected Force\t')
           newFile.write('Charge <positive only>\t')
           newFile.write('\n')

           #data
           for i in range(len(max_forces)):
               newFile.write(str(max_forces[i]) + '\t')
               newFile.write(str(max_forces[i] - force_avg25) + '\t')
               newFile.write(str(posArea[i]) + '\t')
               newFile.write('\n')


########################################################################################

rootdir = os.path.abspath(raw_input('Enter starting directory: '))

#case if data text file path is entered directly
if rootdir.endswith('.txt') and not rootdir.endswith('analysis.txt'):
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
        for t in glob.iglob('*.txt'):
            #catch to bypass analysis text files located in the same folder
            if not t.endswith('analysis.txt'):
                main(t)

        #reset current working directory to the root directory in order to
        #move onto the next file
        os.chdir(rootdir)
        #break out of excess loops
        if end_break:
            break
