# Write a code to automate the collection of the five things I collect from each conductivity file, plus perhaps others.
# That is, the fitting parameters for the Arrhenius plot, the exponent for the power law plot, these two plots.
# The Zabrodskii plot and the conductivity values at 310 K and 435 K.
# The date -- Can combine sample information in excel or something -- would rather find a way to do it in python, but that's not how the data is organized.


import numpy as np
from scipy import optimize
import matplotlib
#matplotlib.rc('text', usetex=True)
matplotlib.rc('xtick', labelsize=12) 
matplotlib.rc('ytick', labelsize=12) 
import matplotlib.pyplot as plt

# Load in a conductivity file. Don't change filenames until later.

filename_freq = input("Enter the Conductivity file you would like to process: ")
print("Your file is ",filename_freq)
f_freq = open(filename_freq,'r')
freq_content = f_freq.readlines()
f_freq.close()


# treat date the way I treat voltage in the volt depend code.
sample_name = input("What is the sample name of this file? ")
t_ramp = input("Is this a heat-up (300to450) (enter ' h') or cool-down (450to300) (enter 'c') file? ")
if t_ramp != 'h':
	if t_ramp != 'c':
		print("Please type 'h' or 'c'")

data_file = []
date_input = input("What is the date of this file in YYYYMMDD? ")
data_file.append(date_input)



# Turn that power spectrum file into an array for python to understand.
headerlen_freq = 19  # 5 for test file, 25 for real file
footerlen_freq = 2 # 2 for test file, 2 for real file?
trim_content_freq = freq_content[headerlen_freq:len(freq_content)-footerlen_freq]

freq_data = []
for row in range(len(trim_content_freq)):
	temp = trim_content_freq[row].split("\t")
	temp[len(temp)-1]=temp[len(temp)-1].rstrip() # remove new line character (\n) from last element
	for item in range(len(temp)):
		temp[item] =float(temp[item])
	freq_data.append(temp)

#print(freq_data)


m_temp = []
temp =[]
for bin in range(len(freq_data[0])):
	for trace in range(len(freq_data)):
		temp.append(freq_data[trace][bin])
	m_temp.append(temp)
	temp = []
#print(m_temp)
m_temp = np.asarray(m_temp) # change into an array that we can do math with.
# m_temp contains the data in arrays such as:
# m_temp[0] = Time(s)
# m_temp[4] = Temperature Sample (K)
# m_temp[5] = 1/kT Sample (1/eV)
# m_temp[7] = Current (A)
# m_temp[9] = Conductivity (Ohm-cm)^-1

# Fit Conductivity vs 1/kT to an exponential -- the Arrhenius plot. Plot as a semi-log (y) plot.

ln_cond = np.log(m_temp[9])
out = optimize.curve_fit(lambda t,a,b: a+b*t, m_temp[5], ln_cond, p0 = (1,-.4))
#print(out)
pfinal = out[0]
print(pfinal)
print(np.exp(pfinal[0]))
data_file.append(np.exp(pfinal[0]))
data_file.append(np.abs(pfinal[1]))
plt.figure()
plt.semilogy(m_temp[5], m_temp[9], 'b-', label='data')
plt.semilogy(m_temp[5], np.exp(pfinal[0])*np.exp(pfinal[1]*m_temp[5]), 'r-', label='fit')
plt.legend()
plt.title('Arrhenius Conductivity Fit \n Sample: '+sample_name+', Date: '+date_input)
plt.xlabel('1/kT Sample (1/eV)')
plt.ylabel('Conductivity (Ohm-cm)^-1')
if t_ramp == 'c':
	plt.text(m_temp[5][0],m_temp[9][len(m_temp[9])-1],'$\sigma (T) = %5.2f * e^{%5.4f/{kT}}$' %(np.exp(pfinal[0]),pfinal[1]),fontsize = 16)#cool-down
if t_ramp == 'h':
	plt.text(m_temp[5][len(m_temp[5])-1],m_temp[9][0],'$\sigma (T) = %5.2f * e^{%5.4f/{kT}}$' %(np.exp(pfinal[0]),pfinal[1]),fontsize = 16)#heat-up
plt.tight_layout()
	
