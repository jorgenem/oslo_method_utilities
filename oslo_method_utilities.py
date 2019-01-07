import numpy as np

def read_mama_2D(filename):
    # Reads a MAMA matrix file and returns the matrix as a numpy array, 
    # as well as a list containing the four calibration coefficients
    # (ordered as [bx, ax, by, ay] where Ei = ai*channel_i + bi)
    # and 1-D arrays of calibrated x and y values for plotting and similar.
    matrix = np.genfromtxt(filename, skip_header=10, skip_footer=1)
    cal = {}
    with open(filename, 'r') as datafile:
        calibration_line = datafile.readlines()[6].split(",")
        # a = [float(calibration_line[2][:-1]), float(calibration_line[3][:-1]), float(calibration_line[5][:-1]), float(calibration_line[6][:-1])]
        # JEM update 20180723: Changing to dict, including second-order term for generality:
        # print("calibration_line =", calibration_line, flush=True)
        cal = {"a0x":float(calibration_line[1]), "a1x":float(calibration_line[2]), "a2x":float(calibration_line[3]), 
             "a0y":float(calibration_line[4]), "a1y":float(calibration_line[5]), "a2y":float(calibration_line[6])}
    # TODO: INSERT CORRECTION FROM CENTER-BIN TO LOWER EDGE CALIBRATION HERE.
    # MAKE SURE TO CHECK rebin_and_shift() WHICH MIGHT NOT LIKE NEGATIVE SHIFT COEFF.
    # (alternatively consider using center-bin throughout, but then need to correct when plotting.)
    Ny, Nx = matrix.shape
    y_array = np.linspace(0, Ny-1, Ny)
    y_array = cal["a0y"] + cal["a1y"]*y_array + cal["a2y"]*y_array**2
    x_array = np.linspace(0, Nx-1, Nx)
    x_array = cal["a0x"] + cal["a1x"]*x_array + cal["a2x"]*x_array**2
    # x_array = np.linspace(cal["a0x"], cal["a0x"]+cal["a1x"]*Nx, Nx) # BIG TODO: This is probably center-bin calibration, 
    # x_array = np.linspace(a[2], a[2]+a[3]*(Ny), Ny) # and should be shifted down by half a bin?
                                                    # Update 20171024: Started changing everything to lower bin edge,
                                                    # but started to hesitate. For now I'm inclined to keep it as
                                                    # center-bin everywhere. 
    return matrix, cal, y_array, x_array # Returning y (Ex) first as this is axis 0 in matrix language


def write_mama_2D(matrix, filename, y_array, x_array, comment=""):
    import time
    outfile = open(filename, 'w')

    # Write mandatory header:
    # outfile.write('!FILE=Disk \n')
    # outfile.write('!KIND=Spectrum \n')
    # outfile.write('!LABORATORY=Oslo Cyclotron Laboratory (OCL) \n')
    # outfile.write('!EXPERIMENT=pyma \n')
    # outfile.write('!COMMENT=none|RE:alfna-20FN:RN:UN:FN:RN: \n')
    # outfile.write('!TIME=DATE:'+time.strftime("%d-%b-%y %H:%M:%S", time.localtime())+'   \n')
    # outfile.write('!CALIBRATION EkeV=6, %12.6E, %12.6E, 0.000000E+00, %12.6E, %12.6E, 0.000000E+00 \n' %(Egamma_range[0], (Egamma_range[1]-Egamma_range[0]), Ex_range[0], (Ex_range[1]-Ex_range[0])))
    # outfile.write('!PRECISION=16 \n')
    # outfile.write('!DIMENSION=2,0:%4d,0:%4d \n' %(len(matrix[:,0]), len(matrix[0,:])))
    # outfile.write('!CHANNEL=(0:%4d,0:%4d) \n' %(len(matrix[:,0]), len(matrix[0,:])))
    header_string ='!FILE=Disk \n'
    header_string +='!KIND=Spectrum \n'
    header_string +='!LABORATORY=Oslo Cyclotron Laboratory (OCL) \n'
    header_string +='!EXPERIMENT= pyma \n'
    header_string +='!COMMENT={:s} \n'.format(comment)
    header_string +='!TIME=DATE:'+time.strftime("%d-%b-%y %H:%M:%S", time.localtime())+'   \n'
    header_string +='!CALIBRATION EkeV=6, %12.6E, %12.6E, 0.000000E+00, %12.6E, %12.6E, 0.000000E+00 \n' %(x_array[0], (x_array[1]-x_array[0]), y_array[0], (y_array[1]-y_array[0]))
    header_string +='!PRECISION=16 \n'
    header_string +="!DIMENSION=2,0:{:4d},0:{:4d} \n".format(len(matrix[0,:])-1, len(matrix[:,0])-1)
    header_string +='!CHANNEL=(0:%4d,0:%4d) ' %(len(matrix[0,:])-1, len(matrix[:,0])-1)

    footer_string = "!IDEND=\n"

    # Write matrix:
    # matrix.tofile(filename, sep='       ', format="{:14.8E}")
    # matrix.tofile(filename, sep=' ', format="%-17.8E")
    np.savetxt(filename, matrix, fmt="%-17.8E", delimiter=" ", newline="\n", header=header_string, footer=footer_string, comments="")

    outfile.close()
