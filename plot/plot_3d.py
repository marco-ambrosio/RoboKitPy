import matplotlib.pyplot as plt
from core.ellipsoid import *


def plot_ellipsoid(ax, ellipsoid, center, scale=0.2, color='b'):
    """
    Plot a velocity ellipsoid for a given Jacobian at the specified center point.

    :param ax: Matplotlib 3D axis object.
    :param ellipsoid: 3x3 matrix that describes the ellipsoid
    :param center: 3D position to plot the ellipsoid (usually the end-effector position).
    :param scale: Scale factor for the ellipsoid size.
    :param color: Color for the robot
    """
    # Ellipsoid parameters
    axes, vectors = ellipsoid
    x_ax, y_ax, z_ax = axes

    # Prepare data for the ellipsoid
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = scale * x_ax * np.outer(np.cos(u), np.sin(v))
    y = scale * y_ax * np.outer(np.sin(u), np.sin(v))
    z = scale * z_ax * np.outer(np.ones_like(u), np.cos(v))

    # Rotate and translate the data
    for i in range(len(x)):
        for j in range(len(x[0])):
            [x[i, j], y[i, j], z[i, j]] = np.dot([x[i, j], y[i, j], z[i, j]], vectors) + center

    # Plot the surface
    ax.plot_surface(x, y, z, rstride=4, cstride=4, color=color, alpha=0.5)


def compute_robot(model, thetalist):
    """
    :param model: instance of the Robot class
    :param thetalist: joint configuration
    :return: name, joints_num, joints_type, J, joints
    """

    # Model attributes
    name = model.name
    joints_num = model.joints_num
    joints_type = model.joints_type

    # Fk and joint positions
    dh_table = model.DH(thetalist)
    fk = fk_dh(dh_table)
    joints = joints_position_from_fk(dh_table)

    # Jacobian
    b_list = model.B()
    J = jacobian_body(b_list, thetalist)

    return name, joints_num, joints_type, J, joints


def plot_robot(model, thetalist, velocity_ellipsoid=False, force_ellipsoid=False, linear=False, scale=0.1):
    """
    Plot the robot using the computed joint coordinates.
    """
    name, joints_num, joints_type, J, joints = compute_robot(model, thetalist)

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot a base plane -----------------------------------------------
    x_length = 0.5
    y_length = 0.5
    x = np.linspace(-x_length / 2, x_length / 2, 100)
    y = np.linspace(-y_length / 2, y_length / 2, 100)
    x, y = np.meshgrid(x, y)
    z = np.zeros_like(x)
    ax.plot_surface(x, y, z, alpha=0.5, color='g')

    # Plot the robot ---------------------------------------------------
    for start, end in zip(joints[:-1], joints[1:]):
        xs, ys, zs = zip(start, end)
        ax.plot(xs, ys, zs, 'b-o')

    # Plot the end-effector marker -------------------------------------
    start_pos = joints[-2]
    end_effector_pos = joints[-1]
    direction = np.array(end_effector_pos) - np.array(start_pos)
    norm = np.linalg.norm(direction)
    direction = direction / norm if norm != 0 else direction
    ax.quiver(end_effector_pos[0], end_effector_pos[1], end_effector_pos[2], direction[0], direction[1], direction[2],
              length=0.1, color='r', normalize=True, arrow_length_ratio=0.5, label='End Effector')

    # Plot velocity and force ellipsoids -------------------------------
    Aw, Av, Bw, Bv = ellipsoids_3d(J)
    if velocity_ellipsoid:
        A = Av if linear else Aw
        plot_ellipsoid(ax, A, end_effector_pos, scale, color='r')
    if force_ellipsoid:
        B = Bv if linear else Bw
        plot_ellipsoid(ax, B, end_effector_pos, scale, color='y')

    # Show the plot ----------------------------------------------------
    ax.view_init(elev=20, azim=45)  # elev=20° above, azim=45° around the z-axis
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-1, 2])
    ax.set_title(f'3D Visualization of the {name}, {joints_type} robot with {joints_num} dof')
    plt.show()

