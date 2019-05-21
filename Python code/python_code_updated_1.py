
'''
* Team Id :  783
* Author List : Swaraj Kaondal , Pratyush Kaware , Shubham Kakirde , Vedant Kayande.
* Filename: progress_task.py
* Theme: Thirsty Crow (TC)
* Functions: find_shortest_path ( dict , str , str ) , movement_instructions ( str* ) ,
                      find_no_of_pebbles () , task () , send_data () , getCameraMatrix() , init_gl() , resize( int , int ) ,
                      detect_markers( frame ) , draw_background( frame ) , init_object_texture( str ) , drawGLScene() ,
                      overlay( frame , list ) .
* Global Variables: ser , texture_object , texture_background , camera_matrix , dist_coeff , cap ,
                                  Pebble_after_pickup , Pot_1 ,  Pebble_before_pickup , Pot_2 , Object_counter ,
                                  INVERSE_MATRIX , arena_config , Robot_start , Instruction , final_instructions , pitcher_nodes ,
                                  pebble_nodes , pebble_axis , pitcher_axis , flag , visited , fetching , shortest_path ,
                                  oriented_shortest_path , node1 , arena , given_orientation , start_flag
'''
import collections
import serial
import time
import numpy as np
import cv2
import cv2.aruco as aruco
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import pygame
import sys
from objloader import *


ser = serial.Serial("COM8", 9600, timeout=0.1)


texture_object = None
texture_background = None

camera_matrix = None
dist_coeff = None
cap = cv2.VideoCapture(0)
Pebble_after_pickup = None
Pot_1 = None
Pebble_before_pickup = None
Pot_2 = None
Pot_3 = None
Pot_4 = None
left_wing = None
right_wing = None
main_body = None
main_body_stone = None
crow_stone = None
legs = None
Object_counter = [ 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ]
j = -1 

INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [ 1.0, 1.0, 1.0, 1.0]])


arena_config = { 0: ("Water Pitcher" , 9 , "1-1" ), 5 :( "Pebble" , 13 , "1-1" ), 2 :( "Pebble" , 11 , "1-1" ) }
Robot_start = "START-2"


Instruction = []

final_instructions = []
final_instructions.append ( 'Z' )

##pitcher_nodes : stores the two possible nodes in a given orientation of the pitcher.
pitcher_nodes = [ "" , "" ]

##pebble_nodes : stores the two possible nodes in a given orientation of the pebble.
pebble_nodes = [ "" , "" ]

pebble_axis = ""
pitcher_axis = ""

##Becomes 1 when traversal starts.
start_flag = 0

first_run_done = 0 

visited = []
no_of_pebbles = 0

##fetching: Looking for pebble or pitcher.
fetching = "Pebbles"

shortest_path = []
slow_list = []
oriented_shortest_path = [ 'None' ]

## node1 : Stores the node at which the bot is current at.
node1 = Robot_start

current_pebble = []
 


##arena : Columns ( vetical zig-zags ) from Right to Left are named from 1 to 6.
##               Each node in a column from top to bottom is assigned an alphabet starting from A.
arena = {
    
                    "START-1" : [ "1-D" ] ,                              "START-2" : [ "6-D" ] ,

                    "1-A" : [ "1-B" , "2-B" ] ,                          "6-A" : [ "6-B" , "5-B" ] ,                                                                       
                    "1-B" : [ "1-A" , "1-C" ] ,                         "6-B" : [ "6-A" , "6-C" ] ,
                    "1-C" : [ "1-B" , "1-D" , "2-D" ] ,             "6-C" : [ "6-B" , "6-D" , "5-D" ] ,
                    "1-D" : [ "START-1" , "1-C" , "1-E" ] ,       "6-D" : [ "START-2" , "6-C" , "6-E" ] ,
                    "1-E" : [ "1-D" , "1-F" , "2-F" ] ,                "6-E" : [ "6-D" , "6-F" , "5-F" ] ,
                    "1-F" : [ "1-E" , "1-G" ]  ,                         "6-F" : [ "6-E" , "6-G" ]  ,
                    "1-G" : [ "1-F" , "2-H" ] ,                         "6-G" : [ "6-F" , "5-H" ] ,

                    "2-A" : [ "2-B" , "3-B" ] ,                         "5-A" : [ "5-B" , "4-B" ] ,                                                                       
                    "2-B" : [ "1-A" , "2-A" , "2-C" ] ,            "5-B" : [ "6-A" , "5-A" , "5-C" ] ,
                    "2-C" : [ "2-B" , "2-D" , "3-D" ] ,            "5-C" : [ "5-B" , "5-D" , "4-D" ] ,
                    "2-D" : [ "1-C" , "2-C" , "2-E" ] ,            "5-D" : [ "6-C" , "5-C" , "5-E" ] ,
                    "2-E" : [ "2-D" , "2-F" , "3-F" ] ,              "5-E" : [ "5-D" , "5-F" , "4-F" ] ,
                    "2-F" : [ "1-E" , "2-E" , "2-G" ]  ,             "5-F" : [ "6-E" , "5-E" , "5-G" ]  ,
                    "2-G" : [ "2-F" , "2-H" , "3-H" ] ,             "5-G" : [ "5-F" , "5-H" , "4-H" ] ,
                    "2-H" : [ "1-G" , "2-G" , "2-I" ] ,            "5-H" : [ "6-G" , "5-G" , "5-I" ] ,
                    "2-I" : [ "2-H" , "3-J" ] ,                          "5-I" : [ "5-H" , "4-J" ] ,

                     "3-A" : [ "3-B" , "4-A" ] ,                       "4-A" : [ "4-B" , "3-A" ] ,                                                                       
                    "3-B" : [ "2-A" , "3-A" , "3-C" ] ,            "4-B" : [ "5-A" , "4-A" , "4-C" ] ,
                    "3-C" : [ "3-B" , "3-D" , "4-C" ] ,            "4-C" : [ "4-B" , "4-D" , "3-C" ] ,
                    "3-D" : [ "2-C" , "3-C" , "3-E" ] ,            "4-D" : [ "5-C" , "4-C" , "4-E" ] ,
                    "3-E" : [ "3-D" , "3-F" , "4-E" ] ,              "4-E" : [ "4-D" , "4-F" , "3-E" ] ,
                    "3-F" : [ "2-E" , "3-E" , "3-G" ]  ,             "4-F" : [ "5-E" , "4-E" , "4-G" ]  ,
                    "3-G" : [ "3-F" , "3-H" , "4-G" ] ,             "4-G" : [ "4-F" , "4-H" , "3-G" ] ,
                    "3-H" : [ "2-G" , "3-G" , "3-I" ] ,            "4-H" : [ "5-G" , "4-G" , "4-I" ] ,
                    "3-I" : [ "3-H" , "3-J" , "4-I" ] ,                "4-I" : [ "4-H" , "4-J" , "3-I" ] , 
                    "3-J" : [ "2-I" , "3-I" , "3-K" ] ,                "4-J" : [ "5-I" , "4-I" , "4-K"  ] ,
                    "3-K" : [ "3-J" ,  "4-K" ] ,                        "4-K" : [ "4-J" , "3-K" ]

                    }


