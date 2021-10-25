#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor, ColorSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.sensor import UltraSonicSensor
from threading import Thread
from time import sleep

sound = Sound()
drive = MoveTank(OUTPUT_B, OUTPUT_C)
colour_sensor = ColorSensor()
touch_sensor = TouchSensor()
sonar = UltraSonicSensor()
CHANGE = 20 # light intensity value determined to be significant

'''
Function: calculates colour based on intensity parameter
Params: intensity   the light intensity to convert to a colour value
Returns: a colour strictly either 'black', 'grey', or 'white'
'''
def get_colour(intensity):
    if intensity <= 20:
        return 'black'
    elif intensity > 20 and intensity < 45:
        return 'grey'
    else return 'white'

'''
Function: turns robot 90 degrees left or right
Params: direction, either right or left 
'''
def turn(direction):
    if direction == 'right':
        drive.on_for_rotations(SpeedPercent(10), SpeedPercent(0), 0.95)
    elif direction == 'left':
        drive.on_for_rotations(SpeedPercent(0), SpeedPercent(10), 0.95)

'''
Function: reverse robot until he reaches a black tile
'''
def reverse_to_black():
    while get_colour(colour_sensor.reflected_light_intensity) == 'black':
        drive.on_for_rotations(SpeedPercent(-10), SpeedPercent(-10), 0.25)
        sound.beep()

'''
Funciton: correct path of robot by rotating and checking for black tiles
'''
def correct_turn():
    
    drive.on_for_rotations(SpeedPercent(-10), SpeedPercent(-10), 0.25) # reverse
    rot = 0 # number of rotations when this equals 10 robot has completed a 90 degree turn
    
    while True:
        
        if rot == 10:
            break
        #Make small incremental turns, checking tile colour after each turn
        #Continues until robot has reached 90 degree turn
        drive.on_for_rotations(SpeedPercent(20), SpeedPercent(0), 0.1) # turn 0.1 rotations to the right
        
        # if detects black or white
        if get_colour(colour_sensor.reflected_light_intensity) == 'black' or get_colour(colour_sensor.reflected_light_intensity) == 'white':
                return
        rot += 1
        
    # turn 270 degrees to make full 360 degree turn
    drive.on_for_rotations(SpeedPercent(20), SpeedPercent(0), 3) 
    
    # makes robot reverse a little to fix overshooting issue
    drive.on_for_rotations(SpeedPercent(-10), SpeedPercent(-10), 0.25)
    
    while True:
        
        # turn left 0.2 rotations
        drive.on_for_rotations(SpeedPercent(0), SpeedPercent(20), 0.2)
        
        # if colour is black or white he is back on track
            if get_colour(colour_sensor.reflected_light_intensity) == 'black' or get_colour(colour_sensor.reflected_light_intensity) == 'white':  # if detects black or white
                return

'''
Function: drive robot forward 0.25 rotations
'''
def forward():
    drive.on_for_rotations(SpeedPercent(25), SpeedPercent(25), 0.25)

'''
Function: drive robot 7 black tiles forward
'''
def go_forward_7_black_tiles(beep=True):
    
    while True:
        
        forward()
        
        # if in grey then robot off track so correct turn
        if get_colour() == 'grey':
            correct_turn()
            
        new_intensity = colour_sensor.reflected_light_intensity
        
        # if robot has detected colour change
        if abs(intensity - new_intensity) > CHANGE:
            # if new intensity decreases it is black
            if (new_intensity < intensity):
                black_count += 1
                if beep == True:
                    sound.beep()
                if black_count == 7:
                    break
        intensity = new_intensity
'''
Function: correct path of robot by reversing to the position of the last black tile encountered
then slightly change the direction the robot is facing then go forward and find the next black tile.
'''
def course_correct(rotation_degree=0.1):
    
    reverse_to_black()
    
    # turn right
    drive.on_for_rotations(SpeedPercent(10), SpeedPercent(0), rotation_degree)
    
    forward()
    
    # while detecting GREY go forward
    while get_colour(colour_sensor.reflected_light_intensity) == 'grey':
        forward()
        
    # now that robot is not on grey check if it detects WHITE
    if get_colour(colour_sensor.reflected_light_intensity) == 'white':
        
        reverse_to_black()
        
        # turn left
        drive.on_for_rotations(SpeedPercent(0), SpeedPercent(10), rotation_degree * 2)
        
        forward()
        
        # while detecting GREY go forward
        while get_colour(colour_sensor.reflected_light_intensity) == 'grey':
            forward()
            
        # now that robot is not on grey check if it detects WHITE
        if get_colour(colour_sensor.reflected_light_intensity) == 'white':
            reverse_to_black()
    return

