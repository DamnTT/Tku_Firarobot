#!/usr/bin/env python
from __future__ import print_function
import rospy
import math
from robot.robot import Robot


SOCCER_BALL_RADIUS = 0

class Block(Robot):
  def __init__(self):
    self.correct_ang = []
    self.cp_value = 0

  def ClassicBlocking(self, ball_dis, ball_ang, front_ang):
    #front_ang = front_ang * -1
    #front_ang_deg = math.degrees(front_ang)
    front_ang_deg=(front_ang_deg + 360) % 360
    #if front_ang_deg>180:
     # front_ang_deg=front_ang_deg-360
    #else:
      #pass
    self.correct_ang.append(front_ang_deg)
    self.cp_value = self.correct_ang[0]
    o_x   = 0
    o_y   = ball_dis * math.sin(math.radians(ball_ang))
    v_x, v_y = self.Rotate(o_x, o_y, -front_ang_deg) 
    v_yaw = self.cp_value - front_ang_deg
    return v_x, v_y, v_yaw
  
  def BlockLimit(self,front_ang):
    #front_ang=front_ang*-1
    #front_ang_deg=math.degrees(front_ang)
    #front_ang_deg=(front_ang_deg+360)%360
    #if front_ang_deg>180:
     # front_ang_deg=front_ang_deg-360
    #else:
     # pass
    self.correct_ang.append(front_ang_deg)
    self.cp_value = self.correct_ang[0]
    v_x=0
    v_y=0
    v_yaw=0#self.cp_value-front_ang_deg
    return v_x, v_y, v_yaw


  def GuardPenalting(self, ball_dis, ball_ang, front_ang):
    ball_dis = ball_dis - SOCCER_BALL_RADIUS
    #front_ang=front_ang*-1
    #front_ang_deg=math.degrees(front_ang)
    #front_ang_deg=(front_ang_deg+360)%360
    #if front_ang_deg>180:
    #  front_ang_deg=front_ang_deg-360
    #else:
    #  pass
    self.correct_ang.append(front_ang_deg)
    self.cp_value = self.correct_ang[0]
    v_x   = (ball_dis * math.cos(math.radians(ball_ang)))
    v_y   = (ball_dis * math.sin(math.radians(ball_ang)))
    v_yaw = ball_ang
    return v_x, v_y, v_yaw

  def Return(self,goal_dis, goal_ang, front_ang):
    #front_ang = front_ang*-1
    #front_ang_deg = math.degrees(front_ang)
    #front_ang_deg = (front_ang_deg+360)%360
    #if front_ang_deg > 180:
    #  front_ang_deg = front_ang_deg-360
    #else:
    #  pass
    self.correct_ang.append(front_ang_deg)
    self.cp_value = self.correct_ang[0]
    distance = 80
    o_x   = distance - abs(goal_dis * math.cos(math.radians(goal_ang)))
    o_y   = goal_dis * math.sin(math.radians(goal_ang))
    v_yaw = self.cp_value-front_ang_deg
    #v_x,v_y = self.Rotate(o_x, o_y, -front_ang_deg)
    return o_x, o_y, v_yaw

  def ClassicPushing(self, ball_dis, ball_ang, front_ang):
    ball_dis = ball_dis - SOCCER_BALL_RADIUS
    #front_ang = front_ang * -1
    #front_ang_deg = math.degrees(front_ang)
    #front_ang_deg = (front_ang_deg + 360) % 360
    #if front_ang_deg > 180:
    #  front_ang_deg = front_ang_deg - 360
    #else:
    #  pass
    self.correct_ang.append(front_ang_deg)
    self.cp_value = self.correct_ang[0]
    o_x   = (ball_dis * math.cos(math.radians(ball_ang)))
    o_y   = (ball_dis * math.sin(math.radians(ball_ang)))
    # v_x, v_y = self.Rotate(o_x, o_y,-front_ang)
    v_yaw = ball_ang
    return o_x, o_y, v_yaw



  


