from robot import Robot

robot = Robot() 

while robot.step() != -1:
    robot.record()
    if not robot.smh_Left():
        robot.rotateLeft90()
        robot.moveForwardTile()
    elif not robot.smh_Ahead():
        robot.moveForwardTile()
    elif not robot.smh_Right():
        robot.rotateRight90()
        robot.moveForwardTile()
    else:
        robot.turnAround()
        robot.moveForwardTile()