'''
Function drives to location of tower so that robot is touching it:
'''
def find_tower():
    
    while touch.is_pressed == False:
        
        # keeps track of the what the closest distance to the tower is from the robots current position
        closest_distance = sonar.distance_centimeters
        
        # keeps track of the direction for the robot to face that has the closest direction to the tower
        direction = 'straight'
        
        # turn right sligtly
        drive.on_for_rotations(SpeedPercent(10), SpeedPercent(0), 0.2)
        
        # check to see if the tower is closer to the robot facing this direction
        if sonar.distance_centimeters < closest_distance:      
            closest_distance = sonar.distance_centimeters
            direction = 'right'
            
        # turn back to original position and the slightly left
        drive.on_for_rotations(SpeedPercent(0), SpeedPercent(10), 0.4)
        
        if sonar.distance_centimeters < closest_distance:
            closest_distance = sonar.distance_centimeters
            direction = 'left'
        
        # drive forward in the direction that is closest to the tower
        if direction == 'left':
            #already facing left so drive forward
            forward()
            
        elif direction == 'right':
            # turn to face right from starting position then drive forward
            drive.on_for_rotations(SpeedPercent(10), SpeedPercent(0), 0.4)
            forward()
            
        
        elif direction == 'straight':
            # turn to face straight 
            drive.on_for_rotations(SpeedPercent(10), SpeedPercent(0), 0.2)
            forward()
            
# main program starts here

color_change = 0 # number of colour changes detected
black_count = 0 # number of black tiles detected
intensity = colour_sensor.reflected_light_intensity

# from starting tile go to first black square (two colour changes) then turn right
while color_change < 2:
    forward()
    new_intensity = colour_sensor.reflected_light_intensity
    
    # if detected a significant change in colour
    if abs(intensity - new_intensity) > CHANGE:
        color_change += 1
    intensity = new_intensity

# turn right ready for couting black tiles
sound.beep()
black_count += 1
turn('right')

# drive robot to the position before 2nd turn while counting the black tiles
go_forward_7_black_tiles()

# turn right
turn('right')
counter = 0
black_count = 0

# go forward until robot has passed 6 black tiles
while True:
    # base case
    if black_count == 6:
        break
        
    forward()
    
    # if detects WHITE
    if get_colour(colour_sensor.reflected_light_intensity) == 'white':
        # robot has veered off track so correct course
        course_correct(0.1)
        
    new_intensity = colour_sensor.reflected_light_intensity
    
    # if there has been a tile change
    if abs(intensity - new_intensity) > CHANGE:
        # if intensity decreases then it is on black
        if (new_intensity < intensity):
            black_count += 1
            sound.beep()
        intensity = new_intensity
        
turn('left')

# will repeat previous black counting as earlier, to have the robot move 7 tiles to be close to the tower (black tile at top left of tower)
go_forward_7_black_tiles(False)

# robot turn right to face the tower
turn('right')

# drive to position touching the tower
find_tower()

# while robot is on a black tile
# Therefore tower is still on the finishing tile, so push it off
while get_colour(colour_senor.reflected_light_intensity) == 'black':
    
    # if he loses the tower find it again
    if touch.is_pressed == False:
        find_tower()
    
    # push tower
    drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 1)

# pushes tower again as it may have detected the white T symbol on the finishing tile and think the tower has been pushed off
drive.on_for_rotations(SpeedPercent(50), Speed(Percent(50), 1)
                       
# if still on a black then it hasn't moved the tower off the finishing tile, and keeps pushing the tower
if get_colour(colour_sensor.reflected_light_intensity) == 'black':
                       
    # while robot isn't on a white tile
    while get_colour(colour_senor.reflected_light_intensity) == 'black':
    
        # if he loses the tower find it again
        if touch.is_pressed == False:
            find_tower()
    
        # push tower
        drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 1)  
                       
 sound.beep()
