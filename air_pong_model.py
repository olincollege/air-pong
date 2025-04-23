from vpython import vector
import math


class PongModel:
    """
    Class for storing the state of a ping pong game.

    Attributes:
        _ball_position - A vector representing the x,y,z position of the ball.
        ball_velocity - A vector representing the velocity of the ball.
        _ball_spin = A vector representing the ball's spin axis,
                with magnitude equal to the ball's spin rate.
    """

    # All variables use base SI units.
    (_table_length, _table_width, _table_height) = (2.74, 1.525, 0.76)
    _table_front = 1
    _ball_mass = 0.0027
    _ball_radius = 0.02
    _time_step = 0.0015
    _acc_gravity = vector(0, 9.8, 0)
    # Constants to be adjusted
    _ball_rebound = 1
    _paddle_friction = 1
    _paddle_spring = 1
    _air_density = 1.225
    _drag_coefficient = 0.7
    _lift_coefficient = 2.5

    def __init__(self):
        """
        Define default ball state in time and space.
        """
        self.time_coefficient = 1
        self._ball_position = vector(1, 0.4, 0)
        self.ball_velocity = vector(1.5, 0, 0)
        self._ball_spin = vector(0, 0, 5)
        self._angle = 0
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
            * self.ball_velocity.mag2
            * vector.cross(
                self.ball_velocity,
                self._ball_spin / (2 * math.pi) * PongModel._time_step,
            )
        )

    def hit_table(self):
        """
        Updates the velocity vector of the ball when it collides with the table.
        """
        if (
            self._ball_position.x
            >= PongModel._table_front - PongModel._ball_radius
            and self._ball_position.x
            <= PongModel._table_front
            + PongModel._table_length
            - PongModel._ball_radius
            and self._ball_position.y
            >= PongModel._table_height - PongModel._ball_radius
        ):
            self.ball_velocity = vector.rotate(
                self.ball_velocity,
                angle=-2 * self._angle,
                axis=vector(0, 0, 1),
            )
            # self._ball_position.y = 2 * PongModel._ball_radius - self._ball_position.y

        # elif (
        #     self._ball_position.y
        #     > PongModel._table_height - PongModel._ball_radius
        # ):
        #     self._ball_position.y = (
        #         2 * (PongModel._table_height - PongModel._ball_radius)
        #         - self._ball_position.y
        #     )
        #     self.ball_velocity = vector.rotate(
        #         self.ball_velocity,
        #         angle=-2 * self._angle,
        #         axis=vector(0, 0, 1),
        #     )
        self._angle = vector.diff_angle(self.ball_velocity, vector(1, 0, 0))

    def trajectory(self):
        """
        Base method for determining where the ball will go next.
        """
        self._mag_force = self.compute_magnus_force()
        self._ball_position += PongModel._time_step * self.ball_velocity
        self.ball_velocity += (
            PongModel._acc_gravity * PongModel._time_step
            + self._mag_force / PongModel._ball_mass
        )
        self._angle = vector.diff_angle(self.ball_velocity, vector(1, 0, 0))
        self.hit_table()

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

    @property
    def ball_position(self):
        return self._ball_position

    @property
    def ball_radius(self):
        return PongModel._ball_radius

    @property
    def table_dim(self):
        return vector(
            PongModel._table_length,
            PongModel._table_width,
            PongModel._table_height,
        )

    @property
    def table_front(self):
        return PongModel._table_front