##given_orientation : Stores the nodes of each cell according to its orientation.
given_orientation = [ {} ,

                      #FOR CELL 1
                      { "3-3" : [ "4-A" , "3-C" ] ,
                        "1-1" : [ "4-B" , "3-B" ] ,
                        "2-2" : [ "4-C" , "3-A" ] ,
                      } ,

                      #FOR CELL 2
                      { "3-3" : [ "3-B" , "2-C" ] ,
                        "1-1" : [ "3-C" , "2-B" ] ,
                        "2-2" : [ "3-D" , "2-A" ] ,
                      } ,

                      #FOR CELL 3
                      { "3-3" : [ "4-C" , "3-E" ] ,
                        "1-1" : [ "4-D" , "3-D" ] ,
                        "2-2" : [ "4-E" , "3-C" ] ,
                      } ,

                      #FOR CELL 4
                      { "3-3" : [ "5-A" , "4-D" ] ,
                        "1-1" : [ "5-B" , "4-C" ] ,
                        "2-2" : [ "5-C" , "4-B" ] ,
                      } ,

                      #FOR CELL 5
                      { "3-3" : [ "2-B" , "1-C" ] ,
                        "1-1" : [ "2-C" , "1-B" ] ,
                        "2-2" : [ "2-D" , "1-A" ] ,
                      } ,

                      #FOR CELL 6
                      { "3-3" : [ "3-D" , "2-E" ] ,
                        "1-1" : [ "3-E" , "2-D" ] ,
                        "2-2" : [ "3-F" , "2-C" ] ,
                      } ,

                      #FOR CELL 7
                      { "3-3" : [ "4-E" , "3-G" ] ,
                        "1-1" : [ "4-F" , "3-F" ] ,
                        "2-2" : [ "4-G" , "3-E" ] ,
                      } ,

                      #FOR CELL 8
                      { "3-3" : [ "5-C" , "4-F" ] ,
                        "1-1" : [ "5-D" , "4-E" ] ,
                        "2-2" : [ "5-E" , "4-D" ] ,
                      } ,

                      #FOR CELL 9
                      { "3-3" : [ "6-A" , "5-D" ] ,
                        "1-1" : [ "6-B" , "5-C" ] ,
                        "2-2" : [ "6-C" , "5-B" ] ,
                      } ,

                      #FOR CELL 10
                      { "3-3" : [ "2-D" , "1-E" ] ,
                        "1-1" : [ "2-E" , "1-D" ] ,
                        "2-2" : [ "2-F" , "1-C" ] ,
                      } ,

                      #FOR CELL 11
                      { "3-3" : [ "3-F" , "2-G" ] ,
                        "1-1" : [ "3-G" , "2-F" ] ,
                        "2-2" : [ "3-H" , "2-E" ] ,
                      } ,

                      #FOR CELL 12
                      { "3-3" : [ "4-G" , "3-I" ] ,
                        "1-1" : [ "4-H" , "3-H" ] ,
                        "2-2" : [ "4-I" , "3-G" ] ,
                      } ,

                      #FOR CELL 13
                      { "3-3" : [ "5-E" , "4-H" ] ,
                        "1-1" : [ "5-F" , "4-G" ] ,
                        "2-2" : [ "5-G" , "4-F" ] ,
                      } ,

                      #FOR CELL 14
                      { "3-3" : [ "6-C" , "5-F" ] ,
                        "1-1" : [ "6-D" , "5-E" ] ,
                        "2-2" : [ "6-E" , "5-D" ] ,
                      } ,

                      #FOR CELL 15
                      { "3-3" : [ "2-F" , "1-G" ] ,
                        "1-1" : [ "2-G" , "1-F" ] ,
                        "2-2" : [ "2-H" , "1-E" ] ,
                      } ,

                      #FOR CELL 16
                      { "3-3" : [ "3-H" , "2-I" ] ,
                        "1-1" : [ "3-I" , "2-H" ] ,
                        "2-2" : [ "3-J" , "2-G" ] ,
                      } ,

                      #FOR CELL 17
                      { "3-3" : [ "4-I" , "3-K" ] ,
                        "1-1" : [ "4-J" , "3-J" ] ,
                        "2-2" : [ "4-K" , "3-I" ] ,
                      } ,

                      #FOR CELL 18
                      { "3-3" : [ "5-G" , "4-J" ] ,
                        "1-1" : [ "5-H" , "4-I" ] ,
                        "2-2" : [ "5-I" , "4-H" ] ,
                      } ,

                      #FOR CELL 19
                      { "3-3" : [ "6-E" , "5-H" ] ,
                        "1-1" : [ "6-F" , "5-G" ] ,
                        "2-2" : [ "6-G" , "5-F" ] ,
                      } 

                      ]


'''
* Function Name: find_shortest_path
* Input: graph --> The arena graph , start --> node from which to start ( root ) , end --> node to be found.
               taboo --> which node should not be present in path.
* Output: Returns the shortest path found between start and end nodes. 
* Logic: BFS algorithm , first stores all the (neigbouring) nodes connected to a node in a queue , checks if
              end node is found and continues to do this for all nodes on the same level.
              If end node is found it stores all its parent nodes and returns it.
              Consequently , this path will be the shortest path as we are seaching in levels.
* Example Call: find_shortest_path ( arena , node1 , node2 )
'''
def find_shortest_path ( graph , start , end , taboo ) :
    k = 100
    flag = 0
    if start == end :
        return [ start ]
    visited_nodes = { start }

    #deque --> double ended queue, that means you can add from both sides.
    #We are using because we want to add from end and use FIFO as well.
    queue = collections . deque ( [ ( start , [] ) ] )

    while queue :

        #removes and returns leftmost member of the deque.
        ( current_node , path ) = queue . popleft ( )
        
        #adds current node
        visited_nodes . add ( current_node )

        #Checks the neighbours of the current node.
        for neighbor in graph [ current_node ] :
            if neighbor == taboo[1] :
                continue

            #when end found.
            if neighbor == end : 
                final_path = path + [ current_node , neighbor ]
                if flag == 0 :
                    k = len ( final_path )
                    flag = 1
            
                if ( taboo[0] not in final_path ) and ( len ( final_path ) <= k ) :
                    return final_path

            #Not going back to visited nodes which can happen
            #because undirected graph. Also eliminates cyclic possibilites.
            #And we know this won't be the shortest path.
            if neighbor in visited_nodes :
                continue

            #Neighbour will become the new current
            #And the path is being updated.
            queue . append ( ( neighbor , path + [ current_node ] ) )

            #Keeps account of the visited nodes.
            visited_nodes . add ( neighbor )
            
    return [ "0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0"]


'''
* Function Name: movement_instructions
* Input: shortest_path --> List containing the nodes to travel through in the shortest path till the end.
              The previous node from where it came is attached for orientation purposes.
* Output: Attaches the turns the bot needs to take for traversing to the nodes given in the shortest path.
                 Creates the instruction set that needs to be sent to the bot.
                 Attaches 'R' to a list for Right , 'L' for Left and 'E' for rotating 180 degrees.
                 
* Logic: Exploits the property of the way the graph is labelled. Colums from right to left are labelled from 1 to 6.
               Nodes in a row from top to bottom from A to 
               The function uses the values of the previous node , the current node on which the bot is
               and the node it needs to go.
               Steps :
               1. First the function checks if current node and next node in same column
                   i.e. if the no. in the node string is the same for e.g. 1 in 1-C.
               2. If not in same column, it checks if the node it came from, i.e the previous node, is above or below the current node
                      i.e if the alphabet in the node string is greater or less than current node for e.g. A in 1-A. (  Different columns not possible. )
                      Let 'a' be If previous node is above the current node  and 'b' if the column no. of the next node is less than current column no. then
                          if a and b both true then rotate Right.
                          if a false and b true then rotate Left.
                          if a true and b false then rotate Left.
                          if a false and b false then rotate Right.
                          
                      Similar, logic for if same column case ( But previous node can be in different column. )
                      
                If previous node and next node is the same then rotates 180 degrees.

                If first node is a START node is also handled.
               
               For e.g. :
               previous node = 2-C , current node = 2-D , next node = 1-C.

               1. current node and next node not in same column, next node column no. is less than previous .
               2. previous node above current node.
               Therefore , the bot should rotate to right.
 
               
* Example Call: movement_instructions ( path )
'''
def movement_instructions ( shortest_path ) :

    for node in range ( 1 ,  (len ( shortest_path )) ) :


##        if ( slow_flag == 1 ) :
##            Instruction . append ( 'S' )
##            slow_flag = 0 
        
        

        print ( "STEP " + str ( node ) + " :" )
        #if last node
        if node == ( len ( shortest_path ) - 1 ) :
            if (shortest_path [ node ] == "START-1" ) or ( shortest_path [ node ] == "START-2"  )  :
                print ( "Rotate full circle" )
            else :
                print ( "Rotate if necessary , Then return to original orientation" )
            continue

        for pair in slow_list :
            if ( (pair[0] == shortest_path [ node + 1 ]) ) :
                Instruction . append ( 'S' )
