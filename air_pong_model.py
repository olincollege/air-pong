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
        angle - A float corresponding to the angle between the ball and table.
            (radians)
        paddle_normal_pair - A list of two lists, each encoding the unit normal
            vector of player 1 and player 2's paddles respectively.
        paddle_velocity_pair - A list of two lists, each encoding the velocity
            vector of player 1 and player 2's paddles respectively (m/s).
        paddle_position_pair - A list of two lists, each encoding the position
            of player 1 and player 2's paddles respectively (m).
        paddle_edges_pair - A list of two 2D arrays, each encoding the position
            of player 1 and player 2's paddle edges respectively (m). The top
            row of the array is the top point of the paddle and the bottom row
            is the bottom point.
        player1_serving - A boolean indicating whether it is player 1's serve.
            False indicates that it is player 2's serve.
        bounce_count - An integer keeping track of the number of bounces on
            each side.
        current_bounce - An integer equal to the bounce_count when the ball
            last hit the net.
        self._ball_home - A boolean that disables trajectory when True.
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
        paddle_force - A float equal to the force applied by a player wielding
            their paddle (N).
    """

    # All variables use base SI units.
    _table_length, _table_width, _table_height = 2.74, 1.525, 0.653796
    _paddle_width, _paddle_length = 0.15, 0.17
    _net_height = 0.1525
    _table_front = (5 - _table_length) / 2
    _ball_mass = 0.0027
    _ball_radius = 0.02
    _time_step = 0.01
    _acc_gravity = vector(0, -9.8, 0)
    _ball_rebound = 0.9
    _paddle_friction = 0.95
    _table_friction = 0.75
    _paddle_stiff = 100
    _air_density = 1.19
    _drag_coefficient = 0.47
    _lift_coefficient = 2.5
    _paddle_force = 0.5

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
        self._paddle_normal_pair = [vector(1, 0, 0).hat, vector(-1, 0, 0)]
        self._paddle_normal = self._paddle_normal_pair[0]
        self._paddle_velocity_pair = [vector(0, 0, 0), vector(0, 0, 0)]
        self._paddle_velocity = self._paddle_velocity_pair[0]
        self._paddle_position_pair = [
            vector(
                PongModel._table_front - 0.05,
                PongModel._table_height,
                0,
            ),
            # Start 5cm away from edge so as not to interfere with serve.
            vector(
                PongModel._table_front + PongModel._table_length + 0.05,
                PongModel._table_height,
                0,
            ),
        ]
        self._paddle_position = self._paddle_position_pair[0]
        self._paddle_edges_pair = [[[], []], [[], []]]
        self._player_score = (0, 0)
        self._win_threshold = win_threshold
        self._serve_increment = serve_increment
        self.update_paddle(
            self._paddle_normal, self._paddle_position, self._paddle_velocity, 0
        )
        self.update_paddle(
            self._paddle_normal_pair[1],
            self._paddle_position_pair[1],
            self._paddle_velocity_pair[1],
            1,
        )
        self._paddle_edges = self._paddle_edges_pair[0]
        self._bounce_count = 0
        self._current_bounce = 0
        self._player1_serving = True
        self._ball_home = True

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
        # Check if ball is above the table and touching the surface.
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
            # Adjust position slightly to prevent double bounce.
            self._ball_position += vector(0, 0.0001, 0)
            # Rotate velocity vector and scale (energy lost in bounce).
            self._ball_velocity = PongModel._ball_rebound * vector.rotate(
                self._ball_velocity,
                angle=2 * self._angle,
                axis=vector(0, 0, 1),
            )
            # Calculate angular momentum converted to linear momentum.
            _sp_angular_momentum = (
                vector.cross(-self._ball_spin, vector(0, -1, 0))
                * self._ball_radius**2
            )
            self._ball_velocity += (
                PongModel._table_friction * _sp_angular_momentum
            )
            # Update spin after bounce.
            self._ball_spin = (
                (1 - PongModel._table_friction)
                * vector.cross(_sp_angular_momentum, vector(0, 1, 0))
                / self._ball_radius**2
            )
            # Update bounce count depending on the active player to
            # detect a point won.
            if self.player_coefficient() == 1:
                self._bounce_count += 1
            else:
                self._bounce_count -= 1
        # Update angle to table after each time_step
        self._angle = vector.diff_angle(self._ball_velocity, vector(1, 0, 0))

    def hit_net(self):
        """
        Updates the velocity vector and spin of the ball when it collides with the net.
        """
        # Check if ball edge is above the center line of the table.
        if round(
            self._ball_position.x
            + self.player_coefficient() * self._ball_radius,
            2,
        ) == PongModel._table_front + round(PongModel._table_length / 2, 2):
            # Check if the center of the ball is below the top of the net.
            if (
                self._ball_position.y
                < PongModel._net_height + PongModel._table_height
            ):
                self._ball_velocity = vector(
                    -0.1 * self.player_coefficient(), 0, 0
                )
            # Check if only the bottom half of ball is below the top of net.
            elif (
                self.ball_position.y - self._ball_radius
                <= PongModel._net_height + PongModel._table_height
                and self._current_bounce != self._bounce_count
            ):
                # Redefine current_bounce so elif statement isn't repeatedly
                # called.
                self._current_bounce = self._bounce_count
                # Rotate and scale velocity depending on spin and contact point.
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
        Method updates ball_position and ball_velocity attributes.
        """
        # Check whether ball is in free motion.
        if self._ball_home is False:
            # Switch which paddle the ball will hit next.
            self.switch_paddle()
            # Check for collisions.
            self.hit_table()
            self.paddle_bounce()
            self.hit_net()
            # Compute forces.
            self._mag_force = self.compute_magnus_force()
            self._drag_force = self.compute_drag()
            # Update position based on current velocity.
            self._ball_position += PongModel._time_step * self._ball_velocity
            # Update velocity based on acting forces.
            self._ball_velocity += (
                PongModel._acc_gravity
                + (self._mag_force + self._drag_force) / PongModel._ball_mass
            ) * PongModel._time_step

    def update_paddle(
        self, paddle_normal, paddle_position, paddle_velocity, player_paddle
    ):
        """
        Updates instance attributes encoding the paddle's state.

        Args:
            paddle_normal - A vector representing the unit normal vector to the paddle.
            paddle_position - A vector representing a coordinate giving the center of mass
            of the paddle.
            paddle_velocity - A vector representing the velocity of the paddle when swung
            at the ball.
            player_paddle - An integer, 0 or 1, corresponding to the index of the list of
            paddles.
        """
        # Update paddle attributes from input for a given paddle.
        self._paddle_normal_pair[player_paddle] = paddle_normal
        self._paddle_velocity_pair[player_paddle] = paddle_velocity
        self._paddle_position_pair[player_paddle] = paddle_position
        # Compute the edges of the paddle based on input normal vector.
        self._paddle_edges_pair[player_paddle] = [
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
        # Convert updated paddle edges into a 2D array.
        self._paddle_edges_pair[player_paddle] = [
            [
                round(self._paddle_edges_pair[player_paddle][0].x, 5),
                round(self._paddle_edges_pair[player_paddle][0].y, 5),
                round(self._paddle_edges_pair[player_paddle][0].z, 5),
            ],
            [
                round(self._paddle_edges_pair[player_paddle][1].x, 5),
                round(self._paddle_edges_pair[player_paddle][1].y, 5),
                round(self._paddle_edges_pair[player_paddle][1].z, 5),
            ],
        ]

    def hit_or_miss(self):
        """
        Method to determine whether the ball hits or misses a paddle at any given
        moment.

        Returns:
            A boolean, True if the ball hits the paddle and False otherwise.
        """
        # Define vector parallel to paddle face (long direction).
        _horizontal_factor = vector.rotate(
            self.player_coefficient()
            * vector.norm(
                vector(
                    self._paddle_normal.x,
                    0,
                    self._paddle_normal.z,
                )
            ),
            angle=np.pi / 2,
            axis=vector(0, 1, 0),
        )
        # Define vector parallel to paddle face (short direction).
        _vertical_factor = vector.rotate(
            _horizontal_factor,
            angle=np.pi / 2,
            axis=(self._paddle_normal),
        )
        # Define a matrix to change basis in terms of the normal vector.
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
        # Define new paddle edges in new basis.
        _paddle_edges_check = np.transpose(
            np.linalg.inv(_change_basis)
            @ np.transpose(np.array(self._paddle_edges))
        )
        # Define new ball position in new basis.
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
        # Check whether ball is in contact with paddle.
        return (
            round(_ball_position_check[1], 4)
            <= round(_paddle_edges_check[0][1], 4)
            and round(_ball_position_check[1], 4)
            >= round(_paddle_edges_check[1][1], 4)
            and round(_paddle_edges_check[0][0], 3)
            >= _ball_position_check[0]
            - self.player_coefficient() * PongModel._ball_radius
            >= _paddle_edges_check[0][0] - self.paddle_dim.y
        )

    def paddle_bounce(self):
        """
        Base method for updating the ball state after hitting a paddle,
        given a velocity and spin for the ball and a velocity and angle for the paddle.
        """
        # Check if the ball is in contact with a paddle.
        _hit_paddle = bool(self.hit_or_miss())
        if _hit_paddle is True:
            # Define initial relative ball speed and position normal to the paddle face.
            _spring_disp = vector.proj(self._ball_position, self._paddle_normal)
            _initial_velocity = abs(
                vector.proj(self._ball_velocity, self._paddle_normal).mag
            ) + abs(vector.proj(self._paddle_velocity, self._paddle_normal).mag)
            # Define a cumulative time step because spring equation is deterministic not iterative.
            _cumm_time = 0
            # Compute velocity parallel to paddle.
            _parallel_velocity = self._ball_radius * vector.cross(
                self._ball_spin, self._paddle_normal
            ) + vector.proj(
                self._paddle_velocity,
                vector.rotate(
                    self._paddle_normal, axis=vector(0, 0, 1), angle=np.pi / 2
                ),
            )
            # Run loop until the ball leaves the paddle face.
            while (
                _spring_disp.mag
                >= vector.proj(
                    self.player_coefficient() * self._ball_position,
                    self._paddle_normal,
                ).mag
            ):
                _cumm_time += PongModel._time_step / 10
                # The force per unit mass due to the paddle-spring/ball system.
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
                # Compute displacement and update position for cum_time.
                self._ball_position += self._paddle_normal * (
                    0.5
                    * PongModel._paddle_force
                    / PongModel._ball_mass
                    * _cumm_time**2
                    - _spring_acc
                    * (PongModel._paddle_stiff / PongModel._ball_mass)
                )
                # Compute final velocity for cum_time.
                self._ball_velocity = (
                    -self.player_coefficient()
                    * self._paddle_normal
                    * (
                        -PongModel._paddle_force
                        / PongModel._ball_mass
                        * _cumm_time
                        + _initial_velocity
                        * np.cos(
                            _cumm_time
                            * np.sqrt(
                                PongModel._paddle_stiff / PongModel._ball_mass
                            )
                        )
                    )
                )
                # Compute relative velocity between paddle face and ball edge
                # (parallel component).
                _parallel_velocity -= _parallel_velocity.hat * (
                    PongModel._paddle_friction
                    * (PongModel._paddle_force / self._ball_mass + _spring_acc)
                    * PongModel._time_step
                )
                # Update spin based on friction force with paddle and relative velocity.
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

    def check_point(self):
        """
        Method for updating the 'player_score' and 'player1_serving' attributes.
        """
        # print(self._bounce_count)
        # Check if player 2 has won a point and update score if so.
        if self._bounce_count == 2 or (
            self.ball_position.y < 0
            and self.ball_position.x < self._table_front
        ):
            self._player_score = (
                self._player_score[0],
                self._player_score[1] + 1,
            )
            # Send ball to home and end trajectory.
            self._ball_position = vector(0, 0, 0)
            self._ball_home = True
            # Change player to serve based on given serve increment.
            if (
                self._player_score[0]
                + self._player_score[1] % self._serve_increment
                == 0
            ):
                self._player1_serving = not (self._player1_serving)
        # Check if player 1 has won a point and update score if so.
        if self._bounce_count == -1 or (
            self.ball_position.y < 0
            and self.ball_position.x > self.table_dim.x + self._table_front
        ):
            self._player_score = (
                self._player_score[0] + 1,
                self._player_score[1],
            )
            # Send ball to home and end trajectory.
            self._ball_position = vector(0, 0, 0)
            self._ball_home = True
            # Change player to serve based on given serve increment.
            if (
                self._player_score[0]
                + self._player_score[1] % self._serve_increment
                == 0
            ):
                self._player1_serving = not (self._player1_serving)

    def check_win(self):
        """
        Method for determining if a player has won.

        Returns:
            An integer corresponding to the winning player or boolean False otherwise.
        """
        # Check if player 1 is has more than the win threshold and is
        # winning by 2.
        if (
            self._player_score[0] >= self._win_threshold
            and self._player_score[0] - 1 > self._player_score[1]
        ):
            return 1
        # Check if player 1 is has more than the win threshold and is
        # winning by 2.
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
        # Set serving x position for player 1.
        _serving_position = PongModel._table_front - 0.1
        # Change serving position if player 2 is serving.
        if self._player1_serving is False:
            _serving_position = (
                PongModel._table_front + PongModel._table_length + 0.1
            )
        # Set ball position and vertical velocity to initial a serve.
        self._ball_position = vector(
            _serving_position, PongModel._table_height, 0
        )
        self._ball_velocity = vector(0, 3, 0)
        self._ball_home = False

    def switch_paddle(self):
        """
        Switch which paddle is active.
        Method updates single paddle state attributes
        based on which side of the table the ball is on.
        """
        _paddle_index = (1 - self.player_coefficient()) // 2
        self._paddle_normal = self._paddle_normal_pair[_paddle_index]
        self._paddle_velocity = self._paddle_velocity_pair[_paddle_index]
        self._paddle_position = self._paddle_position_pair[_paddle_index]
        self._paddle_edges = self._paddle_edges_pair[_paddle_index]

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
    def paddle_dim(self):
        return vector(PongModel._paddle_width, PongModel._paddle_length, 0.011)

    @property
    def table_front(self):
        return PongModel._table_front

    @property
    def net_height(self):
        return PongModel._net_height

    @property
    def ball_spin(self):
        return self._ball_spin

    @property
    def paddle_edges(self):
        return self._paddle_edges_pair

    @property
    def player_score(self):
        return self._player_score

    @property
    def paddle_normal(self):
        return self._paddle_normal_pair

    @property
    def paddle_position(self):
        return self._paddle_position_pair

    @property
    def paddle_velocity(self):
        return self._paddle_velocity_pair