log_cond = np.log10(m_temp[9])
log_T = np.log10(m_temp[4])
out = optimize.curve_fit(lambda t,a,b: a+b*t, log_T, log_cond, p0 = (1,-.4))
#print(out)
pfinal = out[0]
print(pfinal)
print(10**pfinal[0])
data_file.append(pfinal[1])
plt.figure()
plt.loglog(m_temp[4], m_temp[9], 'b-', label='data')
plt.loglog(m_temp[4], 10**pfinal[0]*m_temp[4]**pfinal[1], 'r-', label='fit')
plt.legend()
plt.title('Power Law Conductivity Fit')
plt.xlabel('1/kT Sample (1/eV)')
plt.ylabel('Conductivity (Ohm-cm)^-1')
if t_ramp == 'c':
	plt.text(m_temp[4][len(m_temp[4])-1],m_temp[9][0]/3,'$\sigma (T) = ({%1.2e})*T^{%5.4f}$' %(10**pfinal[0],pfinal[1]),fontsize = 16) #cool-down
if t_ramp == 'h':
	plt.text(m_temp[4][0],m_temp[9][len(m_temp[9])-1]/10,'$\sigma (T) = %5.2f * e^{%1.2e/{kT}}$' %(10**pfinal[0],pfinal[1]),fontsize = 16) #heat-up
plt.tight_layout()


# Now to collect cond(310 K) and cond(435 K).
# This is all specific to cool-down files so far. (The graph text labels are.) I can now use my if-else condition to fix this.
t_step = 0.1
if t_ramp == 'c':
	print('310 K = %5.2f K' %m_temp[4][int(len(m_temp[4])-1-10/t_step)]) # T = 310 K
	print('435 K = %5.2f K' %m_temp[4][int(15/t_step)]) # T = 435 K
	data_file.append(m_temp[9][int(len(m_temp[4])-1-10/t_step)])
	data_file.append(m_temp[9][int(15/t_step)])
if t_ramp == 'h':
	if t_step == 1:
		print('310 K =  %5.2f K' %m_temp[4][int(10/t_step)]) # T = 310 K	
		print('435 K = %5.2f K' %m_temp[4][int(len(m_temp[4])-1-15/t_step)]) # T = 435 K
		data_file.append(m_temp[9][int(10/t_step)])
		data_file.append(m_temp[9][int(len(m_temp[4])-1-15/t_step)])
	elif t_step == 0.1:
		print('310 K =  %5.2f K' %m_temp[4][int(79)]) # T = 310 K	
		print('435 K = %5.2f K' %m_temp[4][int(len(m_temp[4])-121)]) # T = 435 K
		data_file.append(m_temp[9][int(10/t_step)])
		data_file.append(m_temp[9][int(len(m_temp[4])-1-130)])


print(data_file)
plt.show()

# Everything I need is now in variable data_file. Now to add it to a txt file. Go back to copying the code 'fit_PS_Gauss.py'.

save_file = input("Would you like to save this data to the overall txt file ('y' or 'n')? ")

if save_file == 'y':

	new_file = input("Is this a new file ('y' or 'n')? ")
	if new_file == 'n':
		if t_ramp == 'c':
			f = open("all_cond_"+sample_name+"_450to300.txt","r")
		elif t_ramp == 'h':
			f = open("all_cond_"+sample_name+"_300to450.txt","r")			
		f_content = f.readlines()
		f.close()
		#print(f_content)
		data_array = []
		for row in range(len(f_content)):
			temp = f_content[row].split("\t")
			temp=temp[:len(temp)-1] # remove new line character (\n) from last element
			for item in range(len(temp)):
				temp[item] =float(temp[item])
			data_array.append(temp)
		
		data_array.append(data_file)
		
		if t_ramp == 'c':
			f = open("all_cond_"+sample_name+"_450to300.txt","w+")
		elif t_ramp == 'h':
			f = open("all_cond_"+sample_name+"_300to450.txt","w+")
		for i in range(len(data_array)):
			for j in range(len(data_array[0])):
				f.write(str(data_array[i][j])+'\t')
			f.write('\n')
		f.close()
		
	elif new_file == 'y':
		if t_ramp == 'c':
			f = open("all_cond_"+sample_name+"_450to300.txt","w+")
		elif t_ramp == 'h':
			f = open("all_cond_"+sample_name+"_300to450.txt","w+")
		for i in range(len(data_file)):
			f.write(str(data_file[i])+'\t')
		f.write('\n')
		f.close()
	else:
		print("Please type 'y' or 'n' 1")	

elif save_file == 'n':
	print("Enjoy your data! This isn't being saved.")

else:
	print("Please type 'y' or 'n' 2")

