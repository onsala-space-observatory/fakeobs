# Copyright (c) Nordic ARC Node (2013). 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# a. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# b. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# c. Neither the name of the author nor the names of contributors may 
#    be used to endorse or promote products derived from this software 
#    without specific prior written permission.
#
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#



from taskinit import *
from simutil import *
import numpy as np
import shutil
import os


def fakeobs(vis='', outputvis='', model='', incell='', inbright='', incenter='', 
            inwidth='', spw='0', field_name='', frame='LSRK', ref_field=-1, stretch_spw=False, 
            corrupt=False, add_factor=0.0,
            seed=42, tau0=0.0, t_sky=250.0, t_ground=270.0, t_receiver=50.0, 
            overwrite=False):

# Verbose?
 myverb = False

 if myverb:
   print 'VERBOSE MODE ON'



 nm = 'fakeobs'
 indirection = ''

 if myverb:
   print 'LOAD SIMULTIL'

 util = simutil(indirection)
 util.verbose = True

 if myverb:
   print 'SIMULTIL MESSAGE'

 msg = util.msg

 if myverb:
   print 'SETTING INPUTS'

 spw = str(spw)
 field_name=str(field_name)
 incell=str(incell)
 incenter=str(incenter)
 inwidth=str(inwidth)
 inbright=str(inbright)
 frame = str(frame)

 units = {'Hz':1.0,'kHz':1.e3,'MHz':1.e6,'GHz':1.e9}
 frRef = {'LSRK':1,'BARY':3}

 if len(frame)==0:
   frame = 'LSRK'

 if myverb:
   print vis
   print field_name
   print outputvis
   print model
   print incell
   print incenter
   print inwidth
   print spw
   print ref_field
   print corrupt


 if not os.path.exists(vis):
   msg('Measurement set \'%s\' does not exist!'%os.path.basename(vis),origin=nm,priority='error')
   return False
 if not os.path.exists(model):
   msg('Model file \'%s\' does not exist!'%os.path.basename(model),origin=nm,priority='error')
   return False



 if ';' in spw or ':' in spw:
   msg('Only full spw are allowed (e.g. \'0~3\' or \'0,1\'). Aborting!',origin=nm,priority="error")
   return False



 if len(spw)==0:
   selsp = []

 else:

  try:
   spws = spw.split(',')
   selsp = []
   for sp in spws:
    if '~' in sp:
     io = map(int,sp.split('~'))
     selsp += range(io[0],io[1]+1)
    else:
     selsp.append(int(sp))
  except:
   msg("BAD string \'%s\' to set the spectral window. Aborting!"%str(spw),origin=nm,priority="error")
   return False

 write = False
 if os.path.exists(outputvis):
  if not overwrite:
   proceed = raw_input('OK to remove \'%s\'? \n Yes/No (Y):'%os.path.basename(outputvis))
   if 'Y' in proceed or 'y' in proceed or len(proceed)==0:
    write=True
   else:
    msg('%s will be re-used (will trust it\'s OK).'%outputvis,origin=nm,priority='warn')
  else:
   write=True
 else:
  write=False




 if write:
  msg('Removing %s'%outputvis,origin=nm,priority='warn')
  shutil.rmtree(outputvis)
 if not os.path.exists(outputvis):
  msg('Copying data to %s'%os.path.basename(outputvis),origin=nm,priority='warn')
  shutil.copytree(vis,outputvis)


 if myverb:
   print 'OPENING NEW MS'
 
  
 ms.open(outputvis)
 spInfo = ms.getspectralwindowinfo()
 ms.close()

 if myverb:
   print 'SETTING FRAME TO %s'%frame

 if myverb:
   print 'OPEN SPW TABLE' 
 tb.open(os.path.join(outputvis,'SPECTRAL_WINDOW'),nomodify=False)
 if myverb:
   print 'GET FRAME COLUMN' 
 aux = tb.getcol('MEAS_FREQ_REF')
 if myverb:
   print 'SET FRAME VALUES TO %i'%frRef[frame]
 aux[:] = frRef[frame]
 if myverb:
   print 'SET FRAME'
 tb.putcol('MEAS_FREQ_REF',aux)
 tb.close()

 if myverb:
   print 'DONE!'


 if myverb:
   print 'GETTING MS METADATA'

 ms.open(outputvis)
 mtInfo = ms.metadata()


 if myverb:
   print 'SELECTING SPWS'

 if len(selsp)==0:
   selsp = sorted(map(int,spInfo.keys()))

 if min(selsp)<0:
   msg('ERROR! spw ids must be >=0',origin=nm,priority='error')

 try:
  testsp = spInfo[str(max(selsp))]
 except:
  msg('Spectral window %i does not exist! Aborting!'%max(selsp),origin=nm,priority='error')
  return False


 if myverb:
   print 'GETTING SPW FREQUENCY RANGES'


 frs = []
 for sp in selsp:
   frs += [spInfo[str(sp)]['Chan1Freq'],spInfo[str(sp)]['Chan1Freq']+spInfo[str(sp)]['ChanWidth']*spInfo[str(sp)]['NumChan']]

 minFr = min(frs)
 maxFr = max(frs)

 msg('Selected spws: %s'%str(selsp),origin=nm,priority='warn')



 if myverb:
   print 'SETTING FIELDS'


 try:
   fields = mtInfo.fieldsforname(field_name)
 except:
   msg('Field name \'%s\' not found in data. Aborting!'%field_name,origin=nm,priority='error')
   return False

 ms.close()


 ref_field=int(ref_field)
 if ref_field < 0:
  modcoord = True
  msg('Reference position will be taken from model image.',origin=nm,priority='warn')
  ia.open(model)
  refdir = ia.toworld()['numeric']
  ia.close()
 else: 
  ref_field = int(ref_field)
  msg('Reference position will be taken from field %i'%ref_field,origin=nm,priority='warn')
  modcoord = False


 if myverb:
   print 'GETTING SOURCE DIRECTION'


 if not modcoord:
  tb.open(os.path.join(vis,'FIELD'))
  try:
   refdir = tb.getcol('REFERENCE_DIR')[:,0,ref_field]  # TO CHECK WITH MULTI-SOURCE!
  except:
   tb.close()
   msg('Could not get position from ref. field. Aborting!',origin=nm,priority='error')
   return False
  else:
   tb.close()


 if myverb:
   print 'GETTING MODEL FREQUENCIES'

 ia.open(model)
 summ = ia.summary()

 try:
# if True:
  NuAx = list(summ['axisnames']).index('Frequency')

  if incenter=='':
   incenter = '%.1fHz'%(summ['refval'][NuAx]*units[summ['axisunits'][NuAx]])
  if inwidth=='':
   inwidth =  '%.1fHz'%(summ['incr'][NuAx]*units[summ['axisunits'][NuAx]])

 except:
# else:
   msg('ERROR! Model does not have a standard header (or freq. units)',origin=nm,priority='error')

 ia.close()






 if myverb:
   print 'SETTING SOURCE DIRECTION'


 RA = refdir[0]*180./np.pi/15.
 Dec = refdir[1]*180./np.pi
 RAh = int(RA); RAm = (RA-RAh)*60.; RAs = 60.*(RAm-int(RAm)); RAm=int(RAm)
 Decd = int(Dec); Decm = (Dec-Decd)*60.; Decs = 60.*(Decm-int(Decm)); Decm=int(Decm)
 cdir = 'J2000 %ih%02dm%.6f %2id%02dm%.6f'%(RAh,RAm,RAs,Decd,Decm,Decs)

 newmodel = os.path.join(os.path.dirname(outputvis),os.path.basename(model)+'.model')

 write = False
 if os.path.exists(newmodel):
  if not overwrite:
   proceed = raw_input('OK to remove \'%s\'? \n Yes/No (Y):'%os.path.basename(newmodel))
   if 'Y' in proceed or 'y' in proceed or len(proceed)==0:
    write=True
   else:
    msg('%s will be re-used (will trust it\'s OK).'%newmodel,origin=nm,priority='warn')
  else:
   write=True
 else:
  write= False

 if write:
  msg('Removing %s'%newmodel,origin=nm,priority='warn')
  shutil.rmtree(newmodel)

 if myverb:
  print model
  print newmodel
  print inbright
  print cdir
  print incell
  print incenter
  print inwidth

 msg('Preparing model',origin=nm,priority='warn')
 returnpars = util.modifymodel(model, newmodel,
                               inbright,cdir,incell,
                               incenter,inwidth,0,
                               flatimage=False)



 if stretch_spw:

   if myverb:
     print 'STRETCH SPWs'

   ia.open(newmodel)
   summ = ia.summary()

 
   NuAx = list(summ['axisnames']).index('Frequency')
   ImNu0 = summ['refval'][NuAx] - summ['refpix'][NuAx]*summ['incr'][NuAx]
   ImNu1 = summ['refval'][NuAx] + (summ['shape'][NuAx]-summ['refpix'][NuAx])*summ['incr'][NuAx]
   ia.close()

   ImNu0 *= units[summ['axisunits'][NuAx]]
   ImNu1 *= units[summ['axisunits'][NuAx]]

   print '\n\nModel image covers from %.8e to %.8e Hz'%(ImNu0,ImNu1)
   print 'Selected spws cover from %.8e to %.8e Hz'%(minFr,maxFr)
   print 'Will shift and stretch the spws to match the model\n\n'

   Shift = ImNu0
   Stretch = (ImNu1-ImNu0)/(maxFr-minFr)

   tb.open(os.path.join(outputvis,'SPECTRAL_WINDOW'),nomodify=False)

   aux=tb.getcol('CHAN_FREQ')
   aux = (aux-minFr)*Stretch + Shift
   tb.putcol('CHAN_FREQ',aux)

   aux=tb.getcol('CHAN_WIDTH')
   aux *= Stretch
   tb.putcol('CHAN_WIDTH',aux)

   aux=tb.getcol('EFFECTIVE_BW')
   aux *= Stretch
   tb.putcol('EFFECTIVE_BW',aux)

   aux=tb.getcol('RESOLUTION')
   aux *= Stretch
   tb.putcol('RESOLUTION',aux)

   aux=tb.getcol('TOTAL_BANDWIDTH')
   aux *= Stretch
   tb.putcol('TOTAL_BANDWIDTH',aux)

   tb.close()


 msg('Simulating data',origin=nm,priority='warn')

 sm.openfromms(outputvis)
 for spi in selsp:
  msg('Simulating spw %i'%spi,origin=nm,priority='warn')
  if myverb:
    print 'Going to SETDATA'
  sm.setdata(fieldid=list(fields),spwid=spi)
  if myverb:
    print 'Going to PREDICT'
  sm.predict(imagename=newmodel)

 sm.done()


 if myverb:
   print 'DONE WITH SIMULATION'


 if add_factor != 0.0:
   msg('Adding original data to the model',origin=nm,priority="warn")
   for sp in selsp:
     for field in list(fields):
       ms.open(vis)
       msg('Adding data of spw %i'%spi,origin=nm,priority='warn')
       ms.selectinit(datadescid=int(sp))
       ms.select({'field_id':field})
       dats = np.copy(ms.getdata(['data'])['data'])*add_factor
       ms.close()
       ms.open(outputvis,nomodify=False)
       ms.selectinit(datadescid=int(sp))
       ms.select({'field_id':field})
       indat = ms.getdata(['data'])
       indat['data'] += dats
       ms.putdata(indat)
       ms.close()




 if corrupt:

  if myverb:
    print 'ADDING NOISE TO SIMULATION'


  if os.path.exists(outputvis+'.noisy'):
    shutil.rmtree(outputvis+'.noisy')
  msg('Copying %s into its noisy version'%os.path.basename(outputvis),origin=nm,priority='warn')
  shutil.copytree(outputvis,outputvis+'.noisy')
  knowntelescopes = ["ALMASD", "ALMA", "ACA", "SMA", "EVLA", "VLA"]
  tb.open(os.path.join(outputvis,"OBSERVATION"))
  n = tb.getcol("TELESCOPE_NAME")
  telescopename = n[0]
  tb.close()
  known=True
  if telescopename not in knowntelescopes:
    msg("Telescope name \'%s\' is none of ALMA/ACA, (J)VLA, or SMA"%telescopename,origin=nm,priority="warn")
    msg("Data corruption will only account for receivers (if you set t_receiver) and atmosphere (i.e., no spillover nor antenna/correlator related efficiencies).",origin=nm,priority="warn")
    known=False

  eta_p, eta_s, eta_b, eta_t, eta_q, t_rx = util.noisetemp(telescope=telescopename,freq=str(Nu0+DNu*Nchan/2.)+'Hz')
  eta_a = eta_p * eta_s * eta_b * eta_t

  if t_receiver!=0.0:
    t_rx = abs(t_receiver)
  tau0 = abs(tau0)
  t_sky = abs(t_sky)
  t_ground = abs(t_ground)

  sm.openfromms(outputvis+'.noisy')
  sm.setseed(seed)
  for spi in selsp:
   for field in list(fields):
    isdata = sm.setdata(fieldid=[field],spwid=spi)
    if isdata:
      sm.setnoise(spillefficiency=eta_s,correfficiency=eta_q,
                antefficiency=eta_a,trx=t_rx,
                tau=tau0,tatmos=t_sky,tground=t_ground,tcmb=2.725,
                mode="tsys-manual",senscoeff=-1)
      msg('Corrupting data in spw %i'%spi,origin=nm,priority='warn')
      if not known:
        msg("Please, forget the last printouts from \'[noisetemp]\'.\nI\'m indeed using %.2f K as the receiver temperature."%t_rx,origin=nm,priority="warn")
      sm.corrupt()

 sm.done()



 

 return True




#if __name__=='__main__':
#  fakeobs(vis = 'flaggedspw2_self2_v.contsub_subset',
#          outputvis='holadola3.ms',
#          spw='',
#          model='simrotation2.alma.cycle1.1.skymodel',
#       #   field_name='Io',
#          stretch_spw=True,
#          ref_field = -1)
