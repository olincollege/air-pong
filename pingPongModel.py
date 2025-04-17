
class PongModel:
    """
    Class for storing the state of the ping pong game.

    Attributes:
        _ball_position - A list representing the x,y,z position of the ball.
        _ball_velocity - A list representing the velocity vector of the ball.
        _ball_spin = A list representing a vector along the ball's spin axis, 
                with magnitude equal to the ball's spin rate.
    """

    # All variables use base SI units.
    _ball_mass = 0.027
    # Constants to be determined
    _ball_rebound = 1
    _paddle_friction = 1
    _paddle_spring = 1
    _air_density = 1




    def __init__(self):
        """ 
        Define ball state in time and space.
        """
        self.time_coefficient = 1
        self._ball_position = [0, 0, 0]
        self._ball_velocity = [0, 0, 0]
        self._ball_spin = [0, 0, 0]

    def trajectory(self):
        """
        Base method for determining where the ball will go next.
        """
        pass
    
    def hit_paddle(self, paddle_angle, paddle_velocity):
        """
        Base method for updating the ball state after hitting a paddle,
        given a velocity and spin for the ball and a velocity and angle for the paddle.

        Args:
            paddle_angle = A list representing the normal vector to the paddle.
            paddle_velocity = A list representing the velocity vector of the paddle.
        """
        pass

    def swing_paddle(self, paddle_angle, paddle_velocity):
        """
        Base method for moving the paddle given an input velocity and angle.

        Args:
            paddle_angle = A list representing the normal vector to the paddle.
            paddle_velocity = A list representing the velocity vector of the paddle.
        """
        pass

    def time_rate(self, motion_rate):
        """
        Method to update the time coefficient based on an input motion rate.

        Args:
            motion_rate - An integer representing the rate of change of 
            the paddle position.
        """
        pass