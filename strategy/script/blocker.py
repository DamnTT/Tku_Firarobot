#!/usr/bin/env python
import rospy
import sys
import math
import time
from statemachine import StateMachine, State
from robot.robot import Robot
from std_msgs.msg import String
from my_sys import log, SysCheck, logInOne
from methods.chase import Chase
from methods.attack import Attack
from methods.behavior import Behavior
from methods.block import Block
from dynamic_reconfigure.server import Server as DynamicReconfigureServer
from strategy.cfg import RobotConfig
import dynamic_reconfigure.client

class Core(Robot, StateMachine):

  last_ball_dis = 0
  last_time     = time.time()
  idle    = State('Idle', initial = True)

  block     = State('Block')
  wait      = State('Wait')
  r_limit   = State('R_limit')
  l_limit   = State('L_limit')
  push      = State('Push')
  ret       = State('Ret')
  noballret = State('NoBallRet')
  noballwait = State('NoBallWait')
  guard_penalty = State('Guard_Penalty')

  toIdle    = idle.to.itself() | block.to(idle) | wait.to(idle) | r_limit.to(idle) | l_limit.to(idle) | push.to(idle) | ret.to(idle) | noballret.to(idle) | noballwait.to(push) | guard_penalty.to(idle)
  toBlock   = idle.to(block) | wait.to(block) | block.to.itself() | r_limit.to(block) | l_limit.to(block) | ret.to(block) | noballret.to(block) | noballwait.to(block)
  toWait    = idle.to(wait) | block.to(wait) | wait.to.itself() 
  toR_limit = idle.to(r_limit) | block.to(r_limit) | r_limit.to.itself() 
  toL_limit = idle.to(l_limit) | block.to(l_limit) | l_limit.to.itself() 
  toPush    = idle.to(push) | block.to(push) | push.to.itself() | l_limit.to(push) | r_limit.to(push) | noballwait.to(push) | noballret.to(push)
  toRet     = idle.to(ret) | push.to(ret) | ret.to.itself() | guard_penalty.to(ret)
  toNoBallRet = idle.to(noballret) | block.to(noballret) | r_limit.to(noballret) | l_limit.to(noballret) | noballret.to.itself()
  toNoBallWait = idle.to(noballwait) | noballret.to(noballwait) | push.to(noballwait) | noballwait.to.itself() | guard_penalty.to(noballwait)
  toGuard_Penalty = idle.to(guard_penalty) | guard_penalty.to.itself()

  def Callback(self, config, level):
    self.game_start = config['game_start']
    self.game_state = config['game_state']
    self.run_point  = config['run_point']
    self.side       = config['our_goal']
    self.opp_side   = 'Yellow' if config['our_goal'] == 'Blue' else 'Blue'
    self.run_x      = config['run_x']
    self.run_y      = config['run_y']
    self.run_yaw    = config['run_yaw']
    self.strategy_mode = config['strategy_mode']
    self.orb_attack_ang  = config['orb_attack_ang']
    self.atk_shoot_ang  = config['atk_shoot_ang']
   #self.ROTATE_V_ang   = config['ROTATE_V_ang']
    self.remaining_range_v   = config['remaining_range_v']
    self.remaining_range_yaw = config['remaining_range_yaw']
    self.robot.ChangeVelocityRange(config['minimum_v'], config['maximum_v'])
    self.robot.ChangeAngularVelocityRange(config['minimum_w'], config['maximum_w'])
    self.robot.ChangeBallhandleCondition(config['ballhandle_dis'], config['ballhandle_ang'])
    
    self.run_point = config['run_point']

    return config

  def __init__(self, robot_num, sim = False):
    super(Core, self).__init__(sim)
    StateMachine.__init__(self)
    self.CC  = Chase()
    self.AC  = Attack()
    self.BC  = Behavior()
    self.BK  = Block()
    self.left_ang = 0
    dsrv = DynamicReconfigureServer(RobotConfig, self.Callback)

  
  def on_toIdle(self):
    for i in range(0, 10):
        self.MotionCtrl(0,0,0)
    log("To Idle1")
  
  def on_toBlock(self, t, side ,i):
    x, y, yaw = self.BK.ClassicBlocking(t[side]['dis'],\
                                        t[side]['ang'],\
                                        t['ball']['dis'],\
                                        t['ball']['ang'],\
                                        t[side]['right'],\
                                        t[side]['left'],\
                                        i['imu']['ang'],\
                                        t['ball']['speed_pwm_y'])
    self.MotionCtrl(x, y, yaw)
    log("To Block")
    

  def on_toWait(self, t, side):
    x, y, yaw = self.WT.ClassicWaiting(t['ball']['dis'],\
                                       t['ball']['ang'],\
                                       t[side]['dis'],\
                                       t[side]['ang'])
    self.MotionCtrl(x, y, yaw)
    log("To Wait")
  
  def on_toRet(self, t, side):
    x, y, yaw = self.RT.ClassicReturning(t['ball']['ang'],\
                                         t[side]['dis'],\
                                         t[side]['ang'])
    self.MotionCtrl(x, y, yaw)
    log("To Return")

  def on_toNoBallRet(self, t, side):
    x, y, yaw = self.NR.NoBallReturning(t[side]['dis'],\
                                         t[side]['ang'])
    self.MotionCtrl(x, y, yaw)
    log("To Noballreturn")

  def on_toNoBallWait(self, t, side):
    x, y, yaw = self.NW.NoBallWaiting(t[side]['dis'],\
                                      t[side]['ang'])
    self.MotionCtrl(x, y, yaw)
    log("To Noballwait")

  def on_toPush(self, t):
    x, y, yaw = self.PH.ClassicPushung(t['ball']['dis'],\
                                       t['ball']['ang'],\
                                       t['ball']['speed_pwm_x'],\
                                       t['ball']['speed_pwm_y'])
    self.MotionCtrl(x, y, yaw)
    log("To Push")
  
  def on_toR_limit(self, t, side,i):
    x, y, yaw = self.RL.ClassicRlimit(t['ball']['dis'],\
                                       t['ball']['ang'],\
                                       t[side]['dis'],\
                                       t[side]['ang'],\
                                       i['imu']['ang'])
    self.MotionCtrl(x, y, yaw)
    log("To Rlimit")    

  def on_toL_limit(self, t, side,i):
    x, y, yaw = self.LL.ClassicLlimit(t['ball']['dis'],\
                                       t['ball']['ang'],\
                                       t[side]['dis'],\
                                       t[side]['ang'],\
                                       i['imu']['ang'])
    self.MotionCtrl(x, y, yaw)
    log("To Llimit")
  
  def on_toGuard_Penalty(self, t):
    x, y, yaw = self.GP.GuardPenalting(t['ball']['dis'],\
                                       t['ball']['ang'],\
                                       t['ball']['speed_pwm_x'],\
                                       t['ball']['speed_pwm_y'])
    self.MotionCtrl(x, y, yaw)
    log("To Guard Penalty")

  def PubCurrentState(self):
    self.RobotStatePub(self.current_state.identifier)

  def CheckBallHandle(self):
    if self.RobotBallHandle():
      ## Back to normal from Accelerator
      self.ChangeVelocityRange(0, self.maximum_v)
      Core.last_ball_dis = 0

    return self.RobotBallHandle()

  def Accelerator(self, exceed = 100):
    t = self.GetObjectInfo()
    if Core.last_ball_dis == 0:
      Core.last_time = time.time()
      Core.last_ball_dis = t['ball']['dis']
    elif t['ball']['dis'] >= Core.last_ball_dis:
      if time.time() - Core.last_time >= 0.8:
        self.ChangeVelocityRange(0, exceed)
    else:
      Core.last_time = time.time()
      Core.last_ball_dis = t['ball']['dis']

