# (C) 2014-2015 Georg Meisl, Elke Schaper

"""
    :synopsis: ``analysis_prion_propagation_model`` implementes all methods
    connected to the parameter estimation for prion propagation models.
"""

import logging
import numpy as np
from scipy import optimize as opt
import sys
import os
from scipy import misc, special
from matplotlib import pyplot as plt
from matplotlib.colors import colorConverter

# This imports where introduced using futurize to port Python 2 to Python 3 code:
from past.utils import old_div


LOG = logging.getLogger(__name__)


##############################
# DETERMINING INPUT PARAMETERS
##############################
def prion_fitter_input_parameters(dilutions_list):
    ''' Create input parameters for  `fit_prion_model` '''

    parameter_names = ['N_propagons', 'd', 'a', 'nsat', 'mu', 'sig']
    identifiers_all = np.zeros([len(dilutions_list), 6])
    parameters_all = np.zeros([len(dilutions_list), 6])

    for i in range(len(dilutions_list)):
        parameters_all[i,0] = 2*min(dilutions_list)			# number of propagons per well for an undiluted sample 		NEED GOOD GUESS HERE!!!
        parameters_all[i,1] = dilutions_list[i]				# dilutions - known
        parameters_all[i,2] = 1 								# increase in mean signal per prion							NEED GOOD GUESS HERE!!!
        parameters_all[i,3] = 15 							# number of propagons when signal saturates					NEED GOOD GUESS HERE!!!
        parameters_all[i,4] = 0#np.mean(all_neg_controls[i])	# mean of neg control - 0 if normalised
        parameters_all[i,5] = 1#np.std(all_neg_controls[i])	# standard dev of neg control - 1 if normalised

    # Identifiers determine what kind of parameter it is, i.e. 0 means known constant, 1 means global fitting parameter
        identifiers_all[i,0] = 1 								# number of propagons per well for an undiluted sample 		NEEDS TO BE FITTED!!
        identifiers_all[i,2] = 1 								# increase in mean signal per prion	 						NEEDS TO BE FITTED!!
        identifiers_all[i,3] = 1 								# number of propagons when signal saturates			should be fitted but guess around 10 seems to work and not have massive effect
        identifiers_all[i,5] = 0 								# standard dev; 									we can assumes this is same as for neg control, but it can be fitted for nicer results.
    ##############################
    return parameter_names, identifiers_all, parameters_all


##############################
# CONVERTING TO THRESHOLD DATA
##############################
def point_counter(threshold,data):
    """
    Calculate fraction of elements in data smaller than threshold.
    """
    return(sum(i < threshold for i in data)/len(data))

def global_const_threshold(data, k = 100, threshold_limit = 0.1):
    """
    Choose minimum and max thresholds and evaluates the fraction of points
    below the threshold at k intermediate thresholds

    The calculation of thres_data can be sped up (instead of calling point_counter again and again.)

    Args:
        data (np.array OR list of floats): The input data.
        k (int): The number of intermediate thresholds.
        threshold_limit (float): The percentage of the range of min and max value of data, that is used to extend the range to both sides.

    Returns:
        np.array: Thresholds
        np.array: Fraction of points below the threshold.
    """
    data_min = min(data)
    data_max = max(data)
    thres_min = data_min - threshold_limit*(data_max - data_min)  # minimum threshold is below the lowest point.
    thres_max = data_max + threshold_limit*(data_max - data_min) # maximum threshold is above the highest point.
    thresholds = np.linspace(thres_min, thres_max, num=k) # list of thresholds at which fraction below will be evaluated. should give nice sigmoidal with a bit of the plateau before and after.
    thres_data = [point_counter(i_t, data) for i_t in thresholds] # evaluates the fraction of points below the threshold at k evenly spaced points between the minimum and the maximum threshold
    return np.array(thresholds), np.array(thres_data)
#############################


#############################
# NORMALISING DATA TO NEGATIVE CONTROL MEAN AND STDEV
#############################
def neg_control_normaliser(data_sample, data_nc):
    """
    Calculate the fraction of `data_sample` below ascending thresholds.
    Then, normalise the data by mean and std of the negative controls.
    #Elke: In fact, the thresholds are normalized. I don't know why.

    Args:
        data_sample (np.array nx2): define.
        data_nc (np.array): Negative control values.

    Returns:
        np.array nx2: First column: Normalized values. Second column: Threshold values.
    """
    nc_mean = np.mean(data_nc)
    nc_std = np.std(data_nc)
    thresholds, fraction_data_below_threshold = global_const_threshold(data_sample)
    return np.array([(thresholds - nc_mean)/nc_std, fraction_data_below_threshold]).transpose()

#############################


