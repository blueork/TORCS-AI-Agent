import msgParser

# from multipledispatch import dispatch

class CarControl(object):
    '''
    An object holding all the control parameters of the car
    '''
    # TODO range check on set parameters

    def __init__(self, accel = 0.0, brake = 0.0, gear = 1, steer = 0.0, clutch = 0.0, focus = 0, meta = 0):
        '''Constructor'''
        self.parser = msgParser.MsgParser()
        
        self.actions = None
        
        self.accel = accel
        self.brake = brake
        self.gear = gear
        self.steer = steer
        self.clutch = clutch
        self.focus = focus
        self.meta = meta
    
    def setFromMsg(self, str_actions):
        self.actions = self.parser.parse(str_actions)
        
        self.setAccel()
        self.setBrake()
        self.setClutch()
        self.setGear()
        self.setSteer()
        self.setFocus()
        self.setMeta()

    def toMsg(self):
        self.actions = {}
        
        self.actions['accel'] = [self.accel]
        self.actions['brake'] = [self.brake]
        self.actions['gear'] = [self.gear]
        self.actions['steer'] = [self.steer]
        self.actions['clutch'] = [self.clutch]
        self.actions['focus'] = [self.focus]
        self.actions['meta'] = [self.meta]
        
        return self.parser.stringify(self.actions)
    
    def getFloatD(self, name):
        try:
            val = self.actions[name]
        except KeyError:
            val = None
        
        if val != None:
            val = float(val[0])
        
        return val
    
    def getFloatListD(self, name):
        try:
            val = self.actions[name]
        except KeyError:
            val = None
        
        if val != None:
            l = []
            for v in val:
                l.append(float(v))
            val = l
        
        return val
    
    def getIntD(self, name):
        try:
            val = self.actions[name]
        except KeyError:
            val = None
        
        if val != None:
            val = int(val[0])
        
        return val

    def setAccel(self, accel=None):
        if accel is None:
            self.accel = self.getFloatD('accel')    
        else:
            self.accel = accel
    
    # def setAccel(self):
    #     self.accel = self.getFloatD('accel')

    def getAccel(self):
        return self.accel
    
    def setBrake(self, brake=None):
        if brake is None:
            self.brake = self.getFloatD('brake')
        else:
            self.brake = brake
    
    # def setBrake(self):
    #     self.brake = self.getFloatD('brake')

    def getBrake(self):
        return self.brake
    
    def setGear(self, gear=None):
        if gear is None:
            self.gear = self.getFloatD('gear')
        else:
            self.gear = gear

    # def setGear(self):
    #     self.gear = self.getFloatD('gear')
    
    def getGear(self):
        return self.gear
    
    def setSteer(self, steer=None):
        if steer is None:
            self.steer = self.getFloatD('steer')
        else:
            self.steer = steer
    
    # def setSteer(self):
    #     self.steer = self.getFloatD('steer')

    def getSteer(self):
        return self.steer
    
    def setClutch(self, clutch=None):
        if clutch is None:
            self.clutch = self.getFloatD('clutch')
        else:
            self.clutch = clutch
    
    # def setClutch(self):
    #     self.clutch = self.getFloatD('clutch')

    def getClutch(self):
        return self.clutch
    
    def setMeta(self, meta=None):
        if meta is None:
            self.meta = self.getFloatD('meta')
        else:
            self.meta = meta
    
    # def setMeta(self):
    #     self.meta = self.getFloatD('meta')

    def getMeta(self):
        return self.meta
        
    def setFocus(self, focus=None):
        if focus is None:
            self.focus = self.getFloatD('focus')
        else:
            self.focus = focus

    # def setFocus(self):
    #     self.focus = self.getFloatD('focus')

    def getFocus(self):
        return self.focus
        