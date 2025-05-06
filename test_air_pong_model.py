"""
Test model class storing the state of the ping pong game.
"""

import numpy as np
from vpython import vector
import air_pong_model

particle = air_pong_model.PongModel(2, 11)


def test_update_paddle():
    """
    Test that the update_paddle method returns the right edges.
    """
    # Test resulting edges array for a vertical paddle.
    particle.update_paddle(vector(1, 0, 0), vector(0, 0, 0), vector(0, 0, 0), 0)
    assert particle.paddle_edges[0] == [
        [0.0, particle.paddle_dim.x / 2, 0.0],
        [0.0, -particle.paddle_dim.x / 2, 0.0],
    ]
    # Test resulting edges array for a horizontal paddle.
    particle.update_paddle(vector(0, 1, 0), vector(0, 0, 0), vector(0, 0, 0), 0)
    assert particle.paddle_edges[0] == [
        [-particle.paddle_dim.x / 2, 0.0, 0.0],
        [particle.paddle_dim.x / 2, 0.0, 0.0],
    ]
    # Test resulting edges array for a backwards facing and diagonal paddle.
    particle.update_paddle(
        vector(-1, 1, 0).hat,
        vector(0, 0, 0),
        vector(0, 0, 0),
        0,
    )
    assert particle.paddle_edges[0] == [
        [
            -round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            -round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            0,
        ],
        [
            round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            0,
        ],
    ]
    # Test resulting edges array for a downwards facing and diagonal paddle.
    particle.update_paddle(
        vector(1, -1, 0).hat, vector(0, 0, 0), vector(0, 0, 0), 0
    )
    assert particle.paddle_edges[0] == [
        [
            round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            0,
        ],
        [
            -round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            -round(np.sqrt(2) * particle.paddle_dim.x / 4, 5),
            0,
        ],
    ]


def test_check_point():
    """
    Test whether points are properly awarded.
    """
    # Test a serve that misses the other side of the table.
    particle.serve()
    particle.update_paddle(
        vector(1, 1, 0).hat,
        vector(particle.table_front, particle.table_dim.z, 0),
        vector(0, 1, 0),
        0,
    )
    while particle.ball_position.y != 0:
        particle.trajectory()
        particle.check_point()
    assert particle.player_score == (1, 0)

    # Test a serve that misses the server side of the table.
    particle.serve()
    particle.update_paddle(
        vector(1, 0, 0).hat,
        vector(particle.table_front, particle.table_dim.z, 0),
        vector(0, 0, 0),
        0,
    )
    while particle.ball_position.y != 0:
        particle.trajectory()
        particle.check_point()
    assert particle.player_score == (1, 1)

    # Test a serve that results in a double bounce.
    particle.serve()
    particle.update_paddle(
        vector(0.1, 1, 0).hat,
        vector(particle.table_front, particle.table_dim.z, 0),
        vector(0, 0, 0),
        0,
    )
    while particle.ball_position.y != 0:
        particle.trajectory()
        particle.check_point()
    assert particle.player_score == (1, 2)
