import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from scipy import interpolate
#from tkinter import *


######################## Define the text size of each plot globally ###########
SMALL_SIZE = 10
MEDIUM_SIZE = 10
BIGGER_SIZE = 10

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

plt.rcParams["font.family"] = "Times New Roman"
cm = 1/2.54  # centimeters in inches
######################## Define the text size of each plot globally ###########


       
def program_run(entry_pla, entry_sof):
    ###Raw data from PLAXIS
    plaxis_data = pd.read_csv(entry_pla, delimiter = ";") #comma is delimeter        
    #Extracts the coloumns of the dataframe
    x_p, y_p, uz = plaxis_data.iloc[:,0].values, plaxis_data.iloc[:,1].values, plaxis_data.iloc[:,5].values
    ux,uy = plaxis_data.iloc[:,3].values, plaxis_data.iloc[:,4].values
    
    
    ###Raw data from SOFiSTiK
    skip_rows = 4
    skip_last_rows = 1
    sofistik_data_raw = pd.read_csv(entry_sof, sep='\s+',skiprows = skip_rows,skipfooter=skip_last_rows, header=None, names=['Nod','X', 'Y', 'Z', 'A'])
    x_s, y_s, z_s = sofistik_data_raw.iloc[:,1].values, sofistik_data_raw.iloc[:,2].values, sofistik_data_raw.iloc[:,3].values
    z_s = pd.DataFrame(0, index=np.arange(len(x_s)), columns = ['z'])
    

    grid_sofistik_uz = interpolate.griddata((x_p, y_p), uz, (x_s, y_s), method = 'cubic')
    grid_sofistik_uy = interpolate.griddata((x_p, y_p), uy, (x_s, y_s), method = 'cubic')
    grid_sofistik_ux = interpolate.griddata((x_p, y_p), ux, (x_s, y_s), method = 'cubic')
    
    sofistik_data_raw.iloc[:,3] = grid_sofistik_uz
    sofistik_data_raw.loc[:,4] = grid_sofistik_uy
    sofistik_data_raw.loc[:,5] = grid_sofistik_ux
    
    knot = pd.Series('knot', index=np.arange(len(sofistik_data_raw)))
    nr = pd.Series('nr', index=np.arange(len(sofistik_data_raw)))
    typ = pd.Series('typ', index=np.arange(len(sofistik_data_raw)))
    ww= pd.Series('wzz,wyy,wxx', index=np.arange(len(sofistik_data_raw)))
    

    u = [ux,uy,uz]
    grid_sofistik = [grid_sofistik_ux, grid_sofistik_uy, grid_sofistik_uz]
    
    error_x, error_y, error_z = [],[],[]
    
    text = ['x', 'y', 'z']
    
    for i in range(len(text)):
        
        sofistik_data = sofistik_data_raw[sofistik_data_raw.iloc[:,5-i].isnull()]
        
        
        if sofistik_data.empty:
              print("Your data interpolation contains in "+text[i]+" direction no errors!") 
              
              if i == 0:
                  sofistik_export = pd.DataFrame([knot,nr,sofistik_data_raw.iloc[:,0],typ ,ww ,sofistik_data_raw.iloc[:,3]*(-1)*1000, sofistik_data_raw.iloc[:,5]*1000,sofistik_data_raw.iloc[:,6]*1000])
                  sofistik_export = sofistik_export.transpose()
              
        else:
            if i == 0:
              grid_sofistikB = interpolate.griddata((x_p, y_p), u[i], (sofistik_data.iloc[:,1],sofistik_data.iloc[:,2]), method = 'nearest')     
              sofistik_data.iloc[:,5] = grid_sofistikB
              error_x = sofistik_data
              sofistik_data_raw.update(sofistik_data)
              sofistik_export = pd.DataFrame([knot,nr,sofistik_data_raw.iloc[:,0], typ, ww,sofistik_data_raw.iloc[:,3+i]*(-1)*1000])
              sofistik_export = sofistik_export.transpose()
              print("Important message:\n Your data interpolation in "+text[i]+" direction contains errors at "+str(len(sofistik_data))+ " nodes. \n Another interpolation mode (neighbour points) has been set!") 
            elif i == 1:
    
                grid_sofistikB = interpolate.griddata((x_p, y_p), u[i], (sofistik_data.iloc[:,1],sofistik_data.iloc[:,2]), method = 'nearest')     
                sofistik_data.iloc[:,5-i] = grid_sofistikB
                error_y = sofistik_data
                sofistik_data_raw.update(sofistik_data)
                sofistik_export = pd.DataFrame([knot,nr,sofistik_data_raw.iloc[:,0], typ, ww, sofistik_data_raw.iloc[:,3]*(-1)*1000, sofistik_data_raw.iloc[:,5]*1000])
                sofistik_export = sofistik_export.transpose()
                print("Important message:\n Your data interpolation in "+text[i]+" direction contains errors at "+str(len(sofistik_data))+ " nodes. \n Another interpolation mode (neighbour points) has been set!") 
            elif i == 2:
    
                grid_sofistikB = interpolate.griddata((x_p, y_p), u[i], (sofistik_data.iloc[:,1],sofistik_data.iloc[:,2]), method = 'nearest')     
                sofistik_data.iloc[:,5-i] = grid_sofistikB
                error_z = sofistik_data
                sofistik_data_raw.update(sofistik_data)
                sofistik_export = pd.DataFrame([knot,nr,sofistik_data_raw.iloc[:,0],typ ,ww ,sofistik_data_raw.iloc[:,3]*(-1)*1000, sofistik_data_raw.iloc[:,5]*1000,sofistik_data_raw.iloc[:,6]*1000])
                sofistik_export = sofistik_export.transpose()
                print("Important message:\n Your data interpolation in "+text[i]+" direction contains errors at "+str(len(sofistik_data))+ " nodes. \n Another interpolation mode (neighbour points) has been set!")    
    
    np.savetxt(export_path+'\export_SOFiSTiK.txt',sofistik_export,fmt=['%s','%s','%d','%s','%s','%.20e,','%.20e,','%.20e'])
    with open(export_path+'\export_SOFiSTiK.txt', mode = 'r') as file_in:
        with open(export_path+'\export_SOFiSTiK.dat', mode = 'w') as file_out:
            text = file_in.read()
            text = text.replace(', ', ',')
            file_out.write(text)
    
    
    u = [ux,uy,uz]
    grid_sofistik = [grid_sofistik_ux, grid_sofistik_uy, grid_sofistik_uz]
    text = ['x', 'y', 'z']
    error = [error_x, error_y, error_z]
    
    if plots == 1:
        for j in range(len(text)):
            
            sofistik_data = error[j]
            
            # ---------- Abbildung 1 ----------
            fig = plt.figure(figsize=(8.4*cm, 6*cm), dpi=700) 
            ax = fig.add_subplot(111, projection='3d')
            ax.view_init(elev=40, azim=-60)
            
            ax.scatter(x_p, y_p, abs(u[j]), c='k', alpha=0.3, s=0.0005)
            ax.scatter(x_s, y_s, z_s, c='blue', s=0.1)
            
            ax.set_xlabel("x-axis (m)", labelpad=2)
            ax.set_ylabel("y-axis (m)", labelpad=2)
            ax.set_zlabel("$u_z$ (m)", labelpad=2)
            
            # Z-Achse setzen und invertieren
            ax.set_zlim(0, 0.10)
            ax.set_zlim(ax.get_zlim()[::-1])  # Invertieren
            
            plt.subplots_adjust(left=-0.10, right=1, top=1.02, bottom=0.15, wspace=0.5, hspace=0.5)
            plt.savefig('001_rawData_in ' + text[j] + '.png', dpi=700)
            
            
            # ---------- Abbildung 2 ----------
            fig = plt.figure(figsize=(8.4*cm, 6*cm), dpi=700) 
            ax = plt.axes(projection='3d')
            ax.view_init(elev=40, azim=-60)
            
            ax.scatter(x_s, y_s, grid_sofistik[j], c='green', s=1)
            if len(sofistik_data) > 0:

                ax.scatter(sofistik_data.iloc[:, 1], sofistik_data.iloc[:, 2], sofistik_data.iloc[:, 5-j], c='red')
            
            ax.set_xlabel("x-axis (m)", labelpad=2)
            ax.set_ylabel("y-axis (m)", labelpad=2)
            ax.set_zlabel("$u_z$ (m)", labelpad=2)
            
            plt.subplots_adjust(left=-0.10, right=1, top=1.02, bottom=0.15, wspace=0.5, hspace=0.5)
            plt.savefig('002_interpolatedData_in ' + text[j] + '.png', dpi=700)
            
            
            # ---------- Abbildung 3 ----------
            fig = plt.figure(figsize=(8.4*cm, 6*cm), dpi=700) 
            ax = plt.axes(projection='3d')
            ax.view_init(elev=40, azim=-60)
            
            ax.scatter(x_s, y_s, abs(grid_sofistik[j]), c='blue', s=0.1)
            if len(sofistik_data) > 0:

                ax.scatter(sofistik_data.iloc[:, 1], sofistik_data.iloc[:, 2], abs(sofistik_data.iloc[:, 5-j]), c='red')
            
            ax.scatter(x_p, y_p, abs(u[j]), c='k', alpha=0.3, s=0.0005)
            
            ax.set_xlabel("x-axis (m)", labelpad=2)
            ax.set_ylabel("y-axis (m)", labelpad=2)
            ax.set_zlabel("$u_z$ (m)", labelpad=2)
            
            # Z-Achse setzen und invertieren
            ax.set_zlim(0, 0.10)
            ax.set_zlim(ax.get_zlim()[::-1])
            
            plt.subplots_adjust(left=-0.10, right=1, top=1.02, bottom=0.15, wspace=0.5, hspace=0.5)
            plt.savefig('003_combinedData_in ' + text[j] + '.png', dpi=700)





# entry_pla = input("Please add your PLAXIS file in:")
# entry_sof = input("Please add your SOFiSTiK file in:")
# export_path = input("Please add your export path:")

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

plots = 1
entry_pla = os.path.join(DATA_DIR, 'PLAXIS_export.csv')
entry_sof = os.path.join(DATA_DIR, 'SOFISTIK_settlements.txt')
export_path = DATA_DIR

program_run(entry_pla, entry_sof)



    


