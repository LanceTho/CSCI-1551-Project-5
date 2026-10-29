from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, TransparencyAttrib
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Missile
from direct.gui.OnscreenImage import OnscreenImage

class SpaceShip(SphereCollideObject):
    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(SpaceShip, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1)
        self.taskMgr = taskMgr
        self.accept = accept
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.SetKeyBindings()

        self.reloadTime = 0.25
        self.missileDistance = 4000 # Until the missile explodes
        self.missileBay = 1 # Only 1 missile bay to be launched
        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)

        self.EnableHUD()

    def CheckIntervals(self, task):
        for i in Missile.Interavals:
            # isPlaying returns true or false to see if the missile has gotten to the end of its path
            if not Missile.Interavals[i].isPlaying():
                # If its path is done, we get rid of everything to do with that missile
                Missile.cNodes[i].removeNode()
                Missile.fireModels[i].removeNode()
                del Missile.Interavals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + " has reached the ned of its fire solution.")
                # We break because when things are deleted from a dictionary, we have to refactor the dictionary so we can reuse it. This is because when we delete things, there's a gap at that point
                break
        return Task.cont

    def EnableHUD(self):
        self.Hud = OnscreenImage(image = "./Assets/Hud/ReticleIV.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

    def Thrust(self, keyDown):
        if keyDown:
            taskMgr.add(self.ApplyThrust, 'forward-thrust')
        else:
            taskMgr.remove('forward-thrust')

    def ApplyThrust(self, task):
        rate = 5
        trajectory = render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        return Task.cont

    def SetKeyBindings(self):
        # Key bindings for the spaceship's movement
        self.accept('space', self.Thrust, [1])
        self.accept('space-up', self.Thrust, [0])
        # Turns left
        self.accept('a', self.LeftTurn, [1])
        self.accept('a-up', self.LeftTurn, [0])
        # Turns right
        self.accept('d', self.RightTurn, [1])
        self.accept('d-up', self.RightTurn, [0])
        # Turns up
        self.accept('w', self.LookUp, [1])
        self.accept('w-up', self.LookUp, [0])
        # Turns down
        self.accept('s', self.LookDown, [1])
        self.accept('s-up', self.LookDown, [0])
        # Rolls left
        self.accept('q', self.RollLeft, [1])
        self.accept('q-up', self.RollLeft, [0])
        # Rolls right
        self.accept('e', self.RollRight, [1])
        self.accept('e-up', self.RollRight, [0])
        # Fires missile
        self.accept('f', self.Fire)

    def LeftTurn(self, keyDown):
        if keyDown:
            taskMgr.add(self.ApplyLeftTurn, 'left-turn')
        else:
            taskMgr.remove('left-turn')

    def ApplyLeftTurn(self, task):
        # Half a degree every frame
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont

    def RightTurn(self, keyDown):
        if keyDown:
            taskMgr.add(self.ApplyRightTurn, 'right-turn')
        else:
            taskMgr.remove('right-turn')

    def ApplyRightTurn(self, task):
        # Half a degree every frame
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() - rate)
        return Task.cont
    
    def LookUp(self, keyDown):
        if keyDown:
            taskMgr.add(self.ApplyLookUp, 'look-up')
        else:
            taskMgr.remove('look-up')

    def ApplyLookUp(self, task):
        # Half a degree every frame
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont
    
    def LookDown(self, keyDown):
        if keyDown:
            taskMgr.add(self.ApplyLookDown, 'look-down')
        else:
            taskMgr.remove('look-down')

    def ApplyLookDown(self, task):
        # Half a degree every frame
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() - rate)
        return Task.cont
    
    def RollLeft(self, keyDown):
        if keyDown:
            taskMgr.add(self.ApplyRollLeft, 'roll-left')
        else:
            taskMgr.remove('roll-left')

    def ApplyRollLeft(self, task):
        # Half a degree every frame
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() - rate)
        return Task.cont
    
    def RollRight(self, keyDown):
        if keyDown:
            taskMgr.add(self.ApplyRollRight, 'roll-right')
        else:
            taskMgr.remove('roll-right')

    def ApplyRollRight(self, task):
        # Half a degree every frame
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont

    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = render.getRelativeVector(self.modelNode, Vec3.forward()) # The direction the spaceship is facing
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile ' + str(Missile.missileCount)
            
            posVec = self.modelNode.getPos() + inFront # Spawn the missile in front of the nose of the ship
            currentMissile = Missile(loader, "./Assets/Phaser/phaser.egg", render, tag, posVec, 4.0)

            # "fluid = 1" makes collision be checked between the last interval and this interval to make sure that there's nothing in-between both checks that wasn't hit
            Missile.Interavals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Interavals[tag].start()
        else:
            # If we aren't reloading, we want to start reloading
            if not taskMgr.hasTaskNamed('reload'):
                print("Initializing reload...")
                # Call the reload method on no delay
                taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont

    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            print("Reload complete.")
            return Task.done
        elif task.time <= self.reloadTime:
            print("Reload proceeding...")
            return Task.cont
        if self.missileBay > 1:
            self.missileBay = 1