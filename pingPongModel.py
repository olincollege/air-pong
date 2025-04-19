from vpython import vector
import math


class PongModel:
    """
    Class for storing the state of a ping pong game.

    Attributes:
        _ball_position - A list representing the x,y,z position of the ball.
        _ball_velocity - A list representing the velocity vector of the ball.
        _ball_spin = A list representing a vector along the ball's spin axis,
                with magnitude equal to the ball's spin rate.
    """

    # All variables use base SI units.
    _ball_mass = 0.0027
    _ball_radius = 0.02
    _time_step = 0.01
    # Constants to be adjusted
    _ball_rebound = 1
    _paddle_friction = 1
    _paddle_spring = 1
    _air_density = 1.225
    _drag_coefficient = 0.7
    _lift_coefficient = 0.25

    def __init__(self):
        """
        Define default ball state in time and space.
        """
        self.time_coefficient = 1
        self._ball_position = vector(0, 0, 0)
        self._ball_velocity = vector(0, 0, 0)
        self._3d_spin = vector(0, 0, 0)
        self._2d_spin = 0
        self._mag_force = 0

    def compute_magnus_force(self):
        """
        Returns a vector giving the magnus force on the ping pong ball.
        """
        return (
            0.5
            * PongModel._lift_coefficient
            * PongModel._ball_radius**2
            * math.pi
            * self._ball_velocity.mag2
            * vector.cross(
                self._ball_velocity,
                self._3d_spin / (2 * math.pi) * PongModel._time_step,
            )
        )

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
            paddle_angle - A vector representing the normal vector to the paddle.
            paddle_velocity - A vector representing the velocity vector of the paddle.
        """
        pass

    def swing_paddle(self, paddle_angle, paddle_velocity, paddle_position):
        """
        Base method for moving the paddle given an input velocity and angle.

        Args:
            paddle_angle - A vector representing the normal vector to the paddle.
            paddle_velocity - A vector representing the velocity vector of the paddle.
            paddle_position - A vector representing a coordinate giving the center of mass
                of the paddle.
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
