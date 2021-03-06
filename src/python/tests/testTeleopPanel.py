from director import robotsystem
from director.consoleapp import ConsoleApp
from director import transformUtils
from director import visualization as vis
from director import objectmodel as om
from director import teleoppanel
from director import playbackpanel
from director import planningutils

from PythonQt import QtCore, QtGui
import numpy as np



def checkGraspFrame(inputGraspFrame, side):
    '''
    Return True if the given grasp frame matches the grasp frame
    of the teleop robot model's current pose, else False.
    '''

    pose = teleopJointController.q
    teleopGraspFrame = ikPlanner.newGraspToWorldFrame(pose, side, ikPlanner.newGraspToHandFrame(side))

    p1, q1 = transformUtils.poseFromTransform(inputGraspFrame)
    p2, q2 = transformUtils.poseFromTransform(teleopGraspFrame)

    try:
        np.testing.assert_allclose(p1, p2, rtol=1e-3)
        np.testing.assert_allclose(q1, q2, rtol=1e-3)
        return True
    except AssertionError:
        return False


def onIkStartup(ikServer, startSuccess):

    side = 'left'
    goalFrame = transformUtils.frameFromPositionAndRPY([0.5, 0.5, 1.2], [0, 90, -90])

    assert not checkGraspFrame(goalFrame, side)
    frame = teleopPanel.endEffectorTeleop.newReachTeleop(goalFrame, side)
    assert checkGraspFrame(goalFrame, side)

    teleopPanel.ui.planButton.click()
    assert playbackPanel.plan is not None

    teleopPanel.ikPlanner.useCollision = True;
    teleopPanel.ui.planButton.click()
    assert playbackPanel.plan is not None

    frame.setProperty('Edit', True)
    app.startTestingModeQuitTimer()


app = ConsoleApp()
app.setupGlobals(globals())

view = app.createView()
robotsystem.create(view, globals())


ikServer.connectStartupCompleted(onIkStartup)
startIkServer()


w = QtGui.QWidget()
l = QtGui.QGridLayout(w)
l.addWidget(view, 0, 0)
l.addWidget(playbackPanel.widget, 1, 0)
l.addWidget(teleopPanel.widget, 0, 1, 2, 1)
l.setMargin(0)
l.setSpacing(0)
w.show()
w.resize(1600, 900)

app.start(enableAutomaticQuit=False)