##                slow_flag = 1 

        ##Full 180 case handled
        ##Full 180 case handled
        if ( shortest_path [ node - 1 ] == shortest_path [ node + 1 ] ) :
            print ( "Rotate 180 degrees and follow till next node")

            if ( shortest_path [ node ][ 2 ] == 'A' ) :

                if ( shortest_path [ node - 1 ][ 0 ] == shortest_path [ node ][ 0 ] ) :
                    if ( shortest_path [ node ][ 0 ] == '1' or shortest_path [ node ][ 0 ] == '2' or shortest_path [ node ][ 0 ] == '3' ) :
                        Instruction.append('C')
                    else :
                        Instruction.append('A')

                elif ( shortest_path [ node - 1 ][ 0 ] < shortest_path [ node ][ 0 ] ) :
                    Instruction.append('C')

                elif ( shortest_path [ node - 1 ][ 0 ] > shortest_path [ node ][ 0 ] ) :
                    Instruction.append('A')

            elif ( shortest_path [ node ] == '1-G' or shortest_path [ node ] == '2-I' or shortest_path [ node ] == '3-K' ) :

                if ( shortest_path [ node - 1 ][ 0 ] == shortest_path [ node ][ 0 ] ) :
                    if ( shortest_path [ node ][ 0 ] == '1' or shortest_path [ node ][ 0 ] == '2' or shortest_path [ node ][ 0 ] == '3' ) :
                        Instruction.append('A')
                    else :
                        Instruction.append('C')

                elif ( shortest_path [ node - 1 ][ 0 ] < shortest_path [ node ][ 0 ] ) :
                    Instruction.append('A')

                elif ( shortest_path [ node - 1 ][ 0 ] > shortest_path [ node ][ 0 ] ) :
                    Instruction.append('C')

            elif ( shortest_path [ node ] == '1-B' or shortest_path [ node ] == '1-F' ) :
                if ( shortest_path [ node - 1 ][ 2 ] < shortest_path [ node ][ 2 ] ) :
                    Instruction.append('A')
                else :
                    Instruction.append('C')

            elif ( shortest_path [ node ] == '6-B' or shortest_path [ node ] == '6-F' ) :
                if ( shortest_path [ node - 1 ][ 2 ] < shortest_path [ node ][ 2 ] ) :
                    Instruction.append('C')
                else :
                    Instruction.append('A')

            else :
                Instruction.append ('A')


            continue

 
        #for START nodes
        if ( shortest_path [ node ] == "START-1" ) or ( shortest_path [ node ] == "START-2" ) :
            print ( "Follow the line" )
            continue 

        if ( shortest_path [ node - 1 ] ==  "START-1" ) and ( shortest_path [ node + 1] [ 2 ] == 'C' ) :
            print ( "Left" )
            Instruction.append('L')
            continue

        if ( shortest_path [ node - 1 ] ==  "START-1" ) and ( shortest_path [ node + 1] [ 2 ] == 'E' ) :
            print ( "Right" )
            Instruction.append('R')
            continue

        if ( shortest_path [ node - 1 ] ==  "START-2" ) and ( shortest_path [ node + 1 ] [ 2 ] == 'C' ) :
            print ( "Right" )
            Instruction.append('R')
            continue

        if ( shortest_path [ node - 1 ] ==  "START-2" ) and ( shortest_path [ node + 1 ] [ 2 ] == 'E' ) :
            print ( "Left" )
            Instruction.append('L')
            continue

                   
        #Current node and next node in same column.
        if ( shortest_path [ node ] [ 0 ] == shortest_path [ node + 1 ] [ 0 ] ) :

            #Previous and current node in same column.
            if ( shortest_path [ node - 1 ] [ 0 ] == shortest_path [ node ] [ 0 ] ) :

                #Next node below current node
                if ( shortest_path [ node + 1 ] [ 2 ] > shortest_path [ node ] [ 2 ] ) :
                    if ( ( shortest_path [ node ] [ 2 ] == 'B' ) or ( shortest_path [ node ] [ 2 ] == 'D' ) or ( shortest_path [ node ] [ 2 ] == 'F' ) or ( shortest_path [ node ] [ 2 ] == 'H' ) or ( shortest_path [ node ] [ 2 ] == 'J' ) ) :
                        if ( int ( shortest_path [ node ] [ 0 ] ) <= 3 ) :
                            print ( "Left" )
                            Instruction.append('L')
                        else :
                            print ( "Right" )
                            Instruction.append('R')
                    else :
                        if ( int ( shortest_path [ node ] [ 0 ] ) <= 3 ) :
                            print ( "Right" )
                            Instruction.append('R')
                        else :
                            print ( "Left" )
                            Instruction.append('L')
                    continue

                #Next node above current node
                if ( shortest_path [ node + 1 ] [ 2 ] < shortest_path [ node ] [ 2 ] ) :
                    if ( ( shortest_path [ node ] [ 2 ] == 'B' ) or ( shortest_path [ node ] [ 2 ] == 'D' ) or ( shortest_path [ node ] [ 2 ] == 'F' ) or ( shortest_path [ node ] [ 2 ] == 'H' ) or ( shortest_path [ node ] [ 2 ] == 'J' ) ) :
                        if ( int ( shortest_path [ node ] [ 0 ] ) <= 3 ) :
                            print ( "Right" )
                            Instruction.append('R')
                        else :
                            print ( "Left" )
                            Instruction.append('L')
                    else :
                        if ( int ( shortest_path [ node ] [ 0 ] )<= 3 )  :
                            print ( "Left" )
                            Instruction.append('L')
                        else :
                            print ( "Right" )
                            Instruction.append('R')
                    continue
                
            
            #Previous node was to the right column of current node
            if ( shortest_path [ node - 1 ] [ 0 ] > shortest_path [ node ] [ 0 ] ) :

                #Next node below current node
                if ( shortest_path [ node + 1 ] [ 2 ] > shortest_path [ node ] [ 2 ] ) :
                    print ( "Left" )
                    Instruction.append('L')
                    continue

                #Next node above current node
                if ( shortest_path [ node + 1 ] [ 2 ] < shortest_path [ node ] [ 2 ] ) :
                    print ( "Right" )
                    Instruction.append('R')
                    continue

            #Previous node was to the left column of current node
            if ( shortest_path [ node - 1 ] [ 0 ] < shortest_path [ node ] [ 0 ] ) :

                #Next node below current node
                if ( shortest_path [ node + 1 ] [ 2 ] > shortest_path [ node ] [ 2 ] ) :
                    print ( "Right" )
                    Instruction.append('R')
                    continue

                #Next node above current node
                if ( shortest_path [ node + 1 ] [ 2 ] < shortest_path [ node ] [ 2 ] ) :
                    print ( "Left" )
                    Instruction.append('L')
                    continue

        #Current node and next node not in same column
        else :

            #Previous node above current node
            if ( shortest_path [ node - 1 ] [ 2 ] < shortest_path [ node ] [ 2 ] ) :

                #Next node in right column
                if (  shortest_path [ node +1 ] [ 0 ] > shortest_path [ node ] [ 0 ] ) :
                    print ( "Left" )
                    Instruction.append('L')
                    continue

                #Next node in left column
                if (  shortest_path [ node +1 ] [ 0 ] < shortest_path [ node ] [ 0 ] ) :
                    print ( "Right" )
                    Instruction.append('R')
                    continue

            #Previous node below current node
            else :
                
                #Next node in right column
                if (  shortest_path [ node +1 ] [ 0 ] > shortest_path [ node ] [ 0 ] ) :
                    print ( "Right" )
                    Instruction.append('R')
                    continue

                #Next node in left column
                if (  shortest_path [ node +1 ] [ 0 ] < shortest_path [ node ] [ 0 ] ) :
                    print ( "Left" )
                    Instruction.append('L')
                    continue

