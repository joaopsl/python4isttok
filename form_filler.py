from sdas.core.LoadSdasData import LoadSdasData
from sdas.core.StartSdas import StartSdas
import numpy
import sys
from pyISTTOK.special_mean_val import special_mean_val
from pyISTTOK.exposure_time import exposure_time
from pyISTTOK.period_counter import period_counter
from get_shot_report import get_shot_report
import xmlrpclib

from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time

#####################################################################
##                  GLOBAL VARIABLES                               ##
#####################################################################
iplasma_threshold=1.e3
dens_threshold=2.e18
marte_threshold=10
iplasma_ok=1
dens_ok=1
marte_ok=1
#####################################################################

#####################################################################
##                  SDAS ACCESS                                    ##
#####################################################################

# client = StartSdas()
#
# if len(sys.argv) < 2 :
#     shotnr = client.searchMaxEventNumber('0x0000')
# else :
#     shotnr = int(sys.argv[-1])
#
# plasma_curr_channelID='POST.PROCESSED.IPLASMA'; # Unique Identifier for plasma current
# plasma_dens_channelID='POST.PROCESSED.DENSITY'; # Unique Identifier for plasma density
# marte_power_channelID='MARTE_NODE_IVO3.DataCollection.Channel_105'; #Marte channel for the power supply
#
# print '\nSHOT #'+str(shotnr)+'\n'
# print 'Loading data'
#
# try:
#     [iplasma,iplasma_times] = LoadSdasData(client, plasma_curr_channelID, shotnr);
#     iplasma_ok=numpy.all(numpy.isfinite(iplasma))
# except xmlrpclib.Fault:
#     print 'PLASMA CURRENT DATA NOT READY'
#     iplasma_ok=0
# try:
#     [dens,dens_times] =       LoadSdasData(client, plasma_dens_channelID, shotnr);
#     dens_ok=numpy.all(numpy.isfinite(dens))  # check if all finite
# except xmlrpclib.Fault:
#     print 'DENSITY DATA NOT READY'
#     dens_ok=0
# try:
#     [marte,marte_times] =       LoadSdasData(client, marte_power_channelID, shotnr);
#     marte_ok=numpy.all(numpy.isfinite(marte))  # check if all finite
# except xmlrpclib.Fault:
#     print 'MARTE CONTROL DATA NOT READY'
#     marte_ok=0
#
#
# print 'Data loaded\n'
#
#
# if iplasma_ok:
#     print 'FROM IPLASMA   ( thresh',iplasma_threshold,')'
#     iplasma_shot_time = exposure_time(numpy.abs(iplasma),iplasma_times,iplasma_threshold)
#     iplasma_mean_val = special_mean_val(numpy.abs(iplasma),iplasma_threshold)/1.e3
#     print 'Mean current {0:.3f} kA'.format(iplasma_mean_val)
#     iplasma_periods = period_counter(numpy.abs(iplasma),iplasma_threshold)
#     print 'I counted '+str(iplasma_periods)+' periods'
# else:
#     print 'NO IPLASMA DATA'
#
# print ''
#
# if dens_ok:
#     print 'FROM DENSITY   ( thresh',dens_threshold,')'
#     exposure_time(dens,dens_times,dens_threshold)
#     dens_mean_val = special_mean_val(dens,dens_threshold)/1e18;
#     print 'Mean density {0:.2e} m'.format(dens_mean_val*1e18)+u'\u207b\u00b3'
#     dens_periods = period_counter(dens,dens_threshold)
#     print 'I counted '+str(dens_periods)+' periods'
# else:
#     print 'NO DENSITY DATA'
#
# print ''
#
# if marte_ok:
#     print 'FROM MARTE'
#     marte_periods = period_counter(abs(marte),marte_threshold,numpy.append(numpy.ones(10),numpy.zeros(1)))
#     print 'I counted '+str(marte_periods)+' periods'
# else:
#     print 'NO MARTE DATA'
#
# if marte_ok and iplasma_ok and dens_ok:
#     print '\nSucess rate was '+str(iplasma_periods)+'/'+str(marte_periods)
#     if iplasma_periods==marte_periods:
#         print '!!!CONGRATULATIONS!!!'
#     elif iplasma_periods <= marte_periods/2:
#         print '!!!BOOOOOO!!!'
#
# print '\n'

[iplasma_mean_val,dens_mean_val,iplasma_shot_time,iplasma_periods,marte_periods] = get_shot_report()

raw_input("Press Enter to continue into the auto_filler...")

#####################################################################
##                  AUTO FILLER                                    ##
#####################################################################

m = PyMouse()
k = PyKeyboard()

timer_max = 50;

prev_posi = (0,0);
oldr_posi = (0,0);
mouse_ready = False;

for i in range(timer_max):
    curr_posi = m.position()
    print 'Mouse at '+str(curr_posi)+'(timeout in '+str(i+1)+'/'+str(timer_max)+')'
    if curr_posi == prev_posi == oldr_posi:
        mouse_ready = True;
        break
    else:
        oldr_posi = prev_posi;
        prev_posi = curr_posi;
    time.sleep(0.5)

if mouse_ready:
    print "I'm going to click at"+str(curr_posi)
    m.click(m.position()[0],m.position()[1])

    # Shot number
    k.type_string(str(shotnr))
    k.tap_key(k.tab_key)
    #Iplasma in kA
    k.type_string('{0:.2f}'.format(iplasma_mean_val))
    k.tap_key(k.tab_key)
    #density in *1e18m-3
    k.type_string('{0:.2f}'.format(dens_mean_val))
    k.tap_key(k.tab_key)
    #duration in ms
    k.type_string(str(iplasma_shot_time))
    k.tap_key(k.tab_key)

    #Shot comments
    k.type_string('Sn-spectra, ')
    k.type_string('Sn cold at a)XXXX cm. ')
    k.type_string('P_ed)XXXX . ')
    tmp_str = str(iplasma_periods)+'&'+str(marte_periods)+' cycles'
    k.type_string(tmp_str)
    k.tap_key(k.tab_key)
    #k.tap_key(k.enter)