##############################
# EQUATIONS FOR FITTING
##############################
def prions_fbelow_sat(t, n_propagons, d, a, nsat, mu, sig, n_sum=150):
    """
    Calculate <define>.

    Args:
        d (?): Dilution
        t (float): Threshold
        n_propagons (int): The initial number of propagons per well if the sample was not diluted
        a (?): the increase in fluorescence per prion
        data_nc (np.array): Negative control values.
        n_sat (?): the number of prions upon which the fluorescence increase saturates (i.e. adding more prions will not increase the fluorescence significantly)
        mu (?): average value of the negative control
        sig (?): standard deviation of the negative control
        n_sum (int): The number of terms to be summed over. The more terms the more accurate, but the more time the fitting will take. roughly time taken for fitting is porportional to N_sum

    Returns:
        float: <define>

    """
    return np.sum((n_propagons/d)**i*np.exp(-n_propagons/d)/misc.factorial(i)*special.erfc((nsat*a*i/(nsat+i)+mu-t)/np.sqrt(2)/sig)/2 for i in range(n_sum))


def fit_prion_model(times, data, all_parameters_temp, identifiers,
                    parameter_names, model_function, basinhops=3):

    """
    Calculate <define>.

    Args:
        times (n_timepoints by n_runs arrays): <define> # Normalised thresholds
        data (n_timepoints by n_runs arrays): <define> # Fractions below the threshold
        all_parameters_temp (list of ?): A list of all temporary parameters
        identifiers (np.array of np.array of float): A matrix of ones and zeros with two entries for each parameter
        parameter_names (list of str): The name of all parameters: Those that need fitting, and those that are given.
        model_function (func): <define>
        basinhops (int): <define>

    Returns:
        <define>

    .. ToDo:
        - Define what is meant by "timepoints"
    """

    n_parameters=len(parameter_names) # Number of parameters (to be fit, and given)
    n_runs=len(all_parameters_temp[:,0]) # Number of experiments run
    n_timepoints=len(times[:,0]) # Number of "timepoints"
    all_parameters=all_parameters_temp
    for i in range(n_runs):
        for k in range(n_parameters):
            if all_parameters_temp[i,k]==0 and not identifiers[i,k]==0:
                all_parameters[i,k]=1e-20 #an initial guess of zero is pointless and also won't be fitted as parameters are varied multiplicatively in the fitting algorithm


    #>>>>>>>>START>>>>>>>>
    #### FORMATTING PARAMETERS ###
    ##find which parameters are known; this is nust to create output to check, is not needed in actual fitting algorithm
    known_names=list()                                       #names of parameters that are known
    known_numbers=list()                                     #positions of parameters that are known

    for k in range(n_parameters):
        numbers_temp=list()
        for i in range(n_runs):
            if identifiers[i,k]==0 and numbers_temp==list():
                known_names.append(parameter_names[k])
            if identifiers[i,k]==0:
                numbers_temp.append(i+1)
        if not numbers_temp==list():
            if numbers_temp==list(range(1,n_runs+1)): known_numbers.append('all')
            else: known_numbers.append(np.array(numbers_temp))
    known_string='\nThe known parameters are:'
    for i in range(len(known_names)):
        known_string=str(known_string)+'\n'+str(known_names[i])+' for runs '+str(known_numbers[i])


    ##find which parameters are fitting parameters and put them into vector b_init for input into fitting
    ##determine positions of fitting parameters and put them into list pos; i.e. pos will be a list of arrays of coordinates. All coordinates within an array will be fitted globally.
    # The value of the parameter for each list in pos is given in b_init at the same position as the list in pos.
    b_init_list=list()
    pos=list()
    for k in range(n_parameters): #go through each parameter
        for i in range(1,n_runs+1):  #go through all possible numbers of groups
            first_in_group=-1
            temp_pos=list()
            for l in range(n_runs):  #check if identifier corresponds to current group number for each run
                if identifiers[l,k]==i and first_in_group==-1:  #if first parameter in a new group
                    b_init_list.append(all_parameters[l,k]) #append value of this parameter
                    first_in_group=l  #remember position of first parameter in group
                    temp_pos.append([l,k])  #append position of this parameter
                elif identifiers[l,k]==i and not first_in_group==-1 and all_parameters[first_in_group,k]==all_parameters[l,k]:  #parameter in an already existing group
                    temp_pos.append([l,k])  #append position of this parameter

            if not temp_pos==list():  #check if any groups with number i are present in kth column
                pos.append(np.array(temp_pos))  #append positions of group with number i in column k
    #### FORMATTING PARAMETERS ###
    #<<<<<<<END<<<<<<<<<<

    #import pdb; pdb.set_trace()

    # Needed is:
    # b_init: [40000.0, 1.0, 15.0]
    # data: 100*2
    # times: 100*2
    # all_parameters 2*6
    # pos: 3*2*2 [array([[0, 0],[1, 0]]), array([[0, 2], [1, 2]]), array([[0, 3], [1, 3]])]
    # basinhops: 1
    # n_runs: 2
    # model_function: model

    #### FITTING ####
    b_init=np.array(b_init_list)  # construct a vector with all fitting parameters (global, indiv_run1, indiv_run2, ...)
    all_parameters_fit, b_fit, fit = fitting(b_init, data, times, all_parameters, pos, 10000, 1e-14, basinhops, n_runs, model_function)
    #import pdb; pdb.set_trace()
    errors_low, errors_up = error_estimator(b_fit, data, times,all_parameters_fit, pos, n_runs, model_function, all_parameters)
    LOG.info('\n\nFITTING RESULTS:\n{}{}\n'.format(fit, all_parameters_fit))
    return all_parameters_fit, fit, errors_low, errors_up