def slow_down_paths () :

        global given_orientation
        global arena_config
        global slow_list
        global pebble_nodes

        slow_list = []

        for data in arena_config :
            for axis in [ "1-1", "2-2" , "3-3" ] :
                pebble_nodes[0] = given_orientation [ arena_config[ data ][ 1 ] ] [ axis ] [ 0 ]
                pebble_nodes[1] = given_orientation [ arena_config[ data ][ 1 ] ] [ axis ] [ 1 ]
                
                ##IF ON RIGHT OF CELL
                if ( axis == "3-3" ) :
                    if ( pebble_nodes[ 0 ][ 2 ] != "A" ) :
                        node2 = str( pebble_nodes[ 0 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) - 1 ))
                    else :
                        node2 = "0"

                if ( axis == "2-2" ) :
                    if ( pebble_nodes[ 0 ][ 2 ] != "A" ) :
                        node2 = str( pebble_nodes[ 0 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) + 1 ))
                    else :
                        node2 = "0"

                if ( axis == "1-1" ) :
                    if ( pebble_nodes[0] == "6-D" ) :
                        node2 = "START-2"
                    else :
                        if ( pebble_nodes[ 0 ][ 0 ] != "6" ) :
                            if ( pebble_nodes[ 0 ][ 0 ] < '3' ) :
                                node2 = str( chr( ord ( pebble_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) + 1 ))
                            else :
                                node2 = str( chr( ord ( pebble_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) - 1 ))
                                
                            if ( pebble_nodes[ 0 ][ 0 ] == '3' ) :
                                node2 = str( chr( ord ( pebble_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ])))
                        else :
                            if pebble_nodes[0] == "6-D" :
                                node2 = "START-2"
                            else :
                                node2 = "0"

                
                slow = [ pebble_nodes[0] , node2 ]
                slow_list.append ( slow )


                

                ##IF ON LEFT OF CELL
                if ( axis == "3-3" ) :
                    if ( pebble_nodes[ 1 ][ 2 ] != "A" ) :
                        node2 = str( pebble_nodes[ 1 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) + 1 ))
                    else :
                        node2 = "0"
                        
                if ( axis == "2-2" ) :
                    if ( pebble_nodes[ 1 ][ 2 ] != "A" ) :
                        node2 = str( pebble_nodes[ 1 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) - 1 ))
                    else :
                        node2 = "0"

                if ( axis == "1-1" ) :
                    if ( pebble_nodes[1] == "1-D" ) :
                        node2 = "START-1"
                    else :
                        if ( pebble_nodes[ 1 ][ 0 ] != "1" ) :
                            if ( pebble_nodes[ 1 ][ 0 ] > '4' ) :
                                node2 = str( chr( ord ( pebble_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) + 1 ))
                            else :
                                node2 = str( chr( ord ( pebble_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) - 1 ))
                                
                            if ( pebble_nodes[ 1 ][ 0 ] == '4' ) :
                                node2 = str( chr( ord ( pebble_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( pebble_nodes[ 1 ][ 2 ] )
                        else :
                            if pebble_nodes[0] == "1-D" :
                                node2 = "START-1"
                            else :
                                node2 = "0" 
                
                slow = [ pebble_nodes[1] , node2 ]
                slow_list.append ( slow )

        print ( slow_list )

                        
'''
* Function Name: find_no_of_pebbles
* Input: None 
* Output: Returns the no. of pebbles on the arena obtained from given arena config.
* Logic: In for loop checks if "Pebble" is stored stored in the dictionary and if found increments the counter. 
* Example Call: find_no_of_pebbles ()
'''
def find_no_of_pebbles () :
    global no_of_pebbles 
    for data in arena_config :
        if ( arena_config[ data ][ 0 ] == "Pebble" ) :
            no_of_pebbles += 1
    return no_of_pebbles


'''
* Function Name: task
* Input: None 
* Output: Attaches all the instructions in a list called final instructions.
* Logic: Gets data from arena config and determines the optimal node to go to for pebble pickup or drop.
               i.e. it finds the closest node at which the pebble or pitcher is placed.
               Selects where to go to, pebble node or pitcher node and finds the shorter path between the two possible
               nodes on a given axis. Selects a the node right behind them on the axis so that the bot won't need to rotate
               according to the pebble or pitcher axis on reaching the pebble or pitcher node.

                1.First it fetches the optimal node for pebbles i.e. the closest pebble from the given START.
                2.Then stores the path instructions in an list.
                3.Repeats for pitcher and pebble alternatively and keeps on storing the path instructions found.
   
* Example Call: task ()
'''

def task () :
    global final_instructions
    global Instruction
    global fetching
    global shortest_path 
    global oriented_shortest_path
    global node1
    global pitcher_nodes
    global pebble_nodes
    global arena_config
    global pebble_axis 
    global pitcher_axis
    global visited
    global first_run_done
    global current_pebble
    ##Setting it very high for finding shortest when comparing.
    shortest = [ "0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0"]
    shortest_path_A = [ "0" ,"0" ]
    taboo_list = [ "0" , "0" ]
    ##node2 : where the bot needs to reach
    node2 = ""
    parallel_nodes=["",""]
    parallel_node = ""
    axis = ""
    Instruction = []
    already_oriented = 0

    

    ##closest: stores the key of closest pebble in arena config.
    closest = 100

    ##Finds closest pebble on first run.
    if ( first_run_done != 1 ) :
        for data in arena_config :
            if ( arena_config[ data ][ 0 ] == "Pebble" ) :
                if node1 == "START-1" :
                    shortest_path = find_shortest_path( arena , node1 , given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 1 ] , ["0" , "0"]   )
                
                if node1 == "START-2" :
                    shortest_path = find_shortest_path( arena , node1 , given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 0 ]  , ["0" , "0"] )

                if ( len (shortest) > len(shortest_path) ) :
                    closest = data
                    shortest = shortest_path
                    pebble_nodes[0] = given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 0 ]
                    pebble_nodes[1] = given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 1 ]
                    pebble_axis = arena_config[ data ][ 2 ]
                 
        visited . append ( closest )
        print ( "Closest pebble is " + str ( closest ) )
        ##Stores which pebble aruco marker it goes first.
        current_pebble . append ( closest )
                     
            
        

    ##If not first run then find next pitcher and pebble locations.
    if ( first_run_done == 1 ) :
        for data in arena_config :
            if ( arena_config[ data ][ 0 ] == "Water Pitcher" ) and ( data not in visited ) and ( fetching == "Pitcher" ) :
                pitcher_axis = arena_config[ data ][ 2 ]
                pitcher_nodes[0] = given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 0 ]
                pitcher_nodes[1] = given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 1 ]
                visited . append ( data )
                
            if ( arena_config[ data ][ 0 ] == "Pebble" ) and ( data not in visited ) and ( fetching == "Pebbles" ) :
                pebble_axis = arena_config[ data ][ 2 ] 
                pebble_nodes[0] = given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 0 ]
                pebble_nodes[1] = given_orientation [ arena_config[ data ][ 1 ] ] [ arena_config[ data ][ 2 ] ] [ 1 ]
                visited . append ( data )
                ##Stores pebble aruco marker order it goes first
                current_pebble . append ( data )
                print ( "#################################################")
                print ( visited )
                break
        
    
    print ( "Orientation based on " + str ( oriented_shortest_path ) )





    if ( fetching == "Pebbles" ) :
        axis = pebble_axis


    ##Finds the shortest path to the node right behind the node of the given axis so that when the bot comes from that node it 
    ##won't need to rotate on reaching the node from which the pebble has to be picked up and directly enter saving time.
        
        ##IF ON RIGHT OF CELL 
        if ( axis == "3-3" ) :
            if ( pebble_nodes[ 0 ][ 2 ] != "A" ) :
                node2 = str( pebble_nodes[ 0 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) - 1 ))
            else :
                node2 = "0"

        if ( axis == "2-2" ) :
            if ( pebble_nodes[ 0 ][ 2 ] != "A" ) :
                node2 = str( pebble_nodes[ 0 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) + 1 ))
            else :
                node2 = "0"

        if ( axis == "1-1" ) :
            if ( pebble_nodes[0] == "6-D" ) :
                node2 = "START-2"
            else :
                if ( pebble_nodes[ 0 ][ 0 ] != "6" ) :
                    if ( pebble_nodes[ 0 ][ 0 ] < '3' ) :
                        node2 = str( chr( ord ( pebble_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) + 1 ))
                    else :
                        node2 = str( chr( ord ( pebble_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ]) - 1 ))
                        
                    if ( pebble_nodes[ 0 ][ 0 ] == '3' ) :
                        node2 = str( chr( ord ( pebble_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 0 ][ 2 ])))
                else :
                    if pebble_nodes[0] == "6-D" :
                        node2 = "START-2"
                    else :
                        node2 = "0"

        shortest = [ "0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0"]                

        if ( node2 != "0" ) :
            taboo_list = [ pebble_nodes[ 0 ] , oriented_shortest_path[0] ]
            shortest_path_A = find_shortest_path( arena , node1 , node2 , taboo_list )
            print ( "Shortest Path A = " + str ( shortest_path_A ) )
            shortest_path = find_shortest_path( arena , node1 , node2 , ["0" , "0"] )
            k = pebble_nodes [ 0 ]
            shortest = shortest_path_A
            if ( len ( shortest_path_A ) > len ( shortest_path ) ) :
                shortest = shortest_path
            

        ##IF ON LEFT OF CELL
        if ( axis == "3-3" ) :
            if ( pebble_nodes[ 1 ][ 2 ] != "A" ) :
                node2 = str( pebble_nodes[ 1 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) + 1 ))
            else :
                node2 = "0"
                
        if ( axis == "2-2" ) :
            if ( pebble_nodes[ 1 ][ 2 ] != "A" ) :
                node2 = str( pebble_nodes[ 1 ][ 0 ] ) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) - 1 ))
            else :
                node2 = "0"

        if ( axis == "1-1" ) :
            if ( pebble_nodes[1] == "1-D" ) :
                node2 = "START-1"
            else :
                if ( pebble_nodes[ 1 ][ 0 ] != "1" ) :
                    if ( pebble_nodes[ 1 ][ 0 ] > '4' ) :
                        node2 = str( chr( ord ( pebble_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) + 1 ))
                    else :
                        node2 = str( chr( ord ( pebble_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( chr( ord ( pebble_nodes[ 1 ][ 2 ]) - 1 ))
                        
                    if ( pebble_nodes[ 1 ][ 0 ] == '4' ) :
                        node2 = str( chr( ord ( pebble_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( pebble_nodes[ 1 ][ 2 ] )
                else :
                    if pebble_nodes[0] == "1-D" :
                        node2 = "START-1"
                    else :
                        node2 = "0" 
        

        shortest_path = [ "0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0"]
        
        if ( node2 != "0" ) :
            taboo_list = [ pebble_nodes[ 1 ] , oriented_shortest_path[0] ]
            shortest_path_A = find_shortest_path( arena , node1 , node2 , taboo_list )
            print ( "Shortest Path A = " + str ( shortest_path_A ) )
            
                
            shortest_path = find_shortest_path( arena , node1 , node2 , ["0" , "0"] )
            if ( len ( shortest_path_A ) == len ( shortest_path ) ) :
                shortest_path = shortest_path_A            
            
            node2 = pebble_nodes [ 1 ]

        if ( node2 == "0" ) :
            node2 = pebble_nodes[0]


        ##Selects which of the two required nodes is closer 
        if ( len ( shortest ) <= len ( shortest_path ) ) :
            print ( str ( k ) + " is closer" ) 
            node2 = k
            shortest_path = shortest
            shortest_path . append ( pebble_nodes[ 0 ] )
            
        if ( len ( shortest ) > len ( shortest_path ) ) :
            shortest_path . append ( pebble_nodes[ 1 ] )
            print ( str ( node2 ) + " is closer" )
            






    if ( fetching == "Pitcher" ) :

        axis = pitcher_axis
        print ( pitcher_axis )

    ##Finds the shortest path to the node right behind the node of the given qxis so that when the bot comes from that node it 
    ##won't need to rotate on reaching the node from which the pebble has to be picked up and directly enter saving time.

        ##IF ON RIGHT OF CELL
        if ( axis == "3-3" ) :
            if ( pitcher_nodes[ 0 ][ 2 ] != "A" ) :
                node2 = str( pitcher_nodes[ 0 ][ 0 ] ) + "-" + str ( chr( ord ( pitcher_nodes[ 0 ][ 2 ]) - 1 ))
            else :
                node2 = "0"

        if ( axis == "2-2" ) :
            if ( pitcher_nodes[ 0 ][ 2 ] != "A" ) :
                node2 = str( pitcher_nodes[ 0 ][ 0 ] ) + "-" + str ( chr( ord ( pitcher_nodes[ 0 ][ 2 ]) + 1 ))
            else :
                node2 = "0"

        if ( axis == "1-1" ) :
            if pitcher_nodes[ 0 ] == "6-D" :
                node2 = "START-2"
            else :
                if ( pitcher_nodes[ 0 ][ 0 ] != "6" ) :
                    if ( pitcher_nodes[ 0 ][ 0 ] < '3' ) :
                        node2 = str( chr( ord ( pitcher_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pitcher_nodes[ 0 ][ 2 ]) + 1 ))
                    else :
                        node2 = str( chr( ord ( pitcher_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pitcher_nodes[ 0 ][ 2 ]) - 1 ))
                        
                    if ( pitcher_nodes[ 0 ][ 0 ] == '3' ) :
                        node2 = str( chr( ord ( pitcher_nodes[ 0 ][ 0 ] ) + 1 )) + "-" + str ( chr( ord ( pitcher_nodes[ 0 ][ 2 ])))
            

        shortest = [ "0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0"]               

        if ( node2 != "0" ) :
            taboo_list = [ pitcher_nodes[ 0 ] , oriented_shortest_path[0] ]
            shortest_path_A = find_shortest_path( arena , node1 , node2 , taboo_list )
            print ( "Shortest Path A = " + str ( shortest_path_A ) )
            shortest_path = find_shortest_path( arena , node1 , node2 , ["0" , "0"] )
            print ( shortest_path )
            k = pitcher_nodes[0]
            shortest = shortest_path_A
            if ( len ( shortest_path_A ) > len ( shortest_path ) ) :
                shortest = shortest_path

        ##IF ON LEFT OF CELL
        if ( axis == "3-3" ) :
            if ( pitcher_nodes[ 1 ][ 2 ] != "A" ) :
                node2 = str( pitcher_nodes[ 1 ][ 0 ] ) + "-" + str ( chr( ord ( pitcher_nodes[ 1 ][ 2 ]) + 1 ))
            else :
                node2 = "0"
                
        if ( axis == "2-2" ) :
            if ( pitcher_nodes[ 1 ][ 2 ] != "A" ) :
                node2 = str( pitcher_nodes[ 1 ][ 0 ] ) + "-" + str ( chr( ord ( pitcher_nodes[ 1 ][ 2 ]) - 1 ))
            else :
                node2 = "0"

        if ( axis == "1-1" ) :
            if pitcher_nodes[ 1 ] == "1-D" :
                node2 = "START-1"
            else :
                if ( pitcher_nodes[ 1 ][ 0 ] != "1" ) :
                    if ( pitcher_nodes[ 1 ][ 0 ] > '4' ) :
                        node2 = str( chr( ord ( pitcher_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( chr( ord ( pitcher_nodes[ 1 ][ 2 ]) + 1 ))
                    else :
                        node2 = str( chr( ord ( pitcher_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( chr( ord ( pitcher_nodes[ 1 ][ 2 ]) - 1 ))
                        
                    if ( pitcher_nodes[ 1 ][ 0 ] == '4' ) :
                        node2 = str( chr( ord ( pitcher_nodes[ 1 ][ 0 ] ) - 1 )) + "-" + str ( chr( ord ( pitcher_nodes[ 1 ][ 2 ])))


        shortest_path = [ "0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0" ,"0"]
        
        if ( node2 != "0" ) :
            taboo_list = [ pitcher_nodes[ 1 ] , oriented_shortest_path[0] ]
            shortest_path_A = find_shortest_path( arena , node1 , node2 , taboo_list )
            print ( "Shortest Path A = " + str ( shortest_path_A ) )
            shortest_path = find_shortest_path( arena , node1 , node2 , ["0" , "0" ] )
            if len ( shortest_path_A ) == len ( shortest_path ) :
                shortest_path = shortest_path_A
            node2 = pitcher_nodes [ 1 ]

        if ( node2 == "0" ) :
            node2 = pitcher_nodes[0]    
         
    ##Selects which of the two required nodes is closer
        if ( len ( shortest ) < len ( shortest_path ) ) :
            print ( str ( k ) + " is closer" ) 
            node2 = k
            shortest_path = shortest
            shortest_path . append ( pitcher_nodes[ 0 ] )
            
        if ( len ( shortest ) > len ( shortest_path ) ) :
            shortest_path . append ( pitcher_nodes[ 1 ] )
            print ( str ( node2 ) + " is closer" )





        
    oriented_shortest_path . extend ( shortest_path )

    print ( "Shortest path to " + fetching + " at node " + str ( node2 ) )
    print ( shortest_path )
    
    print ( "STEPS :" )
    movement_instructions ( oriented_shortest_path )

    ##Stores previous node for orientation.
    k = shortest_path[ len ( shortest_path ) - 2 ]

    ##Appends 'M' for turning magnet on.
    Instruction . append ( 'M' )    
    print (Instruction)
    
    
    if ( shortest_path[ len ( shortest_path ) - 1 ] == "START-1" ) or ( shortest_path[ len ( shortest_path ) - 1 ] == "START-2" ) :
        oriented_shortest_path = [ 'None' ]
    else :
        oriented_shortest_path = [ k ]

    node1 = node2

    ##If pebble fetched then changing fetching to pitcher or vice versa.
    if fetching == "Pebbles" :
        fetching = "Pitcher"
    else :
        fetching = "Pebbles"

    first_run_done = 1

    ##Appends total instructions for reaching till final node.
    for instructions in Instruction : 
        final_instructions . append ( instructions )




'''
* Function Name: send_data
* Input: None 
* Output: Sends instructions to the bot.
* Logic: Sends all the instructions in the final_instructions array using a for loop. 
* Example Call: send_data ()
'''
def send_data () :
    global final_instructions
    time . sleep ( 0.5 )
    print ( "DATA SENT!" )
    for i in range( 0 , len (final_instructions) ) :
        ser.write( final_instructions[i].encode('utf-8') )




################## Define Utility Functions Here #######################
"""
Function Name : getCameraMatrix()
Input: None
Output: camera_matrix, dist_coeff
Purpose: Loads the camera calibration file provided and returns the camera and
         distortion matrix saved in the calibration file.
"""

def getCameraMatrix() :
        global camera_matrix, dist_coeff
        with np.load('System.npz') as X:
                camera_matrix, dist_coeff, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]



########################################################################

############# Main Function and Initialisations ########################
"""
Function Name : main()
Input: None
Output: None
Purpose: Initialises OpenGL window and callback functions. Then starts the event
         processing loop.
         (*******Checks if the bot is ready*********) in draw_background function.
"""        
def main():
        n = 0
        n = find_no_of_pebbles ()
        print ( n )
        n = 2*n
        i = 0
        slow_down_paths ()

        while ( n > 0 ) :
                i += 1
                print ( "\n\n" + "Move " + str ( i )  )
                task()
                n -= 1
    
        final_instructions . append ( 'X' )
        final_instructions . append ( 'Z' )


        print ( "########################################" )    
        print ( np . array ( final_instructions ) )
        print ( "All tasks done" )
        print ( current_pebble )
        
        glutInit()
        pygame.init()
        getCameraMatrix()
        glutInitWindowSize(640, 480)
        glutInitWindowPosition( 0 , 100)
        glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
        window_id = glutCreateWindow("OpenGL")
        init_gl()
        glutDisplayFunc(drawGLScene)
        glutIdleFunc(drawGLScene)
        glutReshapeFunc(resize)
        glutMainLoop()
        
        

"""
Function Name : init_gl()
Pebble_after_pickup.blendl: None
Output: None
Purpose: Initialises various parameters related to OpenGL scene.
"""  
def init_gl():
        global texture_object, texture_background
        global Pebble_after_pickup
        global Pot_1
        global Pebble_before_pickup
        global Pot_2
        global Pot_3
        global Pot_4
        global left_wing
        global right_wing
        global main_body
        global main_body_stone
        global crow_stone
        global legs
        Pot_counter = 0
        Pebble_counter = 0
        glClearColor(0.0, 0.0, 1.0, 1.0)
        glClearDepth(1.0) 
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)   
        glMatrixMode(GL_MODELVIEW)
        glLightfv(GL_LIGHT0, GL_POSITION, [0,0,1,0])
        texture_background = glGenTextures(1)
        texture_object = glGenTextures(1)
##        Pebble_after_pickup = OBJ('Pebble_after_pickup.obj', swapyz=True )
##        Pebble_before_pickup = OBJ('Pebble_before_pickup.obj', swapyz=True )
##        Pot_1 = OBJ('Pot_1.obj', swapyz=True )
##        Pot_2 = OBJ('Pot_2.obj', swapyz=True )
##        Pot_3 = OBJ('Pot_3.obj', swapyz=True )
##        Pot_4 = OBJ('Pot_4.obj', swapyz=True )
##        left_wing = OBJ('left_wing.obj', swapyz=True )
##        right_wing = OBJ('right_wing.obj', swapyz=True )
##        main_body = OBJ('main_body.obj', swapyz=True )
##        main_body_stone = OBJ('main_body_stone.obj', swapyz=True )
##        crow_stone = OBJ('crow_stone.obj', swapyz=True )
##        legs = OBJ('legs.obj', swapyz=True )

"""
Function Name : resize()
Input: None
Output: None
Purpose: Initialises the projection matrix of OpenGL scene
"""
def resize(w,h):
        ratio = 1.0* w / h
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, ratio, 0.1, 200.0)

"""
Function Name : drawGLScene()
Input: None
Output: None
Purpose: It is the main callback function which is called again and
         again by the event processing loop. In this loop, the webcam frame
         is received and set as background for OpenGL scene. ArUco marker is
         detected in the webcam frame and 3D model is overlayed on the marker
         by calling the overlay() function.
"""
def drawGLScene():

        global start_flag

        ##Checks if the bot is ready.
        if start_flag == 0 :
            Message = ser.read()
            if Message:
                start_flag = 1
                send_data ()
                
        glMatrixMode(GL_MODELVIEW)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ar_list = []
        ret, frame = cap.read()
        if ret == True:
                draw_background(frame)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                ar_list = detect_markers( frame )
                if ar_list != None :
                        overlay(frame,ar_list)
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
        glutSwapBuffers()
        
########################################################################

######################## Aruco Detection Function ######################
"""
Function Name : detect_markers()
Input: img (numpy array)
Output: aruco list in the form [(aruco_id_1, centre_1, rvec_1, tvec_1),(aruco_id_2,
        centre_2, rvec_2, tvec_2), ()....]
Purpose: This function takes the image in form of a numpy array, camera_matrix and
         distortion matrix as input and detects ArUco markers in the image. For each
         ArUco marker detected in image, paramters such as ID, centre coord, rvec
         and tvec are calculated and stored in a list in a prescribed format. The list
         is returned as output for the function
"""


def detect_markers(img):

    
    global corners , ids

    global start_flag

    ##Checks if the bot is ready.
    if start_flag == 0 :
        Message = ser.read()
        if Message:
            start_flag = 1
            send_data ()

    markerLength = 100
    aruco_list = []
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
    parameters = aruco.DetectorParameters_create()
    ids = list ()
    corners, ids, _ = aruco.detectMarkers(img,aruco_dict,parameters = parameters)  
    
    rvec, tvec,_= aruco.estimatePoseSingleMarkers(corners, markerLength, camera_matrix, dist_coeff)
    
    try:
            if len ( ids ) != 0 :

                    number_of_markers = len(ids)
                    aruco_list = []
                    alist = []
                    ids_list = ids
                    Center_list = []
                    rvec_list = []
                    tvec_list = []
                    Cx_sum=0
                    Cy_sum=0
                        
                    # adding center to the list
                    for marker_counter in range(number_of_markers):
                            for coordinate in range(4):
                                    Cx_sum = Cx_sum + corners[marker_counter][0][coordinate][0]
                                    Cy_sum = Cy_sum + corners[marker_counter][0][coordinate][1]
                                    if coordinate == 3:
                                            Center_list.append([Cx_sum/4,Cy_sum/4])
                                            Cx_sum=0
                                            Cy_sum=0
                                            
                    for i in range(len(ids)):
                        alist.append(ids[i][0])
                        alist.append(Center_list[i])
                        alist.append(rvec[i][0])
                        alist.append(tvec[i][0])
                        aruco_list.append(tuple(alist))
                        alist = []
                        

                    ids = []
                    ##################################################################
                    return aruco_list
    except:
            return


########################################################################


################# This is where the magic happens !! ###################
############### Complete these functions as  directed ##################
"""
Function Name : draw_background()
Input: img (numpy array)
Output: None
Purpose: Takes image as input and converts it into an OpenGL texture. That
         OpenGL texture is then set as background of the OpenGL scene.
         *******Checks if the bot is ready*********
         
"""

def draw_background( frame ):
        global start_flag

        ##Checks if the bot is ready.
        if start_flag == 0 :
            Message = ser.read()
            if Message:
                start_flag = 1
                send_data ()

        
        glEnable(GL_TEXTURE_2D)
        bac_image = Image . fromarray ( frame )

        width = bac_image.size[0]
        height = bac_image.size[1]

        bac_image_data = bac_image .tobytes('raw', 'BGRX', 0, -1) 
        glBindTexture(GL_TEXTURE_2D , texture_background )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width , height,0, GL_RGBA, GL_UNSIGNED_BYTE, bac_image_data )

        
        

        unit_vertices = (
                ( 0 , 0 ) ,
                ( 0 , 1 ) ,
                ( 1 , 1 ) ,
                ( 1 , 0 )
                )
        
        vertices =  (
                ( -30 , -30*height/width , 0 ) ,
                ( -30 , 30*height/width , 0 ) ,
                ( 30 , 30*height/width , 0 ) ,
                ( 30 , -30*height/width , 0 )
                )

        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D , texture_background )
        glTranslatef ( 0 , 0 , -30*1.8 )
        glBegin ( GL_QUADS )
        for vertex in range ( 0 , 4 ):
                glTexCoord2f ( unit_vertices [ vertex ][0] , unit_vertices [ vertex ][1]  )
                glVertex3f( vertices [ vertex ][0] , vertices [ vertex ][1]  , vertices [ vertex ][2] ) 
        glEnd ( )
        glPopMatrix()

        return None



        
"""
Function Name : init_object_texture()
Input: Image file path
Output: None
Purpose: Takes the filepath of a texture file as input and converts it into OpenGL
         texture. The texture is then applied to the next object rendered in the OpenGL
         scene.
"""
def init_object_texture(image_filepath):

        global start_flag

        ##Checks if the bot is ready.
        if start_flag == 0 :
            Message = ser.read()
            if Message:
                start_flag = 1
                send_data ()
    
        glEnable(GL_TEXTURE_2D)
        tex_image = Image.open(image_filepath)
        width = tex_image.size[0]
        height = tex_image.size[1]
        tex_image_data = np.array(list(tex_image.getdata()) , np.uint8 )

        glPixelStorei(GL_UNPACK_ALIGNMENT , 4)
        glBindTexture(GL_TEXTURE_2D , texture_object )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width , height,0, GL_RGBA, GL_UNSIGNED_BYTE, tex_image_data)
        glMatrixMode(GL_MODELVIEW)


        return None
        

"""
Function Name : overlay()
Input: img (numpy array), aruco_list, aruco_id, texture_file (filepath of texture file)
Output: None
Purpose: Receives the ArUco information as input and overlays the 3D Model of a teapot
         on the ArUco marker. That ArUco information is used to
         calculate the rotation matrix and subsequently the view matrix. Then that view matrix
         is loaded as current matrix and the 3D model is rendered.
         
         Parts of this code are already completed, you just need to fill in the blanks. You may
         however add your own code in this function.

         Changes pebble/pitcher model state when receives signal.

         
"""

prev_rmtx_pot = []
prev_rmtx_crow = []
prev_rmtx_pebble = []


flagger = [ 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ]

supa_flag = 0

def rotationMatrixToEulerAngles(R) :
 
##    assert(isRotationMatrix(R))
     
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
 
    return [(180/3.14)*x, (180/3.14)*y, (180/3.14)*z] 

ctr = 0
pebble_info = []
pot_info = []
main_counter = 0
def overlay(img, ar_list):
        
        global current_pebble
        global Object_counter
        global j
        global fetching
        global flaggy
        global prev_rvec
        global prev_tvec
        global prev_rmtx_pot
        global prev_rmtx_crow
        global prev_rmtx_pebble
        global supa_flag
        global flagger
        global ctr
        global no_of_pebbles
        global start_flag
        global pebble_info
        global pot_info
        global main_counter

        main_counter += 1
        ##Checks if the bot is ready.
        if start_flag == 0 :
            Message = ser.read()
            if Message:
                start_flag = 1
                send_data ()


        if ( j == -1 ) :
            fetching = "pebble"

        ##When receives a signal toggles between pitcher and pebble model state toggle
        Message = ser.read()
        if Message and start_flag == 1 :
            if ( ctr < 2*no_of_pebbles ) :
                ctr += 1 
                overlay.Pickup_animation = 1
                if fetching == "pitcher" :
                       fetching = "pebble"
                       Object_counter[0] = Object_counter[0] + 1 
                else :
                     j = j + 1
                     fetching = "pitcher"
                     if j < len ( current_pebble ) :
                         Object_counter[ current_pebble[ j ] ] = 1

        for x in ar_list:

                if start_flag == 0 :
                    Message = ser.read()
                    if Message:
                        start_flag = 1
                        send_data ()
                    

                if (x[0] == 10):
                    if(main_counter % 19 == 0):
                        centre, rvec, tvec = x[1], x[2], x[3]
                        cv2.putText(img,'id='+str(x[0]),tuple(map(int,(centre))),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv2.LINE_AA)
                        m = 100/2
                        pts = np.float32([[-m,m,0],[m,m,0],[m,-m,0],[-m,-m,0]])
                        pt_dict = {}
                        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
                        for i in range(len(pts)):
                                 pt_dict[tuple(pts[i])] = tuple(imgpts[i].ravel())
                        dst1 = pt_dict[tuple(pts[0])];   dst2 = pt_dict[tuple(pts[1])];
                        dst3 = pt_dict[tuple(pts[2])];  dst4 = pt_dict[tuple(pts[3])];
                        
                        img = cv2.line(img, dst1, dst2, (0,255,0), 4)
                        img = cv2.line(img, dst2, dst3, (0,255,0), 4)
                        img = cv2.line(img, dst3, dst4, (0,255,0), 4)
                        img = cv2.line(img, dst4, dst1, (0,255,0), 4)
                        
                        
                        
##                        if (prev_rvec_pot[2] == 0 and rvec[2] >= 0 ):
##                            prev_rvec_pot[2] = rvec[2]
##                        if (prev_rvec_pot[2] < 0):
##                            rvec[2] = prev_rvec_pot[2]
##                        
##                        if (prev_rvec_pot[1] == 0 and ( rvec[0] < 3 and rvec[0] > 2 ) ):
##                            prev_rvec_pot[1] = rvec[0]
##                        if (rvec[0] > 3 ):
##                            rvec[0] = prev_rvec_pot[1]
##
##                        if (prev_rvec_pot[3] == 0 and rvec[1] > 0 ):
##                            prev_rvec_pot[3] = rvec[1]
##                        if (rvec[1] <= 0 ):
##                            rvec[1] = prev_rvec_pot[3]

                        

                        mod_tvec = ( tvec[0]*tvec[0] + tvec[1]*tvec[1] + tvec[2]*tvec[2] )**(0.5)
                        tvec[0] = ((tvec[2]/300)*1.5)*( tvec[0] / mod_tvec + 0.02 )
                        tvec[1] = ((tvec[2]/300)*1.5)*( tvec[1] / mod_tvec - 0.1 )
                        tvec[2] = (tvec[2]/300)    

                        rmtx = cv2.Rodrigues(rvec)[0]
                        pot_x , pot_y , pot_z = rotationMatrixToEulerAngles(rmtx)

                        if ( pot_x > 0 ) :
                            x_diff = abs( 180 - pot_x )
                        else :
                            x_diff = abs( -180 - pot_x )
                        y_diff = abs( 0 - pot_y )

                        if ( ( x_diff + y_diff )>= 10 and flagger[0] == 1 ) :
                            rmtx = prev_rmtx_pot
                        else :
                            prev_rmtx_pot = rmtx
                            flagger[0] = 1
                            
                            
                            
##                        if ( pot_z >= 14 and pot_z <= 172 ) :
##                            if ( pot_y > 0 ) :
##                                    prev_rmtx_pot = rmtx
##                                    flagger[0] = 1
##                            if ( pot_y <= 0 and flagger[0] == 1 ) :
##                                rmtx = prev_rmtx_pot
##
##                        else :
##                            if ( pot_y < 0 ) :
##                                    prev_rmtx_pot = rmtx
##                                    flagger[0] = 1
##                            if ( pot_y >= 0 and flagger[0] == 1 ) :
##                                rmtx = prev_rmtx_pot
                             

                        view_matrix_pot = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0]],
                                                                   [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[1]],
                                                                   [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[2]],
                                                                   [0.0       ,0.0       ,0.0       ,1.0    ]])
                        view_matrix_pot = view_matrix_pot * INVERSE_MATRIX
                        view_matrix_pot = np.transpose(view_matrix_pot)
                        pot_info = view_matrix_pot
                        glBindTexture(GL_TEXTURE_2D , texture_object ) 
                        glMatrixMode(GL_MODELVIEW)
                        glPushMatrix()
                        glLoadMatrixd(view_matrix_pot)
                        glScalef(1.1,1.1,1.1)
                        if Object_counter[ 0 ] == 0:
                                glCallList(Pot_1.gl_list)
                        if Object_counter[ 0 ] == 1:
                                glCallList(Pot_2.gl_list)
                        if Object_counter[ 0 ] == 2:
                                glCallList(Pot_3.gl_list)
                        if Object_counter[ 0 ] == 3:
                                glCallList(Pot_4.gl_list)
                                
                        glPopMatrix()
                    else:
                        centre, rvec, tvec = x[1], x[2], x[3]
                        cv2.putText(img,'id='+str(x[0]),tuple(map(int,(centre))),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv2.LINE_AA)
                        m = 100/2
                        pts = np.float32([[-m,m,0],[m,m,0],[m,-m,0],[-m,-m,0]])
                        pt_dict = {}
                        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
                        for i in range(len(pts)):
                                 pt_dict[tuple(pts[i])] = tuple(imgpts[i].ravel())
                        dst1 = pt_dict[tuple(pts[0])];   dst2 = pt_dict[tuple(pts[1])];
                        dst3 = pt_dict[tuple(pts[2])];  dst4 = pt_dict[tuple(pts[3])];
                        
                        img = cv2.line(img, dst1, dst2, (0,255,0), 4)
                        img = cv2.line(img, dst2, dst3, (0,255,0), 4)
                        img = cv2.line(img, dst3, dst4, (0,255,0), 4)
                        img = cv2.line(img, dst4, dst1, (0,255,0), 4)

                        
                        
                        glBindTexture(GL_TEXTURE_2D , texture_object ) 
                        glMatrixMode(GL_MODELVIEW)
                        glPushMatrix()
                        glLoadMatrixd(pot_info)
                        glScalef(1.1,1.1,1.1)
                        if Object_counter[ 0 ] == 0:
                                glCallList(Pot_1.gl_list)
                        if Object_counter[ 0 ] == 1:
                                glCallList(Pot_2.gl_list)
                        if Object_counter[ 0 ] == 2:
                                glCallList(Pot_3.gl_list)
                        if Object_counter[ 0 ] == 3:
                                glCallList(Pot_4.gl_list)
                                
                        glPopMatrix()
                        
                if ( x[0] > 0 ) and ( x[0] < 10 ) :
                    if( main_counter % 20 == 0):
                        main_counter = 0
                        centre, rvec, tvec = x[1], x[2], x[3]
                        cv2.putText(img,'id='+str(x[0]),tuple(map(int,(centre))),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv2.LINE_AA)
                        m = 100/2
                        pts = np.float32([[-m,m,0],[m,m,0],[m,-m,0],[-m,-m,0]])
                        pt_dict = {}
                        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
                        for i in range(len(pts)):
                                 pt_dict[tuple(pts[i])] = tuple(imgpts[i].ravel())
                        dst1 = pt_dict[tuple(pts[0])];   dst2 = pt_dict[tuple(pts[1])];
                        dst3 = pt_dict[tuple(pts[2])];  dst4 = pt_dict[tuple(pts[3])];
                        
                        img = cv2.line(img, dst1, dst2, (0,255,0), 4)
                        img = cv2.line(img, dst2, dst3, (0,255,0), 4)
                        img = cv2.line(img, dst3, dst4, (0,255,0), 4)
                        img = cv2.line(img, dst4, dst1, (0,255,0), 4)

                        mod_tvec = ( tvec[0]*tvec[0] + tvec[1]*tvec[1] + tvec[2]*tvec[2] )**(0.5)
                        tvec[0] = ((tvec[2]/300)*1.5)*( tvec[0] / mod_tvec + 0.02 )
                        tvec[1] = ((tvec[2]/300)*1.5)*( tvec[1] / mod_tvec - 0.1 )
                        tvec[2] = (tvec[2]/300)

                        rmtx = cv2.Rodrigues(rvec)[0]
                        

##                        if ( supa_flag == 0 ) :
##                            for l in range ( 1 , 10 ) :
##                                print ( l )
##                                prev_rmtx_pebble . append ( rmtx )
##                            supa_flag = 1
##
##                        pebble_x , pebble_y , pebble_z = rotationMatrixToEulerAngles(rmtx)
##
##                    
##                        if ( pebble_z >= 14 and pebble_z <= 172 ) :
##                            if ( pebble_y > 0 ) :
##                                    prev_rmtx_pebble[x[0]-1] = rmtx
##                                    flagger[x[0]] = 1
##                            if ( pebble_y <= 0 and flagger[x[0]] == 1 ) :
##                                rmtx = prev_rmtx_pebble[x[0]-1]
##
##                        else :
##                            if ( pebble_y < 0 ) :
##                                    prev_rmtx_pebble = rmtx
##                                    flagger[x[0]] = 1
##                            if ( pebble_y >= 0 and flagger[x[0]] == 1 ) :
##                                rmtx = prev_rmtx_pebble
##                        
                        
                        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0]],
                                                                   [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[1]],
                                                                   [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[2]],
                                                                   [0.0       ,0.0       ,0.0       ,1.0    ]])
                        view_matrix = view_matrix * INVERSE_MATRIX
                        view_matrix = np.transpose(view_matrix)
                        pebble_info[x[0]] = view_matrix

                        init_object_texture("GroundClay002_COL_VAR2_3K.png")
                        glBindTexture(GL_TEXTURE_2D , texture_object )
                        glMatrixMode(GL_MODELVIEW)
                        glPushMatrix()
                        glLoadMatrixd(view_matrix)
                        if Object_counter[x[0]] > 0:
                                glCallList(Pebble_after_pickup.gl_list)
                        if Object_counter[x[0]] == 0:
                                glCallList(Pebble_before_pickup.gl_list)
                        glPopMatrix()
                    else:
                        centre, rvec, tvec = x[1], x[2], x[3]
                        cv2.putText(img,'id='+str(x[0]),tuple(map(int,(centre))),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv2.LINE_AA)
                        m = 100/2
                        pts = np.float32([[-m,m,0],[m,m,0],[m,-m,0],[-m,-m,0]])
                        pt_dict = {}
                        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
                        for i in range(len(pts)):
                                 pt_dict[tuple(pts[i])] = tuple(imgpts[i].ravel())
                        dst1 = pt_dict[tuple(pts[0])];   dst2 = pt_dict[tuple(pts[1])];
                        dst3 = pt_dict[tuple(pts[2])];  dst4 = pt_dict[tuple(pts[3])];
                        
                        img = cv2.line(img, dst1, dst2, (0,255,0), 4)
                        img = cv2.line(img, dst2, dst3, (0,255,0), 4)
                        img = cv2.line(img, dst3, dst4, (0,255,0), 4)
                        img = cv2.line(img, dst4, dst1, (0,255,0), 4)

                        
                        
                        init_object_texture("GroundClay002_COL_VAR2_3K.png")
                        glBindTexture(GL_TEXTURE_2D , texture_object )
                        glMatrixMode(GL_MODELVIEW)
                        glPushMatrix()
                        glLoadMatrixd(pebble_info[x[0]])
                        if Object_counter[x[0]] > 0:
                                glCallList(Pebble_after_pickup.gl_list)
                        if Object_counter[x[0]] == 0:
                                glCallList(Pebble_before_pickup.gl_list)
                        glPopMatrix()
                        
                if x[0] == 11 :
                        centre, rvec, tvec = x[1], x[2], x[3]
                        cv2.putText(img,'id='+str(x[0]),tuple(map(int,(centre))),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1,cv2.LINE_AA)
                        m = 100/2
                        pts = np.float32([[-m,m,0],[m,m,0],[m,-m,0],[-m,-m,0]])
                        pt_dict = {}
                        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
                        for i in range(len(pts)):
                                 pt_dict[tuple(pts[i])] = tuple(imgpts[i].ravel())
                        dst1 = pt_dict[tuple(pts[0])];   dst2 = pt_dict[tuple(pts[1])];
                        dst3 = pt_dict[tuple(pts[2])];  dst4 = pt_dict[tuple(pts[3])];
                        
                        img = cv2.line(img, dst1, dst2, (0,255,0), 4)           #Ploting square around the detected marker.
                        img = cv2.line(img, dst2, dst3, (0,255,0), 4)
                        img = cv2.line(img, dst3, dst4, (0,255,0), 4)
                        img = cv2.line(img, dst4, dst1, (0,255,0), 4)
                        mod_tvec = ( tvec[0]*tvec[0] + tvec[1]*tvec[1] + tvec[2]*tvec[2] )**(0.5)       #Computing the cordinates for Opengl using OpenCv parameters.
                        tvec[0] = ((tvec[2]/300)*1.5)*( tvec[0] / mod_tvec + 0.02 )
                        tvec[1] = ((tvec[2]/300)*1.5)*( tvec[1] / mod_tvec - 0.1 )
                        tvec[2] = tvec[2]/300
                        if(overlay.Pickup_animation == 1):
                            
                            overlay.crow_stone = overlay.crow_stone + 1
                            overlay.Pickup_animation = 0
                            overlay.Pickup_animation_1 = 1
                            overlay.Rotation_counter = 0
                            overlay.Rotate_up_or_down = 0                            
                        if(overlay.Rotate_up_or_down == 0):
                            overlay.Rotation_counter = overlay.Rotation_counter + 4
                            if(overlay.Rotation_counter >= overlay.Total_rotation):
                                overlay.Rotate_up_or_down = 1
                        else:
                            if(overlay.crow_stone % 2 != 0):
                                overlay.main_body = 1
                            else:
                                overlay.main_body = 0
                            overlay.Rotation_counter = overlay.Rotation_counter - 4
                            if(overlay.Rotation_counter == 0):
                                overlay.Pickup_animation_1 = 0
                                overlay.Rotate_up_or_down = 0