class Strategy(object):
  def __init__(self, num, sim=False):
    rospy.init_node('core', anonymous=True)
    self.rate = rospy.Rate(1000)
    self.robot = Core(sim)
    dsrv = Server(StrategyConfig, self.Callback)
    self.dclient = dynamic_reconfigure.client.Client("core", timeout=30, config_callback=None)
    self.main()

  def main(self):
    while not rospy.is_shutdown():      
      self.robot.PubCurrentState()
      targets = self.robot.GetObjectInfo()
      position = self.robot.GetRobotInfo()
      twopoint = self.robot.GetTwopoint()


      if targets is None or targets['ball']['ang'] == 999 and self.robot.game_start:
        print("Can not find ball")
        self.robot.toIdle()

      else:
        if not self.robot.is_idle and not self.game_start:
            self.robot.toIdle()

        if self.robot.is_idle:
          if self.game_start:
            if self.game_state=="Penalty_Kick":
              self.robot.toGuard_Penalty(targets)
            else:
              self.robot.toBlock(targets,self.side,imu)
          
        if self.robot.is_block:
          if targets['ball']['dis'] > 300 and not targets['ball']['dis'] == 999:
            self.robot.toWait(targets,self.side)
          elif twopoint[self.side]['left'] > 115 and twopoint[self.side]['left'] > twopoint[self.side]['right'] and targets['ball']['ang'] <= 0:
            self.robot.toR_limit(targets,self.side,imu)
          elif twopoint[self.side]['right'] > 115 and twopoint[self.side]['left'] < twopoint[self.side]['right'] and targets['ball']['ang'] >= 0:
            self.robot.toL_limit(targets,self.side,imu)
          elif targets['ball']['dis'] <= 300:
            if targets['ball']['dis'] <= 80 and abs(targets['ball']['ang']) < 10:
              self.robot.toPush(targets)      
            else:
              self.robot.toBlock(targets,self.side,imu)
          elif twopoint[self.side]['right'] == 999 or twopoint[self.side]['left'] == 999:
            self.robot.toBlock(targets,self.side,imu)
          if targets['ball']['ang'] == 999:
            self.robot.toNoBallRet(targets,self.side)
            
        if self.robot.is_wait:
          if targets['ball']['dis']>300:
            self.robot.toWait(targets,self.side)          
          elif targets['ball']['dis']<=300:
            self.robot.toBlock(targets,self.side,imu)
            
        if self.robot.is_r_limit:
          if targets['ball']['ang']<=0:
            self.robot.toR_limit(targets,self.side,imu)
          elif targets['ball']['ang']>0:
            self.robot.toBlock(targets,self.side,imu)          
          if twopoint[self.side]['right']>110:
            self.robot.toBlock(targets,self.side,imu)          
          if targets['ball']['dis']<=80:
            self.robot.toPush(targets)          
          if targets['ball']['ang']==999:
            self.robot.toNoBallRet(targets,self.side)

        if self.robot.is_l_limit:
          if targets['ball']['ang']>=0:
            self.robot.toL_limit(targets,self.side,imu)          
          elif targets['ball']['ang']<0:
            self.robot.toBlock(targets,self.side,imu)                     
          if twopoint[self.side]['left']>110:
            self.robot.toBlock(targets,self.side,imu)          
          if targets['ball']['dis']<=80:
            self.robot.toPush(targets)          
          if targets['ball']['ang']==999:
            self.robot.toNoBallRet(targets,self.side)
            
        if self.robot.is_push:
          if targets['ball']['dis']<=80:
            if targets[self.side]['dis']<120:                
              self.robot.toPush(targets)            
            else:                
              self.robot.toRet(targets,self.side)            
          elif targets['ball']['dis']>80 and not targets['ball']['dis']==999:         
            self.robot.toRet(targets,self.side)         
          if targets['ball']['ang']==999:           
            self.robot.toNoBallWait(targets,self.side)            
          elif targets['ball']['dis']>130 and not targets['ball']['dis']==999:            
            self.robot.toRet(targets,self.side)          
          if targets['ball']['ang']==999:               
            self.robot.toNoBallWait(targets,self.side)    

        if self.robot.is_ret:            
          if targets[self.side]['dis']<70:
            #go block
            self.robot.toBlock(targets,self.side,imu)          
          else:
            #keep ret
            self.robot.toRet(targets,self.side)  

        if self.robot.is_noballret:     
          if targets['ball']['ang']==999:
            if targets[self.side]['dis']>=70:
              self.robot.toNoBallRet(targets,self.side)
            else:
              self.robot.toNoBallWait(targets,self.side)
          else:
            if targets[self.side]['dis']<70:
              
              self.robot.toBlock(targets,self.side,imu)
            else:
              if targets['ball']['dis']>80:
                self.robot.toRet(targets,self.side)
              else:                
                self.robot.toPush(targets)
    
        if self.robot.is_noballwait:   
          if targets['ball']['ang']==999:           
            self.robot.toNoBallWait(targets,self.side)
          else:            
            self.robot.toBlock(targets,self.side,imu)
      
        if self.robot.is_guard_penalty:  
          if targets['ball']['dis']<=150:
            if targets[self.side]['dis']<120:            
              self.robot.toGuard_Penalty(targets)
            else:  
              self.robot.toRet(targets,self.side)
          elif targets['ball']['dis']>150 and not targets['ball']['dis']==999:         
            self.robot.toRet(targets,self.side)
          if targets['ball']['ang']==999:            
            self.robot.toNoBallWait(targets,self.side)

        self.rate.sleep()
        
if __name__ == '__main__':
  try:
    if SysCheck(sys.argv[1:]) == "Native Mode":
      log("Start Native")
      s = Strategy(1, False)
    elif SysCheck(sys.argv[1:]) == "Simulative Mode":
      log("Start Sim")
      s = Strategy(1, True)
    # s.main(sys.argv[1:])
    s.main()
  except rospy.ROSInterruptException:
    pass
