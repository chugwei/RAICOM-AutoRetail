#encoding: UTF-8
#!/usr/bin/env python2

class GrabParams(object):

    # get the results by calibration
    ratio = 0.234 #0.216 #0.270 #0.214 0.220
    
    # increase x_bias to move front, or decrease x_bias to move back
    x_bias = 0#-2

    # increase y_bias to move left, or decrease y_bias to move right
    y_bias = 38 #33

    #               	 (+x)front
    #                 	  ^
    #				 	  :
    #				  	  :
    #                 	  :
    # (+y< ..............o..............(-y)ight
    #					  :
    #					  :
    #					  :
    #					  :
    #					 (-x)

    # increase height_bias to move higher, or decrease height_bias to move lower
    height_bias = 160 #矮桌子 150   高桌子160
    
    grab_direct = "front"

    coords_ready_1 = [49.5, -64.3, 410.9, -92.02, -0.28, -91.13] #star 
    #shexiangtoujiaodu:136
    coords_ready = [203, -40, 250, -175, 0, -133] #[203, -40, 240, -175, 0, -136][172.9, -46.2, 278.0, -173.64, 2.68, -137.58] #[203, -40, 240, -175, 0, -136] 
    coords_place_A = [252.8, 100, 140, 153.88, 24.93, 138.77]
    coords_place_B = [252.8, -114.8, 140, 157.4, 23.51, 100.7]
    coords_place_C = [200, 100, 140, 153.88, 24.93, 138.77]
    coords_place_D = [200, -114.8, 140, 157.4, 23.51, 100.7]
    coords_place_X = [203.3, -38.3, 245.8, -178.01, -2.16, -133.35]
    # coords_place_A = [252.8, 100, 149.5, 153.88, 24.93, 138.77]
    # coords_place_B = [252.8, -114.8, 149.5, 157.4, 23.51, 100.7]
    # coords_place_C = [200, 100, 149.5, 153.88, 24.93, 138.77]
    # coords_place_D = [200, -114.8, 149.5, 157.4, 23.51, 100.7]
    # grab_direct = "right"
    # if grab_direct == "right":
    # 	y_bias = -5
    # 	x_bias = 40
    # 	coords_ready = [-59.3, -181.2, 252.8, -178.51, 0.28, 135]
    
    GRAB_MOVE_SPEED =40 #20

    # show image and waitkey
    debug = True #True         

    # please do not change the parameter values below
    IMG_SIZE = 640
    done = False
    cap_num = 2
    usb_dev = "/dev/arm"
    baudrate = 115200

grabParams = GrabParams()

