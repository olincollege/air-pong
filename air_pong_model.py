from vpython import vector
import numpy as np


class PongModel:
    """
    Class for storing the state of a ping pong game.

    Attributes:
        _ball_position - A vector representing the x,y,z position of the ball.
        _ball_velocity - A vector representing the velocity of the ball.
        _ball_spin = A vector representing the ball's spin axis,
                with magnitude equal to the ball's spin rate.
    """

    # All variables use base SI units.
    (_table_length, _table_width, _table_height) = (2.74, 1.525, 0.76)
    (_paddle_width, paddle_depth) = (0.15, 0.17)
    _table_front = 1
    _ball_mass = 0.0027
    _ball_radius = 0.02
    _time_step = 0.001
    _acc_gravity = vector(0, 9.8, 0)
    # Constants to be adjusted
    _ball_rebound = 1
    _paddle_friction = 1
    _table_friction = 0.75
    _paddle_spring = 100
    _air_density = 1.19
    _drag_coefficient = 0.47
    _lift_coefficient = 0.25

    def __init__(self):
        """
        Define default ball state in time and space.
        """
        self.time_coefficient = 1
        self._ball_position = vector(1.5, 0.65, 0)
        self._ball_velocity = vector(-2, 0, 0)
        self._ball_spin = vector(0, 0, 0)
        self._angle = 0
        self._mag_force = vector(0, 0, 0)
        self._drag_force = vector(0, 0, 0)
        self._paddle_edges = [vector(1, 0.55, 0), vector(1, 0.7, 0)]
        self._player_coefficient = 1
        self._paddle_normal = vector(1, 0, 0)
        self._paddle_force = 0.5

    def compute_magnus_force(self):
        """
        Returns a vector giving the magnus force on the ping pong ball.
        """
        return (
            0.5
            * PongModel._lift_coefficient
            * PongModel._ball_radius**2
            * np.pi
            * self._ball_velocity.mag2
            * vector.cross(
                self._ball_velocity,
                self._ball_spin / (2 * np.pi) * PongModel._time_step,
            )
        )

    def compute_drag(self):
        """
        Returns a vector giving the opposing drag force on the ping pong ball.
        """
        return (
            0.5
            * PongModel._air_density
            * vector(
                self._ball_velocity.x**2,
                self._ball_velocity.y**2,
                self._ball_velocity.z**2,
            )
            * PongModel._drag_coefficient
            * np.pi
            * PongModel._ball_radius**2
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
            self._ball_velocity = vector.rotate(
                self._ball_velocity,
                angle=-2 * self._angle,
                axis=vector(0, 0, 1),
            )
            _sp_angular_momentum = (
                vector.cross(-self._ball_spin, vector(0, -1, 0))
                * self._ball_radius**2
            )
            self._ball_velocity += (
                PongModel._table_friction * _sp_angular_momentum
            )
            self._ball_spin = (
                (1 - PongModel._table_friction)
                * vector.cross(_sp_angular_momentum, vector(0, 1, 0))
                / self._ball_radius**2
            )
        self._angle = vector.diff_angle(self._ball_velocity, vector(1, 0, 0))

    def trajectory(self):
        """
        Base method for determining where the ball will go next.
        """
        self.hit_table()
        self.paddle_bounce()
        self._mag_force = self.compute_magnus_force()
        # self._drag_force = self.compute_drag()
        self._drag_force = vector(0, 0, 0)
        self._ball_position += PongModel._time_step * self._ball_velocity
        self._ball_velocity += (
            PongModel._acc_gravity * PongModel._time_step
            + (self._mag_force + self._drag_force)
            * PongModel._time_step
            / PongModel._ball_mass
        )

    def update_paddle(self, paddle_normal, paddle_position, paddle_force):
        """
        Determines whether the ball is in contact with the paddle.

        Args:
            paddle_normal - A vector representing the unit normal vector to the paddle.
            paddle_position - A vector representing a coordinate giving the center of mass
            of the paddle.
            paddle_force - A vector representing the force applied to the paddle when swung
            at the ball.
        """
        self._paddle_normal = paddle_normal
        self._paddle_force = paddle_force
        self._paddle_edges = [
            paddle_position
            + vector.rotate(
                PongModel._paddle_width / 2 * paddle_normal,
                angle=90,
                axis=vector(0, 0, 1),
            ),
            paddle_position
            - vector.rotate(
                PongModel._paddle_width / 2 * paddle_normal,
                angle=90,
                axis=vector(0, 0, 1),
            ),
        ]
        _horizontal_factor = vector.rotate(
            vector.norm(vector(paddle_normal.x, 0, paddle_normal.z)),
            angle=np.pi / 2,
            axis=vector(0, 1, 0),
        )
        _vertical_factor = vector.rotate(
            _horizontal_factor, angle=np.pi / 2, axis=paddle_normal
        )
        _change_basis = np.array(
            [paddle_normal.x, _vertical_factor.x, _horizontal_factor.x],
            [paddle_normal.y, _vertical_factor.y, _horizontal_factor.y],
            [paddle_normal.z, _vertical_factor.z, _horizontal_factor.z],
        )

    def paddle_bounce(self):
        """
        Base method for updating the ball state after hitting a paddle,
        given a velocity and spin for the ball and a velocity and angle for the paddle.
        """
        if (
            self._player_coefficient
            * (self._ball_position.x - PongModel._ball_radius)
            <= self._player_coefficient * self._paddle_edges[0].x
            and self._paddle_edges[0].y
            <= self._ball_position.y
            <= self._paddle_edges[1].y
        ):
            _spring_disp = vector.proj(self._ball_position, self._paddle_normal)
            _initial_velocity = abs(
                vector.proj(self._ball_velocity, self._paddle_normal).mag
            )
            _cumm_time = 0
            print(_spring_disp)
            # Define a cumulative time step because spring equation is deterministic not iterative.
            while (
                _spring_disp.mag
                >= vector.proj(
                    self._player_coefficient * self._ball_position,
                    self._paddle_normal,
                ).mag
            ):
                _cumm_time += PongModel._time_step
                self._ball_position += self._paddle_normal * (
                    0.5
                    * self._paddle_force
                    / PongModel._ball_mass
                    * _cumm_time**2
                    - _initial_velocity
                    / np.sqrt(PongModel._paddle_spring / PongModel._ball_mass)
                    * np.sin(
                        _cumm_time
                        * np.sqrt(
                            PongModel._paddle_spring / PongModel._ball_mass
                        )
                    )
                )
                self._ball_velocity = -self._paddle_normal * (
                    -self._paddle_force / PongModel._ball_mass * _cumm_time
                    + _initial_velocity
                    * np.cos(
                        _cumm_time
                        * np.sqrt(
                            PongModel._paddle_spring / PongModel._ball_mass
                        )
                    )
                )
                print(f"The position is {self._ball_position}")
                print(f"The velocity is {self._ball_velocity}")
                print(f"The elapsed time is {_cumm_time}")

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

    def reset_ball(self):
        """
        Method for establishing ball starting conditions.
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

    @property
    def ball_spin(self):
        return self._ball_spin