###############################


#>>>>>>>>START>>>>>>>>
### FUNCTION DEFINITIONS ###

def parameter_builder(b_tot,all_parameters,pos):
    #b_tot are the fitting parameters only. This reconstructs a vetor of all parameters for each of the runs for input into M_diff_single from b_tot.
    all_parameters_new=all_parameters
    for i in range(len(pos)):
        for k in pos[i]:
            all_parameters_new[(k[0],k[1])]=b_tot[i]
    return all_parameters_new

def M_diff_single(para_scale,para,data_run,t,model_function):
    scaled_para=list(para_scale*abs(para))
    return model_function(t,*scaled_para) - data_run


def M_diff_total(b_tot,datain,times,all_parameters,pos, n_runs, model_function):
    #Calculates the difference between the calculated values for the aggregate concentration and the measured data for all runs to produce a global fit.
    #b_tot are the fitting parameters only. It needs to be done this way due to the way opt works.
    all_parameters_new=parameter_builder(b_tot,np.ones_like(all_parameters),pos)   #due to the rescaling with the initial guess we want ones in the positions which are constants
    Mdiff=0
    for i in range(n_runs):
        Mdiff=Mdiff+np.sum(M_diff_single(all_parameters[i],all_parameters_new[i],datain[:,i],times[:,i],model_function)**2)
    return Mdiff

class MyTakeStep(object):
    def __init__(self, stepsize=1.0):
            self.stepsize = stepsize
            self.step = 0
    def __call__(self, x):
        self.step += 1
        LOG.info('fit progress: {} of 20'.format(self.step))
        r = (self.stepsize*np.random.rand(*x.shape)+1.0)**(np.random.choice([-1,1], size=x.shape))
        a = r*x
        return a

def fitting(b_init,data,times,all_parameters,pos,n_iterations,err_tol,basinhops,n_runs, model_function):
    ## actual fitting
    #fit=opt.fmin(M_diff_total,b_init,args=(data,times,all_parameters,pos),ftol=err_tol,xtol=err_tol,full_output=True,maxfun=n_iterations,maxiter=n_iterations)
    mytakestep = MyTakeStep()
    LOG.info('fit progress: {} of 20'.format(0))
    fit=opt.basinhopping(M_diff_total, np.ones_like(b_init), take_step=mytakestep, minimizer_kwargs={'method':'Nelder-Mead', 'args':(data,times,all_parameters,pos, n_runs, model_function)}, niter=basinhops, disp=True, interval=10)
    b_fit=abs(fit['x'])*b_init

    ## Now rebuild the correct format for the parameters; same as in M_diff_total
    all_parameters_fit=parameter_builder(b_fit,all_parameters,pos)
    return all_parameters_fit, b_fit,fit

def create_single_var_fct(para_for_err, para_ind, b_fit, data, times,parameters, pos, required_accuracy,n_runs, model_function):
    """
    (Helper function for error estimation.)
    Calculate input function with the para_ind-th parameter replaced by
    para_for_err, i.e. this is a function which takes as the first argument any
    one of the parameters in Mdiff_total required accuracy determines how much
    Mdiff can increase, i.e. how likely it is that a measurement falls into the
    given bounds. E.g. 1/2 would correspond to 1 stdev around the mean.
    """
    b_fit_single_changed=np.ones_like(b_fit)
    b_fit_single_changed[para_ind]=para_for_err
    LOG.debug('b_fitsinglech: {}'.format(b_fit_single_changed))
    return M_diff_total(b_fit_single_changed,data,times,parameters,pos,n_runs,model_function)-M_diff_total(np.ones_like(b_fit),data,times,parameters,pos,n_runs,model_function)-required_accuracy

