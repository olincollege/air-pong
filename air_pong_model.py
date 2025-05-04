from vpython import vector
import numpy as np


class PongModel:
    """
    Class for storing the state of a ping pong game.

    Attributes:
        ball_position - A vector representing the x,y,z position of the ball.
        ball_velocity - A vector representing the velocity of the ball.
        ball_spin = A vector representing the ball's spin axis,
                with magnitude equal to the ball's spin rate.
        table_length - Float equal to the length of ping pong table (meters).
        table_width - Float equal to the width of ping pong table (meters).
        table_height - Float equal to the height of ping pong table (meters).
        paddle_width - Float equal to the width of ping pong paddle (meters).
        paddle_length -  Float equal to the length of ping pong paddle (meters).
        net_height - Float equal to the height of the net (meters).
        table_front - Float giving the position of the front of the ping
            pong table (meters).
        ball_mass - Float equal to the mass of the ball (kg).
        ball_radius - Float equal to the radius of the ball (m).
        time_step - Float establishing the amount of time between frames (sec).
        acc_gravity - Float giving the acceleration due to gravity (ms^-2)
        ball_rebound - Float corresponding to the percentage of kinetic energy
            conserved in a table bounce.
        paddle_friction - Float representing the paddle coefficient of friction.
        table_friction - Float representing the percentage of angular momentum
            transferred in the bounce.
        paddle_stiff - Float representing the stiffness of the paddle rubber
            (N/m).
        air_density - Float representing the density of air (kgm^-3).
        drag_coefficient - Float representing the coefficient of drag for a
            sphere.
        lift_coefficient - Float representing the coefficient of lift of a
            ping pong ball.
        paddle_force - The force applied by a player wielding their paddle (N).
    """

    # All variables use base SI units.
    _table_length, _table_width, _table_height = 2.74, 1.525, 0.76
    _paddle_width, paddle_length = 0.15, 0.17
    _net_height = 0.1525
    _table_front = 1
    _ball_mass = 0.0027
    _ball_radius = 0.02
    _time_step = 0.001
    _acc_gravity = vector(0, -9.8, 0)
    # Constants to be adjusted
    _ball_rebound = 0.97
    _paddle_friction = 0.95
    _table_friction = 0.75
    _paddle_stiff = 100
    _air_density = 1.19
    _drag_coefficient = 0.47
    _lift_coefficient = 2.5
    _paddle_force = 0.5
    _bounce_count = 0
    player1_serving = True
    _current_bounce = 0

    def __init__(self, win_threshold, serve_increment):
        """
        Define default ball state in time and space.

        Args:
            win_threshold - An integer designating how many points to play to.
            serve_increment - An integer dictating the number of points before the
                serve switches players.
        """
        self._ball_position = vector(
            PongModel._table_front, PongModel._table_height + 0.3, 0
        )
        self._ball_velocity = vector(0, 0, 0)
        self._ball_spin = vector(0, 0, 0)
        self._angle = 0
        self._mag_force = vector(0, 0, 0)
        self._drag_force = vector(0, 0, 0)
        self._paddle_edges = [
            (vector(1, 0.4, 0)),
        ]
        self._paddle_normal = vector(1, 0, 0)
        self._paddle_velocity = vector(0, 0, 0)
        self._paddle_position = vector(0, 0, 0)
        self._player_score = (0, 0)
        self._win_threshold = win_threshold
        self._serve_increment = serve_increment

    def compute_magnus_force(self):
        """
        Returns a vector giving the magnus force (N) on the ping pong ball.
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
        Returns a vector giving the opposing drag force (N) on the ping pong ball.
        """
        return (
            0.5
            * PongModel._air_density
            * vector(
                -self._ball_velocity.hat.x * self._ball_velocity.x**2,
                -self._ball_velocity.hat.y * self._ball_velocity.y**2,
                -self._ball_velocity.hat.z * self._ball_velocity.z**2,
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
            + PongModel._ball_radius
            and self._ball_position.y
            < PongModel._table_height + PongModel._ball_radius
        ):
            self._ball_position += vector(0, 0.0001, 0)
            self._ball_velocity = PongModel._ball_rebound * vector.rotate(
                self._ball_velocity,
                angle=2 * self._angle,
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
            if self.player_coefficient() == 1:
                PongModel._bounce_count += 1
            else:
                PongModel._bounce_count -= 1
        self._angle = vector.diff_angle(self._ball_velocity, vector(1, 0, 0))

    def hit_net(self):
        """
        Updates the velocity vector and spin of the ball when it collides with the net.
        """
        if round(
            self._ball_position.x
            + self.player_coefficient() * self._ball_radius,
            2,
        ) == PongModel._table_front + round(PongModel._table_length / 2, 2):
            if (
                self._ball_position.y
                < PongModel._net_height + PongModel._table_height
            ):
                self._ball_velocity = vector(
                    -0.1 * self.player_coefficient(), 0, 0
                )
                print("net bounce")
            elif (
                self.ball_position.y - self._ball_radius
                <= PongModel._net_height + PongModel._table_height
                and PongModel._current_bounce != PongModel._bounce_count
            ):
                print("let")
                PongModel._current_bounce = PongModel._bounce_count
                self._ball_velocity = vector.rotate(
                    2
                    * np.arcsin(
                        (
                            self._ball_position.y
                            - PongModel._net_height
                            - PongModel._table_height
                        )
                        / PongModel._ball_radius
                    )
                    / np.pi
                    * self._ball_velocity,
                    axis=vector(0, 0, 1) + self._ball_spin,
                    angle=np.arccos(
                        (
                            self._ball_position.y
                            - PongModel._net_height
                            - PongModel._table_height
                        )
                        / PongModel._ball_radius
                    ),
                )

    def trajectory(self):
        """
        Base method for determining where the ball will go next after a time_step.
        """
        self.hit_table()
        self.paddle_bounce()
        self.hit_net()
        self._mag_force = self.compute_magnus_force()
        self._drag_force = self.compute_drag()
        self._ball_position += PongModel._time_step * self._ball_velocity
        self._ball_velocity += (
            PongModel._acc_gravity
            + (self._mag_force + self._drag_force) / PongModel._ball_mass
        ) * PongModel._time_step
        print(self._ball_spin)

    def update_paddle(
        self,
        paddle_normal,
        paddle_position,
        paddle_velocity,
    ):
        """
        Updates instance attributes encoding the paddle's state.

        Args:
            paddle_normal - A vector representing the unit normal vector to the paddle.
            paddle_position - A vector representing a coordinate giving the center of mass
            of the paddle.
            paddle_velocity - A vector representing the velocity of the paddle when swung
            at the ball.
        """
        self._paddle_normal = paddle_normal
        self._paddle_velocity = paddle_velocity
        self._paddle_position = paddle_position
        self._paddle_edges = [
            paddle_position
            + vector.rotate(
                PongModel._paddle_width / 2 * paddle_normal,
                angle=np.pi / 2,
                axis=vector(0, 0, 1),
            ),
            paddle_position
            - vector.rotate(
                PongModel._paddle_width / 2 * paddle_normal,
                angle=np.pi / 2,
                axis=vector(0, 0, 1),
            ),
        ]
        self._paddle_edges = [
            [
                self._paddle_edges[0].x,
                self._paddle_edges[0].y,
                self._paddle_edges[0].z,
            ],
            [
                self._paddle_edges[1].x,
                self._paddle_edges[1].y,
                self._paddle_edges[1].z,
            ],
        ]

    def hit_or_miss(self):
        """
        Method to determine whether the ball hits or misses the paddle at any given
        moment.

        Returns:
            A boolean, True if the ball hits the paddle and False otherwise.
        """
        _horizontal_factor = vector.rotate(
            vector.norm(
                vector(
                    self._paddle_normal.x,
                    0,
                    self._paddle_normal.z,
                )
            ),
            angle=np.pi / 2,
            axis=vector(0, 1, 0),
        )
        _vertical_factor = vector.rotate(
            _horizontal_factor,
            angle=np.pi / 2,
            axis=(self._paddle_normal),
        )
        _change_basis = np.array(
            [
                [
                    self._paddle_normal.x,
                    _vertical_factor.x,
                    _horizontal_factor.x,
                ],
                [
                    self._paddle_normal.y,
                    _vertical_factor.y,
                    _horizontal_factor.y,
                ],
                [
                    self._paddle_normal.z,
                    _vertical_factor.z,
                    _horizontal_factor.z,
                ],
            ]
        )
        _paddle_edges_check = np.transpose(
            np.linalg.inv(_change_basis)
            @ np.transpose(np.array(self.paddle_edges))
        )
        _ball_position_check = np.transpose(
            np.linalg.inv(_change_basis)
            @ np.transpose(
                np.array(
                    [
                        self.ball_position.x,
                        self.ball_position.y,
                        self.ball_position.z,
                    ]
                )
            )
        )
        # print(_paddle_edges_check)
        # print(_ball_position_check)
        return (
            round(_ball_position_check[1], 4)
            <= round(_paddle_edges_check[0][1], 4)
            and round(_ball_position_check[1], 4)
            >= round(_paddle_edges_check[1][1], 4)
            and round(_paddle_edges_check[0][0], 3)
            >= _ball_position_check[0]
            - self.player_coefficient() * PongModel._ball_radius
        )

    def paddle_bounce(self):
        """
        Base method for updating the ball state after hitting a paddle,
        given a velocity and spin for the ball and a velocity and angle for the paddle.
        """
        _hit_paddle = bool(self.hit_or_miss())
        if _hit_paddle is True:
            _spring_disp = vector.proj(self._ball_position, self._paddle_normal)
            _initial_velocity = abs(
                vector.proj(self._ball_velocity, self._paddle_normal).mag
            ) + abs(vector.proj(self._paddle_velocity, self._paddle_normal).mag)
            _cumm_time = 0
            # Define a cumulative time step because spring equation is deterministic not iterative.
            _parallel_velocity = self._ball_radius * vector.cross(
                self._ball_spin, self._paddle_normal
            ) + vector.proj(
                self._paddle_velocity,
                vector.rotate(
                    self._paddle_normal, axis=vector(0, 0, 1), angle=np.pi / 2
                ),
            )
            print(f"the parallel velocity is {_parallel_velocity}")
            while (
                _spring_disp.mag
                >= vector.proj(
                    self.player_coefficient() * self._ball_position,
                    self._paddle_normal,
                ).mag
            ):
                _cumm_time += PongModel._time_step / 10
                _spring_acc = (
                    _initial_velocity
                    / (
                        (PongModel._paddle_stiff / PongModel._ball_mass)
                        ** (3 / 2)
                    )
                    * np.sin(
                        _cumm_time
                        * np.sqrt(
                            PongModel._paddle_stiff / PongModel._ball_mass
                        )
                    )
                )
                self._ball_position += self._paddle_normal * (
                    0.5
                    * PongModel._paddle_force
                    / PongModel._ball_mass
                    * _cumm_time**2
                    - _spring_acc
                    * (PongModel._paddle_stiff / PongModel._ball_mass)
                )
                self._ball_velocity = -self._paddle_normal * (
                    -PongModel._paddle_force / PongModel._ball_mass * _cumm_time
                    + _initial_velocity
                    * np.cos(
                        _cumm_time
                        * np.sqrt(
                            PongModel._paddle_stiff / PongModel._ball_mass
                        )
                    )
                )
                _parallel_velocity -= _parallel_velocity.hat * (
                    PongModel._paddle_friction
                    * (PongModel._paddle_force / self._ball_mass + _spring_acc)
                    * PongModel._time_step
                )

                self._ball_spin = vector(
                    0,
                    0,
                    (
                        _parallel_velocity.mag
                        - vector.proj(
                            self._paddle_velocity, self._paddle_normal
                        ).mag
                    )
                    / self._ball_radius,
                )
                # print(f"The position is {self._ball_position}")
                # print(f"The velocity is {self._ball_velocity}")
                # print(f"The elapsed time is {_cumm_time}")

    def check_point(self):
        """
        Method for updating the 'player_score' 'player_serving attributes.
        """
        if PongModel._bounce_count == 2:
            self._player_score = (
                self._player_score[0] + 1,
                self._player_score[1],
            )
            if self._player_score % self._serve_increment == 0:
                PongModel.player1_serving = not (PongModel.player1_serving)

        if PongModel._bounce_count == -1:
            self._player_score = (
                self._player_score[0],
                self._player_score[1] + 1,
            )
            if self._player_score % self._serve_increment == 0:
                PongModel.player1_serving = not (PongModel.player1_serving)

    def check_win(self):
        """
        Method for determining if a player has won.

        Returns:
            An integer corresponding to the winning player or boolean False otherwise.
        """
        if (
            self._player_score[0] >= self._win_threshold
            and self._player_score[0] - 1 > self._player_score[1]
        ):
            return 1
        if (
            self._player_score[1] >= self._win_threshold
            and self._player_score[1] - 1 > self._player_score[0]
        ):
            return 2
        return False

    def player_coefficient(self):
        """
        Returns integers -1 or 1 depending on which side of the table
        the ball is on: -1 for right and 1 for left.
        """
        if (
            self._ball_position.x
            < PongModel._table_front + PongModel._table_length / 2
        ):
            return 1
        return -1

    def serve(self):
        """
        Initiate a serve consisting of a predefined initial ball position
        and velocity.
        """
        _serving_position = PongModel._table_front - 0.05
        if self.player1_serving is False:
            _serving_position = (
                PongModel._table_front + PongModel._table_length + 0.05
            )
        self._ball_position = vector(
            _serving_position, PongModel._table_height, 0
        )
        self._ball_velocity = vector(0, 2, 0)

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

    @property
    def paddle_edges(self):
        return self._paddle_edges

    @property
    def player_score(self):
        return self._player_score

    @property
    def paddle_normal(self):
        return self._paddle_normal

    @property
    def paddle_position(self):
        return self._paddle_position

    @property
    def paddle_velocity(self):
        return self._paddle_velocity
