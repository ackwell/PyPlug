
"""
**PyPlug** is a rudimentary implementation of the 'Component' decoupling
pattern, somewhat inspired by [this post](http://gameprogrammingpatterns.com/component.html)
by Bob Nystrom.

It exposes two classes, the `Socket` and the `Plug`. A plug should handle a single behaviour --
for example, should specify the portion of a spritemap that should be displayed -- and that's
it. It should then be connected to a socket, through which the plugs can communicate.

Through doing this, you should be able to have a small number of entities, which can be
controlled by connecting and disconnecting plugs as required to influence their behaviour.

Source is on github: https://github.com/ackwell/PyPlug
"""

from collections import defaultdict

# === Socket ===

class Socket(object):
	"""
	Handles `Plug` connections.
	All plugs will be given a reference to their parent `Socket`, through which they should
	interact with other plugs to perform their behaviour.
	"""

	def __init__(self):
		# Need to use `super().__setattr__` to avoid my own `__setattr__`
		super().__setattr__('_connections', defaultdict(list))
		super().__setattr__('_compiled_connections', [])

	def connect(self, plug, priority=0):
		"""
		Connect a plug to the socket.
		If multiple plugs that supply the same name are connected, the one loaded *last* will be
		used.

		An optional parameter `priority` can be passed, which will allow overriding the above.
		The higher the priority, the later it is considered to be loaded. A priority of `1` will
		*always* override a priority of `0` (the default). 
		"""
		plug.socket = self
		self._connections[priority].append(plug)
		self._compile_connections()
		plug.connected()

	def disconnect(self, plug):
		"""
		Disconnect the plug from the socket.

		If, for whatever reason, you have multiple references to the same plug in your socket's
		connections, this will remove all of them. But seriously, what are you doing?
		"""
		plug.disconnected()
		for priority in (item[0] for item in self._connections.items() if plug in item[1]):
			while True:
				try:
					self._connections[priority].remove(plug)
				except ValueError:
					break
		self._compile_connections()

	def _compile_connections(self):
		"""
		Private.

		Used to flatten the priority-based `_connections` dictionary into a single array to
		speed up looping.
		"""
		super().__setattr__('_compiled_connections', [])
		for _, connections in sorted(self._connections.items()):
			self._compiled_connections.extend(connections)

	def __getattr__(self, name):
		"""
		When a plug (or something else, for that matter) requests an attribute of the socket,
		delegate it to the connected plugs.
		"""
		result = None
		for connection, attr in self._find_supplies(name):
			result = getattr(connection, attr)
		return result

	def __setattr__(self, name, value):
		"""
		Much like with retrieving an attribute, if something attempts to set an attribute,
		delegate to connected plugs. Will set the attribute on *all* plugs that supply it.
		(possibly not the best choice, need to think on it.)
		"""
		for connection, attr in self._find_supplies(name):
			setattr(connection, attr, value)

	def _find_supplies(self, name):
		"""
		Private.

		Loops over avaliable connections to check if `name` is supplied by any of them, and
		yeilds the object and attribute name in the case it is supplied.
		"""
		supplied = False
		for connection in self._compiled_connections:
			if name in connection._supplies:
				supplied = True
				yield (connection, connection._supplies[name])

		# If no connection supplies `name`, throw a hissy about it.
		if not supplied:
			raise ValueError('The property `{}` is not supplied to this socket.'.format(name))

# === Plug ===

class Plug(object):
	"""
	A class used to define a single behaviour. Once connected to a `Socket`, can supply
	functionality and data containers to that socket.
	"""

	def __init__(self):
		self.socket = None
		self._supplies = {}

	def connected(self):
		"""
		This function will be called once the plug has been firmly connected to the socket.
		`self.socket` will be avaliable at this point.
		"""
		pass
	
	def disconnected(self):
		"""
		This function will be called as the plug is being disconnected from the socket.
		`self.socket` will be avaliable, but not for much longer. Use it to clean up any mess
		your plug might have generated.
		"""
		pass

	def supply(self, name, alias=None):
		"""
		Mark this plug's attribute `name` as being avaliable to the socket. (External objects/plugs
		can access it as a direct attribute of the socket.)

		If the optional parameter `alias` is passed, the attribute `name` will be avaliable on the
		socket as `alias`, instead.
		"""
		if not alias:
			alias = name
		self._supplies[alias] = name