def error_estimator(b_fit, data, times,parameters, pos, n_runs, model_function, all_parameters, required_accuracy=0.5):
    """
    returns an array of errors, same layout as the corresponding parameters
    sort this out to make sure it only varies fitting parameters!!!
    """
    errors_temp_up=np.ones_like(b_fit)
    errors_temp_low=np.ones_like(b_fit)
    for i in range(len(b_fit)):
        for bound_up in (1.01,1.02,1.05,1.1,1.2,1.5,2.0,10):
            funval=create_single_var_fct(bound_up,i,b_fit,data,times,parameters,pos,required_accuracy,n_runs, model_function)
            if funval>0:         #i.e. the function values at the 2 bound differ, which is needed for brentq
                errors_temp_up[i]=opt.brentq(create_single_var_fct,1.0,bound_up ,args=( i, b_fit, data, times,parameters, pos,required_accuracy, n_runs, model_function)) #finds where the difference in errors equals required_accuracy; the initial guess is 1 due to rescaling
                break
            elif bound_up==10: #if twice the value still gives no sign change, the error is larger than double, just return 2
                errors_temp_up[i]= 10
        for bound_low in (0.99,0.98,0.95,0.9,0.8,0.7,0.6,0.5,0.1): #same as obove with upper bounds only this time the limit is 1/2
            funval=create_single_var_fct(bound_low,i,b_fit,data,times,parameters,pos,required_accuracy,n_runs,model_function)
            if funval>0:
                errors_temp_low[i]=opt.brentq(create_single_var_fct,1.0,bound_low ,args=( i, b_fit, data, times,parameters, pos,required_accuracy, n_runs,model_function)) #finds where the difference in errors equals required_accuracy; the initial guess is 1 due to rescaling
                break
            elif bound_low==0.1:
                errors_temp_low[i]= 0.1
    errors_b_up=(errors_temp_up-np.ones_like(b_fit))*b_fit
    errors_b_low=(errors_temp_low-np.ones_like(b_fit))*b_fit
    errors_low=parameter_builder(errors_b_low,0*all_parameters,pos) #input a zero array so all constants will have 0 error
    errors_up=parameter_builder(errors_b_up,0*all_parameters,pos) #input a zero array so all constants will have 0 error
    return np.abs(errors_low), errors_up


### FUNCTION DEFINITIONS ###
#<<<<<<<END<<<<<<<<<<


###############################
# PLOTTING
###############################
def pastel(colour, weight=2.4):
    """
    Convert colour into a nice pastel shade.

    Convert colour into a nice pastel shade.

    Attributes:
        colour (define type): define
        weight (float): define

    Returns:
        (define type): define

    ..ToDo: Beautify
    """
    rgb = np.asarray(colorConverter.to_rgb(colour))
    # scale colour
    maxc = max(rgb)
    if maxc < 1.0 and maxc > 0:
        # scale colour
        scale = old_div(1.0, maxc)
        rgb = rgb * scale
    # now decrease saturation
    total = rgb.sum()
    slack = 0
    for x in rgb:
        slack += 1.0 - x

    # want to increase weight from total to weight
    # pick x s.t.  slack * x == weight - total
    # x = (weight - total) / slack
    x = old_div((weight - total), slack)

    rgb = [c + (x * (1.0-c)) for c in rgb]

    return rgb


def plot_prion_propagation_model_fit(model_function, parameters, data, times, title, label_names, path = "/Users/elkeschaper/Downloads", tag = "foo"):
    """
    Plot the Meisl curve of data, fit, and number of propagons.

    Plot the Meisl curve of data, fit, and number of propagons.

    Attributes:
        model_function (define type): define
        parameters (define type): define
        data (define type): define
        times (define type): define
        title (define type): define
        label_names (define type): define

    Returns:

    ..ToDo: Beautify
    """

    N_graphs=len(parameters[:,0])
    for i in range(N_graphs):
        plt.plot(times[:,i], data[:,i], 'o',markersize=7,mec=plt.get_cmap('spectral')(old_div(float(i),(N_graphs+1))),color=pastel(plt.get_cmap('spectral')(old_div(float(i),(N_graphs+1))),weight=2))
    for i in range(N_graphs):
        plt.plot(times[:,i], model_function(times[:,i], *parameters[i,:]), '-',color=plt.get_cmap('spectral')(old_div(float(i),(N_graphs+1))),linewidth=3, label=str(label_names[i]))

    plt.title(str(title))
    plt.ylim([-0.1,1.1])
    plt.xlabel('Threshold, centred on mean, in of stdev of neg control',size='large')
    plt.ylabel('Fraction of below the threshold',size='large')
    plt.legend(loc='best', shadow=True)
    #import pdb; pdb.set_trace()
    plt.savefig(os.path.join(path, tag + ".png"), bbox_inches='tight')
    plt.close()

