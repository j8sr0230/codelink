import numpy as np
import awkward as ak
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D  # noqa


kuka_kr_6_chain: Chain = Chain(name="kuka_kr_6", links=[
	OriginLink(),
	URDFLink(
		name="A1",
		origin_translation=np.array([0, 0, 0]),
		origin_orientation=np.array([0, 0, 0]),
		rotation=np.array([0, 0, 1]),
	),
	URDFLink(
		name="A2",
		origin_translation=np.array([260, 0, 675]),
		origin_orientation=np.array([0, 0, 0]),
		rotation=np.array([0, 1, 0]),
	),
	URDFLink(
		name="A3",
		origin_translation=np.array([0, 0, 680]),
		origin_orientation=np.array([0, 0, 0]),
		rotation=np.array([0, 1, 0]),
	),
	URDFLink(
		name="A4",
		origin_translation=np.array([670, 0, -35]),
		origin_orientation=np.array([0, 0, 0]),
		rotation=np.array([1, 0, 0]),
	),
	URDFLink(
		name="A5",
		origin_translation=np.array([0, 0, 0]),
		origin_orientation=np.array([0, 0, 0]),
		rotation=np.array([0, 1, 0]),
	),
	URDFLink(
		name="A6",
		origin_translation=np.array([115, 0, 0]),
		origin_orientation=np.array([0, 0, 0]),
		rotation=np.array([1, 0, 0]),
	)
], active_links_mask=[False, True, True, True, True, True, True])

a1: np.ndarray = np.radians(0)
a2: np.ndarray = np.radians(0)
a3: np.ndarray = np.radians(0)
a4: np.ndarray = np.radians(0)
a5: np.ndarray = np.radians(90)
a6: np.ndarray = np.radians(0)

# Forward kinematic
pos_ori: np.ndarray = kuka_kr_6_chain.forward_kinematics(joints=[0, a1, a2, a3, a4, a5, a6])
print("Position for", np.degrees([a1, a2, a3, a4, a5, a6]), "deg ->", np.round(pos_ori[:3, 3], 2), "mm")

# Inverse kinematic
axes: np.array = kuka_kr_6_chain.inverse_kinematics(
	target_position=pos_ori[:3, 3],
	# target_orientation=pos_ori[:3, :3],
	# orientation_mode="all"
	target_orientation=np.degrees([1, 0, 0]),
	orientation_mode="Z"
)
print("Axes for", np.round(np.round(pos_ori[:3, 3], 2), 2), " mm ->", np.round(np.degrees(axes[1:]), 2), "deg")

# Plotting forward and inverse result
ax = matplotlib.pyplot.figure().add_subplot(111, projection='3d')
kuka_kr_6_chain.plot([0, a1, a2, a3, a4, a5, a6], ax)
kuka_kr_6_chain.plot(axes, ax)
matplotlib.pyplot.show()

# Numpy array composing by slicing
a: np.ndarray = np.array([1, 2, 3, 4, 5, 6])
print(a)
print(a[[0, 3, 4, 0, 3, 4]])

# Transform Awkward Record to Awkward Array
ar: ak.Array = ak.Array([[(1, 1), (2, 2), (3, 3)]])
grafted_ar: ak.Array = ak.unflatten(ar, counts=1, axis=-1)
ak.concatenate(ak.unzip(grafted_ar), axis=-1).show()