##                        if (overlay.flicker_counter < 1) :
##                            overlay.flicker_counter = overlay.flicker_counter + 1
##                            overlay.rvec_sample = overlay.rvec_sample + rvec
##                            overlay.Calculated_rvec = overlay.rvec_sample/1    
##                        else :
##                            if (rvec[0] < overlay.Calculated_rvec[0] + 0.) and (rvec[0] > overlay.Calculated_rvec[0] - 0.1) :
##                                overlay.Calculated_rvec[0] = rvec[0]
##                            if (rvec[1] < overlay.Calculated_rvec[1] + 0.1) and (rvec[1] > overlay.Calculated_rvec[1] - 0.1) :
##                                overlay.Calculated_rvec[1] = rvec[1]
##                            if (rvec[2] < overlay.Calculated_rvec[2] + 0.1) and (rvec[2] > overlay.Calculated_rvec[0] - 0.1) :
##                                overlay.Calculated_rvec[2] = rvec[2]
                        ############################# FOR MAIN BODY##########################
##                        rvec = overlay.Calculated_rvec

                        
                        tvec[1] = tvec[1] - 0.0065*overlay.Rotation_counter
                            
                        rmtx = cv2.Rodrigues(rvec)[0]
                        crow_x , crow_y , crow_z = rotationMatrixToEulerAngles(rmtx)
                        
                        if ( ( crow_z > 101 and crow_z <= 180 ) or ( crow_z >= -180 and crow_z <= -91 ) ):
                                
                            if  ( (  ( ( crow_x > 0 and crow_y < 0 ) or ( crow_x > 0 and crow_y > 0 ) ) ) and flagger[10] == 1 ) :
                                for a in range ( 0 , 3 ) :
                                    rmtx[a][1] = prev_rmtx_crow[a][1]
                                    rmtx[a][2] = prev_rmtx_crow[a][2]

                            else :
                                prev_rmtx_crow = rmtx
                                flagger[10] = 1
                        elif ( ( crow_z >= 0 and crow_z <= 101 ) ) :
                            
                            if  ( ( ( crow_x < 0 and crow_y < 0 ) ) and flagger[10] == 1 ) :
                                    for a in range ( 0 , 3 ) :
                                        rmtx[a][1] = prev_rmtx_crow[a][1]
                                        rmtx[a][2] = prev_rmtx_crow[a][2]
                            else :
                                prev_rmtx_crow = rmtx 
                                flagger[10] = 1

                        else  :
                            if  ( (( crow_x < 0 and crow_y > 0 ) ) and flagger[10] == 1 ) :
                                for a in range ( 0 , 3 ) :
                                    rmtx[a][1] = prev_rmtx_crow[a][1]
                                    rmtx[a][2] = prev_rmtx_crow[a][2]
                            else :
                                prev_rmtx_crow = rmtx 
                                flagger[10] = 1
                        
                        view_matrix_crow_body = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0]],
                                                                   [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[1]],
                                                                   [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[2]],
                                                                   [0.0       ,0.0       ,0.0       ,1.0    ]])
                        view_matrix_crow_body = view_matrix_crow_body * INVERSE_MATRIX
                        view_matrix_crow_body = np.transpose(view_matrix_crow_body)

                        
                        if(overlay.main_body == 1):
                            init_object_texture("GroundClay002_COL_VAR2_3K.png")                   
                            glMatrixMode(GL_MODELVIEW)
                            glPushMatrix()
                            glLoadMatrixd(view_matrix_crow_body)
                            if(overlay.Pickup_animation_1 == 1):
                                glRotatef(overlay.Rotation_counter*1.5, 0,1 , 0)
                                glTranslatef(-overlay.Rotation_counter/57,0,-overlay.Rotation_counter/140)
                            glScalef(0.8,0.8,0.8)
                            glCallList(crow_stone.gl_list)
                            glPopMatrix()
                        init_object_texture("crow_wing.png")                   
                        glMatrixMode(GL_MODELVIEW)
                        glPushMatrix()
                        glLoadMatrixd(view_matrix_crow_body)
                        if(overlay.Pickup_animation_1 == 1):
                            glRotatef(overlay.Rotation_counter*1.5, 0,1 , 0)
                            glTranslatef(-overlay.Rotation_counter/57,0,-overlay.Rotation_counter/140)
                        if(overlay.main_body == 0):
                            glScalef(0.8,0.8,0.8)
                            glCallList(main_body.gl_list)
                        else:
                            glScalef(0.8,0.8,0.8)
                            glCallList(main_body_stone.gl_list)
                        glPopMatrix()
                        glPushMatrix()
                        glLoadMatrixd(view_matrix_crow_body)
                        if(overlay.Pickup_animation_1 == 1):
                            glRotatef(overlay.Rotation_counter*1.5, 0,1 , 0)
                            glTranslatef(-overlay.Rotation_counter/57,0,-overlay.Rotation_counter/140)
                        else:
                            glTranslatef(overlay.Rotation_counter/90,overlay.Rotation_counter/55,overlay.Rotation_counter/120)
                            glRotatef(overlay.Rotation_counter, 1, 0 , 0)
                            glRotatef(-overlay.Rotation_counter/1.5, 0, 1 , 0)
                        glScalef(0.8,0.8,0.8)
                        glCallList(left_wing.gl_list)
                        glPopMatrix()
                        glPushMatrix()
                        glLoadMatrixd(view_matrix_crow_body)
                        if(overlay.Pickup_animation_1 == 1):
                            glRotatef(overlay.Rotation_counter*1.5, 0,1 , 0)
                            glTranslatef(-overlay.Rotation_counter/57,0,-overlay.Rotation_counter/140)
                        else:
                            glTranslatef(overlay.Rotation_counter/90,-overlay.Rotation_counter/55,overlay.Rotation_counter/120)
                            glRotatef(-overlay.Rotation_counter, 1, 0 , 0)
                            glRotatef(-overlay.Rotation_counter/1.5, 0, 1 , 0)
                        glScalef(0.8,0.8,0.8)
                        glCallList(right_wing.gl_list)
                        glPopMatrix()
                        glPushMatrix()
                        glLoadMatrixd(view_matrix_crow_body)
                        glScalef(0.8,0.8,0.8)
                        glCallList(legs.gl_list)
                        glPopMatrix()
overlay.rvec_sample = 0
overlay.flicker_counter = 0
overlay.Calculated_rvec = 0
overlay.prev_rvec = 0
overlay.main_body = 0
overlay.crow_stone = 0
overlay.Pickup_animation_1 = 0
overlay.Pickup_animation = 0
overlay.Rotation_counter = 0
overlay.Rotate_up_or_down = 0
overlay.Total_rotation = 40       

########################################################################

if __name__ == "__main__":

        main()
